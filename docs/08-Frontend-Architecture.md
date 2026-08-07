# AURA HR - Frontend Architecture Document

**Project:** AURA HR - Enterprise HR & Employee Management Platform with Agentic AI  
**Document:** Frontend Architecture Specification  
**Version:** 1.0  
**Framework:** Next.js + TypeScript  
**UI:** Tailwind CSS + shadcn/ui  

---

## Table of Contents

1. Frontend Overview
2. Frontend Architecture Principles
3. Technology Stack
4. Next.js Application Structure
5. Feature-Based Architecture
6. Routing Architecture
7. Component Architecture
8. Design System
9. State Management
10. API Integration
11. Authentication Flow
12. Role-Based UI Rendering
13. Dashboard Architecture
14. AI Assistant UI Architecture
15. Notification System
16. Form Management
17. Error Handling
18. Performance Optimization
19. Frontend Security
20. Development Standards

---

## 1. Frontend Overview

### 1.1 Purpose

The AURA HR frontend provides a modern enterprise interface for employees, managers, HR teams, and administrators.

The frontend handles:
* User interaction
* Dashboard visualization
* Forms
* Data tables
* AI assistant interface
* Notifications
* Reports
* Workflow approvals

### 1.2 Target Users

#### Employee
* Profile management
* Leave requests
* Attendance
* Documents
* AI HR assistant

#### Manager
* Team dashboard
* Leave approval
* Employee insights
* Performance reports

#### HR Team
* Employee management
* Recruitment
* Payroll
* Compliance

#### Administrator
* User management
* Permissions
* System configuration

---

## 2. Frontend Architecture Principles

### 2.1 Feature-Based Organization

The application is organized by business features rather than file types:
* `employees`
* `leave`
* `attendance`
* `recruitment`
* `ai`

**Benefits:**
* Easier maintenance
* Better scalability
* Independent feature development

### 2.2 Component Reusability

Common UI elements are shared across features:
* Button
* Modal
* Table
* Form
* Card
* Chart

### 2.3 Type Safety

The application strictly leverages TypeScript to deliver:
* Fewer runtime errors
* Enhanced IDE autocomplete
* Confident refactoring

---

## 3. Technology Stack

| Area | Technology |
| :--- | :--- |
| **Framework** | Next.js 15 |
| **Language** | TypeScript |
| **Styling** | Tailwind CSS |
| **Components** | shadcn/ui |
| **Forms** | React Hook Form |
| **Validation** | Zod |
| **Client State** | Zustand |
| **Server State** | TanStack Query |
| **Charts** | Recharts |
| **Icons** | Lucide React |

---

## 4. Next.js Application Structure

```text
frontend/
src/
├── app/
│   ├── (auth)/
│   └── (dashboard)/
├── components/
├── features/
│   ├── employees/
│   ├── attendance/
│   ├── leave/
│   ├── recruitment/
│   ├── payroll/
│   └── ai/
├── hooks/
├── services/
├── store/
├── types/
├── utils/
├── lib/
└── constants/
```

---

## 5. Feature-Based Architecture

Each feature module encapsulates its own UI, API handlers, state logic, and validation schemas:

```text
feature/
├── components/
├── hooks/
├── api/
├── types/
├── schemas/
└── utils/
```

### Example: Employee Module

```text
employees/
├── components/
│   ├── EmployeeTable.tsx
│   └── EmployeeForm.tsx
├── api/
│   └── employee.api.ts
├── types/
│   └── employee.types.ts
└── schemas/
    └── employee.schema.ts
```

---

## 6. Routing Architecture

The platform uses the Next.js App Router pattern:

```text
app/
├── login/
├── dashboard/
├── employees/
├── attendance/
├── leaves/
├── recruitment/
├── payroll/
├── ai-assistant/
└── settings/
```

### 6.1 Protected Routes

```text
User Opens Page ──> Check Token ──> Validate Session ──> Allow Access OR Redirect to Login
```

---

## 7. Component Architecture

### 7.1 Shared Components
Global components shared across modules:
* `Button`
* `Input`
* `Modal`
* `DataTable`
* `Navbar`
* `Sidebar`

### 7.2 Feature Components
Domain-specific view components:
* `EmployeeCard`
* `EmployeeProfile`
* `EmployeeTimeline`

### 7.3 Layout Components
App wrapper layouts:
* `DashboardLayout`
* `AuthLayout`
* `AdminLayout`

---

## 8. Design System

AURA HR follows an enterprise-grade dashboard design system with standardized UI patterns:

