from fastapi import FastAPI
from app.api import router

app = FastAPI(
    title="AI Inference Service",
    description="Synchronous and Asynchronous AI Predictions",
    version="1.0.0"
)

# -------------------------
# Health Check
# -------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}

# -------------------------
# API Routes
# -------------------------
# All endpoints are handled inside app/api.py
app.include_router(router)