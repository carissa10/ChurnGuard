-- ChurnShield Database Schema for Supabase

-- 1. Users table (authentication)
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  role VARCHAR(50) DEFAULT 'analyst',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Customers table
CREATE TABLE IF NOT EXISTS customers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id VARCHAR(50) UNIQUE NOT NULL,
  age INT,
  salary_k FLOAT,
  tenure_years FLOAT,
  number_of_logins INT,
  complaints INT,
  engagement_score FLOAT,
  subscription_type VARCHAR(50),
  region VARCHAR(100),
  device_type VARCHAR(50),
  signup_date DATE,
  last_active_date DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Single Predictions table
CREATE TABLE IF NOT EXISTS predictions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id VARCHAR(50) NOT NULL,
  churn_prediction INT NOT NULL,
  risk_score FLOAT NOT NULL,
  risk_band VARCHAR(20) NOT NULL,
  churn_probability FLOAT NOT NULL,
  model_version VARCHAR(50),
  predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- 4. Batch Predictions (main batch job)
CREATE TABLE IF NOT EXISTS batch_predictions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  batch_name VARCHAR(255),
  file_name VARCHAR(255) NOT NULL,
  total_records INT NOT NULL,
  total_churn INT NOT NULL,
  average_risk_score FLOAT NOT NULL,
  low_risk_count INT,
  medium_risk_count INT,
  high_risk_count INT,
  model_accuracy FLOAT,
  model_precision FLOAT,
  model_recall FLOAT,
  model_f1_score FLOAT,
  model_auc_score FLOAT,
  decision_threshold FLOAT,
  processed_by UUID NOT NULL,
  processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(50) DEFAULT 'completed',
  FOREIGN KEY (processed_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 5. Batch Prediction Results (individual results)
CREATE TABLE IF NOT EXISTS batch_prediction_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  batch_id UUID NOT NULL,
  customer_id VARCHAR(50) NOT NULL,
  churn_prediction INT NOT NULL,
  risk_score FLOAT NOT NULL,
  risk_band VARCHAR(20) NOT NULL,
  churn_probability FLOAT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (batch_id) REFERENCES batch_predictions(id) ON DELETE CASCADE,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- 6. Prediction History (audit trail)
CREATE TABLE IF NOT EXISTS prediction_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  prediction_id UUID,
  action VARCHAR(50) NOT NULL,
  old_value JSONB,
  new_value JSONB,
  changed_by UUID,
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 7. NLP Sentiment Analysis Results
CREATE TABLE IF NOT EXISTS nlp_sentiment_analysis (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id VARCHAR(50),
  review_text TEXT,
  sentiment_label VARCHAR(20) NOT NULL,
  sentiment_score FLOAT NOT NULL,
  confidence FLOAT,
  analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- 8. Model Performance Metrics (track over time)
CREATE TABLE IF NOT EXISTS model_performance_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  accuracy FLOAT NOT NULL,
  precision FLOAT NOT NULL,
  recall FLOAT NOT NULL,
  f1_score FLOAT NOT NULL,
  auc_score FLOAT NOT NULL,
  decision_threshold FLOAT NOT NULL,
  model_version VARCHAR(50),
  recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enable Row Level Security (RLS) for security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE batch_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE batch_prediction_results ENABLE ROW LEVEL SECURITY;

-- Create indexes for common queries (PostgreSQL syntax)
CREATE INDEX IF NOT EXISTS idx_customers_customer_id ON customers(customer_id);
CREATE INDEX IF NOT EXISTS idx_predictions_customer_id ON predictions(customer_id);
CREATE INDEX IF NOT EXISTS idx_predictions_predicted_at ON predictions(predicted_at);
CREATE INDEX IF NOT EXISTS idx_batch_predictions_processed_by ON batch_predictions(processed_by);
CREATE INDEX IF NOT EXISTS idx_batch_predictions_processed_at ON batch_predictions(processed_at);
CREATE INDEX IF NOT EXISTS idx_batch_predictions_status ON batch_predictions(status);
CREATE INDEX IF NOT EXISTS idx_batch_prediction_results_batch_id ON batch_prediction_results(batch_id);
CREATE INDEX IF NOT EXISTS idx_batch_prediction_results_customer_id ON batch_prediction_results(customer_id);
CREATE INDEX IF NOT EXISTS idx_prediction_history_prediction_id ON prediction_history(prediction_id);
CREATE INDEX IF NOT EXISTS idx_prediction_history_changed_at ON prediction_history(changed_at);
CREATE INDEX IF NOT EXISTS idx_nlp_sentiment_customer_id ON nlp_sentiment_analysis(customer_id);
CREATE INDEX IF NOT EXISTS idx_nlp_sentiment_analyzed_at ON nlp_sentiment_analysis(analyzed_at);
CREATE INDEX IF NOT EXISTS idx_predictions_risk_band ON predictions(risk_band);
CREATE INDEX IF NOT EXISTS idx_predictions_churn_prediction ON predictions(churn_prediction);
CREATE INDEX IF NOT EXISTS idx_model_metrics_recorded_at ON model_performance_metrics(recorded_at);
