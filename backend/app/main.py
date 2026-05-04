from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.api.character_router import router as character_router
from app.api.event_router import router as event_router
from app.db.character_repo import init_db
from app.db.event_repo import init_events_db
from app.db.task_repo import init_task_db
from app.services.scheduler import start_scheduler, stop_scheduler

app = FastAPI(
    title="mahabharataOS API",
    description="Backend API for the AI Executive Operating System",
    version="0.1.0",
)

# Set up CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialise DB and seed data on startup
@app.on_event("startup")
def on_startup():
    for label, fn in [
        ("characters", init_db),
        ("events", init_events_db),
        ("tasks", init_task_db),
    ]:
        try:
            fn()
        except Exception as e:
            import logging
            logging.getLogger("uvicorn.error").error(
                f"[startup] Failed to initialise {label} DB: {e}"
            )
    
    # Start the background runner
    try:
        start_scheduler()
    except Exception as e:
        import logging
        logging.getLogger("uvicorn.error").error(f"[startup] Failed to start scheduler: {e}")

@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()

app.include_router(api_router, prefix="/api")
app.include_router(character_router, prefix="/api")
app.include_router(event_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "mahabharataOS Backend is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
