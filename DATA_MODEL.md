# Gazior Ops — Production Data Model

> **Stack:** Python (FastAPI) · SQLAlchemy ORM · PostgreSQL (with asyncpg and pgvector)  
> **Architecture:** Multi-tenant SaaS · AI-integrated · RBAC-enforced

This document outlines the data schemas. To ensure a fast go-to-market for the internal Gazior team, the models are split into **Phase 1 (Core MVP)** for immediate implementation, and **Phase 2 (SaaS & Enterprise)** for features that will be built later as the product scales for public release.

---

## 🟢 PHASE 1: Core MVP (Immediate Implementation)

These models are the absolute minimum required to get the team using Gazior Ops for daily task management.

### 1. Multi-Tenancy & Identity

#### `Workspace`
The root container for all projects, users, and settings.
- `id`: UUID (Primary Key)  
- `name`: String
- `slug`: String (Unique, e.g., `gazior-rnd`)
- `logo_url`: String (Nullable)
- `timezone`: String (default `UTC`)
- `description`: String(nullable)
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime (Nullable)
- `created_by_id`: UUID (Foreign Key -> User.id, Nullable)
- `updated_by_id`: UUID (Foreign Key -> User.id, Nullable)

#### `User`
Global identity for a person. A user can belong to multiple Workspaces.
- `id`: UUID (Primary Key)
- `email`: String (Unique)
- `full_name`: String
- `avatar_url`: String (Nullable)
- `hashed_password`: String — *bcrypt or argon2*
- `is_active`: Boolean (default `true`)
- `is_superadmin`: Boolean (default `false`) — *Grants access to the platform owner's dashboard*
- `last_login`: DateTime (Nullable)
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime (Nullable)
- `created_by_id`: UUID (Foreign Key -> User.id, Nullable)
- `updated_by_id`: UUID (Foreign Key -> User.id, Nullable)

#### `WorkspaceMember`
Maps Users to Workspaces with specific Role-Based Access Control (RBAC).
- `id`: UUID (Primary Key)
- `workspace_id`: UUID (Foreign Key -> Workspace.id)
- `user_id`: UUID (Foreign Key -> User.id)
- `role`: Enum (`OWNER`, `ADMIN`, `MEMBER`, `VIEWER`, `GUEST`)
- `joined_at`: DateTime
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime (Nullable)
- `created_by_id`: UUID (Foreign Key -> User.id, Nullable)
- `updated_by_id`: UUID (Foreign Key -> User.id, Nullable)

> **Index:** Unique composite on `(workspace_id, user_id)`.

#### `Invitation`
Manages the user onboarding flow into a workspace.
- `id`: UUID (Primary Key)
- `workspace_id`: UUID (Foreign Key -> Workspace.id)
- `inviter_id`: UUID (Foreign Key -> User.id)
- `email`: String — *Invitee's email*
- `role`: Enum (`OWNER`, `ADMIN`, `MEMBER`, `VIEWER`, `GUEST`)
- `token`: String (Unique) — *Secure random token for the invite link*
- `status`: Enum (`PENDING`, `ACCEPTED`, `EXPIRED`, `REVOKED`) (default `PENDING`)
- `expires_at`: DateTime
- `accepted_at`: DateTime (Nullable)
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime (Nullable)
- `created_by_id`: UUID (Foreign Key -> User.id, Nullable)
- `updated_by_id`: UUID (Foreign Key -> User.id, Nullable)

#### `Team` (Department)
Groups users into functional units (e.g., 'Engineering', 'Design').
- `id`: UUID (Primary Key)
- `workspace_id`: UUID (Foreign Key -> Workspace.id)
- `name`: String
- `lead_id`: UUID (Foreign Key -> User.id, Nullable)
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime (Nullable) 
- `created_by_id`: UUID (Foreign Key -> User.id, Nullable)
- `updated_by_id`: UUID (Foreign Key -> User.id, Nullable)

#### `TeamMember` (Pivot Table)
- `id` UUID (Primary Key)
- `team_id`: UUID (Foreign Key -> Team.id)
- `user_id`: UUID (Foreign Key -> User.id)
- `role`: Sring
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime (Nullable) 
- `created_by_id`: UUID (Foreign Key -> User.id, Nullable)
- `updated_by_id`: UUID (Foreign Key -> User.id, Nullable)


### 2. Organization & Workflow

#### `Initiative` (Roadmap / Goal)
High-level strategic objectives that map directly to the frontend `Overview` and `Roadmap` views.
- `id`: UUID (Primary Key)
- `workspace_id`: UUID (Foreign Key -> Workspace.id)
- `name`: String (e.g., 'Platform Foundation')
- `summary`: Text
- `owner_id`: UUID (Foreign Key -> User.id)
- `health_status`: Enum (`ON_TRACK`, `IN_REVIEW`, `NEEDS_FOCUS`, `COMPLETED`)
- `progress_percentage`: Integer (0-100)
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime (Nullable)
- `created_by_id`: UUID (Foreign Key -> User.id, Nullable)
- `updated_by_id`: UUID (Foreign Key -> User.id, Nullable)

