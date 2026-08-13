**Project:** AURA HR - Enterprise HR & Employee Management Platform with Agentic AI  
**Backend Framework:** Django + Django REST Framework  
**Version:** 1.0  
**Status:** Draft

---

# Table of Contents

1. Backend Overview
2. Backend Architecture Principles
3. Django Project Structure
4. Application Modules
5. Layered Architecture
6. API Architecture
7. Service Layer Design
8. Data Access with Model Managers
9. Model Design Principles
10. Authentication Architecture
11. Authorization System
12. Background Processing
13. Notification System
14. File Management
15. AI Integration Architecture
16. Error Handling
17. Logging Strategy
18. Testing Strategy
19. Backend Development Standards

---

# 1. Backend Overview

## 1.1 Purpose

The AURA HR backend provides the core business logic and APIs required for the HR platform.

Responsibilities:

- User authentication
- Employee management
- Recruitment management
- Attendance processing
- Leave workflows
- Payroll operations
- Document handling
- AI agent communication
- Notification processing
- Audit tracking

---

## 1.2 Backend Technology Stack

| Component | Technology |
|---|---|
| Framework | Django |
| API | Django REST Framework |
| Database | PostgreSQL |
| Cache | Redis |
| Background Jobs | Celery |
| Authentication | JWT |
| AI Framework | LangGraph + LangChain |
| Storage | S3 Compatible Storage |

---

# 2. Backend Architecture Principles

## 2.1 Separation of Concerns

The backend follows:

```
API
 ↓
Business Logic
 ↓
Data Access
 ↓
Database
```

Each layer has a specific responsibility.

---

## 2.2 Modular Design

Each business domain is an independent Django application.

Example:
- `employees`
- `attendance`
- `leave`
- `recruitment`
- `ai`

Benefits:

- Easier maintenance
- Independent development
- Future microservice migration

---

## 2.3 Service-Based Business Logic

Business rules should NOT exist inside views.

**Wrong:**

```python
class EmployeeView(APIView):
    def post(self, request):
        # Direct view save logic
        save_employee()
```

**Correct:**

```
View
 ↓
EmployeeService
 ↓
Employee.objects  (model manager)
 ↓
Database
```

---

# 3. Django Project Structure

Recommended structure:

```
backend/
├── config/
│   ├── settings/
│   ├── urls.py
│   └── celery.py
├── apps/
│   ├── authentication/
│   ├── users/
│   ├── organization/
│   ├── employees/
│   ├── attendance/
│   ├── leave/
│   ├── recruitment/
│   ├── payroll/
│   ├── assets/
│   ├── documents/
│   ├── notifications/
│   ├── reports/
│   ├── ai/
│   └── audit/
├── common/
├── requirements/
├── manage.py
└── Dockerfile
```

---

# 4. Application Modules

## 4.1 Authentication App
Responsible for:
- Login
- Logout
- JWT tokens
- Password reset
- User sessions

## 4.2 Employee App
Responsible for:
- Employee profiles
- Employee lifecycle
- Skills
- Documents
- Reporting hierarchy

## 4.3 Attendance App
Responsible for:
- Check-in
- Check-out
- Attendance calculation
- Attendance correction

## 4.4 Leave App
Responsible for:
- Leave application
- Approval workflow
- Leave balance calculation

## 4.5 Recruitment App
Responsible for:
- Job posting
- Candidates
- Interviews
- AI resume analysis

## 4.6 Payroll App
Responsible for:
- Salary processing
- Payslips
- Payroll reports

## 4.7 AI App
Responsible for:
- AI gateway
- Agent execution
- Tool calling
- RAG
- AI logs

---

# 5. Layered Architecture

AURA HR follows a four-layer backend architecture.

```
              API Layer          views, serializers, permissions
                 ↓
          Service Layer          business rules, transactions, audit
                 ↓
     Model / Manager Layer       queries and persistence
                 ↓
             Database
```

## 5.1 API Layer
**Technology:** Django REST Framework

**Responsibilities:**
- Receive HTTP requests
- Validate input
- Authenticate users
- Return responses

**Contains:**
- `views.py`
- `serializers.py`
- `urls.py`
- `permissions.py`

**Example Endpoints:**
- `POST /api/employees/`
- `GET /api/employees/`
- `PUT /api/employees/{id}`

---

## 5.2 Service Layer
Contains business logic.

**Example Functions:**

*Employee Service:*
- `create_employee()`
- `update_employee()`
- `terminate_employee()`

*Leave Service:*
- `apply_leave()`
- `approve_leave()`
- `calculate_balance()`

*AI Service:*
- `execute_agent()`
- `process_document()`
- `generate_response()`

---

## 5.3 Model / Manager Layer
**Purpose:** Queries and persistence.