* **Navigation:** Sidebar, top navbar, dynamic breadcrumbs.
* **Data Display:** Data tables, information cards, analytical charts, key metric indicators.
* **Forms:** Text inputs, select dropdowns, date pickers, file upload dropzones.

---

## 9. State Management

### 9.1 Client State
* **Technology:** Zustand
* **Stores:** `authStore`, `uiStore`, `notificationStore`
* **Scope:** User session metadata, active theme settings, sidebar open/collapsed state, user preference flags.

### 9.2 Server State
* **Technology:** TanStack Query
* **Scope:** Remote API synchronization, response caching, optimistic updates, background refetching, mutation lifecycle handlers (e.g., `useEmployees()`).

---

## 10. API Integration

```text
React Component ──> Custom Hook ──> API Service ──> Django REST API
```

### Example Service Definition (`employee.api.ts`)
* `getEmployees()`
* `createEmployee()`
* `updateEmployee()`
* `deleteEmployee()`

---

## 11. Authentication Flow

```text
User Submits Credentials ──> Auth API ──> Issue JWT Token ──> Persist Token ──> Redirect to Dashboard
```

### Token Lifecycle
* Short-lived access tokens
* Secure refresh token rotation
* Silent background session renewal

---

## 12. Role-Based UI Rendering

The interface dynamically adapts navigation links and action controls based on user privileges:

* **Employee Access:** Dashboard, Leave, Attendance, Personal Documents, AI Assistant.
* **HR Access:** Executive Dashboard, Employee Directory, Recruitment Portal, Payroll Processing, System Reports.

```text
Permission Check ──> Render Authorized Components / Hide Restricted Actions
```

---

## 13. Dashboard Architecture

Dashboards render role-tailored widget configurations:

* **Employee Dashboard:** Today's Attendance, Leave Balances, Upcoming Holidays, My Documents, AI Assistant widget.
* **Manager Dashboard:** Direct Reports, Pending Approvals, Team Attendance Overview, Performance Highlights.
* **HR Dashboard:** Total Headcount, Open Requisitions, Attrition Metrics, Compliance Alerts, AI Organizational Insights.

---

## 14. AI Assistant UI Architecture

The embedded AI Assistant operates as a core workflow accelerator:

```text
User Input ──> AI Interface ──> AI Orchestrator ──> Structured Action Output ──> User Confirmation / Execution
```

### Capabilities
* Natural language chat interface
* Contextual conversation threads
* File dropzone for resume/document ingestion
* Interactive confirmation cards for sensitive operations
* Asynchronous workflow approval triggers

### Operational Example

```
User: "Generate joining letter for Ahmed."
AI:   "I found Ahmed's details. Would you like me to generate the letter?"
      [ Confirm & Generate ]  [ Cancel ]
```

---

## 15. Notification System

Provides real-time visibility into workflow updates and system events:

```text
Backend Event ──> Notification API ──> Frontend Query Poll / Socket ──> Notification Indicator Update
```

* Real-time toast alerts
* Centralized notification panel
* Read/unread state updates

---

## 16. Form Management

Form state and schema validation are coupled using **React Hook Form** and **Zod**.

### Example Schema Requirements
* `name`: Required string field
* `email`: Valid email format rule
* `joining_date`: Required date selection

---

## 17. Error Handling

The application provides graceful fallback boundaries for runtime exceptions:

* **API Errors:** Friendly toast notifications with error messages.
* **Validation Errors:** In-line form validation messaging.
* **Network Failures:** Connection retry indicators.
* **Permission Denied:** Clean authorization fallback views.

---

## 18. Performance Optimization

* **Code Splitting:** Dynamic feature imports with Next.js App Router.
* **Lazy Loading:** Asynchronous loading for resource-intensive heavy components (charts, modals).
* **Data Caching:** Intelligent query caching and deduplication using TanStack Query.
* **Image Optimization:** Automated image format conversion and responsive sizing using `next/image`.

---

## 19. Frontend Security

* Secure token persistence and authorization header injection
* Contextual HTML sanitization against cross-site scripting (XSS)
* Client-side and server-side input schema validation
* Role-based view guards on private page routes
* Strict HTTPS communication enforcement

---

## 20. Development Standards

* Full strict-mode TypeScript implementation
* Strict adherence to unified ESLint & Prettier rules
* Modular component architecture with strict single-responsibility patterns
* Complete encapsulation of feature boundaries
* Standardized semantic naming conventions across variables and hooks

---

## Conclusion

The AURA HR frontend architecture provides a scalable, maintainable, and modern enterprise application structure. The architecture supports traditional HR operations while providing an advanced AI-powered user experience through the integrated AI assistant.
