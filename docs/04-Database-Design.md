# AURA HR - Database Design Document

**Project:** AURA HR - Enterprise HR & Employee Management Platform with Agentic AI  
**Document:** Database Design Specification  
**Version:** 1.0  
**Status:** Draft  
**Database:** PostgreSQL 16+

---

# Table of Contents

1. Database Overview
2. Database Architecture
3. Database Design Principles
4. Entity Relationship Overview
5. Authentication & Authorization Tables
6. Organization Management Tables
7. Employee Management Tables
8. Attendance Management Tables
9. Leave Management Tables
10. Recruitment Management Tables
11. Payroll Management Tables
12. Asset Management Tables
13. Document Management Tables
14. Notification Tables
15. Audit Logging Tables
16. AI Platform Database Design
17. RAG Knowledge Base Design
18. AI Workflow Engine Tables
19. Reporting & Analytics Tables
20. Database Indexing Strategy
21. Data Security Strategy
22. Soft Delete Strategy
23. Backup & Recovery Strategy
24. Future Database Expansion

---

# 1. Database Overview

## 1.1 Purpose

The AURA HR database is responsible for storing all operational, transactional, analytical, and AI-related information required by the platform.

The database supports:

- Employee lifecycle management
- Organization structure
- Attendance tracking
- Leave management
- Recruitment processes
- Payroll processing
- Asset tracking
- Document management
- AI conversations
- AI agent execution
- Knowledge retrieval
- Workflow automation
- Audit compliance

---

# 2. Database Architecture

AURA HR uses a hybrid data architecture.

```
                AURA HR DATA PLATFORM


                     PostgreSQL

                          |

    ------------------------------------------------

    |                    |                       |

Transaction Data      AI Data              Audit Data

    |                    |                       |


Employees             Agents              Logs
Attendance            Conversations       Activities
Payroll               Embeddings          Changes
Recruitment           Knowledge           Events
```

---

# 3. Database Technology

## Primary Database

PostgreSQL 16+

Reasons:
- ACID compliance
- Strong relational model
- Enterprise reliability
- Advanced indexing
- JSON support
- pgvector support

---

## Additional Storage

### Redis

Used for:
- Cache
- Background job queues
- Temporary AI state
- Rate limiting

---

### Object Storage

Used for:
- Employee documents
- Resumes
- Contracts
- Certificates
- Generated reports

Examples:
- AWS S3
- MinIO
- Azure Blob Storage

---

### Vector Storage

Technology:
PostgreSQL + pgvector

Used for:
- HR policies
- Knowledge documents
- AI semantic search

---

# 4. Database Design Principles

## 4.1 UUID Primary Keys

All major tables use UUID identifiers.

Example:
- `employee_id`
- `document_id`
- `conversation_id`

Benefits:
- Security
- Distributed system ready
- Microservice compatible

---

## 4.2 Timestamp Tracking

Every table contains:
- `created_at`
- `updated_at`

---

## 4.3 Audit Support

Critical tables maintain:
- `created_by`
- `updated_by`

---

## 4.4 Data Normalization

Database follows:
- Third Normal Form
- Avoid duplication
- Maintain consistency

---

# 5. Authentication & Authorization Tables

## 5.1 users

Purpose:
Stores login accounts.

Fields:

| Field | Type |
|---|---|
| id | UUID |
| email | VARCHAR |
| password_hash | VARCHAR |
| first_name | VARCHAR |
| last_name | VARCHAR |
| is_active | BOOLEAN |
| last_login | TIMESTAMP |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |

---

## 5.2 roles

Stores system roles.

Examples:
- Employee
- Manager
- HR
- Recruiter
- Payroll Admin
- Administrator
- CEO

Fields:

| Field | Type |
|---|---|
| id | UUID |
| name | VARCHAR |
| description | TEXT |

---

## 5.3 permissions

Stores granular permissions.

Examples:
- `employee.create`
- `employee.update`
- `leave.approve`
- `payroll.view`

Fields:

