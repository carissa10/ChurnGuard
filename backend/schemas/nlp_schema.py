from pydantic import BaseModel, Field
from typing import List

class SentimentPredictionInput(BaseModel):
    text: str = Field(..., description="The text to analyze")
    lang: str = Field("id", description="Language of the text: 'id' or 'en'")

class SentimentPredictionResult(BaseModel):
    text: str
    sentiment: str = Field(..., description="Predicted sentiment class (e.g. Positive, Negative, Neutral)")
    confidence: float = Field(..., description="Probability of the predicted class")

class SentimentPredictionResponse(BaseModel):
    status: str
    result: SentimentPredictionResult

class BatchSentimentPredictionResponse(BaseModel):
    status: str
    total_records: int
    results: List[SentimentPredictionResult]
