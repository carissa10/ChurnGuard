import os
from supabase import create_client, Client
from datetime import datetime
import json
import logging

logger = logging.getLogger("supabase_service")

class SupabaseService:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL", "https://axnhgrzosjtarnynngno.supabase.co")
        self.key = os.getenv("SUPABASE_KEY", "sb_publishable_ANSY7fbv52Xjc_dcyCWLFg_2MFYC8z1")
        self.client: Client = create_client(self.url, self.key)
        logger.info("Supabase client initialized")

    # ==================== PREDICTIONS ====================
    
    def save_single_prediction(self, customer_id: str, prediction_data: dict):
        """Save single customer prediction"""
        try:
            data = {
                "customer_id": customer_id,
                "churn_prediction": prediction_data["churn_prediction"],
                "risk_score": prediction_data["risk_score"],
                "risk_band": prediction_data["risk_band"],
                "churn_probability": prediction_data["churn_probability"],
                "model_version": "xgboost_v1",
                "predicted_at": datetime.now().isoformat()
            }
            result = self.client.table("predictions").insert(data).execute()
            logger.info(f"Saved prediction for customer {customer_id}")
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
            raise

    def get_prediction_history(self, customer_id: str, limit: int = 10):
        """Get prediction history for a customer"""
        try:
            result = self.client.table("predictions") \
                .select("*") \
                .eq("customer_id", customer_id) \
                .order("predicted_at", desc=True) \
                .limit(limit) \
                .execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error fetching prediction history: {e}")
            return []

    # ==================== BATCH PREDICTIONS ====================
    
    def create_batch_prediction(self, batch_data: dict, user_id: str):
        """Create batch prediction record"""
        try:
            data = {
                "batch_name": batch_data.get("batch_name", "batch"),
                "file_name": batch_data["file_name"],
                "total_records": batch_data["total_records"],
                "total_churn": batch_data["total_churn"],
                "average_risk_score": batch_data["average_risk_score"],
                "low_risk_count": batch_data.get("low_risk_count", 0),
                "medium_risk_count": batch_data.get("medium_risk_count", 0),
                "high_risk_count": batch_data.get("high_risk_count", 0),
                "model_accuracy": batch_data.get("model_accuracy", 0.9128),
                "model_precision": batch_data.get("model_precision", 0.8915),
                "model_recall": batch_data.get("model_recall", 0.9342),
                "model_f1_score": batch_data.get("model_f1_score", 0.9128),
                "model_auc_score": batch_data.get("model_auc_score", 0.9567),
                "decision_threshold": batch_data.get("decision_threshold", 0.6111),
                "processed_by": user_id,
                "status": "completed"
            }
            result = self.client.table("batch_predictions").insert(data).execute()
            logger.info(f"Created batch prediction: {result.data[0]['id']}")
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating batch prediction: {e}")
            raise

    def save_batch_results(self, batch_id: str, results: list):
        """Save batch prediction results"""
        try:
            batch_results = [
                {
                    "batch_id": batch_id,
                    "customer_id": res["CustomerID"],
                    "churn_prediction": res["churn_prediction"],
                    "risk_score": res["risk_score"],
                    "risk_band": res["risk_band"],
                    "churn_probability": res["churn_probability"]
                }
                for res in results
            ]
            
            # Insert in chunks to avoid payload limits
            chunk_size = 1000
            for i in range(0, len(batch_results), chunk_size):
                chunk = batch_results[i:i+chunk_size]
                self.client.table("batch_prediction_results").insert(chunk).execute()
            
            logger.info(f"Saved {len(batch_results)} batch results")
            return True
        except Exception as e:
            logger.error(f"Error saving batch results: {e}")
            raise

    def get_batch_predictions(self, limit: int = 20):
        """Get recent batch predictions"""
        try:
            result = self.client.table("batch_predictions") \
                .select("*") \
                .order("processed_at", desc=True) \
                .limit(limit) \
                .execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error fetching batch predictions: {e}")
            return []

    def get_batch_results(self, batch_id: str):
        """Get results for a specific batch"""
        try:
            result = self.client.table("batch_prediction_results") \
                .select("*") \
                .eq("batch_id", batch_id) \
                .execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error fetching batch results: {e}")
            return []

    # ==================== CUSTOMERS ====================
    
    def save_or_update_customer(self, customer_data: dict):
        """Save or update customer data"""
        try:
            customer_id = customer_data.get("CustomerID") or customer_data.get("customer_id")
            existing = self.client.table("customers") \
                .select("id") \
                .eq("customer_id", customer_id) \
                .execute()
            
            data = {
                "customer_id": customer_id,
                "age": customer_data.get("age"),
                "salary_k": customer_data.get("salary_k"),
                "tenure_years": customer_data.get("tenure_years"),
                "number_of_logins": customer_data.get("number_of_logins"),
                "complaints": customer_data.get("complaints"),
                "engagement_score": customer_data.get("engagement_score"),
                "subscription_type": customer_data.get("subscription_type"),
                "region": customer_data.get("region"),
                "device_type": customer_data.get("device_type"),
                "signup_date": customer_data.get("signup_date"),
                "last_active_date": customer_data.get("last_active_date")
            }
            
            if existing.data:
                # Update existing
                self.client.table("customers") \
                    .update(data) \
                    .eq("customer_id", customer_id) \
                    .execute()
            else:
                # Insert new
                self.client.table("customers").insert(data).execute()
            
            logger.info(f"Saved/updated customer {customer_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving customer: {e}")
            raise

    def get_customer(self, customer_id: str):
        """Get customer data"""
        try:
            result = self.client.table("customers") \
                .select("*") \
                .eq("customer_id", customer_id) \
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error fetching customer: {e}")
            return None

    # ==================== NLP SENTIMENT ====================
    
    def save_nlp_sentiment(self, customer_id: str, review_text: str, 
                          sentiment_label: str, sentiment_score: float, confidence: float):
        """Save NLP sentiment analysis result"""
        try:
            data = {
                "customer_id": customer_id,
                "review_text": review_text,
                "sentiment_label": sentiment_label,
                "sentiment_score": sentiment_score,
                "confidence": confidence,
                "analyzed_at": datetime.now().isoformat()
            }
            result = self.client.table("nlp_sentiment_analysis").insert(data).execute()
            logger.info(f"Saved sentiment analysis for {customer_id}")
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error saving sentiment: {e}")
            raise

    def get_sentiment_history(self, customer_id: str, limit: int = 10):
        """Get sentiment analysis history"""
        try:
            result = self.client.table("nlp_sentiment_analysis") \
                .select("*") \
                .eq("customer_id", customer_id) \
                .order("analyzed_at", desc=True) \
                .limit(limit) \
                .execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error fetching sentiment history: {e}")
            return []

    # ==================== MODEL METRICS ====================
    
    def save_model_metrics(self, metrics: dict):
        """Save model performance metrics"""
        try:
            data = {
                "accuracy": metrics["accuracy"],
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "f1_score": metrics["f1_score"],
                "auc_score": metrics["auc_score"],
                "decision_threshold": metrics["decision_threshold"],
                "model_version": "xgboost_v1",
                "recorded_at": datetime.now().isoformat()
            }
            result = self.client.table("model_performance_metrics").insert(data).execute()
            logger.info("Saved model metrics")
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
            raise

    def get_latest_model_metrics(self):
        """Get latest model performance metrics"""
        try:
            result = self.client.table("model_performance_metrics") \
                .select("*") \
                .order("recorded_at", desc=True) \
                .limit(1) \
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error fetching metrics: {e}")
            return None

    # ==================== STATISTICS ====================
    
    def get_dashboard_stats(self):
        """Get aggregated dashboard statistics"""
        try:
            # Total predictions
            preds = self.client.table("predictions").select("count", count="exact").execute()
            total_predictions = preds.count if hasattr(preds, 'count') else 0
            
            # Churn rate
            churn_preds = self.client.table("predictions") \
                .select("count", count="exact") \
                .eq("churn_prediction", 1) \
                .execute()
            total_churn = churn_preds.count if hasattr(churn_preds, 'count') else 0
            
            churn_rate = (total_churn / total_predictions * 100) if total_predictions > 0 else 0
            
            # Risk distribution
            low_risk = self.client.table("predictions") \
                .select("count", count="exact") \
                .eq("risk_band", "Low Risk") \
                .execute()
            
            medium_risk = self.client.table("predictions") \
                .select("count", count="exact") \
                .eq("risk_band", "Medium Risk") \
                .execute()
            
            high_risk = self.client.table("predictions") \
                .select("count", count="exact") \
                .eq("risk_band", "High Risk") \
                .execute()
            
            return {
                "total_predictions": total_predictions,
                "total_churn": total_churn,
                "churn_rate": round(churn_rate, 2),
                "risk_distribution": {
                    "low": low_risk.count if hasattr(low_risk, 'count') else 0,
                    "medium": medium_risk.count if hasattr(medium_risk, 'count') else 0,
                    "high": high_risk.count if hasattr(high_risk, 'count') else 0
                }
            }
        except Exception as e:
            logger.error(f"Error fetching dashboard stats: {e}")
            return None

# Global instance
supabase_service = SupabaseService()