#### `Project`
A collection of Tasks within a Workspace.
- `id`: UUID (Primary Key)
- `workspace_id`: UUID (Foreign Key -> Workspace.id)
- `name`: String
- `identifier`: String (e.g., `GAZ` — used to prefix task numbers like `GAZ-123`)
- `description`: Text (Nullable)
- `owner_id`: UUID (Foreign Key -> User.id)
- `status`: Enum (`PLANNED`, `ACTIVE`, `ON_HOLD`, `COMPLETED`, `ARCHIVED`) (default `PLANNED`)
- `visibility`: Enum (`PUBLIC`, `PRIVATE`) (default `PRIVATE`)
- `status_changed_at`: DateTime
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime (Nullable)
- `created_by_id`: UUID (Foreign Key -> User.id, Nullable)
- `updated_by_id`: UUID (Foreign Key -> User.id, Nullable)

> **Index:** Unique composite on `(workspace_id, identifier)`.

#### `Cycle`
Time-boxed boundaries for agile methodologies.
- `id`: UUID (Primary Key)
- `project_id`: UUID (Foreign Key -> Project.id)
- `name`: String (e.g., `Cycle 42`)
- `start_date`: Date
- `end_date`: Date
- `status`: Enum (`PLANNED`, `ACTIVE`, `COMPLETED`) (default `PLANNED`)
- `status_changed_at`: DateTime
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime (Nullable)
- `created_by_id`: UUID (Foreign Key -> User.id, Nullable)
- `updated_by_id`: UUID (Foreign Key -> User.id, Nullable)

### 3. Core Issue Tracker

#### `Task` (Issue / Ticket)
The central entity for work items.
- `id`: UUID (Primary Key)
- `workspace_id`: UUID (Foreign Key -> Workspace.id)
- `project_id`: UUID (Foreign Key -> Project.id)
- `cycle_id`: UUID (Foreign Key -> Cycle.id, Nullable)
- `parent_task_id`: UUID (Foreign Key -> Task.id, Nullable) — *Enables Epics and Sub-tasks*
- `number`: Integer (Auto-incrementing per project)
- `identifier`: String (Computed: `Project.identifier + '-' + number`, e.g., `GAZ-101`)
- `title`: String
- `description`: Text (Markdown enabled, Nullable)
- `status`: Enum (`BACKLOG`, `TODO`, `IN_PROGRESS`, `IN_REVIEW`, `DONE`, `CANCELED`) (default `BACKLOG`)
- `priority`: Enum (`URGENT`, `HIGH`, `MEDIUM`, `LOW`, `NONE`) (default `NONE`)
- `position`: Integer
- `assignee_id`: UUID (Foreign Key -> User.id, Nullable)
- `reporter_id`: UUID (Foreign Key -> User.id)
- `story_points`: Float (Nullable)
- `due_date`: Date (Nullable)
- `ai_summary`: Text (Nullable) — *Auto-generated summarization*
- `is_archived`: Boolean (default `false`)
- `archived_at`: DateTime (Nullable)
- `archived_by_id`: UUID (Foreign Key -> User.id, Nullable)
- `status_changed_at`: DateTime
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime (Nullable)
- `created_by_id`: UUID (Foreign Key -> User.id, Nullable)
- `updated_by_id`: UUID (Foreign Key -> User.id, Nullable)

> **Index:** Unique composite on `(project_id, number)`.

#### `TaskHistory`
Purpose:
Track field-level changes for tasks.
This powers:
* activity timeline
* audit logs
* debugging
* analytics

Schema:
- `id`: UUID (Primary Key)
- `task_id`: UUID (Foreign Key -> Task.id)
- `field_name`: String
- `old_value`: Text (Nullable)
- `new_value`: Text (Nullable)
- `changed_by_id`: UUID (Foreign Key -> User.id)
- `changed_at`: DateTime

#### `Label`
Tags for categorizing tasks.
- `id`: UUID (Primary Key)
- `project_id`: UUID (Foreign Key -> Project.id)
- `name`: String
- `color`: String (Hex code, e.g., `#FF5733`)

#### `TaskLabel` (Pivot Table)
- `id`: UUID (Primary Key)
- `task_id`: UUID (Foreign Key -> Task.id)
- `label_id`: UUID (Foreign Key -> Label.id)


### 4. Collaboration & Audit Trails

