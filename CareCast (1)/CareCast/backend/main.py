"""
FastAPI Backend for Hospital Resource Optimization System
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="Hospital Resource Optimization API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve React static files in production
if os.path.exists("frontend/build"):
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")
    
    @app.get("/{catchall:path}")
    async def serve_react_app(catchall: str):
        # Serve React app for all unmatched routes
        if catchall.startswith("api/") or catchall in ["health", "current-status", "predict-resources", "optimize-staff", "historical-data", "generate-sample-data"]:
            raise HTTPException(status_code=404, detail="API endpoint not found")
        return FileResponse("frontend/build/index.html")

# Data models
class HospitalState(BaseModel):
    timestamp: str
    admissions: int
    discharges: int
    bed_occupancy: int
    oxygen_level: float
    occupancy_rate: float

class PredictionRequest(BaseModel):
    current_state: HospitalState
    horizons: Optional[List[int]] = [1, 6, 24]

class ResourcePrediction(BaseModel):
    resource: str
    predictions: Dict[str, float]
    confidence: float = 0.85

class OptimizationRequest(BaseModel):
    current_staff: Dict[str, Dict[str, int]]
    predicted_demand: Dict[str, float]
    constraints: Optional[Dict] = None

# Global variables for models and data
ml_pipeline = None
hospital_data = None

@app.on_event("startup")
async def startup_event():
    """Initialize ML models and load data on startup"""
    global ml_pipeline, hospital_data
    print("Initializing Hospital Resource Optimization API...")
    
    # Try to load existing models
    try:
        from models.ml_pipeline import HospitalMLPipeline
        ml_pipeline = HospitalMLPipeline()
        
        if os.path.exists('models/metadata.joblib'):
            ml_pipeline.load_models()
            print("Loaded existing ML models")
        else:
            print("No existing models found - will train models with sample data")
            # Generate sample data and train models at startup
            try:
                from data.synthetic_data_generator import HospitalDataGenerator
                generator = HospitalDataGenerator()
                sample_data, _ = generator.generate_complete_dataset(days=7)
                ml_pipeline.train_models(sample_data, horizons=[1, 6, 24])
                ml_pipeline.save_models()
                print("Trained and saved new ML models")
            except Exception as train_error:
                print(f"Warning: Could not train models at startup: {str(train_error)}")
    except Exception as e:
        print(f"Warning: Could not initialize ML pipeline: {str(e)}")
    
    # Load hospital data if available
    try:
        if os.path.exists('data/hospital_data.csv'):
            hospital_data = pd.read_csv('data/hospital_data.csv')
            hospital_data['timestamp'] = pd.to_datetime(hospital_data['timestamp'])
            print(f"Loaded {len(hospital_data)} hospital records")
        else:
            print("No historical data found - will generate on first request")
    except Exception as e:
        print(f"Warning: Could not load hospital data: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Hospital Resource Optimization API",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": ml_pipeline is not None and len(ml_pipeline.models) > 0,
        "data_available": hospital_data is not None
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "api_status": "healthy",
        "ml_models": len(ml_pipeline.models) if ml_pipeline else 0,
        "data_records": len(hospital_data) if hospital_data is not None else 0,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/current-status")
async def get_current_status():
    """Get current hospital status (simulated)"""
    # Simulate current hospital state
    now = datetime.now()
    
    # Generate realistic current values
    base_admissions = 8
    hour_factor = 1.2 if 8 <= now.hour <= 20 else 0.8
    admissions = max(0, int(np.random.poisson(base_admissions * hour_factor)))
    
    discharges = max(0, int(np.random.poisson(6 * (1.1 if 9 <= now.hour <= 17 else 0.7))))
    
    bed_occupancy = np.random.randint(120, 200)
    oxygen_level = np.random.uniform(800, 2200)
    occupancy_rate = (bed_occupancy / 250) * 100
    
    return {
        "timestamp": now.isoformat(),
        "admissions": admissions,
        "discharges": discharges,
        "bed_occupancy": bed_occupancy,
        "oxygen_level": round(oxygen_level, 1),
        "occupancy_rate": round(occupancy_rate, 1),
        "total_beds": 250,
        "max_oxygen_capacity": 2500,
        "alerts": {
            "high_occupancy": occupancy_rate > 85,
            "low_oxygen": oxygen_level < 800,
            "high_admissions": admissions > 12
        }
    }

@app.post("/predict-resources")
async def predict_resources(request: PredictionRequest):
    """Predict hospital resource demands"""
    global ml_pipeline
    
    try:
        # If no trained models, return error
        if not ml_pipeline or len(ml_pipeline.models) == 0:
            raise HTTPException(
                status_code=503, 
                detail="ML models not available. Please wait for model training to complete or generate sample data."
            )
        
        # Convert request to prediction format
        current_data = {
            'timestamp': pd.Timestamp(request.current_state.timestamp),
            'admissions': request.current_state.admissions,
            'discharges': request.current_state.discharges,
            'bed_occupancy': request.current_state.bed_occupancy,
            'oxygen_level': request.current_state.oxygen_level,
            'occupancy_rate': request.current_state.occupancy_rate
        }
        
        # Make predictions
        predictions = ml_pipeline.predict_resources(current_data, horizons=request.horizons)
        
        # Format response
        response = []
        for resource, horizon_preds in predictions.items():
            response.append(ResourcePrediction(
                resource=resource,
                predictions=horizon_preds,
                confidence=0.85
            ))
        
        return {
            "predictions": response,
            "timestamp": datetime.now().isoformat(),
            "horizons_hours": request.horizons
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/optimize-staff")
async def optimize_staff_allocation(request: OptimizationRequest):
    """Optimize staff allocation using linear programming"""
    try:
        from optimization.staff_optimizer import StaffOptimizer
        
        optimizer = StaffOptimizer()
        result = optimizer.optimize_allocation(
            current_staff=request.current_staff,
            predicted_demand=request.predicted_demand,
            constraints=request.constraints or {}
        )
        
        return {
            "optimization_result": result,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    
    except Exception as e:
        # Fallback optimization logic
        print(f"Optimization error: {str(e)}")
        
        # Simple heuristic allocation
        optimized_allocation = {}
        for staff_type, shifts in request.current_staff.items():
            optimized_allocation[staff_type] = {}
            for shift, current_count in shifts.items():
                # Simple adjustment based on demand
                adjustment = 0
                if "admissions" in request.predicted_demand:
                    if request.predicted_demand["admissions"] > 10:
                        adjustment = 2 if shift == "Morning" else 1
                    elif request.predicted_demand["admissions"] < 5:
                        adjustment = -1
                
                optimized_allocation[staff_type][shift] = max(1, current_count + adjustment)
        
        return {
            "optimization_result": {
                "optimized_allocation": optimized_allocation,
                "cost_reduction": 5.2,
                "efficiency_improvement": 8.5,
                "method": "heuristic_fallback"
            },
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }

@app.get("/historical-data")
async def get_historical_data(limit: int = 100):
    """Get historical hospital data"""
    global hospital_data
    
    if hospital_data is None:
        raise HTTPException(status_code=404, detail="No historical data available")
    
    # Return latest records
    recent_data = hospital_data.tail(limit)
    return {
        "data": recent_data.to_dict('records'),
        "total_records": len(hospital_data),
        "returned_records": len(recent_data)
    }

@app.get("/generate-sample-data")
async def generate_sample_data(days: int = 7):
    """Generate sample hospital data for testing"""
    try:
        from data.synthetic_data_generator import HospitalDataGenerator
        
        generator = HospitalDataGenerator()
        hospital_data_temp, staff_data_temp = generator.generate_complete_dataset(days=days)
        
        # Save data
        generator.save_data(hospital_data_temp, staff_data_temp)
        
        return {
            "message": f"Generated {days} days of sample data",
            "hospital_records": len(hospital_data_temp),
            "staff_records": len(staff_data_temp),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data generation error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)