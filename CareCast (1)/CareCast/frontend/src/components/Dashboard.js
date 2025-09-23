import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Dashboard = ({ currentStatus, onRefresh }) => {
  const [predictions, setPredictions] = useState(null);
  const [optimization, setOptimization] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (currentStatus) {
      fetchPredictions();
    }
  }, [currentStatus]);

  const fetchPredictions = async () => {
    if (!currentStatus) return;
    
    try {
      const response = await axios.post('/predict-resources', {
        current_state: {
          timestamp: currentStatus.timestamp,
          admissions: currentStatus.admissions,
          discharges: currentStatus.discharges,
          bed_occupancy: currentStatus.bed_occupancy,
          oxygen_level: currentStatus.oxygen_level,
          occupancy_rate: currentStatus.occupancy_rate
        },
        horizons: [1, 6, 24]
      });
      setPredictions(response.data);
    } catch (error) {
      console.error('Failed to fetch predictions:', error);
    }
  };

  const optimizeStaff = async () => {
    if (!currentStatus || !predictions) return;
    
    setLoading(true);
    try {
      const currentStaff = {
        'Nurses': {'Morning': 20, 'Evening': 15, 'Night': 12},
        'Doctors': {'Morning': 12, 'Evening': 10, 'Night': 6},
        'Support_Staff': {'Morning': 8, 'Evening': 6, 'Night': 4}
      };

      const predictedDemand = {};
      predictions.predictions.forEach(pred => {
        if (pred.predictions['1h']) {
          predictedDemand[pred.resource] = pred.predictions['1h'];
        }
      });

      const response = await axios.post('/optimize-staff', {
        current_staff: currentStaff,
        predicted_demand: predictedDemand,
        constraints: {
          max_budget: 15000,
          min_total_staff: 60
        }
      });
      
      setOptimization(response.data);
    } catch (error) {
      console.error('Failed to optimize staff:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (value, thresholds) => {
    if (value >= thresholds.high) return 'high';
    if (value >= thresholds.medium) return 'medium';
    return 'normal';
  };

  const getAlerts = (status) => {
    const alerts = [];
    
    if (status.alerts.high_occupancy) {
      alerts.push({
        type: 'danger',
        message: `High bed occupancy: ${status.occupancy_rate.toFixed(1)}% (Critical threshold: 85%)`
      });
    }
    
    if (status.alerts.low_oxygen) {
      alerts.push({
        type: 'warning', 
        message: `Low oxygen level: ${status.oxygen_level.toFixed(0)}L (Warning threshold: 800L)`
      });
    }
    
    if (status.alerts.high_admissions) {
      alerts.push({
        type: 'warning',
        message: `High admission rate: ${status.admissions} patients/hour (Normal: <12)`
      });
    }
    
    if (alerts.length === 0) {
      alerts.push({
        type: 'success',
        message: 'All systems operating within normal parameters'
      });
    }
    
    return alerts;
  };

  if (!currentStatus) {
    return <div>Loading dashboard...</div>;
  }

  const alerts = getAlerts(currentStatus);

  return (
    <div className="dashboard">
      <button onClick={onRefresh} className="refresh-button">
        Refresh Data
      </button>

      {/* Current Status Cards */}
      <div className="status-card">
        <h3>Current Hospital Status</h3>
        <div className="metric">
          <span className="metric-label">Bed Occupancy</span>
          <span className={`metric-value ${getStatusColor(currentStatus.occupancy_rate, {high: 85, medium: 70})}`}>
            {currentStatus.bed_occupancy}/{currentStatus.total_beds} ({currentStatus.occupancy_rate.toFixed(1)}%)
          </span>
        </div>
        <div className="metric">
          <span className="metric-label">Oxygen Level</span>
          <span className={`metric-value ${getStatusColor(2500 - currentStatus.oxygen_level, {high: 1700, medium: 1000})}`}>
            {currentStatus.oxygen_level.toFixed(0)}L / {currentStatus.max_oxygen_capacity}L
          </span>
        </div>
        <div className="metric">
          <span className="metric-label">Admissions (Current Hour)</span>
          <span className={`metric-value ${getStatusColor(currentStatus.admissions, {high: 12, medium: 8})}`}>
            {currentStatus.admissions} patients
          </span>
        </div>
        <div className="metric">
          <span className="metric-label">Discharges (Current Hour)</span>
          <span className="metric-value normal">
            {currentStatus.discharges} patients
          </span>
        </div>
      </div>

      {/* Alerts */}
      <div className="status-card alerts-section">
        <h3>System Alerts</h3>
        {alerts.map((alert, index) => (
          <div key={index} className={`alert ${alert.type}`}>
            {alert.message}
          </div>
        ))}
      </div>

      {/* Predictions */}
      {predictions && (
        <div className="status-card predictions-card">
          <h3>Resource Demand Predictions</h3>
          <div className="predictions-grid">
            {predictions.predictions.map((prediction, index) => (
              <div key={index} className="prediction-item">
                <h4>{prediction.resource.replace('_', ' ')}</h4>
                <div className="horizon-predictions">
                  <div className="horizon-item">
                    <div className="label">1 Hour</div>
                    <div className="value">{prediction.predictions['1h']?.toFixed(1) || 'N/A'}</div>
                  </div>
                  <div className="horizon-item">
                    <div className="label">6 Hours</div>
                    <div className="value">{prediction.predictions['6h']?.toFixed(1) || 'N/A'}</div>
                  </div>
                  <div className="horizon-item">
                    <div className="label">24 Hours</div>
                    <div className="value">{prediction.predictions['24h']?.toFixed(1) || 'N/A'}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Staff Optimization */}
      <div className="optimization-section">
        <div className="staff-optimization">
          <h3>Staff Allocation Optimization</h3>
          <button 
            onClick={optimizeStaff} 
            disabled={loading || !predictions}
            className="optimization-button"
          >
            {loading ? 'Optimizing...' : 'Optimize Staff Allocation'}
          </button>
          
          {optimization && (
            <div style={{marginTop: '16px'}}>
              <h4>Optimization Results</h4>
              <div className="metric">
                <span className="metric-label">Status</span>
                <span className="metric-value normal">{optimization.optimization_result.method || 'Optimal'}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Total Cost</span>
                <span className="metric-value">${optimization.optimization_result.cost_reduction || 0}/day saved</span>
              </div>
              <div className="metric">
                <span className="metric-label">Efficiency Improvement</span>
                <span className="metric-value">{optimization.optimization_result.efficiency_improvement || 0}%</span>
              </div>
              
              {optimization.optimization_result.optimized_allocation && (
                <div style={{marginTop: '12px'}}>
                  <strong>Recommended Staff Allocation:</strong>
                  {Object.entries(optimization.optimization_result.optimized_allocation).map(([staffType, shifts]) => (
                    <div key={staffType} style={{marginTop: '8px'}}>
                      <strong>{staffType.replace('_', ' ')}: </strong>
                      {Object.entries(shifts).map(([shift, count]) => 
                        `${shift}: ${count}`
                      ).join(', ')}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;