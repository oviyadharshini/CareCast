# Hospital Resource Optimization System

A comprehensive machine learning system for predicting and optimizing hospital resource allocation using real-time data analytics.

## System Overview

This end-to-end ML system provides:

- **Predictive Analytics**: XGBoost-based forecasting for hospital resources (1h, 6h, 24h horizons)
- **Resource Optimization**: Linear programming optimization for staff allocation using PuLP
- **Real-time Dashboard**: React-based visualization with live predictions and alerts
- **Synthetic Data Generation**: Realistic hospital time-series data generator
- **RESTful API**: FastAPI backend for all system interactions

## Features

### 🔮 Predictive Models
- Forecasts bed occupancy, oxygen supply, and admission rates
- Multi-horizon predictions (1h, 6h, 24h)
- XGBoost implementation with feature engineering
- Real-time model retraining capabilities

### ⚡ Resource Optimization
- Staff allocation optimization using linear programming (PuLP)
- Constraint-based optimization with budget and operational limits
- Cost reduction and efficiency improvement analytics
- Multi-shift and multi-role optimization

### 📊 Dashboard & Visualization
- Real-time hospital status monitoring
- Interactive predictions display
- System alerts and notifications
- Staff optimization recommendations
- Responsive web interface

### 🏥 Hospital Data Simulation
- Realistic time-series data generation
- Multiple resource types: beds, oxygen, staff, admissions
- Seasonal and hourly patterns
- Configurable data scenarios

## Project Structure

```
hospital-optimization/
├── backend/                 # FastAPI backend application
│   └── main.py             # Main API server
├── data/                   # Data generation and storage
│   └── synthetic_data_generator.py
├── models/                 # ML pipeline and trained models
│   └── ml_pipeline.py      # XGBoost prediction pipeline
├── optimization/           # Resource optimization modules
│   └── staff_optimizer.py  # PuLP-based staff optimization
├── frontend/               # React dashboard
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.js         # Main application
│   │   └── index.js       # Entry point
│   └── package.json       # Frontend dependencies
├── requirements.txt        # Python dependencies
├── Dockerfile             # Multi-stage Docker build
└── README.md              # This file
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend development)
- Docker (optional, for containerized deployment)

### 1. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Generate sample data
python data/synthetic_data_generator.py

# Start the FastAPI server
cd backend
python main.py
```

The API will be available at `http://localhost:5000`

### 2. Frontend Setup

```bash
# Install Node.js dependencies
cd frontend
npm install

# Start the development server
npm start
```

The dashboard will be available at `http://localhost:3000`

### 3. Docker Deployment

```bash
# Build and run with Docker
docker build -t hospital-optimization .
docker run -p 5000:5000 hospital-optimization
```

## API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API health check |
| `/current-status` | GET | Current hospital status |
| `/predict-resources` | POST | Generate resource predictions |
| `/optimize-staff` | POST | Optimize staff allocation |
| `/historical-data` | GET | Retrieve historical data |
| `/generate-sample-data` | GET | Generate synthetic data |

### Example API Usage

#### Get Current Status
```bash
curl http://localhost:5000/current-status
```

#### Generate Predictions
```bash
curl -X POST http://localhost:5000/predict-resources \
  -H "Content-Type: application/json" \
  -d '{
    "current_state": {
      "timestamp": "2024-01-01T12:00:00",
      "admissions": 8,
      "discharges": 6,
      "bed_occupancy": 180,
      "oxygen_level": 1200,
      "occupancy_rate": 72.0
    },
    "horizons": [1, 6, 24]
  }'
```

#### Optimize Staff Allocation
```bash
curl -X POST http://localhost:5000/optimize-staff \
  -H "Content-Type: application/json" \
  -d '{
    "current_staff": {
      "Nurses": {"Morning": 20, "Evening": 15, "Night": 12},
      "Doctors": {"Morning": 12, "Evening": 10, "Night": 6},
      "Support_Staff": {"Morning": 8, "Evening": 6, "Night": 4}
    },
    "predicted_demand": {
      "admissions": 14,
      "bed_occupancy": 180
    }
  }'
```

## Machine Learning Pipeline

### Data Generation
The synthetic data generator creates realistic hospital time-series data including:
- **Admissions/Discharges**: Hourly patient flow with day/night and weekend patterns
- **Bed Occupancy**: Dynamic bed utilization based on patient flow
- **Oxygen Levels**: Tank levels with consumption patterns and refill events
- **Staff Schedules**: Multi-shift staffing across different roles

### Prediction Models
- **Algorithm**: XGBoost Regressor
- **Features**: Time-based features, lag features, rolling statistics, interaction features
- **Targets**: Admissions, bed occupancy, oxygen levels
- **Horizons**: 1-hour, 6-hour, and 24-hour predictions

### Optimization Engine
- **Method**: Linear Programming using PuLP
- **Objective**: Minimize staffing costs while meeting demand
- **Constraints**: Minimum coverage, budget limits, operational requirements
- **Variables**: Staff count by type (Nurses, Doctors, Support) and shift (Morning, Evening, Night)

## Configuration

### Environment Variables
- `PORT`: API server port (default: 5000)
- `HOST`: Server host (default: 0.0.0.0)
- `DEBUG`: Debug mode (default: False)

### Model Configuration
- Prediction horizons: Configurable in API requests
- Training data size: Adjustable in data generator
- Optimization constraints: Customizable per request

## Development

### Running Tests
```bash
# Backend tests (when implemented)
python -m pytest tests/

# Frontend tests
cd frontend
npm test
```

### Adding New Features
1. **New Prediction Models**: Add to `models/ml_pipeline.py`
2. **Additional Optimization**: Extend `optimization/staff_optimizer.py`
3. **Dashboard Components**: Add to `frontend/src/components/`
4. **API Endpoints**: Extend `backend/main.py`

## System Requirements

### Minimum Requirements
- CPU: 2 cores
- RAM: 4GB
- Storage: 2GB
- Python 3.11+
- Node.js 18+ (for development)

### Production Requirements
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 10GB+
- Load balancer (for high availability)
- Database (PostgreSQL/MongoDB for persistent storage)

## Deployment Options

### Local Development
```bash
# Backend only
python backend/main.py

# Full stack with frontend
npm run dev  # In frontend directory
python backend/main.py  # In separate terminal
```

### Docker Production
```bash
docker build -t hospital-optimization .
docker run -d -p 5000:5000 --name hospital-opt hospital-optimization
```

### Cloud Deployment
- **AWS**: ECS/EKS with Application Load Balancer
- **GCP**: Cloud Run or GKE
- **Azure**: Container Instances or AKS

## Monitoring & Logging

- API request/response logging
- Model performance tracking
- Resource usage monitoring
- Error rate and latency metrics

## Security Considerations

- Input validation on all API endpoints
- Rate limiting for API requests
- CORS configuration for cross-origin requests
- Environment variable management for secrets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with appropriate tests
4. Submit a pull request with detailed description

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
- Create an issue in the repository
- Check the API documentation at `/docs` (FastAPI auto-generated)
- Review the system logs for debugging

## Acknowledgments

- **XGBoost**: Gradient boosting framework
- **PuLP**: Linear programming library
- **FastAPI**: Modern web framework for APIs
- **React**: Frontend user interface framework
- **Chart.js**: Data visualization library