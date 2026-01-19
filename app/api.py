import os
import re
import joblib
from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult

from app.models import TextPayload, PredictionResponse
from tasks.ml_tasks import run_inference
from tasks.celery_app import celery_app

router = APIRouter()


# =========================================================
# Environment Variables
# =========================================================
MODEL_PATH = os.getenv("MODEL_PATH", "models/sentiment_model.pkl")
VECTORIZER_PATH = os.getenv("VECTORIZER_PATH", "models/tfidf_vectorizer.pkl")


# =========================================================
# Load ML Artifacts (FastAPI Sync Inference)
# =========================================================
try:
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load ML models: {e}")


# =========================================================
# Text Preprocessing
# =========================================================
def preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text


# =========================================================
# SYNCHRONOUS PREDICTION ENDPOINT
# =========================================================
@router.post("/predict_sync", response_model=PredictionResponse)
def predict_sync(payload: TextPayload):
    try:
        cleaned_text = preprocess(payload.text)
        X = vectorizer.transform([cleaned_text])

        prediction = model.predict(X)[0]
        confidence = max(model.predict_proba(X)[0])

        return PredictionResponse(
            prediction=prediction,
            confidence=round(confidence, 3)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# ASYNCHRONOUS PREDICTION ENDPOINT (Celery)
# =========================================================
@router.post("/predict_async")
def predict_async(payload: TextPayload):
    task = run_inference.delay(payload.text)

    return {
        "task_id": task.id,
        "status": "queued"
    }


# =========================================================
# TASK STATUS & RESULT ENDPOINT
# =========================================================
@router.get("/status/{task_id}")
def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": task_result.status
    }

    if task_result.status == "SUCCESS":
        response["result"] = task_result.result

    elif task_result.status == "FAILURE":
        response["error"] = str(task_result.result)

    return response
