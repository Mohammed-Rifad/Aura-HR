# AURA HR
![tests](https://github.com/Mohammed-Rifad/Aura-HR/actions/workflows/tests.yml/badge.svg)

An HR platform with an AI assistant that can only see what you can see.

Employees, leave, attendance and company policy — plus an agent that answers
questions about them by calling the same scoped queries the REST API uses. It
can propose changes, but it can never make one without a person clicking
approve.


```mermaid
flowchart LR
    B["Browser"]
    N["Next.js 16<br/>Vercel"]
    D["Django REST<br/>Render · Docker"]
    S["Service layer<br/>every write goes through here"]
    A["Agent loop<br/>10 tools, max 6 steps"]
    P[("Postgres + pgvector<br/>Neon")]
    G["Gemini API"]

    B -->|JWT| N
    N -->|REST + SSE| D
    D --> S
    D --> A
    A -->|"same scoped queries"| S
    A <-->|"prompt / tool calls"| G
    S --> P
    A -->|"AIToolCall, AuditLog"| P
```

**Live demo:** https://aura-hr-rho.vercel.app
**API docs:** https://aura-hr-j0jp.onrender.com/api/docs/

> The backend is on a free tier and sleeps after 15 minutes idle. The first
> request may take ~50 seconds.

## Try it

| Role | Email | Password |
|---|---|---|
| Admin | `admin@aurahr.com` | `Password@123` |
| Manager | `manager@aurahr.com` | `Password@123` |
| Employee | `aaron.nguyen@aurahr.com` | `Password@123` |

Worth trying, in this order:

1. As the **manager**, open **Assistant** and ask
   *"Show me pending leave requests"*, then *"Approve the one for Robert
   Johnson"*. You get a confirmation card. Nothing has changed yet.
2. Click **Approve**. Now it has.
3. Sign in as the **employee** and ask the same question. The agent can't
   find it — same code, same tool, different user.

That third step is the point of the project.

## The AI layer

### The agent loop

No framework. A `while` loop that asks the model, runs whatever tool it asks
for, hands back the result, and repeats until it writes an answer — bounded
at six steps.

```
question → model → wants a tool? → run it (scoped to the user) → back to the model
                 → no tool?      → that's the answer
```

Ten tools, all read-only except two. Every one takes the authenticated user
as its first argument and filters through `common/scoping.py` — the single
definition of "which employee rows may this person see".

```mermaid
sequenceDiagram
    actor M as Manager
    participant UI as Next.js
    participant API as Django
    participant DB as Postgres
    participant G as Gemini

    M->>UI: "Approve Robert's leave"
    UI->>API: POST /ai/chat/stream/
    API->>G: question + tool descriptions
    G-->>API: call get_leave_requests
    API->>DB: query scoped to this manager
    API->>G: the rows
    G-->>API: call approve_leave_request

    Note over API: name is in WRITE_TOOLS<br/>the loop refuses to run it
    API->>DB: save PendingAction
    API-->>UI: "Approve 3 days for Robert?"
    Note over M,UI: nothing has changed

    M->>UI: clicks Approve
    UI->>API: POST /ai/actions/{id}/approve/
    Note over API: id only — arguments<br/>re-read from the row
    API->>DB: SELECT FOR UPDATE, can_approve()
    API->>DB: approve_leave() — balance moves
    API-->>UI: "Done."
```

### The approval gate

Two of the ten tools write. The loop refuses to run them:

```python
if call.name in WRITE_TOOLS:
    # don't run it — save it and ask a human
```

It writes a `PendingAction` row and tells the model it's waiting. A person
approves in a **separate HTTP request**, which re-reads the arguments from
that row — the browser only ever holds an ID, so a user can't be shown one
action and have their client submit another. Permission is re-checked at
execution time, and the row is locked with `select_for_update` so a
double-click can't approve twice.

Membership of `WRITE_TOOLS` is a set in the code. The model isn't consulted
and can't opt out, which is why prompt injection has nothing to persuade.

### RAG

Company documents are chunked, embedded with `gemini-embedding-2` (768
dimensions), and stored in Postgres with `pgvector`. Search filters
permissions **inside the SQL**:

```sql
WHERE (employee_id IS NULL OR employee_id IN (...))   -- first
ORDER BY embedding <=> :question                       -- then
LIMIT 5
```

Filtering afterwards in Python would leak: an unauthorised user would get a
*shorter* list, and the missing rows would tell them a document exists.

Retrieved passages are fenced with a random per-request token so a document
can't close the fence and issue instructions. Tested with a policy file
containing a planted injection — the agent ignored it, and couldn't have
executed the write anyway.

### Everything is logged

`AIToolCall` records every tool the agent ran, who asked, whether it was
allowed, and how long it took. Refusals are logged as carefully as
successes — they're the record of the scoping rules firing. Visible at
**AI activity** as an admin.

## Architecture

```
Next.js (Vercel)  ──►  Django REST (Render, Docker)  ──►  Postgres + pgvector (Neon)
                              │
                              └──►  Gemini API
```

| Decision | Why |
|---|---|
| Service layer owns every write | The rules hold for the API, the admin and the agent alike |
| Querysets are the security boundary | A permission class can't protect a list endpoint |
| No repository layer | Django's ORM is already one |
| Hand-written agent loop, not LangGraph | The approval gate spans two HTTP requests; the state had to be a Django model for the audit log anyway, and a checkpointer would have been a second store of the same thing |
| Server-sent events, not websockets | One-directional, and it works through any proxy |
| Threaded gunicorn workers | A stream holds a worker for ~15 seconds; the default sync worker would block the site |

## Security

- JWT with rotation and a blacklist; unverified accounts can't sign in
- Row scoping defined once in `common/scoping.py`, used by the API,
  the dashboard and every AI tool
- Append-only `AuditLog` and `AIToolCall` — no write path through the API
- Soft deletes; nothing is destroyed
- Agent permissions derive from the JWT, never from the conversation

## Stack

**Backend** — Django 6.0, DRF 3.17, Postgres + pgvector, `google-genai`,
gunicorn, Docker
**Frontend** — Next.js 16, React 19, Tailwind 4, Base UI, zustand, axios
**Infra** — Render, Vercel, Neon

~7,600 lines of Python and ~6,600 of TypeScript across 98 API endpoints.

## Running it locally

```bash
git clone https://github.com/Mohammed-Rifad/Aura-HR.git
cd Aura-HR

# Backend
cd backend
python -m venv venv && venv/Scripts/activate      # or source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                              # fill in DB and GEMINI_API_KEY
python manage.py migrate
python manage.py seed_demo
python manage.py runserver

# Frontend
cd ../frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
npm run dev
```

Postgres needs the `vector` extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

To load a policy document for the assistant to search:

```bash
python manage.py ingest_document sample_docs/employee_handbook.md --title "Employee Handbook"
```

## What I'd do next

Being honest about the edges:

- **Tests are thin.** 35 tests, all on the leave module — the part with
  arithmetic that must not drift. The rest is manually verified across all
  four roles.
- **No emailed invites.** An admin issues a temporary password and passes it
  on. The right version is a one-time link so the credential never goes
  through a third person, and a forced change on first login.
- **Uploaded files aren't persistent** — the free tier's disk is ephemeral.
  Document *chunks* live in Postgres so search works, but the original files
  don't survive a redeploy. S3 would fix it.
- **No background queue.** A long agent run holds a request open. Celery
  would move it off the request cycle.
