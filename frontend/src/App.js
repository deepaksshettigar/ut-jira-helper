import React, { useState, useEffect } from 'react';
import axios from 'axios';
import JiraTaskList from './components/JiraTaskList';
import Header from './components/Header';

function App() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // In a real app, this would fetch data from the FastAPI backend
    // Example: fetchJiraTasks();
    
    // For demonstration, we'll use some mock data
    const mockTasks = [
      { id: 'JIRA-1', title: 'Implement login page', status: 'In Progress' },
      { id: 'JIRA-2', title: 'Fix navigation bug', status: 'To Do' },
      { id: 'JIRA-3', title: 'Update documentation', status: 'Done' }
    ];
    
    // Simulate API call
    setTimeout(() => {
      setTasks(mockTasks);
      setLoading(false);
    }, 1000);
  }, []);

  // Example function to fetch tasks from backend
  const fetchJiraTasks = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/tasks');
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