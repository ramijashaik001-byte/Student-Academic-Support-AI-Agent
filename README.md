# 🎓 AI Student Academic Support Agent

A production-style, end-to-end intelligent academic support platform designed to assist university students with academic queries using official college documents, course materials, examination schedules, assignment instructions, and institutional bylaws.

Built with **FastAPI**, **React 19 + TypeScript + Vite**, **Tailwind CSS**, **ChromaDB / Hybrid Lexical Ranker**, and a humanized conversational AI mentor.

---

## 🌟 Highlights & Key Capabilities

1. **Humanized AI Academic Mentor**:
   - Communicates in a warm, empathetic, respectful, and friendly mentor tone.
   - Fully transparent that it is an AI academic assistant.
   - Multi-turn conversational memory with coreference resolution (e.g. understanding follow-ups like *"What if I have 72%?"* in the context of attendance rules).
   - Honestly acknowledges uncertainty: never fabricates examination dates, marks, deadlines, or bylaws.
2. **Grounded Retrieval-Augmented Generation (RAG)**:
   - Supports multi-format ingestion: **PDF**, **DOCX**, **TXT**, and **CSV**.
   - Sentence-aware document chunking (400–700 chars with semantic overlap preserving sentence boundaries).
   - Hybrid Vector Retrieval (ChromaDB semantic search + BM25 lexical keyword matching for course codes and dates).
   - Structured citation cards displaying exact Document Title, Page Number / Section, and verified source excerpt.
   - **Zero-Cost Offline Fallback Guarantee**: Operates 100% offline without requiring paid API keys, with optional plug-and-play support for Google Gemini (`gemini-1.5-flash`) or OpenAI (`gpt-4o-mini`).
3. **Complete Human Escalation Workflow**:
   - Automatically detects low confidence (< 0.40) or requests for discretionary exceptions (condonation waivers, marks appeals) and offers faculty escalation.
   - Interactive support ticket system with ticket numbers (e.g., `TICK-2026-0001`).
   - Two-way conversation thread between students and assigned faculty advisors.
   - Status transitions: `Open` ➔ `Assigned` ➔ `In Progress` ➔ `Waiting for Student` ➔ `Resolved` ➔ `Closed`.
4. **Persistent In-App Notification Center**:
   - Event-driven notifications dispatched on faculty replies, ticket status updates, new academic announcements, and schedule revisions.
   - Real-time unread badge counter, mark as read, and mark all as read.
5. **Strict Role-Based Access Control (RBAC)**:
   - **Student Portal**: Personalized dashboard, academic assistant chat, knowledge base search, verified schedules & timetables, support tickets tracker, student profile.
   - **Faculty Portal**: Overview KPI cards, assigned courses, course materials upload dropzone with indexing status (`Uploaded` ➔ `Processing` ➔ `Indexed`), escalations inbox, announcement publisher, knowledge base feedback.
   - **Admin Portal**: Institutional analytics calculated from actual database records (not mock numbers!), user management, academic structure (departments/courses/subjects), document master, RAG vector store diagnostics, audit logs, AI engine settings.
   - **Instant Persona Switcher**: Evaluate Student, Faculty, and Admin personas in 1 click from the top navigation bar!

---

## 🛠️ Technology Stack

- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, React Router DOM, Axios, Lucide React icons, Recharts
- **Backend**: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy ORM, Uvicorn, Bcrypt, PyJWT
- **Database**: SQLite (default local development) with PostgreSQL production connection support
- **RAG & Vector Engine**: ChromaDB persistent client + Hybrid BM25/Cosine lexical-semantic ranker
- **Document Extractors**: `pypdf`, `python-docx`, `reportlab`, `csv`

---

## 📂 Project Structure

