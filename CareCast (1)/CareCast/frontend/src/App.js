import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import Header from './components/Header';

function App() {
  const [currentStatus, setCurrentStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCurrentStatus();
    const interval = setInterval(fetchCurrentStatus, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchCurrentStatus = async () => {
    try {
      const response = await fetch('/current-status');
      if (!response.ok) throw new Error('Failed to fetch status');
      const data = await response.json();
      setCurrentStatus(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading Hospital Dashboard...</p>
      </div>
    );
  }

  return (
    <div className="App">
      <Header />
      <main className="main-content">
        {error && (
          <div className="error-banner">
            <p>Error: {error}</p>
            <button onClick={fetchCurrentStatus} className="retry-button">
              Retry
            </button>
          </div>
        )}
        <Dashboard currentStatus={currentStatus} onRefresh={fetchCurrentStatus} />
      </main>
    </div>
  );
}

export default App;