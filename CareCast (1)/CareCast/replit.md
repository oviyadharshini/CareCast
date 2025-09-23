# Overview

The Hospital Resource Optimization System is a comprehensive machine learning application that predicts and optimizes hospital resource allocation using real-time data analytics. The system combines predictive modeling with optimization algorithms to help hospitals efficiently manage resources like bed occupancy, oxygen supply, staff allocation, and patient admissions. It features a React-based dashboard for real-time visualization, FastAPI backend for data processing, XGBoost models for forecasting, and linear programming optimization for staff scheduling.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: React 18 with functional components and hooks
- **Styling**: CSS modules with responsive grid layouts
- **Data Visualization**: Chart.js and React-Chart.js-2 for interactive charts and graphs
- **State Management**: React hooks (useState, useEffect) for local component state
- **API Integration**: Axios for HTTP requests to the FastAPI backend
- **Build System**: Create React App with standard build pipeline
- **Routing**: React Router DOM for single-page application navigation

## Backend Architecture
- **Framework**: FastAPI with async/await patterns for high-performance API endpoints
- **API Design**: RESTful API with clear separation of concerns
- **Data Models**: Pydantic models for request/response validation and serialization
- **CORS Configuration**: Configured for development with localhost origins
- **Static File Serving**: Integrated React build serving for production deployment
- **Error Handling**: HTTP exception handling with appropriate status codes

## Machine Learning Pipeline
- **Primary Algorithm**: XGBoost for time-series forecasting with multiple prediction horizons (1h, 6h, 24h)
- **Feature Engineering**: Time-based features (hour, day of week, seasonality) and lag features
- **Model Training**: Scikit-learn pipeline with train/test splits and cross-validation
- **Model Persistence**: Joblib for model serialization and loading
- **Prediction Types**: Multi-target prediction for admissions, bed occupancy, and oxygen levels
- **Performance Metrics**: MAE and MSE for model evaluation

## Optimization Engine
- **Algorithm**: Linear programming using PuLP library
- **Optimization Target**: Staff allocation across multiple shifts and roles
- **Constraints**: Budget limits, minimum/maximum staff requirements, operational constraints
- **Objective Function**: Cost minimization while meeting predicted demand
- **Staff Categories**: Nurses, Doctors, Support Staff across Morning/Evening/Night shifts

## Data Management
- **Data Generation**: Synthetic time-series data generator with realistic hospital patterns
- **Data Format**: Pandas DataFrames for in-memory data processing
- **Time Series Handling**: Hourly frequency data with seasonal and daily patterns
- **Feature Storage**: JSON and CSV formats for data persistence
- **Real-time Processing**: Streaming data updates with configurable refresh intervals

# External Dependencies

## Core ML Libraries
- **XGBoost 3.0.5**: Primary machine learning algorithm for predictive modeling
- **Scikit-learn 1.7.2**: Model evaluation, preprocessing, and pipeline management
- **Pandas 2.3.2**: Data manipulation and time-series processing
- **NumPy 2.3.3**: Numerical computations and array operations

## Optimization Libraries
- **PuLP 3.3.0**: Linear programming solver for staff optimization
- **Joblib 1.5.2**: Model serialization and parallel processing

## Web Framework
- **FastAPI 0.117.1**: Async web framework for API development
- **Uvicorn 0.36.0**: ASGI server for FastAPI deployment
- **Pydantic 2.11.9**: Data validation and serialization

## Frontend Dependencies
- **React 18.2.0**: Core frontend framework
- **Chart.js 4.3.0**: Data visualization library
- **React-Chart.js-2 5.2.0**: React wrapper for Chart.js
- **Axios 1.4.0**: HTTP client for API communication
- **React Router DOM 6.11.0**: Client-side routing

## Data Visualization
- **Matplotlib 3.10.6**: Static plotting for backend analytics
- **Seaborn 0.13.2**: Statistical data visualization
- **Plotly 6.3.0**: Interactive plotting capabilities

## Development Tools
- **Python-multipart 0.0.20**: File upload handling in FastAPI
- **React Scripts 5.0.1**: Build and development tools for React
- **Create React App**: Standard React development environment