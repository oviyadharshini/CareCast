# Running Hospital Resource Optimization System Locally

This guide provides step-by-step instructions for running the Hospital Resource Optimization System on your local computer.

## System Requirements

### Programming Languages & Runtime
- **Python 3.11** (specified in Dockerfile)
- **Node.js 18+** (specified in Dockerfile, needed for frontend)
- **npm** (comes with Node.js, for package management)

### System Dependencies (for optimization solver)
- **CBC solver** (`coinor-cbc` package)
  - On Ubuntu/Debian: `apt-get install coinor-cbc`
  - On macOS: `brew install coin-or-tools/coinor/cbc`
  - On Windows: Download CBC binaries or use Windows Subsystem for Linux

### Build Tools (for Python packages)
- **gcc** (C compiler)
- **g++** (C++ compiler)
- These are needed for compiling XGBoost and other scientific Python packages

## Python Dependencies (Backend)

The following packages are required (from `requirements.txt`):

```
fastapi==0.117.1
uvicorn==0.36.0
xgboost==3.0.5
pulp==3.3.0
pandas==2.3.2
numpy==2.3.3
scikit-learn==1.7.2
pydantic==2.11.9
python-multipart==0.0.20
matplotlib==3.10.6
seaborn==0.13.2
plotly==6.3.0
joblib==1.5.2
```

## Node.js Dependencies (Frontend)

The following packages are required (from `frontend/package.json`):

```
react@18.2.0
react-dom@18.2.0
react-scripts@5.0.1
axios@1.4.0
chart.js@4.3.0
react-chartjs-2@5.2.0
react-router-dom@6.11.0
web-vitals@2.1.4
(plus testing libraries)
```

## Installation & Setup

### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Generate sample data (optional)
python data/synthetic_data_generator.py
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# For development (runs on port 3000)
npm start

# For production build
npm run build
```

## Running the Application

### Option 1: Development Mode (Frontend + Backend separately)

```bash
# Terminal 1: Start backend (port 5000)
python backend/main.py

# Terminal 2: Start frontend dev server (port 3000)
cd frontend && npm start
```

- Backend API: http://localhost:5000
- Frontend: http://localhost:3000
- Frontend automatically proxies API calls to backend

### Option 2: Production Mode (Backend serves built frontend)

```bash
# Build frontend first
cd frontend && npm run build

# Run backend (serves both API and frontend on port 5000)
python backend/main.py
```

- Full application: http://localhost:5000

## Project Structure Created

The application will create these directories during runtime:

- `models/` - ML model files (9 XGBoost models)
- `data/` - Generated hospital data files
- `frontend/build/` - Built React application (after npm run build)

## Network Requirements

- **Port 5000**: Backend API server
- **Port 3000**: Frontend development server (dev mode only)
- Backend has CORS configured for localhost:3000

## Alternative: Docker

If you prefer Docker instead of local installation:

```bash
# Build and run with Docker
docker build -t hospital-optimization .
docker run -p 5000:5000 hospital-optimization
```

This handles all system dependencies automatically but requires Docker to be installed.

## Troubleshooting

### Common Issues

1. **CBC solver not found**: Install `coinor-cbc` package for your operating system
2. **Python package compilation errors**: Ensure gcc/g++ build tools are installed
3. **Node.js version issues**: Use Node.js 18+ for compatibility
4. **Port conflicts**: Ensure ports 3000 and 5000 are available

### Verification

Test that the system is working:

```bash
# Test backend health
curl http://localhost:5000/health

# Test current status
curl http://localhost:5000/current-status

# Test predictions
curl -X POST http://localhost:5000/predict-resources \
  -H "Content-Type: application/json" \
  -d '{"current_state":{"timestamp":"2024-01-01T12:00:00","admissions":8,"discharges":6,"bed_occupancy":180,"oxygen_level":1200,"occupancy_rate":72.0},"horizons":[1,6,24]}'
```

## Features Available

Once running, the system provides:

- **Real-time Hospital Dashboard**: Monitor bed occupancy, oxygen levels, admissions
- **Predictive Analytics**: 1h, 6h, and 24h resource demand forecasting
- **Staff Optimization**: Linear programming-based staff allocation
- **Interactive Web Interface**: React-based dashboard with live updates
- **RESTful API**: Complete API for integrations and custom applications