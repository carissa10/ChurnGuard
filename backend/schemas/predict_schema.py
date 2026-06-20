from pydantic import BaseModel, Field
from typing import Optional, List

class ChurnPredictionInput(BaseModel):
    CustomerID: str = Field(..., description="Unique customer identifier")
    age: int = Field(..., ge=0, description="Customer age")
    salary_k: float = Field(..., ge=0.0, description="Customer salary in thousands")
    tenure_years: float = Field(..., ge=0.0, description="Number of years as a customer")
    number_of_logins: int = Field(..., ge=0, description="Number of logins")
    complaints: int = Field(..., ge=0, description="Number of complaints filed")
    engagement_score: float = Field(..., ge=0.0, description="Customer engagement score")
    subscription_type: str = Field(..., description="Type of subscription (e.g., Basic, Standard, Premium)")
    region: str = Field(..., description="Region where customer resides")
    device_type: str = Field(..., description="Type of device used (e.g., Mobile, Desktop, Tablet)")
    signup_date: str = Field(..., description="Signup date in YYYY-MM-DD format")
    last_active_date: str = Field(..., description="Last active date in YYYY-MM-DD format")

class ChurnPredictionResult(BaseModel):
    CustomerID: str
    risk_score: float = Field(..., description="Risk score percentage, bounded at 0-100")
    risk_band: str = Field(..., description="Risk tier: Low Risk, Medium Risk, High Risk")
    churn_prediction: int = Field(..., description="Predicted churn: 0 (No), 1 (Yes)")
    churn_probability: float = Field(..., description="Probability of churn (0.0 to 1.0)")

class ChurnPredictionResponse(BaseModel):
    status: str
    result: ChurnPredictionResult

class ModelPerformanceMetrics(BaseModel):
    accuracy: float = Field(..., description="Model accuracy on validation set")
    precision: float = Field(..., description="Precision score for churn class")
    recall: float = Field(..., description="Recall (sensitivity) score for churn class")
    f1_score: float = Field(..., description="F1-score for churn class")
    auc_score: float = Field(..., description="Area Under ROC Curve")
    decision_threshold: float = Field(..., description="Decision threshold used for predictions")

class RiskAnalysisSummary(BaseModel):
    low_risk_count: int = Field(..., description="Total customers in Low Risk band")
    medium_risk_count: int = Field(..., description="Total customers in Medium Risk band")
    high_risk_count: int = Field(..., description="Total customers in High Risk band")

class BatchChurnPredictionResponse(BaseModel):
    status: str
    total_records: int
    total_churn: int
    average_risk_score: float
    model_performance: ModelPerformanceMetrics
    risk_analysis: RiskAnalysisSummary
    results: List[ChurnPredictionResult]
    database_status: Optional[str] = Field(None, description="Database save status message")
