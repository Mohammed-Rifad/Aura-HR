# AURA HR - API Specification Document

**Project:** AURA HR - Enterprise HR & Employee Management Platform with Agentic AI  
**Document:** REST API Specification  
**Version:** 1.0  
**Backend:** Django REST Framework  
**API Version:** v1  

---

## Table of Contents

1. API Overview
2. API Design Principles
3. Base URL Structure
4. Authentication APIs
5. User APIs
6. Organization APIs
7. Employee APIs
8. Attendance APIs
9. Leave APIs
10. Recruitment APIs
11. Payroll APIs
12. Asset APIs
13. Document APIs
14. Notification APIs
15. AI APIs
16. Reporting APIs
17. Error Handling
18. Pagination
19. Filtering and Searching
20. API Security

---

## 1. API Overview

### Purpose

The AURA HR API provides communication between frontend applications, backend services, and AI systems.

The API handles:
* Authentication
* Employee operations
* HR workflows
* Recruitment
* AI interaction
* Reports
* Notifications

---

## 2. API Design Principles

The API follows strict standards to ensure consistency and reliability across services.

### REST Architecture
Resources are represented logically as URLs:
* `/employees/`
* `/leaves/`
* `/documents/`

### Versioning
All APIs use explicit version tags in the path segment:
* `/api/v1/employees/`

### JSON Communication
Requests and responses use standard JSON formatting:

**Request Format:**
```json
{
  "name": "Ahmed"
}
```

**Response Format:**
```json
{
  "success": true,
  "data": {}
}
```

---

## 3. Base URL Structure

* **Production:** `https://api.aura-hr.com/api/v1/`
* **Development:** `http://localhost:8000/api/v1/`

---

## 4. Authentication APIs

### 4.1 Login
* **Endpoint:** `POST /auth/login/`
* **Purpose:** Authenticate user and issue authorization tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "user": {
    "id": "uuid",
    "name": "Ahmed",
    "role": "HR"
  }
}
```

### 4.2 Refresh Token
* **Endpoint:** `POST /auth/token/refresh/`

**Request:**
```json
{
  "refresh": "token"
}
```

**Response:**
```json
{
  "access": "new_access_token"
}
```

### 4.3 Logout
* **Endpoint:** `POST /auth/logout/`

---

## 5. User APIs

### Get Current User
* **Endpoint:** `GET /users/me/`

**Response:**
```json
{
  "id": "uuid",
  "name": "Ahmed",
  "email": "ahmed@test.com",
  "role": "Manager"
}
```

---

## 6. Organization APIs

### Departments

#### List Departments
* **Endpoint:** `GET /departments/`

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "IT"
  }
]
```

#### Create Department
* **Endpoint:** `POST /departments/`

**Request:**
```json
{
  "name": "Artificial Intelligence"
}
```

### Designations

#### List Designations
* **Endpoint:** `GET /designations/`

---

## 7. Employee APIs

### 7.1 List Employees
* **Endpoint:** `GET /employees/`
* **Query Parameters:** `?page=1&department=IT&status=active&search=Ahmed`

**Response:**
```json
{
  "count": 100,
  "results": [
    {
      "id": "uuid",
      "name": "Ahmed",
      "department": "IT",
      "designation": "Developer"
    }
  ]
}
```

### 7.2 Create Employee
* **Endpoint:** `POST /employees/`
* **Permission:** HR / Admin

**Request:**
```json
{
  "first_name": "Ahmed",
  "last_name": "Ali",
  "department": "IT",
  "designation": "Developer",
  "joining_date": "2026-08-01"
}
```

### 7.3 Get Employee Details
* **Endpoint:** `GET /employees/{id}/`

**Response:**
```json
{
  "id": "uuid",
  "name": "Ahmed",
  "skills": ["Python", "Django"],
  "department": "IT"
}
```

### 7.4 Update Employee
* **Endpoint:** `PUT /employees/{id}/`

### 7.5 Employee Timeline
* **Endpoint:** `GET /employees/{id}/timeline/`
* **Returns:** Joining, Promotions, Transfers, Documents, Leave history.

---

## 8. Attendance APIs

### 8.1 Check In
* **Endpoint:** `POST /attendance/check-in/`

**Request:**
```json
{
  "employee_id": "uuid"
}
```

### 8.2 Check Out
* **Endpoint:** `POST /attendance/check-out/`

### 8.3 Attendance History
* **Endpoint:** `GET /attendance/`
* **Filters:** `employee`, `month`, `year`, `status`

### 8.4 Attendance Report
* **Endpoint:** `GET /attendance/report/`

---

## 9. Leave APIs

### 9.1 Apply Leave
* **Endpoint:** `POST /leaves/`

