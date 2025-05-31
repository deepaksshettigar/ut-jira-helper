import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import Header from './components/Header';
import './App.css';

function App() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchJiraTasks();
  }, []);

  // Example function to fetch tasks from backend
  const fetchJiraTasks = async () => {
    try {
      setLoading(true);
      // Use relative path for API call so it works when served from backend
      const response = await axios.get('/api/tasks');
      setTasks(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching Jira tasks:', err);
      setError('Failed to fetch tasks. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <Header />
      <main>
        {error && <div className="error-message">{error}</div>}
        {loading ? (
          <div style={loadingStyle}>
            <p>Loading dashboard...</p>
          </div>
        ) : (
          <Dashboard tasks={tasks} />
        )}
      </main>
    </div>
  );
}

// Loading style
const loadingStyle = {
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  height: '50vh',
  fontSize: '1.1rem',
  color: '#666'
};

export default App;