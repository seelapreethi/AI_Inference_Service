from fastapi import FastAPI
from celery.result import AsyncResult

from app.api import router
from tasks.celery_app import celery_app  # ✅ already exists in your project

app = FastAPI(
    title="AI Inference Service",
    description="Synchronous and Asynchronous AI Predictions",
    version="1.0.0"
)

# -------------------------
# Health Check (unchanged)
# -------------------------
@app.get("/")
def health_check():
    return {"status": "ok"}

# -------------------------
# Existing routes (unchanged)
# -------------------------
app.include_router(router)

# -------------------------
# NEW: Async task status API (ADDED ONLY)
# -------------------------
@app.get("/status/{task_id}")
def get_task_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "state": task.state
    }

    if task.successful():
        response["result"] = task.result
    elif task.failed():
        response["error"] = str(task.result)

    return response
