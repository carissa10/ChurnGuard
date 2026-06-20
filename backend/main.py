from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import predict, nlp, auth
from services.ml_service import ml_service
from services.nlp_service import nlp_service
from services.supabase_service import supabase_service
import uvicorn
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Customer Churn Prediction Analytics API",
    description="API Backend for predicting customer churn using XGBoost",
    version="1.0.0"
)

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits all origins; adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(predict.router)
app.include_router(nlp.router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {
        "app": "Customer Churn Prediction API",
        "status": "online",
        "model_loaded": ml_service.model is not None,
        "features_loaded": ml_service.feature_columns is not None,
        "supabase_connected": True
    }

# Startup logic event
@app.on_event("startup")
def startup_event():
    print("--------------------------------------------------")
    print("CUSTOMER CHURN API STARTING UP")
    print(f"Python executable: {sys.executable}")
    print(f"XGBoost model loaded: {ml_service.model is not None}")
    print(f"Imputation stats loaded: {ml_service.impute_stats is not None}")
    print(f"Clipping boundaries loaded: {ml_service.clip_bounds is not None}")
    print(f"Feature columns loaded: {ml_service.feature_columns is not None}")
    print(f"NLP model loaded: {nlp_service.model is not None}")
    print(f"Supabase connected: {supabase_service.client is not None}")
    print("--------------------------------------------------")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
