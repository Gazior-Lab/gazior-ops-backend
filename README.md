# Gazior Ops Backend

A scalable, production-ready backend system for **Gazior Ops** — a multi-tenant SaaS task management and operations platform built with FastAPI and PostgreSQL.

> **Stack:** Python · FastAPI · SQLAlchemy 2.0 (async) · PostgreSQL (asyncpg) · Pydantic · JWT Auth  
> **Architecture:** Layered (Clean) Architecture · Async-first · RBAC-enforced

---

## 📋 Table of Contents

- [Changelog](#-changelog)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture-overview)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Database Models](#️-database-models)
- [Environment Variables](#-environment-variables)
- [Development](#-development)
- [Testing](#-testing)
- [Project Structure](#-project-structure)
- [Security](#-security)

---

## 📅 Changelog

### `v1.2.0` — Team & Team Member API *(Latest)*

- ✅ **New:** `GET /api/v1/teams` — List teams scoped to a workspace
- ✅ **New:** `GET /api/v1/teams/{team_id}` — Get a single team by ID
- ✅ **New:** `POST /api/v1/teams` — Create a team (OWNER/ADMIN only)
- ✅ **New:** `PATCH /api/v1/teams/{team_id}` — Rename team or change lead
- ✅ **New:** `DELETE /api/v1/teams/{team_id}` — Soft-delete a team
- ✅ **New:** `GET /api/v1/teams/{team_id}/members` — List team members
- ✅ **New:** `POST /api/v1/teams/{team_id}/members` — Add a user to a team
- ✅ **New:** `PATCH /api/v1/teams/{team_id}/members/{user_id}` — Update member role
- ✅ **New:** `DELETE /api/v1/teams/{team_id}/members/{user_id}` — Remove a member
- ✅ **New:** `TeamMemberRole` enum (`LEAD`, `MEMBER`, `VIEWER`) in `core/enums/common.py`
- ✅ **New:** `TeamRepository`, `TeamMemberRepository`, `TeamService`
- ✅ **New:** Pydantic schemas for Team and TeamMember
- ✅ **New:** Demo data in `demo_data/team.json`
- ✅ **Updated:** `tests/test_app_surface.py` — 9 team routes verified in smoke test

### `v1.1.0` — Task Management API

- Full Task CRUD with filtering, pagination, and archiving
- Bulk status update endpoint
- Task identifier lookup (`/tasks/identifier/{identifier}`)
- Task soft-delete with `deleted_at` tracking

### `v1.0.0` — Foundation

- JWT authentication (`register`, `login`, `me`)
- Multi-tenant Workspaces with RBAC
- Workspace member management (invite, update role, remove)
- Workspace invitation workflow
- Core layered architecture (API → Service → Repository → Model)

---

## ✨ Features

### Core Functionality

- 🔐 **Authentication & Authorization** — JWT-based auth with OAuth2 password flow
- 👥 **Multi-Tenant Workspaces** — RBAC with roles: OWNER, ADMIN, MEMBER, VIEWER, GUEST
- ✅ **Task Management** — Full CRUD with filtering, pagination, bulk operations, and archiving
- 🏢 **Team Management** — Create functional units (e.g., Engineering, Design) within workspaces; manage membership with LEAD / MEMBER / VIEWER roles
- 🏗️ **Project Organization** — Projects, cycles, initiatives, and teams
- 🏷️ **Labels & Tags** — Task categorization with custom labels
- 💬 **Comments & Attachments** — Collaboration tools with markdown support
- 📊 **Audit Trails** — Task history tracking and system audit logs

### Security Features

- 🔒 **Workspace-level Authorization** — Every endpoint verifies workspace membership
- 👮 **Team Admin Guard** — Team and TeamMember mutations require workspace OWNER or ADMIN
- 🔑 **Password Validation** — Strength requirements (8+ chars, mixed case, digits)
- 🛡️ **Soft Deletes** — All deletions are reversible with `deleted_at` tracking
- 🔍 **Input Validation** — Strict Pydantic schemas on all request/response boundaries
- 🚫 **Error Sanitization** — No internal error details exposed to clients

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Framework** | [FastAPI](https://fastapi.tiangolo.com/) (Async) |
| **Database** | PostgreSQL with [asyncpg](https://magicstack.github.io/asyncpg/) |
| **ORM** | [SQLAlchemy 2.0](https://docs.sqlalchemy.org/) (async sessions) |
| **Validation** | [Pydantic](https://docs.pydantic.dev/) v2 |
| **Auth** | JWT (PyJWT) with OAuth2 |
| **Migrations** | Alembic (async support) |
| **Password Hashing** | Argon2 (via pwdlib) |
| **Package Management** | pip / pyproject.toml |
| **Code Quality** | Ruff, Mypy, Pytest |

---

## 📂 Architecture Overview

This backend follows a **Layered (Clean) Architecture** with strict separation of concerns:

```
┌─────────────────────────────────────────────────┐
│  API Layer (app/api/)                           │
│  - FastAPI routers & endpoints                  │
│  - Request/Response handling                    │
│  - Dependency injection (get_db, get_current_user)│
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  Service Layer (app/services/)                  │
│  - Business logic                               │
│  - Authorization checks                         │
│  - Cross-cutting concerns                       │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  Repository Layer (app/repositories/)           │
│  - Database queries (SQLAlchemy 2.0)            │
│  - CRUD operations                              │
│  - Data access abstraction                      │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  Data Layer (app/models/)                       │
│  - SQLAlchemy ORM models                        │
│  - Table definitions & relationships            │
└─────────────────────────────────────────────────┘
```

### Layer Responsibilities

- **`app/api/`** — Controller Layer: FastAPI routers, dependencies, HTTP endpoints
- **`app/schemas/`** — Validation Layer: Pydantic DTOs for strict type-checking
- **`app/services/`** — Business Logic Layer: Core application features
- **`app/repositories/`** — Data Access Layer: Centralized SQLAlchemy queries
- **`app/models/`** — Data Layer: SQLAlchemy table definitions
- **`app/core/`** — Cross-cutting: Security, exceptions, config, enums
- **`app/db/`** — Infrastructure: Async engines, sessions, connection pooling

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Virtual environment (recommended)

### 1. Clone & Setup

```bash
# Clone the repository
git clone <repository-url>
cd gazior-ops-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the root directory:

```env
# Application Settings
APP_ENV=development
DEBUG=True

# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/gazior_ops

# Security
SECRET_KEY=your-super-secret-key-change-in-production
```

> ⚠️ **Important:** Never commit `.env` files to version control. Use strong, unique `SECRET_KEY` values in production.

### 4. Database Setup

```bash
# Option 1: Auto-create tables (development only, when APP_ENV=development)
python run.py

# Option 2: Use Alembic migrations (recommended for production)
alembic upgrade head
```

### 5. Run the Server

```bash
python run.py
```

The API will be available at:
- **Base URL:** `http://localhost:8000`
- **Interactive Docs:** `http://localhost:8000/docs`
- **ReDoc Docs:** `http://localhost:8000/redoc`

---

## 📡 API Documentation

### Authentication Endpoints (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/login` | OAuth2 login for access token | No |
| GET | `/auth/me` | Get current user profile | Yes |

---

### Workspace Endpoints (`/api/v1/workspaces`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/workspaces` | List all workspaces (paginated) | Yes |
| GET | `/workspaces/my` | Get user's workspaces | Yes |
| GET | `/workspaces/slug/{slug}` | Get workspace by slug | Yes |
| GET | `/workspaces/{id}` | Get workspace with members | Yes |
| POST | `/workspaces` | Create workspace (creator becomes OWNER) | Yes |
| PATCH | `/workspaces/{id}` | Update workspace | Yes (OWNER/ADMIN) |
| DELETE | `/workspaces/{id}` | Soft delete workspace | Yes (OWNER only) |
| GET | `/workspaces/{id}/members` | List workspace members | Yes |
| POST | `/workspaces/{id}/members` | Add member to workspace | Yes (OWNER/ADMIN) |
| PATCH | `/workspaces/{id}/members/{user_id}` | Update member role | Yes (OWNER only) |
| DELETE | `/workspaces/{id}/members/{user_id}` | Remove member | Yes |
| GET | `/workspaces/{id}/invitations` | List pending invitations | Yes |
| POST | `/workspaces/{id}/invitations` | Send an invitation | Yes (OWNER/ADMIN) |
| DELETE | `/workspaces/{id}/invitations/{id}` | Revoke invitation | Yes (OWNER/ADMIN) |
| GET | `/workspaces/{id}/stats` | Get workspace statistics | Yes |

---

### Task Endpoints (`/api/v1/tasks`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/tasks` | List tasks (with filters & pagination) | Yes |
| GET | `/tasks/{task_id}` | Get task by ID | Yes |
| GET | `/tasks/identifier/{identifier}` | Get task by identifier (e.g., GAZ-123) | Yes |
| POST | `/tasks` | Create new task | Yes |
| PATCH | `/tasks/{task_id}` | Update task | Yes |
| DELETE | `/tasks/{task_id}` | Soft delete task | Yes |
| POST | `/tasks/{task_id}/archive` | Archive task | Yes |
| POST | `/tasks/{task_id}/unarchive` | Unarchive task | Yes |
| POST | `/tasks/bulk/status` | Bulk update task statuses | Yes |

#### Query Parameters for Task Listing

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | `0` | Offset for pagination |
| `limit` | int | `100` | Results per page (max 500) |
| `workspace_id` | int | — | Filter by workspace |
| `project_id` | int | — | Filter by project |
| `cycle_id` | int | — | Filter by cycle |
| `status` | enum | — | `BACKLOG` · `TODO` · `IN_PROGRESS` · `IN_REVIEW` · `DONE` · `CANCELED` |
| `assignee_id` | int | — | Filter by assignee |
| `priority` | enum | — | `URGENT` · `HIGH` · `MEDIUM` · `LOW` · `NONE` |
| `search` | string | — | Full-text search across title, identifier, description |

---

### Team Endpoints (`/api/v1/teams`) 🆕

> Teams are functional units (e.g., Engineering, Design) within a workspace.  
> All mutating operations require the caller to be a workspace **OWNER** or **ADMIN**.

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/teams?workspace_id={id}` | List teams in a workspace (paginated) | Yes |
| GET | `/teams/{team_id}` | Get team by ID | Yes |
| POST | `/teams` | Create a new team | Yes (OWNER/ADMIN) |
| PATCH | `/teams/{team_id}` | Update team name or lead | Yes (OWNER/ADMIN) |
| DELETE | `/teams/{team_id}` | Soft-delete a team | Yes (OWNER/ADMIN) |
| GET | `/teams/{team_id}/members` | List team members (paginated) | Yes |
| POST | `/teams/{team_id}/members` | Add a user to a team | Yes (OWNER/ADMIN) |
| PATCH | `/teams/{team_id}/members/{user_id}` | Update a member's role | Yes (OWNER/ADMIN) |
| DELETE | `/teams/{team_id}/members/{user_id}` | Remove a member from a team | Yes (OWNER/ADMIN) |

#### Team Create / Update Payload

```json
// POST /api/v1/teams
{
  "name": "Engineering",
  "workspace_id": 1,
  "lead_id": 3
}

// PATCH /api/v1/teams/{team_id}
{
  "name": "Platform Engineering",
  "lead_id": 5
}
```

#### Team Member Roles

| Role | Description |
|------|-------------|
| `LEAD` | Team lead — typically the person who manages the team |
| `MEMBER` | Standard team member (default) |
| `VIEWER` | Read-only participant |

#### Add / Update Member Payload

```json
// POST /api/v1/teams/{team_id}/members
{
  "user_id": 4,
  "role": "MEMBER"
}

// PATCH /api/v1/teams/{team_id}/members/{user_id}
{
  "role": "LEAD"
}
```

#### Query Parameters for Team Listing

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `workspace_id` | int | **required** | Filter by workspace |
| `skip` | int | `0` | Offset for pagination |
| `limit` | int | `100` | Results per page (max 500) |
| `search` | string | — | Search by team name |

---

## 🗄️ Database Models

The data model is designed for **multi-tenant SaaS** with strict tenant isolation.

### Phase 1: Core MVP (Implemented)

| Model | Description |
|-------|-------------|
| **User** | Global identity with email, password, and activity tracking |
| **Workspace** | Root container for all projects and users |
| **WorkspaceMember** | RBAC mapping with roles (OWNER, ADMIN, MEMBER, VIEWER, GUEST) |
| **Team** | Department/functional unit grouping within a workspace |
| **TeamMember** | Pivot table mapping users to teams with roles (LEAD, MEMBER, VIEWER) |
| **Invitation** | User onboarding workflow into workspaces |
| **Project** | Task collections with unique identifiers (e.g., GAZ) |
| **Cycle** | Time-boxed agile iterations within a project |
| **Initiative** | Strategic objectives and roadmaps |
| **Task** | Central work item with status, priority, assignments, and AI summaries |
| **TaskHistory** | Field-level audit trail for tasks |
| **Label** | Task categorization tags |
| **TaskLabel** | Pivot table linking tasks to labels |
| **Comment** | Task discussions and system events |
| **Attachment** | File uploads linked to tasks |
| **Update** | Team announcements / megaphone feed |

### Phase 2: Future SaaS & Enterprise (Planned)

- Custom Fields & Values
- Notifications & Subscriptions
- API Keys & Webhooks
- Workspace/Project Settings
- User Profiles & Preferences
- System Audit Logs
- Analytics Snapshots
- AI Task Breakdowns
- Vector Embeddings (pgvector)

> 📖 **Complete Schema Documentation:** See [DATA_MODEL.md](DATA_MODEL.md)

---

## 🔧 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | — | PostgreSQL connection string (asyncpg) |
| `SECRET_KEY` | ✅ | — | JWT signing secret (use strong random value) |
| `APP_ENV` | ❌ | `production` | Application environment (`development`, `production`) |
| `DEBUG` | ❌ | `False` | Enable debug mode |
| `DB_POOL_SIZE` | ❌ | `10` | Database connection pool size |
| `DB_MAX_OVERFLOW` | ❌ | `20` | Max overflow connections |
| `DB_POOL_TIMEOUT` | ❌ | `30` | Pool timeout (seconds) |
| `DB_POOL_RECYCLE` | ❌ | `1800` | Connection recycle time (seconds) |

### Example `.env` for Development

```env
APP_ENV=development
DEBUG=True
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/gazior_ops_dev
SECRET_KEY=dev-secret-key-change-in-production
DB_POOL_SIZE=5
```

---

## 💻 Development

### Code Style

This project uses:
- **Ruff** for linting and formatting
- **Mypy** for type checking
- **Pytest** for testing

```bash
# Lint the code
ruff check .

# Format the code
ruff format .

# Type check
mypy app/
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Async Session Management

All database operations use async sessions with automatic commit/rollback handled by the `get_db` dependency:

```python
# Automatic transaction management in endpoints
@router.post("/resource")
async def create_resource(
    data: ResourceCreate,
    db: AsyncSession = Depends(get_db),  # Auto-commits on success, rolls back on error
    current_user=Depends(get_current_user),
):
    service = ResourceService(db)
    return await service.create_resource(data)
```

---

## 🧪 Testing

```bash
# Run all tests
.venv/bin/pytest

# Run with verbose output
.venv/bin/pytest -v

# Run specific test file
.venv/bin/pytest tests/test_app_surface.py

# Run with coverage
.venv/bin/pytest --cov=app --cov-report=html
```

### Smoke Tests (`tests/test_app_surface.py`)

A no-database smoke test suite validates the full OpenAPI surface on every run:

- ✅ Root endpoint returns expected message
- ✅ `/docs`, `/redoc`, and `/openapi.json` are accessible
- ✅ All registered routes appear in the OpenAPI spec (auth + workspaces + tasks + **teams**)

---

## 📁 Project Structure

```
gazior-ops-backend/
├── app/
│   ├── api/                        # Controller Layer
│   │   ├── dependencies.py         # FastAPI deps (get_db, get_current_user, check_workspace_membership)
│   │   └── endpoints/
│   │       ├── v1/                 # API v1 routes
│   │       │   ├── auth.py         # Authentication endpoints
│   │       │   ├── task.py         # Task endpoints
│   │       │   ├── team.py         # Team & TeamMember endpoints ✨
│   │       │   └── workspace.py    # Workspace & member endpoints
│   │       └── v2/                 # API v2 (future)
│   ├── core/                       # Cross-cutting concerns
│   │   ├── config.py               # Pydantic settings
│   │   ├── exceptions.py           # Custom exception classes
│   │   ├── security.py             # JWT create/decode helpers
│   │   └── enums/
│   │       └── common.py           # All domain enums (incl. TeamMemberRole ✨)
│   ├── db/                         # Database infrastructure
│   │   ├── database.py             # Async engine & session management
│   │   └── init_db.py              # Dev-only table auto-creation
│   ├── models/                     # SQLAlchemy ORM models (16 total)
│   │   ├── user.py
│   │   ├── workspace.py
│   │   ├── workspace_member.py
│   │   ├── team.py                 # Team model ✨
│   │   ├── team_member.py          # TeamMember pivot model ✨
│   │   ├── task.py
│   │   └── ...
│   ├── repositories/               # Data Access Layer
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── team.py                 # TeamRepository ✨
│   │   ├── team_member.py          # TeamMemberRepository ✨
│   │   ├── workspace.py
│   │   └── workspace_member.py
│   ├── schemas/                    # Pydantic DTOs
│   │   ├── auth.py
│   │   ├── task.py
│   │   ├── team.py                 # Team & TeamMember schemas ✨
│   │   └── workspace.py
│   ├── services/                   # Business Logic Layer
│   │   ├── auth_service.py
│   │   ├── task_service.py
│   │   ├── team_service.py         # TeamService ✨
│   │   └── workspace_service.py
│   ├── utils/
│   │   └── password.py             # Password hashing (Argon2)
│   ├── main.py                     # FastAPI app entry point
│   └── __init__.py
├── alembic/                        # Database migrations
│   ├── versions/
│   └── env.py
├── demo_data/                      # Ready-to-use API demo payloads
│   ├── auth.json
│   ├── invitation.json
│   ├── placeholders.json
│   ├── task.json
│   ├── team.json                   # Team & TeamMember demo data ✨
│   └── workspace.json
├── tests/                          # Test suite
│   ├── conftest.py                 # Pytest configuration & env defaults
│   └── test_app_surface.py         # OpenAPI surface smoke tests
├── .env                            # Environment variables (gitignored)
├── alembic.ini                     # Alembic configuration
├── DATA_MODEL.md                   # Complete schema documentation
├── pyproject.toml                  # Project metadata & tool config
├── requirements.txt                # Python dependencies
├── run.py                          # Development server runner
└── README.md                       # This file
```

---

## 🔒 Security

### Authentication & Authorization

- **JWT Tokens** — Access tokens with configurable expiration (default: 15 minutes)
- **OAuth2 Password Flow** — Standard OAuth2 compatible login
- **Workspace Membership** — Every workspace/task endpoint verifies user membership
- **Role-Based Access Control** — Granular permissions based on user roles

### Permission Matrix

| Resource | Read | Create | Update | Delete |
|----------|------|--------|--------|--------|
| Workspace | Any member | Authenticated | OWNER / ADMIN | OWNER |
| Workspace Member | Any member | OWNER / ADMIN | OWNER | OWNER / ADMIN / Self |
| Team | Any member | OWNER / ADMIN | OWNER / ADMIN | OWNER / ADMIN |
| Team Member | Any member | OWNER / ADMIN | OWNER / ADMIN | OWNER / ADMIN |
| Task | Any member | Any member | Any member | Any member |

### Password Requirements

- Minimum 8 characters
- Maximum 128 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- Hashed with Argon2 (via pwdlib)

### Data Protection

- **Soft Deletes** — All deletions use `deleted_at` timestamp (recoverable)
- **Audit Fields** — `created_by_id`, `updated_by_id` track all changes
- **Input Sanitization** — All inputs validated via Pydantic schemas
- **Error Handling** — Generic error messages (no stack traces or internal details)
- **SQL Injection Protection** — Parameterized queries via SQLAlchemy ORM

### Best Practices

✅ Never commit `.env` files  
✅ Use strong, unique `SECRET_KEY` in production  
✅ Enable HTTPS in production  
✅ Rotate JWT secret periodically  
✅ Monitor and rate-limit login endpoints  
✅ Regular database backups  
✅ Keep dependencies updated  

---

## 📝 License

Proprietary — All rights reserved.

---

## 🤝 Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Write/update tests
4. Ensure linting passes (`ruff check .`, `mypy app/`)
5. Submit a pull request

---

## 📞 Support

For questions or issues, please contact the development team.

---

**Built with ❤️ using FastAPI**
