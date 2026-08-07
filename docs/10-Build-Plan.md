# AURA HR — 20-Day Build Plan

**Start:** 2026-08-07 · **Ship:** 2026-08-27
**Budget:** ~5–6 focused hours/day (~110 hours)
**Goal:** A deployed, demoable portfolio project that gets interviews.
**Protected priority:** AI depth. If time runs short, HR modules get cut — not the agent.

---

## 1. Scope decision

The architecture doc describes a 6–9 month system. This plan builds a **vertical slice** of it: fewer modules, but every one of them real, and an AI layer that genuinely works.

### In scope

| Area | What ships |
|---|---|
| Auth & RBAC | JWT login/refresh/logout, 4 roles, permission classes, `/me` |
| Organization | Department, Designation |
| Employees | Full profile, manager hierarchy, documents with expiry (visa/passport) |
| Leave | Leave types, balances, apply → approve/reject workflow |
| Attendance | Check-in/out, daily records, summaries |
| Audit | Every write action logged with actor, before/after |
| **AI agent** | LangGraph agent, real tool calling, **RBAC enforced inside tools**, tool-call audit log |
| **RAG** | Policy doc upload → chunk → embed → pgvector → permission-scoped retrieval |
| **Human-in-the-loop** | Write actions pause for approval, resume via checkpointer |
| Frontend | Next.js + shadcn/ui: dashboard, employee table, leave flows, **streaming AI workspace with visible tool calls** |
| Ship | Deployed with a live URL, README with GIFs, 3-min demo video |

### Explicitly out of scope

Payroll · Recruitment · Assets · Reports module · Notifications beyond in-app · Multi-tenancy · Celery (except one optional task) · Kubernetes · Microservices · Mobile

Say this out loud in interviews. "I scoped deliberately" is a senior signal. "I ran out of time" is not.

---

## 2. Tech decisions to lock in now

| Decision | Choice | Why |
|---|---|---|
| Database | **PostgreSQL + pgvector, hosted (Neon free tier)** from Day 1 | Avoids local pgvector install pain on Windows, and your dev DB *is* your deploy DB — no migration surprise on Day 18 |
| LLM | **Anthropic Claude** via `langchain-anthropic` | Best-in-class tool calling, which is the whole point of this project |
| Model | `claude-opus-5` (default) | $5/$25 per 1M tokens. `claude-sonnet-5` at $3/$15 is a reasonable cheaper swap — your call, but decide once and note it in an ADR |
| Embeddings | **Local `sentence-transformers` (all-MiniLM-L6-v2, 384-dim)** | Anthropic has no embeddings endpoint. Local means zero cost, no extra key, works offline — **and it's a strong interview answer**: "I didn't want employee documents leaving our infrastructure for embedding." Ties directly to the data-privacy gap in the architecture doc |
| Agent framework | LangGraph | Its `interrupt` + Postgres checkpointer is what makes human-in-the-loop actually work across HTTP |
| Frontend | Next.js App Router + Tailwind + shadcn/ui + TanStack Query + Zustand | As specified in your docs |
| Deploy | Railway or Render (backend + Postgres) + Vercel (frontend) | Free/cheap tiers, ~1 hour total |

**Budget for API spend:** roughly $20–40 across 20 days of development and testing. Set a spend limit in the console on Day 12.

---

## 3. The plan

### Phase 0 — Foundation (Days 1–3)

**Day 1 — Infrastructure**
- `git init`, `.gitignore` (`.env`, `venv/`, `db.sqlite3`, `media/`, `staticfiles/`, `__pycache__/`, `node_modules/`), first commit, push to GitHub
- Create Neon project, enable pgvector (`CREATE EXTENSION vector;`), put the connection string in `.env`, flip `DB_ENGINE=postgresql`
- Generate a real `SECRET_KEY`
- `requirements.txt`
- Decide `apps/` vs flat layout — **do it now**, it touches every import later
- Flesh out `common/`: `BaseModel` (already done), soft-delete mixin, custom DRF exception handler, standard response envelope

**Day 2 — Auth & RBAC**
- `users`: serializers, `/api/v1/auth/login|refresh|logout|me`, password change
- Permission classes: `IsHR`, `IsManager`, `IsOwnerOrHR`, plus a reusable role-check base
- Seed script (`manage.py seed_demo`) creating one user per role
- Test each endpoint with each role. This is your security foundation — get it right once

**Day 3 — Core models**
- `organizations`: Department, Designation
- `employees`: Employee (OneToOne User, self-FK manager, department, designation, dates, status), EmployeeDocument (type, file, issue/expiry date)
- Migrations, Django admin registration so you can eyeball data
- **The expiry dates matter** — they power the AI compliance demo

### Phase 1 — Core HR backend (Days 4–7)

**Day 4 — Employees API**
- Service layer (`employees/services.py`) + ViewSets, filtering, search, pagination
- Role-scoped querysets: employee sees self, manager sees team, HR sees all
- Document upload endpoint
- `drf-spectacular` for Swagger at `/api/docs/`

**Day 5 — Leave**
- Models: LeaveType, LeaveBalance, LeaveRequest (status enum, approver FK)
- `leave/services.py`: `apply_leave`, `approve_leave`, `reject_leave`, `get_balance` — with balance validation and overlap checks
- API + role-scoped approval permissions

**Day 6 — Attendance + Audit**
- Attendance: check-in/out endpoints, daily records, monthly summary
- `audit` app: generic `AuditLog` model + a service call from each write path (actor, action, model, object id, before, after, IP)
- The audit log is what makes AI actions traceable — it's a load-bearing part of the AI story, not a nice-to-have

