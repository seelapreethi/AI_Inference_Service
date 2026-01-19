from pydantic import BaseModel, Field

class TextPayload(BaseModel):
    text: str = Field(..., min_length=1, description="Input text for prediction")

class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
