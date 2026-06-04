from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.routers import profiles, jobs, applications

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hirebot API",
    description="AI-powered job hunting platform backend",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles.router)
app.include_router(jobs.router)
app.include_router(applications.router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "hirebot-api"}
