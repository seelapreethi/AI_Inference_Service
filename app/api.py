import os
import re
import joblib
from fastapi import APIRouter, HTTPException
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from celery.result import AsyncResult
from tasks.celery_app import celery_app

from app.models import TextPayload, PredictionResponse
from tasks.ml_tasks import run_inference

router = APIRouter()

MODEL_PATH = os.getenv("MODEL_PATH", "models/sentiment_model.pkl")
VECTORIZER_PATH = os.getenv("VECTORIZER_PATH", "models/tfidf_vectorizer.pkl")

# -----------------------
# Training data fallback
# -----------------------
texts = [
    "I love this movie",
    "This movie is amazing",
    "Fantastic acting",
    "Great storyline",
    "I hate this movie",
    "This film is terrible",
    "Worst movie ever",
    "Bad acting"
]

labels = [
    "positive","positive","positive","positive",
    "negative","negative","negative","negative"
]

def preprocess(text: str):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text

# -----------------------
# Load or create model
# -----------------------
def load_model():

    if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):

        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)

        # check if fitted
        if hasattr(vectorizer, "idf_"):
            return model, vectorizer

    # fallback training
    processed = [preprocess(t) for t in texts]

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(processed)

    model = LogisticRegression()
    model.fit(X, labels)

    os.makedirs("models", exist_ok=True)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    return model, vectorizer


model, vectorizer = load_model()

# -----------------------
# Sync endpoint
# -----------------------
@router.post("/predict_sync", response_model=PredictionResponse)
def predict_sync(payload: TextPayload):

    try:
        cleaned = preprocess(payload.text)

        X = vectorizer.transform([cleaned])

        prediction = model.predict(X)[0]

        confidence = float(model.predict_proba(X).max())

        return PredictionResponse(
            prediction=prediction,
            confidence=round(confidence,3)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Inference failed: {str(e)}"
        )


# -----------------------
# Async endpoint
# -----------------------
@router.post("/predict_async")
def predict_async(payload: TextPayload):

    task = run_inference.delay(payload.text)

    return {
        "task_id": task.id,
        "status": "queued"
    }

@router.get("/status/{task_id}")
def get_task_status(task_id: str):

    task = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": task.status
    }

    if task.status == "SUCCESS":
        response["result"] = task.result

    elif task.status == "FAILURE":
        response["error"] = str(task.result)

    return response