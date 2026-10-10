from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import engine, Base
from app.routers import (
    auth_router, chat_router, documents_router,
    tickets_router, academic_router, announcements_router,
    notifications_router, admin_router, academic_router_enhanced
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schemas on startup
    Base.metadata.create_all(bind=engine)
    # Automatically seed database if empty
    try:
        from seed_data import seed_database
        seed_database()
    except Exception as e:
        print(f"Startup database check/seed notification: {e}")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Production-Grade AI Student Academic Support Platform.\n"
        f"{settings.DEVELOPER_INFO}\n\n"
        "Features: Grounded RAG with citations, sentence-aware chunking, "
        "conversational memory, human escalation tickets, role-based access control, "
        "and real-time notifications."
    ),
    lifespan=lifespan
)

# Configure CORS for local Vite development & staging
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(auth_router.router)
app.include_router(chat_router.router)
app.include_router(documents_router.router)
app.include_router(tickets_router.router)
app.include_router(academic_router.router)
app.include_router(academic_router_enhanced.router)
app.include_router(announcements_router.router)
app.include_router(notifications_router.router)
app.include_router(admin_router.router)


@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "online",
        "docs_url": "/docs",
        "llm_provider": settings.LLM_PROVIDER
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "project": settings.PROJECT_NAME
    }