| Field | Type |
|---|---|
| id | UUID |
| module | VARCHAR |
| action | VARCHAR |
| description | TEXT |

---

## 5.4 user_roles

Relationship:
User Many-to-Many Role

Fields:

| Field | Type |
|---|---|
| user_id | UUID |
| role_id | UUID |

---

# 6. Organization Management Tables

## 6.1 companies

Purpose:
Supports future SaaS multi-tenancy.

Fields:

| Field | Type |
|---|---|
| id | UUID |
| name | VARCHAR |
| logo | VARCHAR |
| address | TEXT |
| timezone | VARCHAR |
| currency | VARCHAR |
| created_at | TIMESTAMP |

---

## 6.2 departments

Stores company departments.

Examples:
- IT
- HR
- Finance
- Marketing

Fields:

| Field | Type |
|---|---|
| id | UUID |
| company_id | UUID |
| name | VARCHAR |
| description | TEXT |
| manager_id | UUID |

---

## 6.3 designations

Stores employee positions.

Examples:
- Software Engineer
- Senior Developer
- Engineering Manager
- Director

Fields:

| Field | Type |
|---|---|
| id | UUID |
| department_id | UUID |
| title | VARCHAR |
| level | VARCHAR |

---

# 7. Employee Management Tables

## 7.1 employees

Main employee table.

Fields:

| Field | Type |
|---|---|
| id | UUID |
| user_id | UUID |
| employee_code | VARCHAR |
| first_name | VARCHAR |
| last_name | VARCHAR |
| email | VARCHAR |
| phone | VARCHAR |
| department_id | UUID |
| designation_id | UUID |
| manager_id | UUID |
| joining_date | DATE |
| employment_type | VARCHAR |
| employment_status | VARCHAR |

Employment Status:
- Active
- Probation
- On Leave
- Resigned
- Terminated

---

## 7.2 employee_profiles

Additional employee information.

Fields:
- `id`
- `employee_id`
- `address`
- `nationality`
- `emergency_contact`
- `marital_status`
- `blood_group`
- `profile_photo`

---

## 7.3 employee_skills

Stores employee skills.

Examples:
- Python
- Django
- React
- Machine Learning
- AWS

Fields:
- `id`
- `employee_id`
- `skill_name`
- `proficiency`

---

# 8. Attendance Management Tables

## 8.1 attendance_records

Stores daily attendance.

Fields:

| Field | Type |
|---|---|
| id | UUID |
| employee_id | UUID |
| attendance_date | DATE |
| check_in | TIMESTAMP |
| check_out | TIMESTAMP |
| working_hours | DECIMAL |
| status | VARCHAR |

Status:
- Present
- Absent
- Late
- Half Day
- Remote

---

## 8.2 attendance_corrections

Stores attendance correction requests.

Fields:
- `id`
- `employee_id`
- `date`
- `reason`
- `requested_time`
- `status`
- `approved_by`

---

# 9. Leave Management Tables

## 9.1 leave_types

Examples:
- Annual Leave
- Sick Leave
- Emergency Leave
- Maternity Leave

---

## 9.2 leave_balances

Stores employee leave balance.

Fields:
- `id`
- `employee_id`
- `leave_type_id`
- `allocated_days`
- `used_days`
- `remaining_days`

---

## 9.3 leave_requests

Fields:
- `id`
- `employee_id`
- `leave_type_id`
- `start_date`
- `end_date`
- `reason`
- `status`
- `approved_by`

---

# 10. Recruitment Management Tables

## 10.1 job_postings

Stores available positions.

Fields:
- `id`
- `department_id`
- `title`
- `description`
- `requirements`
- `status`
- `created_by`

---

## 10.2 candidates

Stores applicants.

Fields:
- `id`
- `name`
- `email`
- `phone`
- `resume_url`
- `experience`
- `skills`
- `status`

---

## 10.3 interviews

Stores interview process.

Fields:
- `id`
- `candidate_id`
- `interviewer_id`
- `schedule_time`
- `feedback`
- `status`

---

## 10.4 ai_candidate_scores

Stores AI evaluation.