**Day 7 — Buffer + demo data**
- Seed **60–80 realistic employees** across departments, with attendance history, leave records, and a handful of documents expiring in the next 30–60 days
- Tests for the leave service (balance math is the easiest thing to get subtly wrong)
- Catch up on anything that slipped

### Phase 2 — Frontend (Days 8–11)

**Day 8 — Shell & auth**
- `create-next-app`, Tailwind, shadcn/ui init, folder structure
- API client with automatic token refresh on 401
- Zustand auth store, login page, route protection, role-aware redirects

**Day 9 — Layout & dashboard**
- Sidebar + topbar, role-based nav
- Dashboard: stat cards, headcount-by-department chart, upcoming document expiries, pending approvals

**Day 10 — Employees UI**
- Data table: server-side sort/filter/paginate, search
- Detail page with tabs (profile, documents, leave history)
- Create/edit forms with React Hook Form + Zod

**Day 11 — Leave & attendance UI**
- Apply-leave form with live balance display
- Manager approvals inbox
- Attendance page + check-in/out widget

### Phase 3 — The AI layer (Days 12–17) ← this is the differentiator

**Day 12 — Agent skeleton**
- `ai` app. LLM provider abstraction (one module, one swap point)
- LangGraph `StateGraph`: agent node ↔ tool node, Postgres checkpointer, `thread_id` per conversation
- First 2 read-only tools: `search_employees`, `get_employee_details`
- `POST /api/v1/ai/chat` — non-streaming first, get it working end to end

**Day 13 — Tools + the security story**
- Full tool suite: `get_leave_balance`, `create_leave_request`, `approve_leave`, `get_expiring_documents`, `attendance_summary`, `headcount_analytics`
- **Every tool takes the calling user's identity and enforces permission inside itself.** An employee asking "show me everyone's salary" gets refused at the tool layer, not by the prompt
- `AIToolCall` model: log every invocation — tool, args, caller, allowed/denied, duration, result size
- Structured Pydantic schemas for tool args

**Day 14 — RAG**
- Document upload → text extraction (PDF/DOCX) → chunking → embed → pgvector
- `DocumentChunk` model with a `vector` column **and an ACL column**
- Retrieval **pre-filters by permission in the SQL WHERE clause** — not post-filtering. Be ready to explain why
- `search_policies` tool wired into the agent

**Day 15 — Human-in-the-loop**
- LangGraph `interrupt` before any write tool
- `PendingApproval` model, `GET /api/v1/ai/approvals`, `POST /api/v1/ai/approvals/{id}/{approve|reject}`
- Resume the graph from the checkpointer on approval
- This is the hardest part of the project. Budget the whole day

**Day 16 — Streaming + AI UI**
- SSE streaming endpoint
- AI workspace page: message stream, **live tool-call cards showing name/args/result**, approval prompts inline, conversation history
- The visible tool calls are what make the demo land. Don't skip the visual polish here

**Day 17 — AI hardening**
- Prompt injection guards: retrieved document content wrapped and marked as data, never instructions; no write tool fires on document-derived intent without confirmation
- Error handling, retry, graceful degradation when the API is down
- AI logs viewer page (token usage, tool calls, latency) — cheap to build, looks very professional

### Phase 4 — Ship (Days 18–20)

**Day 18 — Deploy**
- Dockerfile + `docker-compose.yml` for local parity
- Deploy backend (Railway/Render), frontend (Vercel), point at Neon
- Environment config, CORS, HTTPS, `collectstatic`, media storage
- Run the seed script against production. **Get a working live URL today** — don't leave this to Day 20

**Day 19 — Polish & bug bash**
- Loading skeletons, empty states, error boundaries, toasts
- Responsive check, dark mode
- Walk every user role through every flow and fix what breaks

**Day 20 — The pitch**
- README: what it is, architecture diagram (Mermaid), screenshots, GIF of the AI agent doing something real, setup instructions, tech decisions
- 3-minute demo video: log in as HR → ask the agent "which employees have visas expiring next month?" → watch the tools fire → ask it to draft leave approval → approval gate appears → approve → done
- Fix the architecture doc's broken fence and headings (30 min — it's linked from the README)
- Interview talking points doc: the 5 hardest problems and how you solved them

---

## 4. Weekly checkpoints

- **End of Day 7** — Backend API is complete and documented in Swagger. If not, cut attendance.
- **End of Day 11** — Frontend can log in, list employees, apply for leave. If not, cut the attendance UI.
- **End of Day 17** — Agent calls real tools with permission enforcement, RAG answers policy questions, approvals work. **If you are behind here, cut Day 15 (human-in-the-loop) before cutting Day 13 (tool-level RBAC).** Tool RBAC is the better interview story.
- **End of Day 20** — Live URL, README, video.

---

## 5. Interview talking points to bank as you go

Keep a running note. These are the answers that separate you from other candidates:

1. **"AI never touches the database."** Every agent action goes through a tool that validates permission, logs execution, and returns structured output.
2. **RBAC at the tool layer, not the prompt.** A prompt can be talked around. A permission check in Python cannot.
3. **Permission-scoped RAG via pre-filtering.** Post-filtering leaks through result ranking; pre-filtering pushes the ACL into the vector query.
4. **Human-in-the-loop across an HTTP boundary.** LangGraph interrupt + Postgres checkpointer + thread_id — explain why a stateless API makes this non-trivial.
5. **Indirect prompt injection.** An uploaded resume containing instructions is the real attack surface in an HR AI system. Explain what you did about it.
6. **Deliberate scope.** You cut payroll and recruitment to build one thing properly.

---

## 6. Daily rhythm

Each morning, say **"Day N"** and we'll work through that day's tasks together — I'll write code with you, explain each piece, and review what you built. At the end of each day, commit with a clear message. Your commit history is part of the portfolio.
