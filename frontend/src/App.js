import React, { useState, useEffect } from 'react';
import axios from 'axios';
import JiraTaskList from './components/JiraTaskList';
import Header from './components/Header';

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
        <h1>UT Jira Helper</h1>
        {error && <div className="error-message">{error}</div>}
        {loading ? (
          <p>Loading tasks...</p>
        ) : (
          <JiraTaskList tasks={tasks} />
        )}
      </main>
    </div>
  );
}

export default App;