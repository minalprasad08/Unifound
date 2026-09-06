# UniFound System Architecture

## Overview

UniFound is architected as a modular, decoupled full-stack platform consisting of five main subsystems:

1. **Frontend Web Client (React + TypeScript + Vite)**
   - High-polish responsive user interface.
   - Client-side routing with JWT-backed authenticated route guards.
   - Dedicated views for Students, Faculty, and Campus Administrators.

2. **Backend REST API (FastAPI + SQLAlchemy + Pydantic)**
   - RESTful endpoints covering Auth, Items, Claims, Verification, and System Metrics.
   - Clean Service Layer architecture isolating business logic from database operations.
   - Role-Based Access Control (USER vs ADMIN).

3. **Database Layer (SQLAlchemy 2.0 ORM + Alembic Migrations + PostgreSQL/SQLite)**
   - Relational data model managing Users, Items, Claims, Notifications, and Audit Logs.
   - Alembic versioned migrations with automatic schema synchronization.

4. **Model Context Protocol (MCP) Server & Client**
   - Implements standardized MCP protocol tools (`search_items`, `find_matches`, `get_claim`, `get_statistics`, etc.).
   - Mediates access between AI agents and the UniFound service layer. AI agents never touch the database directly.

5. **Agentic AI Subsystem**
   - Multi-agent orchestration:
     - **Orchestrator Agent**: ReAct loop, tool selection, multi-step execution.
     - **Matching Agent**: Multi-factor matching engine with explainable confidence scoring.
     - **Claim Analysis Agent**: Automated evidence consistency evaluation.
     - **Reflection/Validation Agent**: Safety and correctness validator.

```mermaid
graph TD
    User([Campus User / Admin]) --> Frontend[React + Vite Frontend]
    Frontend -->|HTTP / JSON + JWT| BackendAPI[FastAPI Backend]
    
    subgraph Core System
        BackendAPI --> ServiceLayer[Service Layer]
        ServiceLayer --> DB[(PostgreSQL / SQLite)]
    end

    subgraph Agentic & MCP Layer
        AIAgent[Orchestrator Agent] -->|Tool Calls| MCPClient[MCP Client]
        MCPClient -->|JSON-RPC / stdio| MCPServer[UniFound MCP Server]
        MCPServer --> ServiceLayer
        AIAgent --> MatchingEngine[Matching Engine]
        AIAgent --> ClaimAgent[Claim Analysis Agent]
        AIAgent --> ReflectionAgent[Reflection & Validation Agent]
    end
```

---

## Production Database Schema (Phase 2)

```mermaid
erDiagram
    USERS ||--o{ ITEMS : "reports"
    USERS ||--o{ CLAIMS : "files as claimant"
    USERS ||--o{ CLAIMS : "reviews as admin"
    USERS ||--o{ NOTIFICATIONS : "receives"
    USERS ||--o{ AUDIT_LOGS : "triggers as actor"
    ITEMS ||--o{ CLAIMS : "has"

    USERS {
        int id PK
        string email UK
        string password_hash
        string full_name
        string phone
        string department
        string student_id
        enum role "USER | ADMIN"
        boolean is_active
        boolean is_verified
        datetime created_at
        datetime updated_at
    }

    ITEMS {
        int id PK
        enum item_type "LOST | FOUND"
        string title
        text description
        string category
        string location
        datetime incident_date
        string image_url
        enum status "OPEN | CLAIM_PENDING | CLAIMED | RESOLVED | CLOSED"
        int reported_by FK
        datetime created_at
        datetime updated_at
    }

    CLAIMS {
        int id PK
        int item_id FK
        int claimant_id FK
        text description
        text evidence
        enum status "PENDING | APPROVED | REJECTED | CANCELLED"
        text admin_notes
        int reviewed_by FK
        datetime reviewed_at
        datetime created_at
        datetime updated_at
    }

    NOTIFICATIONS {
        int id PK
        int user_id FK
        string title
        text message
        enum type "INFO | MATCH_ALERT | CLAIM_UPDATE | SYSTEM"
        boolean is_read
        datetime created_at
    }

    AUDIT_LOGS {
        int id PK
        int actor_id FK
        string action
        string entity_type
        int entity_id
        text details
        datetime created_at
    }
```

---

## ItemStatus Lifecycle State Machine

```
     [ Report Filed ]
            │
            ▼
        ┌───────┐
        │  OPEN │ ◄──────────────────────────┐
        └───┬───┘                            │
            │ (Claim Filed)                  │ (All Claims
            ▼                                │  Rejected / Cancelled)
     ┌──────────────┐                        │
     │ CLAIM_PENDING├────────────────────────┘
     └──────┬───────┘
            │ (Admin Approves Claim)
            ▼
        ┌─────────┐
        │ CLAIMED │
        └────┬────┘
             │ (Handover Confirmed by Owner)
             ▼
        ┌──────────┐
        │ RESOLVED │
        └────┬─────┘
             │ (Archived / Closed)
             ▼
        ┌────────┐
        │ CLOSED │
        └────────┘
```

### Allowed Status Transitions

| Current Status | Allowed Target Statuses | Trigger Event |
|----------------|--------------------------|---------------|
| `OPEN` | `CLAIM_PENDING`, `CLOSED` | Claim submitted by user, or reporter cancels report |
| `CLAIM_PENDING` | `OPEN`, `CLAIMED`, `CLOSED` | Rejection of pending claims, admin approval, or cancellation |
| `CLAIMED` | `RESOLVED`, `CLOSED` | Item physically returned to confirmed owner |
| `RESOLVED` | `CLOSED` | Case archived by administrator |
| `CLOSED` | *(Terminal)* | Archived or cancelled |

---

## Integrity Constraints & Business Rules

1. **One Active Claim Per User + Item**:
   - Enforced by composite partial unique index:
     `uq_active_claim_per_user_item` on `(item_id, claimant_id)` where `status = 'PENDING'`.
   - Validated at the service layer in `ClaimService.create()`.
2. **User Soft-Delete & Preservation of History**:
   - Users are never hard-deleted in production flows; instead `user.is_active = False` is set via `UserService.deactivate()`.
   - Preserves complete integrity of historical reports, claims, reviewer records, and audit logs.
3. **Public Registration Security**:
   - Public registration endpoints (`/api/v1/auth/register`) strictly instantiate `UserRole.USER`. Admin accounts cannot be created by external web clients.
   - Initial administrative access is provisioned securely via `ADMIN_INITIAL_EMAIL` and `ADMIN_INITIAL_PASSWORD` environment variables without static production defaults.
