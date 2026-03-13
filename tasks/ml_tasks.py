import os
import joblib
import logging
import re
import string

from tasks.celery_app import celery_app

# ---------------------------------------------------
# Logging Configuration
# ---------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------
# Paths
# ---------------------------------------------------
MODEL_PATH = os.getenv("MODEL_PATH", "models/sentiment_model.pkl")
VECTORIZER_PATH = os.getenv("VECTORIZER_PATH", "models/tfidf_vectorizer.pkl")

MODEL_VERSION = "1.0"

# ---------------------------------------------------
# Load ML Model and Vectorizer
# ---------------------------------------------------
try:
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    logger.info("ML model and vectorizer loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model or vectorizer: {str(e)}")
    model = None
    vectorizer = None


# ---------------------------------------------------
# Text Preprocessing
# ---------------------------------------------------
def preprocess(text: str) -> str:
    """
    Clean input text before sending to ML model
    """
    text = text.lower()
    text = re.sub(f"[{string.punctuation}]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ---------------------------------------------------
# Celery ML Inference Task
# ---------------------------------------------------
@celery_app.task(bind=True)
def run_inference(self, text: str):
    """
    Runs sentiment prediction asynchronously
    """

    try:

        logger.info(f"Task {self.request.id} started")

        if model is None or vectorizer is None:
            return {
                "task_id": self.request.id,
                "error": "Model or vectorizer not loaded"
            }

        # Step 1: preprocess text
        processed_text = preprocess(text)

        # Step 2: convert text to vector
        vector = vectorizer.transform([processed_text])

        # Step 3: model prediction
        prediction = model.predict(vector)[0]

        # Step 4: confidence score
        if hasattr(model, "predict_proba"):
            confidence = model.predict_proba(vector).max()
        else:
            confidence = 1.0

        logger.info(
            f"Task {self.request.id} | input='{text}' | prediction='{prediction}' | confidence={confidence}"
        )

        return {
            "task_id": self.request.id,
            "model_version": MODEL_VERSION,
            "input_text": text,
            "processed_text": processed_text,
            "prediction": "positive" if prediction == 1 else "negative",
            "confidence": float(confidence)
        }

    except Exception as e:

        logger.error(f"Task {self.request.id} failed: {str(e)}")

        return {
            "task_id": self.request.id,
            "error": str(e)
        }