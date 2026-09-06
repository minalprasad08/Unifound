# UniFound – AI-Powered Lost & Found Management System

UniFound is a full-stack, AI-powered lost and found management platform built for modern campuses and organizations. The system streamlines reporting, intelligent matching, and verified claiming of lost and found items using intelligent multi-factor matching, a dedicated Model Context Protocol (MCP) server, and an Agentic AI Orchestrator.

---

## 🚀 Key Features Roadmap

- **Core Lifecycle**: User accounts, lost & found item reporting with image upload, category tagging, search, and claim workflows.
- **Role-Based Access**: Granular permissions distinguishing campus community members (`USER`) from campus security/administrators (`ADMIN`).
- **AI Matching Engine**: Explainable similarity scoring across categories, semantic descriptions, campus locations, timestamps, and item visual features.
- **Dedicated MCP Server**: Standardized MCP tools decoupled from the database layer, allowing secure tool execution by AI agents.
- **Agentic AI Orchestrator**: Multi-agent ReAct workflow incorporating dynamic tool discovery, multi-step execution, and reflection/validation before responses.
- **Security**: JWT authentication, hashed credentials, input validation with Pydantic, CORS protections, and audit logging.

---

## 📁 Project Structure

```
unifound/
├── backend/          # FastAPI REST API, SQLAlchemy ORM, JWT Auth, Alembic
├── frontend/         # React, Vite, TypeScript, modern responsive UI
├── ai/               # AI/ML matching engine and Agentic ReAct orchestrator
├── mcp_server/       # Model Context Protocol server exposing UniFound tools
├── tests/            # End-to-end and integration test suites
├── docs/             # Architectural specifications, API specs, and diagrams
├── .env.example      # Example environment variables
├── .gitignore        # Git ignore rules
└── README.md         # Master project documentation
```

---

## 🛠️ Tech Stack

- **Frontend**: React 19, TypeScript, Vite, Modern Vanilla CSS Design System with Glassmorphism
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic
- **Database**: PostgreSQL (Production) / SQLite (Development & Testing)
- **Security**: OAuth2 with JWT (HS256), Password hashing with Passlib/Bcrypt
- **Protocol & Agents**: Model Context Protocol (MCP), Agentic ReAct Multi-Agent System

---

## 📦 Phase Status

- [x] **Phase 1: Project Foundation, Architecture, & Authentication System**
- [x] **Phase 2: Production Database Layer (SQLAlchemy 2.0, Alembic, 5 Core Models)**
- [x] **Phase 3: Production Authentication & Authorization (Hardened JWT, RBAC Guards, /users/me)**
- [x] **Phase 4: Lost & Found Core Module (Reporting, My Reports, Image Upload, Audit Logging)**
- [x] **Phase 5: Search & Filtering Engine (Database-level, Pagination, Full Faceting)**
- [x] **Phase 6: Ownership Claims & Admin Management (Claim Lifecycle, Notifications, Admin Queue)**
- [x] **Phase 7: React Frontend Completion & UX (User Dashboard, Admin Stats, Notifications Hub)**
- [x] **Phase 8: AI/ML Item Matching (Deterministic Multi-Factor Scoring, 0-100 Confidence, Potential Matches UI)**
- [x] **Phase 9: AI Image Analysis (Local Vision Provider, Visual Attributes, 10% Visual Match Boost)**
- [x] **Phase 10: Dedicated UniFound MCP Server & Client Integration (Official Python MCP SDK, 6 Tools, Dynamic Discovery, Auth Context)**
- [x] **Phase 11: Agentic AI ReAct Orchestrator (ReAct Loop, LLM Gateway, Reflection Agent, Multi-Step Tool Execution)**
- [x] **Phase 12: Notifications & Admin Analytics (Event-Driven Alerts, Match Alerts, Parameterized SQL Aggregation, Deep Horizon Analytics)**
- [x] **Phase 13: Security & Production Hardening (Fail-Fast Secrets, Rate Limiting, HTTP Security Headers, Pillow Verification, Prompt Injection Defense, 158/158 Passing Tests)**
- [x] **Phase 14: Comprehensive QA, Reliability & End-to-End Validation (17-Step User Flow, 12-Step Admin Flow, Authorization Matrix, State Transitions, 168/168 Passing Tests, QA Report)**
- [x] **Phase 15: Deployment & Final Validation (Production Configuration, PostgreSQL DDL Verification, Live ASGI & Frontend Deployment, 14-Step Live Smoke Test, Final Deployment Report)**

---

## 🚀 Production Deployment (Phase 15)

### 1. Environment & Database Configuration

Copy the production configuration template:
```bash
cp .env.production.example .env
```
Ensure strong values are configured:
* `DATABASE_URL`: `postgresql://user:password@host:5432/unifound_production`
* `SECRET_KEY`: Cryptographically secure secret (minimum 32 characters)
* `ENVIRONMENT`: `production`
* `DEBUG`: `False`

### 2. Run Database Migrations (PostgreSQL)

```bash
cd backend
alembic upgrade head
```

### 3. Launch Backend (ASGI Production Server)

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
```

Health check is available at `GET /health` or `GET /api/v1/health`.

### 4. Build and Serve Frontend

```bash
cd frontend
npm run build
# Serve dist/ using Nginx, Caddy, or static host
```

For detailed validation metrics and audit results, see [`docs/PHASE_15_DEPLOYMENT_REPORT.md`](docs/PHASE_15_DEPLOYMENT_REPORT.md).

---

## ⚡ Getting Started (Local Development)

### 1. Backend Setup

```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs will be available at `http://localhost:8000/docs`.

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend application will be accessible at `http://localhost:5173`.

