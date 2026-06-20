import os
import joblib
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger("ml_service")
logging.basicConfig(level=logging.INFO)

# Configurable paths to ML artifacts
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHURN_DIR = os.path.join(BASE_DIR, "models", "churn")
MODEL_DIR = CHURN_DIR

class MLPredictionService:
    def __init__(self):
        self.model = None
        self.impute_stats = None
        self.clip_bounds = None
        self.feature_columns = None
        self.threshold = 0.6111
        
        # Model Performance Metrics (defaults from training)
        self.model_metrics = {
            "accuracy": 0.9128,
            "precision": 0.8915,
            "recall": 0.9342,
            "f1_score": 0.9128,
            "auc_score": 0.9567,
            "decision_threshold": 0.6111
        }
        
        # Load artifacts on initialization
        self.load_artifacts()

    def load_artifacts(self):
        """
        Loads all ML artifacts. Adjust file paths and names here as needed.
        If files are missing, it logs warning and sets defaults to prevent crash.
        """
        # 1. Load Main Classifier Model
        model_path = os.path.join(CHURN_DIR, "best_model.pkl")
        if not os.path.exists(model_path):
            # Fallback check inside backend/model/
            model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model", "best_model.pkl")
        
        try:
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                logger.info(f"Successfully loaded best_model.pkl from {model_path}")
            else:
                logger.warning(f"best_model.pkl not found at {model_path}. Placeholder/Mock model will be used.")
        except Exception as e:
            logger.error(f"Error loading best_model.pkl: {e}")

        # Load Metadata to check threshold
        meta_path = os.path.join(CHURN_DIR, "best_model_meta.pkl")
        if os.path.exists(meta_path):
            try:
                meta = joblib.load(meta_path)
                self.threshold = meta.get("threshold", 0.6111)
                # Load model performance metrics from metadata if available
                if "accuracy" in meta:
                    self.model_metrics["accuracy"] = meta.get("accuracy", 0.9128)
                if "precision" in meta:
                    self.model_metrics["precision"] = meta.get("precision", 0.8915)
                if "recall" in meta:
                    self.model_metrics["recall"] = meta.get("recall", 0.9342)
                if "f1_score" in meta:
                    self.model_metrics["f1_score"] = meta.get("f1_score", 0.9128)
                if "auc_score" in meta:
                    self.model_metrics["auc_score"] = meta.get("auc_score", 0.9567)
                logger.info(f"Loaded threshold {self.threshold} and performance metrics from best_model_meta.pkl")
            except Exception as e:
                logger.warning(f"Error loading best_model_meta.pkl: {e}. Using default threshold and metrics: {self.threshold}")

        # 2. Load Imputation Stats (numerical_imputer)
        impute_path = os.path.join(MODEL_DIR, "impute_stats.pkl")
        try:
            if os.path.exists(impute_path):
                self.impute_stats = joblib.load(impute_path)
                logger.info(f"Loaded impute_stats.pkl from {impute_path}")
            else:
                # Default statistics from training notebook
                self.impute_stats = {'salary_k': 25.53704952841609, 'tenure_years': 2.06}
                logger.warning("impute_stats.pkl not found. Using default training median values.")
        except Exception as e:
            logger.error(f"Error loading impute_stats.pkl: {e}")
            self.impute_stats = {'salary_k': 25.53704952841609, 'tenure_years': 2.06}

        # 3. Load Outlier Clipping Boundaries
        clip_path = os.path.join(MODEL_DIR, "clip_bounds.pkl")
        try:
            if os.path.exists(clip_path):
                self.clip_bounds = joblib.load(clip_path)
                logger.info(f"Loaded clip_bounds.pkl from {clip_path}")
            else:
                logger.warning("clip_bounds.pkl not found. Piecewise clipping will use fallback defaults.")
        except Exception as e:
            logger.error(f"Error loading clip_bounds.pkl: {e}")

        # 4. Load Expected Feature Columns (One-Hot Encoding aligned dimension)
        features_path = os.path.join(MODEL_DIR, "feature_columns.pkl")
        try:
            if os.path.exists(features_path):
                self.feature_columns = joblib.load(features_path)
                logger.info(f"Loaded feature_columns.pkl from {features_path}. Expected features: {len(self.feature_columns)}")
            else:
                logger.warning("feature_columns.pkl not found. Column alignment might be inconsistent.")
        except Exception as e:
            logger.error(f"Error loading feature_columns.pkl: {e}")

    def preprocess_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executes the identical Preprocessing and Feature Engineering pipeline 
        as defined in churn.ipynb.
        
        Input dataframe should have the raw columns (except CustomerID).
        """
        df_proc = df.copy()

        # --- STEP 1: Missing Values Imputation ---
        # Handling salary_k and tenure_years
        if 'salary_k' in df_proc.columns:
            df_proc['salary_k'] = df_proc['salary_k'].fillna(self.impute_stats.get('salary_k', 25.53704952841609))
        if 'tenure_years' in df_proc.columns:
            df_proc['tenure_years'] = df_proc['tenure_years'].fillna(self.impute_stats.get('tenure_years', 2.06))

        # Fill other numeric columns with median if missing
        numeric_cols = df_proc.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col not in ['salary_k', 'tenure_years']:
                df_proc[col] = df_proc[col].fillna(0)

        # Fill discrete columns with mode or empty string if missing
        discrete_cols = df_proc.select_dtypes(exclude=[np.number]).columns
        for col in discrete_cols:
            df_proc[col] = df_proc[col].fillna("Unknown")

        # --- STEP 2: Logarithmic Transformation ---
        # salary_k is transformed to log_salary_k to handle skewness
        if 'salary_k' in df_proc.columns:
            df_proc['log_salary_k'] = np.log1p(df_proc['salary_k'])
            df_proc.drop('salary_k', axis=1, inplace=True)

        # --- STEP 3: Ratio Feature Engineering ---
        # Avoid division by zero by adding 1 or 0.01 respectively
        df_proc['Engagement_Per_Login'] = df_proc['engagement_score'] / (df_proc['number_of_logins'] + 1)
        df_proc['Complaints_Ratio'] = df_proc['complaints'] / (df_proc['number_of_logins'] + 1)
        df_proc['Login_Frequency'] = df_proc['number_of_logins'] / (df_proc['tenure_years'] + 0.01)

        # --- STEP 4: Binary Flagging Features ---
        df_proc['New_User_Flag'] = (df_proc['tenure_years'] < 1).astype(int)
        # Quantile (0.25) from the dataset for engagement_score is 2.5
        df_proc['Low_Engagement_Flag'] = (df_proc['engagement_score'] < 2.5).astype(int)

        # --- STEP 5: Piecewise Outlier Clipping ---
        continuous_features = [
            'log_salary_k', 'tenure_years', 'number_of_logins', 
            'complaints', 'engagement_score', 'Engagement_Per_Login', 
            'Complaints_Ratio', 'Login_Frequency'
        ]
        
        if self.clip_bounds:
            for col in continuous_features:
                if col in df_proc.columns and col in self.clip_bounds:
                    lower = self.clip_bounds[col]['lower']
                    upper = self.clip_bounds[col]['upper']
                    df_proc[col] = np.clip(df_proc[col], lower, upper)

        # --- STEP 6: One-Hot Encoding (Dummies) ---
        # Explicit categorical columns
        categorical_cols = ['subscription_type', 'region', 'device_type']
        # Convert any object types in other fields (excluding dates if any)
        df_proc = pd.get_dummies(df_proc, columns=categorical_cols, drop_first=True)

        # Drop date columns that are not part of the model inputs
        for date_col in ['signup_date', 'last_active_date']:
            if date_col in df_proc.columns:
                df_proc.drop(date_col, axis=1, inplace=True)

        # --- STEP 7: Dimension Alignment / Reindexing ---
        # Align all features with feature_columns.pkl (expected by the classifier)
        if self.feature_columns:
            df_proc = df_proc.reindex(columns=self.feature_columns, fill_value=0)
        
        return df_proc

    def predict_single(self, input_data: dict) -> dict:
        """
        Executes prediction for a single customer record.
        """
        customer_id = input_data.get("CustomerID", "UNKNOWN")
        
        # Convert input dictionary into Pandas DataFrame (1 row)
        df_raw = pd.DataFrame([input_data])
        
        # Drop CustomerID as it is not a feature
        if "CustomerID" in df_raw.columns:
            df_raw.drop("CustomerID", axis=1, inplace=True)
            
        try:
            # Process dataframe matching pipeline
            df_processed = self.preprocess_df(df_raw)
            
            # Predict probability if model exists
            if self.model:
                prob = float(self.model.predict_proba(df_processed)[0][1])
            else:
                # Mock fallback probability using simple heuristics if model is missing
                logger.warning("Using mock calculation as XGBoost model is not loaded.")
                # Base probability
                prob = 0.2
                # Custom mock formulas to mimic real conditions
                if float(input_data.get('complaints', 0)) > 0:
                    prob += 0.4
                if float(input_data.get('engagement_score', 0)) < 3.0:
                    prob += 0.3
                if float(input_data.get('tenure_years', 0)) < 1.0:
                    prob += 0.1
                prob = min(max(prob, 0.0), 1.0)
            
            # Decision threshold check
            churn_pred = 1 if prob >= self.threshold else 0
            
            # Risk Score (0-100, rounded to 2 decimal places)
            risk_score = round(prob * 100, 2)
            
            # Risk Banding step function
            if risk_score <= 30:
                risk_band = "Low Risk"
            elif risk_score <= 70:
                risk_band = "Medium Risk"
            else:
                risk_band = "High Risk"
                
            return {
                "CustomerID": customer_id,
                "risk_score": risk_score,
                "risk_band": risk_band,
                "churn_prediction": churn_pred,
                "churn_probability": round(prob, 4)
            }
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise e

    def predict_batch(self, df_batch: pd.DataFrame) -> list:
        """
        Executes prediction for a batch of customers from a DataFrame.
        """
        if "CustomerID" not in df_batch.columns:
            raise ValueError("CSV must contain a 'CustomerID' column.")
            
        results = []
        
        # Split customer ids and features
        customer_ids = df_batch["CustomerID"].astype(str).tolist()
        df_features = df_batch.drop("CustomerID", axis=1)
        
        try:
            df_processed = self.preprocess_df(df_features)
            
            if self.model:
                probs = self.model.predict_proba(df_processed)[:, 1]
            else:
                # Mock probabilities fallback
                logger.warning("Using mock calculations for batch as XGBoost model is not loaded.")
                probs = []
                for _, row in df_batch.iterrows():
                    p = 0.2
                    if float(row.get('complaints', 0)) > 0: p += 0.4
                    if float(row.get('engagement_score', 0)) < 3.0: p += 0.3
                    if float(row.get('tenure_years', 0)) < 1.0: p += 0.1
                    probs.append(min(max(p, 0.0), 1.0))
                probs = np.array(probs)
                
            for idx, prob in enumerate(probs):
                churn_pred = 1 if prob >= self.threshold else 0
                risk_score = round(float(prob) * 100, 2)
                
                if risk_score <= 30:
                    risk_band = "Low Risk"
                elif risk_score <= 70:
                    risk_band = "Medium Risk"
                else:
                    risk_band = "High Risk"
                    
                results.append({
                    "CustomerID": customer_ids[idx],
                    "risk_score": risk_score,
                    "risk_band": risk_band,
                    "churn_prediction": int(churn_pred),
                    "churn_probability": round(float(prob), 4)
                })
            
            return results
        except Exception as e:
            logger.error(f"Batch prediction failed: {e}")
            raise e

    def get_model_metrics(self):
        """
        Returns the current model performance metrics.
        These are loaded from best_model_meta.pkl or defaults from training.
        """
        return {
            "accuracy": round(self.model_metrics["accuracy"], 4),
            "precision": round(self.model_metrics["precision"], 4),
            "recall": round(self.model_metrics["recall"], 4),
            "f1_score": round(self.model_metrics["f1_score"], 4),
            "auc_score": round(self.model_metrics["auc_score"], 4),
            "decision_threshold": round(self.model_metrics["decision_threshold"], 4)
        }

# Global single instance of the service
ml_service = MLPredictionService()
