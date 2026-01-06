# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import router as chat_router

app = FastAPI(
    title="LegalChat API",
    version="1.0.0",
    description="Simple RESTful API for Legal Consultant Agent"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Router dengan prefix /api/v1 (Best Practice Versioning)
app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Buat jalanin: uvicorn app.main:app --reload