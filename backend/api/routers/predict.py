from fastapi import APIRouter, UploadFile, File, HTTPException, Header
import pandas as pd
import io
from schemas.predict_schema import (
    ChurnPredictionInput,
    ChurnPredictionResponse,
    BatchChurnPredictionResponse,
    ChurnPredictionResult
)
from services.ml_service import ml_service
from services.supabase_service import supabase_service
from services.auth_service import auth_service
import logging

logger = logging.getLogger("predict_router")
router = APIRouter(prefix="/api")

def get_current_user_id(authorization: str = Header(None)):
    """Extract user ID from JWT token"""
    if not authorization:
        return "anonymous"
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = auth_service.verify_token(token)
        return payload.get("user_id") if payload else "anonymous"
    except:
        return "anonymous"

@router.post("/predict_single", response_model=ChurnPredictionResponse)
def predict_single(payload: ChurnPredictionInput, authorization: str = Header(None)):
    """
    Predict churn for a single customer.
    Receives JSON input, drops CustomerID, transforms values, runs prediction.
    Saves result to Supabase database.
    """
    try:
        input_data = payload.model_dump()
        result = ml_service.predict_single(input_data)
        
        # Save customer and prediction to Supabase
        try:
            user_id = get_current_user_id(authorization)
            
            # Save/update customer data
            supabase_service.save_or_update_customer(input_data)
            
            # Save prediction
            supabase_service.save_single_prediction(
                payload.CustomerID, 
                result
            )
            logger.info(f"Saved prediction for {payload.CustomerID}")
        except Exception as db_error:
            logger.warning(f"Failed to save to Supabase: {db_error}")
            # Don't fail the prediction if database save fails
        
        return {
            "status": "success",
            "result": ChurnPredictionResult(**result)
        }
    except Exception as e:
        logger.error(f"Single prediction API failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/predict_batch", response_model=BatchChurnPredictionResponse)
async def predict_batch(file: UploadFile = File(...), authorization: str = Header(None)):
    """
    Upload a CSV file of customer data, perform the identical preprocessing pipeline,
    and return aggregate metrics and detailed predictions.
    Saves batch results and all predictions to Supabase database.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")
        
    try:
        # Read uploaded file content
        contents = await file.read()
        
        # Parse into Pandas DataFrame
        try:
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        except Exception as e:
            logger.error(f"Failed to parse CSV file: {e}")
            raise HTTPException(status_code=400, detail="Invalid CSV format. Please check the file.")
            
        # Ensure CustomerID exists
        if "CustomerID" not in df.columns:
            raise HTTPException(status_code=400, detail="CSV must contain a 'CustomerID' column.")
            
        # Required columns for model features
        required_cols = [
            "age", "salary_k", "tenure_years", "number_of_logins", 
            "complaints", "engagement_score", "subscription_type", 
            "region", "device_type", "signup_date", "last_active_date"
        ]
        
        # Check that we have the required columns
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=400, 
                detail=f"CSV is missing the following columns required for prediction: {', '.join(missing_cols)}"
            )
            
        # Run batch prediction
        prediction_list = ml_service.predict_batch(df)
        
        # Calculate aggregates
        total_records = len(prediction_list)
        total_churn = sum(1 for res in prediction_list if res["churn_prediction"] == 1)
        
        # Average risk score calculation
        if total_records > 0:
            avg_risk_score = round(sum(res["risk_score"] for res in prediction_list) / total_records, 2)
        else:
            avg_risk_score = 0.0
            
        # Calculate risk distribution
        low_risk_count = sum(1 for res in prediction_list if res["risk_band"] == "Low Risk")
        medium_risk_count = sum(1 for res in prediction_list if res["risk_band"] == "Medium Risk")
        high_risk_count = sum(1 for res in prediction_list if res["risk_band"] == "High Risk")
        
        # Get model performance metrics
        model_metrics = ml_service.get_model_metrics()
        
        results = [ChurnPredictionResult(**res) for res in prediction_list]
        
        # Save to Supabase
        batch_id = None
        supabase_error = None
        try:
            user_id = get_current_user_id(authorization)
            
            # Create batch prediction record
            batch_data = {
                "batch_name": file.filename.replace(".csv", ""),
                "file_name": file.filename,
                "total_records": total_records,
                "total_churn": total_churn,
                "average_risk_score": avg_risk_score,
                "low_risk_count": low_risk_count,
                "medium_risk_count": medium_risk_count,
                "high_risk_count": high_risk_count,
                "model_accuracy": model_metrics["accuracy"],
                "model_precision": model_metrics["precision"],
                "model_recall": model_metrics["recall"],
                "model_f1_score": model_metrics["f1_score"],
                "model_auc_score": model_metrics["auc_score"],
                "decision_threshold": model_metrics["decision_threshold"]
            }
            
            batch_record = supabase_service.create_batch_prediction(batch_data, user_id)
            batch_id = batch_record["id"] if batch_record else None
            
            # Save individual customer data and batch results
            for _, row in df.iterrows():
                supabase_service.save_or_update_customer(row.to_dict())
            
            # Save batch prediction results
            if batch_id:
                supabase_service.save_batch_results(batch_id, prediction_list)
            
            logger.info(f"Saved batch prediction {batch_id} with {total_records} records")
        except Exception as db_error:
            supabase_error = str(db_error)
            logger.error(f"Failed to save batch to Supabase: {db_error}")
            # Continue processing but track error for response
        
        return {
            "status": "success",
            "total_records": total_records,
            "total_churn": total_churn,
            "average_risk_score": avg_risk_score,
            "model_performance": {
                "accuracy": model_metrics["accuracy"],
                "precision": model_metrics["precision"],
                "recall": model_metrics["recall"],
                "f1_score": model_metrics["f1_score"],
                "auc_score": model_metrics["auc_score"],
                "decision_threshold": model_metrics["decision_threshold"]
            },
            "risk_analysis": {
                "low_risk_count": low_risk_count,
                "medium_risk_count": medium_risk_count,
                "high_risk_count": high_risk_count
            },
            "results": results,
            "database_status": ("❌ Error: " + supabase_error) if supabase_error else "✅ Data saved to Supabase"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Batch prediction API failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")