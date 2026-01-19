from tasks.celery_app import celery_app
import time
import random

@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
    retry_backoff=True,
    retry_jitter=True,
    soft_time_limit=10,
    time_limit=15
)
def run_inference(self, text: str):
    try:
        # Simulate random failure
        if random.choice([True, False]):
            raise RuntimeError("Random inference failure")

        time.sleep(2)

        sentiment = "positive" if "love" in text.lower() else "neutral"

        return {
            "input": text,
            "sentiment": sentiment
        }

    except Exception as exc:
        raise self.retry(exc=exc)
