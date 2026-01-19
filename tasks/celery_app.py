import os
from celery import Celery

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")

BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

celery_app = Celery(
    "ai_inference",
    broker=BROKER_URL,
    backend=BROKER_URL,
    include=["tasks.ml_tasks"]
)

celery_app.conf.task_track_started = True
