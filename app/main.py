
from fastapi import FastAPI

from app.api.routes import data
from app.database.connection import Base, engine
from app.database import models

from app.api.routes import analytics

from app.api.routes import rag

from app.api.routes import agents

from app.api.routes import reports

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI Financial Intelligence",
    description=(
        "AI-Powered Business Intelligence "
        "and Financial Decision Support System"
    ),
    version="1.0.0"
)


app.include_router(data.router)
app.include_router(analytics.router)

@app.get("/")
def home():

    return {
        "message": "Welcome to AI Financial Intelligence",
        "status": "running"
    }


@app.get("/api/health")
def health_check():

    return {
        "status": "healthy",
        "application": "AI Financial Intelligence",
        "version": "1.0.0"
    }

app.include_router(rag.router)

app.include_router(agents.router)

app.include_router(reports.router)