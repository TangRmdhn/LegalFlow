# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import chat

app = FastAPI(
    title="LegalTech Consultant API",
    version="1.0.0",
    description="AI Agent for Indonesian Legal Software Consulting"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Router
app.include_router(chat.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "running", "service": "legal-agent-v1"}

# Script entry point (opsional kalau mau run pake python src/main.py)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)