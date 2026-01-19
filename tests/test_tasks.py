import pytest
from tasks.ml_tasks import run_inference

def test_run_inference_task():
    # Direct call for testing (synchronous)
    result = run_inference.apply(args=["I really enjoyed this movie"])
    assert result.successful() is True
    data = result.result
    assert data["input"] == "I really enjoyed this movie"
    assert data["sentiment"] in ["positive", "negative", "neutral"]