Fields:
- `id`
- `candidate_id`
- `score`
- `strengths`
- `weaknesses`
- `recommendation`

---

# 11. Payroll Management Tables

## 11.1 salary_records

Stores salary information.

Fields:
- `id`
- `employee_id`
- `basic_salary`
- `allowances`
- `deductions`
- `effective_date`

---

## 11.2 payslips

Fields:
- `id`
- `employee_id`
- `month`
- `year`
- `gross_salary`
- `net_salary`
- `document_url`

---

# 12. Asset Management Tables

## 12.1 assets

Stores company assets.

Examples:
- Laptop
- Mobile
- Vehicle
- ID Card

Fields:
- `id`
- `asset_code`
- `category`
- `serial_number`
- `status`
- `purchase_date`

---

## 12.2 asset_assignments

Tracks ownership.

Fields:
- `id`
- `asset_id`
- `employee_id`
- `assigned_date`
- `returned_date`

---

# 13. Document Management Tables

## 13.1 documents

Stores metadata.

Fields:
- `id`
- `employee_id`
- `document_type`
- `file_path`
- `expiry_date`
- `uploaded_by`

Examples:
- Contract
- Passport
- Certificate
- Resume

---

# 14. Notification Tables

## notifications

Fields:
- `id`
- `user_id`
- `title`
- `message`
- `type`
- `is_read`
- `created_at`

---

# 15. Audit Logging Tables

## audit_logs

Tracks all important activities.

Fields:
- `id`
- `user_id`
- `module`
- `action`
- `old_value`
- `new_value`
- `ip_address`
- `created_at`

---

# 16. AI Platform Database Design

## 16.1 ai_agents

Stores AI agents.

Examples:
- HR Agent
- Recruitment Agent
- Analytics Agent
- Knowledge Agent

Fields:
- `id`
- `name`
- `description`
- `status`
- `configuration`

---

## 16.2 ai_conversations

Stores AI sessions.

Fields:
- `id`
- `user_id`
- `agent_id`
- `session_id`
- `created_at`

---

## 16.3 ai_messages

Stores chat messages.

Fields:
- `id`
- `conversation_id`
- `role`
- `content`
- `timestamp`

---

## 16.4 ai_tool_executions

Stores tool calls.

Fields:
- `id`
- `agent_id`
- `tool_name`
- `input`
- `output`
- `execution_time`
- `status`

---

# 17. RAG Knowledge Base Tables

## 17.1 knowledge_documents

Stores AI searchable documents.

Examples:
- HR Policy
- Employee Handbook
- Company Rules

---

## 17.2 document_chunks

Stores processed text.

Fields:
- `id`
- `document_id`
- `content`
- `metadata`
- `embedding`

---

# 18. Workflow Engine Tables

## workflows

Stores automated workflows.

Examples:
- Employee onboarding
- Leave approval
- Recruitment process

---

## workflow_steps

Stores workflow execution steps.

Fields:
- `id`
- `workflow_id`
- `step_name`
- `action`
- `sequence`

---

# 19. Database Indexing Strategy

Important indexes:
- `employee_code`
- `email`
- `department_id`
- `manager_id`
- `attendance_date`
- `leave_status`
- `created_at`

---

# 20. Data Security Strategy

Security measures:
- Encryption
- RBAC
- Permission checks
- Audit logging
- Restricted document access

---

# 21. Soft Delete Strategy

Critical records use soft deletion.

Fields:
- `is_deleted`
- `deleted_at`

Data is preserved for audit purposes.

---

# 22. Backup Strategy

Database:
- Daily backup

Documents:
- Cloud backup

Retention:
- Minimum 30 days

---

# 23. Future Database Expansion

Future improvements:
- Data warehouse
- Event streaming
- Graph database
- Advanced analytics
- AI organizational intelligence

---

# Conclusion

The AURA HR database architecture provides a scalable foundation for an enterprise HR platform with Agentic AI capabilities.

The design supports current business requirements while allowing future expansion into a complete AI-powered enterprise automation ecosystem.