There is no separate repository layer — Django's model manager already is one.
Reusable queries live on custom managers.

**Example — `EmployeeManager`:**
- `active()`
- `for_manager(user)`
- `with_expiring_documents(days)`

**Benefits:**
- Named, reusable queries
- Still lazy and chainable, so `select_related` and pagination keep working
- One less layer to maintain

See ADR-008 in `03-System-Architecture.md`.

---

# 6. API Architecture

## REST API Structure
Base URL: `/api/v1/`

### Employee APIs
- `GET /api/v1/employees/`
- `POST /api/v1/employees/`
- `GET /api/v1/employees/{id}`
- `PUT /api/v1/employees/{id}`

### Leave APIs
- `GET /leaves/`
- `POST /leaves/`
- `POST /leaves/{id}/approve/`
- `POST /leaves/{id}/reject/`

### AI APIs
- `POST /api/v1/ai/chat/`
- `POST /api/v1/ai/document/analyze/`
- `POST /api/v1/ai/workflow/`

---

# 7. Service Layer Design

Example: **Employee Creation Flow**

```
API Request
 ↓
EmployeeView
 ↓
EmployeeService
 ↓
Validation
 ↓
Employee.objects
 ↓
Database
 ↓
Audit Log
 ↓
Notification
```

---

# 8. Data Access with Model Managers

We do not implement the repository pattern separately. `Model.objects` is
already a repository, and wrapping it costs more than it returns — a wrapper
that returns lists instead of querysets breaks laziness, chaining,
`select_related`, and pagination.

Reusable queries go on a custom manager:

```python
class EmployeeManager(models.Manager):
    def active(self):
        return self.filter(status=Employee.Status.ACTIVE)

    def for_manager(self, user):
        """Only the people who report to this user."""
        return self.active().filter(manager__user=user)

    def with_expiring_documents(self, days=30):
        cutoff = timezone.now().date() + timedelta(days=days)
        return self.active().filter(
            documents__expiry_date__lte=cutoff
        ).distinct()
```

Used from a service:

```python
def list_team(manager_user):
    return Employee.objects.for_manager(manager_user).select_related("department")
```

Rule of thumb for where logic goes:

| Situation | Put it in |
|---|---|
| One model, plain save | Serializer |
| Multiple models, rules, or a transaction | Service |
| A query you write more than once | Manager |

See ADR-008 in `03-System-Architecture.md`.

---

# 9. Model Design Principles

Models should:
- Represent data only
- Avoid business logic
- Have clear relationships

Example: **Employee Model**

```python
class Employee(models.Model):
    employee_code = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
```

---

# 10. Authentication Architecture

Authentication uses: **JWT Authentication**

**Flow:**

```
User Login
 ↓
Validate Credentials
 ↓
Generate JWT
 ↓
Frontend Stores Token
 ↓
API Requests
 ↓
Token Verification
```

---

# 11. Authorization System

Uses: **Role Based Access Control (RBAC)**

Examples:
- **Employee:** View own profile, apply leave
- **Manager:** Approve team leave
- **HR:** Manage employees

---

# 12. Background Processing

Technology: **Celery + Redis**

Used for:
- Emails
- Reports
- AI processing
- Document generation

Example Flow:

```
Resume Uploaded
 ↓
Celery Task
 ↓
AI Analysis
 ↓
Save Result
 ↓
Notify Recruiter
```

---

# 13. Notification System

Architecture:

```
Business Event
 ↓
Notification Service
 ↓
Queue
 ↓
Email / In-App Notification
```

---

# 14. File Management

Files are **NOT** stored in the database.

Database stores:
- `file_url`
- `file_type`
- `metadata`

Actual files are stored in: **AWS S3**

---

# 15. AI Integration Architecture

Backend communicates with the AI layer.

Flow:

```
User
 ↓
Django API
 ↓
AI Service
 ↓
LangGraph Agent
 ↓
Tools
 ↓
Business Services
 ↓
Response
```

---

# 16. Error Handling

Standard error response format:

```json
{
  "success": false,
  "message": "Permission denied",
  "error_code": "AUTH_001"
}
```

---

# 17. Logging Strategy

Logs captured:
- Application logs
- API logs
- Security logs
- AI execution logs

---

# 18. Testing Strategy

Testing levels:
- **Unit Testing:** Services, Utilities
- **API Testing:** Endpoints, Authentication, Permissions
- **Integration Testing:** Database, AI workflows, Background jobs

---

# 19. Backend Development Standards

Rules:
- Use type hints
- Follow PEP8
- Write reusable services
- Avoid business logic in views
- Write tests for critical modules
- Maintain documentation

---

# Conclusion

The AURA HR backend architecture provides a scalable, maintainable, enterprise-grade foundation. The design supports traditional HR operations while allowing advanced Agentic AI capabilities through secure integration.