**Request:**
```json
{
  "type": "Annual Leave",
  "start_date": "2026-08-10",
  "end_date": "2026-08-12",
  "reason": "Family event"
}
```

### 9.2 Leave Balance
* **Endpoint:** `GET /leaves/balance/`

**Response:**
```json
{
  "annual": 20,
  "sick": 10
}
```

### 9.3 Approve Leave
* **Endpoint:** `POST /leaves/{id}/approve/`
* **Permission:** Manager

### 9.4 Reject Leave
* **Endpoint:** `POST /leaves/{id}/reject/`

---

## 10. Recruitment APIs

### 10.1 Job Posting
* **Create Endpoint:** `POST /jobs/`

**Request:**
```json
{
  "title": "Python Developer",
  "description": "Backend Developer"
}
```

### 10.2 Candidates
* **List Endpoint:** `GET /candidates/`

### 10.3 Upload Resume
* **Endpoint:** `POST /candidates/{id}/resume/`

### 10.4 AI Candidate Analysis
* **Endpoint:** `POST /candidates/{id}/analyze/`

**Response:**
```json
{
  "score": 87,
  "recommendation": "Strong Candidate"
}
```

---

## 11. Payroll APIs

### Salary
* **Endpoint:** `GET /employees/{id}/salary/`

### Generate Payslip
* **Endpoint:** `POST /payroll/generate/`

**Request:**
```json
{
  "employee_id": "uuid",
  "month": "August",
  "year": 2026
}
```

---

## 12. Asset APIs

### List Assets
* **Endpoint:** `GET /assets/`

### Assign Asset
* **Endpoint:** `POST /assets/{id}/assign/`

**Request:**
```json
{
  "employee_id": "uuid"
}
```

---

## 13. Document APIs

### Upload Document
* **Endpoint:** `POST /documents/`
* **Request Format:** Multipart form data (`file`, `document_type`, `employee_id`)

### Download Document
* **Endpoint:** `GET /documents/{id}/download/`

---

## 14. Notification APIs

### Get Notifications
* **Endpoint:** `GET /notifications/`

### Mark As Read
* **Endpoint:** `POST /notifications/{id}/read/`

---

## 15. AI APIs

### 15.1 AI Chat
* **Endpoint:** `POST /ai/chat/`

**Request:**
```json
{
  "message": "How many leave days do I have?"
}
```

**Response:**
```json
{
  "answer": "You have 20 annual leave days remaining."
}
```

### 15.2 AI Agent Execution
* **Endpoint:** `POST /ai/execute/`

**Request:**
```json
{
  "task": "Generate employee joining letter",
  "employee_id": "uuid"
}
```

### 15.3 Document Analysis
* **Endpoint:** `POST /ai/document/analyze/`
* **Usage:** Resume analysis, Policy analysis, Contract review.

### 15.4 AI Workflow
* **Endpoint:** `POST /ai/workflow/start/`

**Request:**
```json
{
  "workflow": "employee_onboarding",
  "employee_id": "uuid"
}
```

---

## 16. Reporting APIs

### Employee Statistics
* **Endpoint:** `GET /reports/employees/`
* **Returns:** Total employees, Department distribution, Joining trends.

### Attendance Analytics
* **Endpoint:** `GET /reports/attendance/`

### Attrition Analysis
* **Endpoint:** `GET /reports/attrition/`

---

## 17. Error Handling

### Standard Error Format
```json
{
  "success": false,
  "error": {
    "code": "EMPLOYEE_001",
    "message": "Employee not found"
  }
}
```

### Common Error Codes

| Code | Meaning |
| :--- | :--- |
| `AUTH_001` | Invalid login |
| `AUTH_002` | Permission denied |
| `EMP_001` | Employee not found |
| `VALID_001` | Invalid data |
| `SERVER_001` | Internal error |

---

## 18. Pagination

* **Default Parameters:** `page=1`, `page_size=20`

**Response Structure:**
```json
{
  "count": 200,
  "next": "http://api.aura-hr.com/api/v1/employees/?page=2",
  "previous": null,
  "results": []
}
```

---

## 19. Filtering and Searching

* **Search Example:** `/employees/?search=Ahmed`
* **Filtering Example:** `/employees/?department=IT`
* **Ordering Example:** `/employees/?ordering=joining_date`

---

## 20. API Security

All protected APIs require the following header:
```
Authorization: Bearer JWT_TOKEN
```

### Core Security Controls
* Permission checks (Role-Based Access Control)
* Rate limiting
* Request validation against schemas
* Comprehensive audit logging
* HTTPS encryption strictly enforced

---

## Conclusion

The AURA HR API architecture provides a clean, scalable, and secure communication layer between frontend applications, backend services, and AI systems. The API design supports enterprise HR operations while enabling advanced Agentic AI workflows.
