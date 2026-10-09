import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.api.routes import router
from backend.app.database.db import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MOIL Manganese Intelligence — AI-Powered Mining Digital Twin",
    description="Enterprise REST API for Manganese Prospectivity, Reserve Estimation, Production Shortfall Forecasting, Root Cause Analysis, AI Action Recommendations, and Digital Twin What-If Simulation.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "title": "MOIL Manganese Intelligence — AI-Powered Mining Digital Twin API",
        "docs_url": "/docs",
        "health_url": "/api/health",
        "dashboard_summary": "/api/dashboard/summary"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=port, reload=True)
