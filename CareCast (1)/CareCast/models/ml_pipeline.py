"""
Machine Learning Pipeline for Hospital Resource Prediction
Uses XGBoost for time-series forecasting of hospital resource demands.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

class HospitalMLPipeline:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.target_columns = ['admissions', 'bed_occupancy', 'oxygen_level']
        
    def create_time_features(self, df):
        """Create time-based features for ML model"""
        df = df.copy()
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['is_business_hours'] = ((df['hour'] >= 9) & (df['hour'] <= 17)).astype(int)
        df['is_night'] = ((df['hour'] <= 6) | (df['hour'] >= 22)).astype(int)
        return df
    
    def create_lag_features(self, df, target_col, lags=[1, 2, 3, 6, 12, 24]):
        """Create lag features for time series prediction"""
        for lag in lags:
            df[f'{target_col}_lag_{lag}'] = df[target_col].shift(lag)
        
        # Rolling statistics
        df[f'{target_col}_roll_mean_6'] = df[target_col].rolling(window=6, min_periods=1).mean()
        df[f'{target_col}_roll_std_6'] = df[target_col].rolling(window=6, min_periods=1).std()
        df[f'{target_col}_roll_mean_24'] = df[target_col].rolling(window=24, min_periods=1).mean()
        
        return df
    
    def prepare_features(self, df):
        """Prepare all features for ML model"""
        df = self.create_time_features(df)
        
        # Create lag features for each target
        for target in self.target_columns:
            if target in df.columns:
                df = self.create_lag_features(df, target)
        
        # Add interaction features
        df['occupancy_oxygen_ratio'] = df['bed_occupancy'] / (df['oxygen_level'] + 1)
        df['admission_rate_trend'] = df['admissions'].rolling(window=6, min_periods=1).mean()
        df['discharge_rate_trend'] = df['discharges'].rolling(window=6, min_periods=1).mean()
        
        # Fill NaN values
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        return df
    
    def create_prediction_targets(self, df, horizons=[1, 6, 24]):
        """Create prediction targets for different time horizons"""
        targets = {}
        
        for target_col in self.target_columns:
            if target_col in df.columns:
                for horizon in horizons:
                    target_name = f'{target_col}_next_{horizon}h'
                    targets[target_name] = df[target_col].shift(-horizon)
        
        return targets
    
    def train_models(self, df, horizons=[1, 6, 24]):
        """Train XGBoost models for different prediction horizons"""
        print("Preparing features...")
        df_features = self.prepare_features(df)
        
        # Define feature columns (exclude timestamp and targets)
        exclude_cols = ['timestamp'] + self.target_columns
        self.feature_columns = [col for col in df_features.columns if col not in exclude_cols]
        
        print("Creating prediction targets...")
        targets = self.create_prediction_targets(df_features, horizons)
        
        # Train models for each target and horizon
        for target_name, target_values in targets.items():
            print(f"Training model for {target_name}...")
            
            # Prepare training data
            X = df_features[self.feature_columns]
            y = target_values
            
            # Remove rows with NaN targets
            mask = ~y.isna()
            X_clean = X[mask]
            y_clean = y[mask]
            
            if len(y_clean) < 50:  # Skip if insufficient data
                continue
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_clean, y_clean, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Train XGBoost model
            model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1
            )
            
            model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            print(f"{target_name} - MAE: {mae:.2f}, RMSE: {rmse:.2f}")
            
            # Store model
            self.models[target_name] = model
        
        print(f"Trained {len(self.models)} models successfully!")
    
    def predict_resources(self, current_data, horizons=[1, 6, 24]):
        """Make predictions for specified time horizons"""
        if isinstance(current_data, dict):
            # Convert single data point to DataFrame and add missing columns with defaults
            df = pd.DataFrame([current_data])
            
            # Add missing columns with default values
            required_columns = ['total_beds', 'consumption_rate', 'refill_event', 'max_capacity', 'bed_stress', 'oxygen_stress']
            for col in required_columns:
                if col not in df.columns:
                    if col == 'total_beds':
                        df[col] = 250
                    elif col == 'max_capacity':
                        df[col] = 2500
                    elif col == 'consumption_rate':
                        df[col] = 15.0
                    elif col == 'refill_event':
                        df[col] = False
                    elif col == 'bed_stress':
                        df[col] = df['occupancy_rate'] > 85 if 'occupancy_rate' in df.columns else False
                    elif col == 'oxygen_stress':
                        df[col] = df['oxygen_level'] < 800 if 'oxygen_level' in df.columns else False
                    else:
                        df[col] = 0
        else:
            df = current_data.copy()
        
        # Prepare features
        df_features = self.prepare_features(df)
        
        # Ensure all required feature columns are present
        missing_features = [col for col in self.feature_columns if col not in df_features.columns]
        for col in missing_features:
            df_features[col] = 0  # Default value for missing features
        
        X = df_features[self.feature_columns].iloc[-1:] # Use latest data point
        
        predictions = {}
        
        for target_col in self.target_columns:
            predictions[target_col] = {}
            
            for horizon in horizons:
                model_name = f'{target_col}_next_{horizon}h'
                
                if model_name in self.models:
                    pred = self.models[model_name].predict(X)[0]
                    predictions[target_col][f'{horizon}h'] = max(0, pred)  # Ensure non-negative
                else:
                    # Fallback prediction
                    current_value = df[target_col].iloc[-1] if target_col in df.columns else 0
                    predictions[target_col][f'{horizon}h'] = current_value
        
        return predictions
    
    def get_feature_importance(self, top_n=10):
        """Get feature importance for all models"""
        importance_data = {}
        
        for model_name, model in self.models.items():
            feature_importance = model.feature_importances_
            importance_df = pd.DataFrame({
                'feature': self.feature_columns,
                'importance': feature_importance
            }).sort_values('importance', ascending=False).head(top_n)
            
            importance_data[model_name] = importance_df.to_dict('records')
        
        return importance_data
    
    def save_models(self, model_dir='models'):
        """Save trained models to disk"""
        os.makedirs(model_dir, exist_ok=True)
        
        for model_name, model in self.models.items():
            model_path = f'{model_dir}/{model_name}.joblib'
            joblib.dump(model, model_path)
        
        # Save feature columns
        metadata = {
            'feature_columns': self.feature_columns,
            'target_columns': self.target_columns,
            'model_names': list(self.models.keys()),
            'trained_at': datetime.now().isoformat()
        }
        
        joblib.dump(metadata, f'{model_dir}/metadata.joblib')
        print(f"Models saved to {model_dir}/")
    
    def load_models(self, model_dir='models'):
        """Load trained models from disk"""
        try:
            # Load metadata
            metadata = joblib.load(f'{model_dir}/metadata.joblib')
            self.feature_columns = metadata['feature_columns']
            self.target_columns = metadata['target_columns']
            
            # Load models
            for model_name in metadata['model_names']:
                model_path = f'{model_dir}/{model_name}.joblib'
                if os.path.exists(model_path):
                    self.models[model_name] = joblib.load(model_path)
            
            print(f"Loaded {len(self.models)} models from {model_dir}/")
            return True
        except Exception as e:
            print(f"Error loading models: {str(e)}")
            return False

if __name__ == "__main__":
    # Example usage
    from data.synthetic_data_generator import HospitalDataGenerator
    
    # Generate synthetic data
    generator = HospitalDataGenerator()
    hospital_data, _ = generator.generate_complete_dataset(days=30)
    
    # Train ML pipeline
    pipeline = HospitalMLPipeline()
    pipeline.train_models(hospital_data)
    pipeline.save_models()
    
    # Test prediction
    current_state = {
        'timestamp': pd.Timestamp.now(),
        'admissions': 8,
        'discharges': 6,
        'bed_occupancy': 180,
        'oxygen_level': 1200,
        'occupancy_rate': 72.0
    }
    
    predictions = pipeline.predict_resources(current_state)
    print("\nSample Predictions:")
    for resource, horizons in predictions.items():
        print(f"{resource}: {horizons}")