#### `Comment`
User discussions on a Task.
- `id`: UUID (Primary Key)
- `task_id`: UUID (Foreign Key -> Task.id)
- `author_id`: UUID (Foreign Key -> User.id, Nullable) — *Null when `is_system_event = true`*
- `content`: Text (Markdown)
- `is_system_event`: Boolean (default `false`) — *Represents an automated audit log entry*
- `edited_at`: DateTime (Nullable)
- `created_at`: DateTime
- `updated_at`: DateTime (default `created_at`) 
- `deleted_at`: DateTime (Nullable)
- `created_by_id`: UUID (Foreign Key -> User.id, Nullable)
- `updated_by_id`: UUID (Foreign Key -> User.id, Nullable)

#### `Attachment`
Files linked to tasks.
- `id`: UUID (Primary Key)
- `task_id`: UUID (Foreign Key -> Task.id)
- `uploader_id`: UUID (Foreign Key -> User.id)
- `file_name`: String 
- `file_url`: String (S3 URL or similar)
- `mime_type`: String
- `size_bytes`: Integer
- `created_at`: DateTime
- `updated_at`: DateTime
- `deleted_at`: DateTime (Nullable)
- `created_by_id`: UUID (Foreign Key -> User.id, Nullable)
- `updated_by_id`: UUID (Foreign Key -> User.id, Nullable)

#### `Update` (Announcement)
Team updates mapped to the frontend "Recent Updates" / Megaphone feed.
- `id`: UUID (Primary Key)
- `workspace_id`: UUID (Foreign Key -> Workspace.id)
- `author_id`: UUID (Foreign Key -> User.id)
- `title`: String
- `content`: Text (Markdown)
- `tag`: String (e.g., 'Launch', 'System', 'Performance')
- `department`: String (Nullable)
- `created_at`: DateTime

### 5. AI & Generative Integrations

#### `AITaskBreakdown`
Stores AI-generated sub-tasks derived from a description, pending user approval.
- `id`: UUID (Primary Key)
- `task_id`: UUID (Foreign Key -> Task.id)
- `proposed_subtasks`: JSON 
- `status`: Enum (`PENDING_REVIEW`, `APPROVED`, `REJECTED`) (default `PENDING_REVIEW`)
- `created_at`: DateTime

#### `AIContextKnowledge`
Stores vector embeddings for tasks/projects to enable semantic search (RAG pattern).
- `id`: UUID (Primary Key)
- `workspace_id`: UUID (Foreign Key -> Workspace.id) — *Required for tenant isolation*
- `entity_type`: String (e.g., `Task`, `Comment`, `Document`)
- `entity_id`: UUID
- `embedding`: Vector (pgvector extension in PostgreSQL) 
- `content_chunk`: Text 
- `created_at`: DateTime

---

##  PHASE 2: Future SaaS & Enterprise (To Build Later)

*These features add immense value for a public SaaS, but introduce significant complexity. They are documented here for future-proofing but should be skipped during the initial internal launch.*

### 6. Settings & Advanced Preferences

#### `WorkspaceSettings`
Workspace-level configurations.
- `id`: UUID (Primary Key)
- `workspace_id`: UUID (Foreign Key -> Workspace.id, Unique)
- `default_language`: String (e.g., `en-US`)
- `sso_enforced`: Boolean (default `false`)
- `allowed_email_domains`: JSON (Nullable)
- `updated_at`: DateTime

#### `ProjectSettings`
Project-specific preferences and workflow configurations.
- `id`: UUID (Primary Key)
- `project_id`: UUID (Foreign Key -> Project.id, Unique)
- `default_cycle_length_days`: Integer (e.g., `14`)
- `allow_guest_viewers`: Boolean (default `false`)
- `require_task_approvals`: Boolean (default `false`)
- `track_time_estimates`: Boolean (default `false`)
- `updated_at`: DateTime

#### `UserProfile`
User-specific preferences.
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key -> User.id, Unique) 
- `theme`: Enum (`LIGHT`, `DARK`, `SYSTEM`) (default `SYSTEM`)
- `timezone`: String (e.g., `America/New_York`) (default `UTC`)
- `email_notifications`: Boolean (default `true`)
- `bio`: Text (Nullable)
- `title`: String (Nullable)

### 7. Advanced Extensibility (Custom Fields)

#### `CustomField`
Allows users to define attributes specific to their project.
- `id`: UUID (Primary Key)
- `project_id`: UUID (Foreign Key -> Project.id)
- `name`: String (e.g., `Client Name`, `Severity`)
- `field_type`: Enum (`TEXT`, `NUMBER`, `DATE`, `DROPDOWN`, `BOOLEAN`)
- `options`: JSON (Nullable) 
- `is_required`: Boolean (default `false`)
- `display_order`: Integer (default `0`) 

