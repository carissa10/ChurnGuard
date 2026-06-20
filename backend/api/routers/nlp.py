from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
import io
from schemas.nlp_schema import (
    SentimentPredictionInput,
    SentimentPredictionResponse,
    BatchSentimentPredictionResponse,
    SentimentPredictionResult
)
from services.nlp_service import nlp_service
import logging

logger = logging.getLogger("nlp_router")
router = APIRouter(prefix="/api/nlp")

@router.post("/predict_single", response_model=SentimentPredictionResponse)
def predict_single(payload: SentimentPredictionInput):
    """
    Predict sentiment for a single text input.
    """
    try:
        result = nlp_service.predict_single(payload.text, lang=payload.lang)
        
        return {
            "status": "success",
            "result": SentimentPredictionResult(**result)
        }
    except Exception as e:
        logger.error(f"NLP Single prediction API failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/predict_batch", response_model=BatchSentimentPredictionResponse)
async def predict_batch(file: UploadFile = File(...), lang: str = 'id'):
    """
    Upload a CSV file of text data to predict sentiments.
    Expected CSV format: Must have a 'text' column.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")
        
    try:
        contents = await file.read()
        try:
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        except Exception as e:
            logger.error(f"Failed to parse CSV file: {e}")
            raise HTTPException(status_code=400, detail="Invalid CSV format. Please check the file.")
            
        if "text" not in df.columns:
            # Maybe there's a column like 'review' or 'content'
            potential_cols = ['review', 'content', 'message', 'sentence']
            for col in potential_cols:
                if col in df.columns:
                    df.rename(columns={col: "text"}, inplace=True)
                    break
            
            if "text" not in df.columns:
                raise HTTPException(status_code=400, detail="CSV must contain a 'text' column.")
            
        texts = df['text'].astype(str).tolist()
        prediction_list = nlp_service.predict_batch(texts, lang=lang)
        
        results = [SentimentPredictionResult(**res) for res in prediction_list]
        
        return {
            "status": "success",
            "total_records": len(results),
            "results": results
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"NLP Batch prediction API failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")
