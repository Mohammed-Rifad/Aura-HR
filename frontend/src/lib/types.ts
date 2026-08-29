export type Role = "ADMIN" | "HR" | "MANAGER" | "EMPLOYEE";

export type User = {
  id: string;
  email: string;
  employee: { id: string; employee_id: string } | null;
  first_name: string;
  last_name: string;
  full_name: string;
  phone: string;
  role: Role;
  profile_picture: string | null;
  is_verified: boolean;
  date_joined: string;
  last_login: string | null;
};

export type LoginResponse = {
  access: string;
  refresh: string;
  user: User;
};

/** Every list endpoint returns this shape — see common/pagination.py */
export type Paginated<T> = {
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

/** Every error returns this shape — see common/exceptions.py */
export type ApiError = {
  success: false;
  message: string;
  errors: Record<string, string[]>;
  code: string;
};

export type EmployeeStatus = "ACTIVE" | "ON_NOTICE" | "EXITED";

export type EmployeeListItem = {
  id: string;
  employee_id: string;
  full_name: string;
  email: string;
  department_name: string;
  designation_title: string;
  status: EmployeeStatus;
};

export type LeaveStatus = "PENDING" | "APPROVED" | "REJECTED" | "CANCELLED";

export type LeaveRequestListItem = {
  id: string;
  employee_code: string;
  employee_name: string;
  leave_type_code: string;
  start_date: string;
  end_date: string;
  days: string;          // DecimalField serialises as a string
  status: LeaveStatus;
  status_display: string;
};

export type LeaveType = {
  id: number;
  name: string;
  code: string;
  default_days_per_year: number;
  is_paid: boolean;
};

export type LeaveBalance = {
  id: string;
  leave_type: { id: number; name: string; code: string };
  year: number;
  allocated: string;
  used: string;
  pending: string;
  available: string;
};

export type AttendanceStatus = "PRESENT" | "HALF_DAY" | "ABSENT" | "ON_LEAVE";

export type Attendance = {
  id: string;
  employee_code: string;
  employee_name: string;
  date: string;
  check_in: string | null;
  check_out: string | null;
  work_hours: string;
  status: AttendanceStatus;
  status_display: string;
  notes: string;
};


// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

export type DepartmentCount = {
  code: string;
  name: string;
  count: number;
};

export type BalanceSummary = {
  code: string;
  name: string;
  allocated: string;
  used: string;
  available: string;
};

export type DashboardSummary = {
  headcount: number;
  headcount_total: number;
  by_department: DepartmentCount[];
  pending_approvals: number;
  expiring_documents: number;
  on_leave_today: number;
  my_balances: BalanceSummary[];
  expiring_soon: ExpiringDocument[];        // <- add
  awaiting_approval: AwaitingApproval[];    // <- add
};

export type ExpiringDocument = {
  id: string;
  employee_id: string;
  employee_name: string;
  document_type: string;
  expiry_date: string;
  days_left: number;
};

export type AwaitingApproval = {
  id: string;
  employee_name: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  days: string;
};


// ---------------------------------------------------------------------------
// Organisation
// ---------------------------------------------------------------------------

export type Department = {
  id: number;
  name: string;
  code: string;
  description: string;
  is_active: boolean;
  employee_count?: number;
};

export type Designation = {
  id: number;
  title: string;
  description: string;
  is_active: boolean;
};

export type EmployeeDocument = {
  id: string;
  document_type: string;
  document_type_display: string;
  document_number: string;
  file: string;
  issue_date: string | null;
  expiry_date: string | null;
  is_expiring_soon: boolean;
};

export type EmploymentType = "FULL_TIME" | "PART_TIME" | "CONTRACT" | "INTERN";

export type EmployeeDetail = {
  id: string;
  employee_id: string;
  user: User;
  department: { id: number; name: string; code: string };
  designation: { id: number; title: string };
  manager: EmployeeListItem | null;
  date_of_birth: string | null;
  date_of_joining: string;
  date_of_exit: string | null;
  employment_type: EmploymentType;
  status: EmployeeStatus;
  documents: EmployeeDocument[];
  created_at: string;
  updated_at: string;
};

export type AttendanceSummary = {
  year: number;
  month: number;
  days_recorded: number;
  total_hours: string;
  present: number;
  half_day: number;
  absent: number;
  on_leave: number;
};

/** One event off the /ai/chat/stream/ connection. */
export type ChatEvent =
  | { type: "start"; conversation: string }
  | { type: "tool"; name: string; args: Record<string, unknown> }
  | { type: "result"; name: string; ok: boolean }
  | { type: "proposal"; action_id: string; summary: string }
  | { type: "answer"; text: string }
  | { type: "error"; message: string }
  | { type: "done"; title: string };

export type PendingActionStatus =
  | "PENDING"
  | "APPROVED"
  | "REJECTED"
  | "EXPIRED"
  | "FAILED";

export type PendingAction = {
  id: string;
  summary: string;
  status: PendingActionStatus;
  is_open: boolean;
};

/** One bubble in the chat. */
export type ChatTurn = {
  id: string;
  role: "user" | "model";
  text: string;
  /** ok is undefined while the tool is still running. */
  tools: { name: string; ok?: boolean }[];
  action?: PendingAction;
};


export type AIToolCall = {
  id: string;
  tool_name: string;
  arguments: Record<string, unknown>;
  actor_label: string;
  allowed: boolean;
  error: string;
  duration_ms: number;
  result_size: number;
  created_at: string;
};

export type ApprovalLogEntry = {
  id: string;
  tool_name: string;
  summary: string;
  status: PendingActionStatus;
  requested_by: string;
  decided_by: string | null;
  decided_at: string | null;
  error: string;
  created_at: string;
};

export type AIActivitySummary = {
  total: number;
  refused: number;
  awaiting_approval: number;
  by_tool: { tool_name: string; count: number }[];
};


export type AuditAction =
  | "CREATE"
  | "UPDATE"
  | "DELETE"
  | "APPROVE"
  | "REJECT"
  | "CANCEL"
  | "LOGIN";

export type AuditLogEntry = {
  id: string;
  action: AuditAction;
  action_display: string;
  model_name: string;
  object_id: string;
  object_label: string;
  actor_label: string;
  /** { field: { before, after } } — one entry per field that changed. */
  changes: Record<string, { before: string | null; after: string | null }>;
  ip_address: string | null;
  created_at: string;
};