```
ai-student-academic-support-agent/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   └── academic_agent.py          # Grounded mentor engine & LLM dispatcher
│   │   ├── rag/
│   │   │   ├── chunker.py                 # Sentence-aware chunking
│   │   │   ├── extractors.py              # PDF, DOCX, TXT, CSV extractors
│   │   │   └── vector_store.py            # ChromaDB & Hybrid ranker
│   │   ├── routers/
│   │   │   ├── academic_router.py         # Departments, Courses, Subjects, Schedules
│   │   │   ├── admin_router.py            # Analytics, Users, RAG Health, Audit Logs, Settings
│   │   │   ├── announcements_router.py    # Campus announcements
│   │   │   ├── auth_router.py             # Login, Register, Me, Demo Switcher
│   │   │   ├── chat_router.py             # Chat Q&A, Conversations, Citations, Feedback
│   │   │   ├── documents_router.py        # Upload, Status, Reindex, Delete
│   │   │   ├── notifications_router.py    # In-app notifications
│   │   │   └── tickets_router.py          # Support tickets & escalation
│   │   ├── services/
│   │   │   ├── audit_service.py           # Institutional audit trail
│   │   │   ├── document_service.py        # File processing & vector indexing
│   │   │   ├── notification_service.py    # Persistent notification events
│   │   │   └── ticket_service.py          # Escalation lifecycle management
│   │   ├── auth.py                        # Bcrypt & JWT token management
│   │   ├── config.py                      # App settings & environment resolution
│   │   ├── database.py                    # SQLAlchemy engine & SQLite foreign key pragma
│   │   ├── dependencies.py                # RBAC guards & current user extraction
│   │   ├── main.py                        # FastAPI application entrypoint & lifespan
│   │   ├── models.py                      # Normalized SQLAlchemy models
│   │   └── schemas.py                     # Pydantic v2 request/response schemas
│   ├── sample_documents/                  # Pre-generated realistic academic files
│   ├── tests/                             # 17 automated pytest unit & integration tests
│   ├── create_sample_docs.py              # Generator for sample PDFs, DOCXs, TXTs, CSVs
│   ├── seed_data.py                       # Pre-populates realistic database records
│   ├── requirements.txt                   # Backend dependencies
│   └── .env                               # Environment configuration
├── frontend/
│   ├── src/
│   │   ├── api/                           # Axios API client
│   │   ├── components/                    # Navbar, Sidebar, CitationCard, EscalateModal, etc.
│   │   ├── context/                       # AuthContext & session state
│   │   ├── pages/
│   │   │   ├── admin/                     # Admin analytics, users, RAG status, settings
│   │   │   ├── faculty/                   # Faculty overview, materials, escalations, notices
│   │   │   ├── student/                   # Student dashboard, chat, KB, schedules, tickets
│   │   │   ├── Login.tsx                  # Sign in with 1-click demo logins
│   │   │   └── Register.tsx               # Academic registration
│   │   ├── types/                         # TypeScript interfaces
│   │   ├── App.tsx                        # React Router configuration
│   │   ├── index.css                      # Tailwind styling & smooth scrollbars
│   │   └── main.tsx                       # React application entrypoint
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚡ Quick Start Guide (Windows)

### Prerequisites
- Python 3.12 (`py` or `python`)
- Node.js v18+ and npm

---

### Step 1: Install Dependencies

#### Backend Dependencies:
```powershell
cd C:\Users\ramij\.gemini\antigravity\scratch\ai-student-academic-support-agent\backend
py -m pip install -r requirements.txt
```

#### Frontend Dependencies:
```powershell
cd C:\Users\ramij\.gemini\antigravity\scratch\ai-student-academic-support-agent\frontend
npm install
```

---

### Step 2: Initialize Database and Ingest Sample Documents
The database seeding script generates 7 realistic academic documents and indexes them:
```powershell
cd C:\Users\ramij\.gemini\antigravity\scratch\ai-student-academic-support-agent\backend
py create_sample_docs.py
py seed_data.py
```

---

### Step 3: Run the Application

#### Start the FastAPI Backend:
```powershell
cd C:\Users\ramij\.gemini\antigravity\scratch\ai-student-academic-support-agent\backend
py -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Backend: [http://localhost:8000](http://localhost:8000)
- Interactive Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

#### Start the React Frontend:
In a second terminal:
```powershell
cd C:\Users\ramij\.gemini\antigravity\scratch\ai-student-academic-support-agent\frontend
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

---

## 🔑 Demo Evaluator Credentials

Use these pre-seeded accounts or use the **1-Click Role Switcher** in the top navigation bar:

| Role | Name | Email | Password | Details |
| :--- | :--- | :--- | :--- | :--- |
| **Student** | Ramija Shaik | `ramija.student@campus.edu` | `Student@123` | B.Tech CSE Sem 6, Roll: 2026-CS-101 |
| **Student** | Rahul Verma | `rahul.student@campus.edu` | `Student@123` | B.Tech CSE Sem 6, Roll: 2026-CS-102 |
| **Faculty** | Prof. Rajesh Sharma | `prof.sharma@campus.edu` | `Faculty@123` | CSE HOD & Operating Systems Professor |
| **Faculty** | Dr. Anita Rao | `dr.anita@campus.edu` | `Faculty@123` | Data Science & DBMS Professor |
| **Administrator** | Dr. Campus Admin | `admin@campus.edu` | `Admin@123` | Dean of Academic Affairs & Senate Admin |

---

## 🧪 Automated Testing

Run the backend test suite:
```powershell
cd C:\Users\ramij\.gemini\antigravity\scratch\ai-student-academic-support-agent\backend
py -m pytest tests -v
```
All 17 automated tests verify authentication, RBAC authorization, PDF/DOCX/TXT/CSV parsers, chunking, similarity retrieval, citations, follow-up memory, student data isolation, and escalation workflows.