#### `TaskCustomFieldValue`
Stores the actual data for custom fields on tasks.
- `id`: UUID (Primary Key)
- `task_id`: UUID (Foreign Key -> Task.id)
- `field_id`: UUID (Foreign Key -> CustomField.id)
- `value_text`: Text (Nullable) 
- `value_number`: Float (Nullable) 
- `value_date`: Date (Nullable)
- `value_boolean`: Boolean (Nullable) 
- `value_option`: String (Nullable)

### 8. Notifications & Subscriptions

#### `Notification`
In-app notifications delivered to users.
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key -> User.id) 
- `actor_id`: UUID (Foreign Key -> User.id, Nullable)
- `type`: Enum (`TASK_ASSIGNED`, `COMMENT_ADDED`, `STATUS_CHANGED`, `MENTION`, `INVITATION`)
- `entity_type`: String (e.g., `Task`, `Comment`)
- `entity_id`: UUID 
- `payload`: JSON (Nullable) 
- `read_at`: DateTime (Nullable) 
- `created_at`: DateTime

#### `TaskWatcher`
Tracks users subscribed to notifications for a task.
- `task_id`: UUID (Foreign Key -> Task.id)
- `user_id`: UUID (Foreign Key -> User.id)

### 9. Developer Integrations

#### `APIKey`
Programmatic access tokens scoped to a workspace.
- `id`: UUID (Primary Key)
- `workspace_id`: UUID (Foreign Key -> Workspace.id)
- `created_by_id`: UUID (Foreign Key -> User.id)
- `name`: String 
- `hashed_key`: String 
- `key_prefix`: String 
- `scopes`: JSON 
- `last_used_at`: DateTime (Nullable)
- `expires_at`: DateTime (Nullable) 
- `created_at`: DateTime
- `revoked_at`: DateTime (Nullable) 

#### `Webhook`
Workspace-level outbound event hooks for third-party integrations (e.g., Slack).
- `id`: UUID (Primary Key)
- `workspace_id`: UUID (Foreign Key -> Workspace.id)
- `created_by_id`: UUID (Foreign Key -> User.id)
- `name`: String (e.g., `Slack Alerts`)
- `url`: String 
- `secret`: String 
- `events`: JSON 
- `is_active`: Boolean (default `true`)
- `last_triggered_at`: DateTime (Nullable)
- `created_at`: DateTime

### 10. System Administration & Analytics (Dashboards)

To power high-level "Admin Dashboards" and operations efficiently, these tables prevent the API from having to run expensive `COUNT(*)` queries on millions of rows.

#### `SystemAuditLog` (Super Admin Level)
Logs critical system-wide operations.
- `id`: UUID (Primary Key)
- `actor_id`: UUID (Foreign Key -> User.id)
- `action`: String (e.g., `WORKSPACE_CREATED`, `USER_BANNED`)
- `ip_address`: String
- `metadata`: JSON
- `created_at`: DateTime

#### `ProjectVelocitySnapshot` (Project Dashboard)
Daily snapshot generated by cron jobs for project burn-down charts and overview metrics.
- `id`: UUID (Primary Key)
- `project_id`: UUID (Foreign Key -> Project.id)
- `date`: Date
- `total_tasks`: Integer
- `completed_tasks`: Integer
- `total_story_points`: Float
- `completed_story_points`: Float

#### `WorkspaceAnalyticsSnapshot` (Super Admin Dashboard)
Daily aggregate of workspace usage for the platform owner's billing/management dashboard.
- `id`: UUID (Primary Key)
- `workspace_id`: UUID (Foreign Key -> Workspace.id)
- `date`: Date
- `active_users`: Integer
- `new_tasks_created`: Integer
- `storage_used_bytes`: Integer

---

## Performance Index Recommendations

Task indexes:
* workspace_id
* project_id
* status
* assignee_id
* due_date
* created_at DESC
* is_archived

Soft delete optimization:
WHERE deleted_at IS NULL

## UUID Strategy

Use:
UUID v7

Reason:
* Better index performance
* Time-ordered IDs
* Scales better for large datasets

## Appendix — Design Decisions

- **Two-Phased Execution:** Complex features (Custom Fields, Webhooks, granular settings) are relegated to Phase 2 to prevent backend engineering gridlock during the initial MVP sprint.
- **`Comment.updated_at` defaults to `created_at`:** Avoids nullable ambiguity; clearly distinguishes "never edited" from "edited once".
- **Typed Columns in `TaskCustomFieldValue`:** Ensures type-safe filtering and sorting at the DB level, avoiding application-side casting later.
- **Tenant Isolation:** `AIContextKnowledge` explicitly requires `workspace_id` to prevent cross-tenant vector data leakage in similarity searches.
- **Security:** `APIKey` stores only a hash + prefix. `Invitation.token` is decoupled from its ID to prevent enumeration.
