import React from 'react';

function JiraTaskList({ tasks }) {
  // Helper function to format dates
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  if (!tasks || tasks.length === 0) {
    return <p>No tasks found.</p>;
  }

  return (
    <div style={containerStyle}>
      <h2>Your Jira Tasks</h2>
      <ul style={listStyle}>
        {tasks.map(task => (
          <li key={task.id} style={taskItemStyle}>
            <div style={taskHeaderStyle}>
              <span style={taskIdStyle}>{task.id}</span>
              <span style={getStatusStyle(task.status)}>{task.status}</span>
            </div>
            <h3 style={taskTitleStyle}>{task.title}</h3>
            {task.description && (
              <p style={taskDescriptionStyle}>{task.description}</p>
            )}
            {task.assignee && (
              <p style={assigneeStyle}>Assigned to: {task.assignee}</p>
            )}
            <div style={taskDatesStyle}>
              {task.created_date && (
                <span style={dateItemStyle}>
                  📅 Created: {formatDate(task.created_date)}
                </span>
              )}
              {task.updated_date && (
                <span style={dateItemStyle}>
                  🔄 Updated: {formatDate(task.updated_date)}
                </span>
              )}
              {task.start_date && (
                <span style={dateItemStyle}>
                  🟢 Start: {formatDate(task.start_date)}
                </span>
              )}
              {task.due_date && (
                <span style={dateItemStyle}>
                  🔴 Due: {formatDate(task.due_date)}
                </span>
              )}
              {task.resolved_date && (
                <span style={dateItemStyle}>
                  ✅ Resolved: {formatDate(task.resolved_date)}
                </span>
              )}
              {task.priority && (
                <span style={priorityStyle}>
                  ⭐ Priority: {task.priority}
                </span>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

// Basic inline styles for demonstration
const containerStyle = {
  padding: '1rem'
};

const listStyle = {
  listStyle: 'none',
  padding: 0,
  margin: 0
};

const taskItemStyle = {
  border: '1px solid #ddd',
  borderRadius: '4px',
  padding: '1rem',
  marginBottom: '1rem',
  backgroundColor: '#fff',
  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
};

const taskHeaderStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  marginBottom: '0.5rem'
};

const taskIdStyle = {
  color: '#0052CC',
  fontWeight: 'bold'
};

const taskTitleStyle = {
  margin: '0.5rem 0',
  fontSize: '1.1rem'
};

const taskDescriptionStyle = {
  margin: '0.5rem 0',
  fontSize: '0.9rem',
  color: '#666',
  lineHeight: 1.4
};

const assigneeStyle = {
  margin: '0.5rem 0',
  fontSize: '0.9rem',
  color: '#333',
  fontWeight: '500'
};

const taskDatesStyle = {
  display: 'flex',
  flexDirection: 'column',
  gap: '0.25rem',
  marginTop: '0.75rem'
};

const dateItemStyle = {
  fontSize: '0.8rem',
  color: '#666',
  display: 'flex',
  alignItems: 'center',
  gap: '0.25rem'
};

const priorityStyle = {
  fontSize: '0.8rem',
  color: '#666',
  display: 'flex',
  alignItems: 'center',
  gap: '0.25rem',
  fontWeight: '500'
};

// Function to determine status badge style based on status
const getStatusStyle = (status) => {
  let backgroundColor;
  
  switch(status.toLowerCase()) {
    case 'done':
      backgroundColor = '#36B37E'; // Green
      break;
    case 'in progress':
      backgroundColor = '#0052CC'; // Blue
      break;
    case 'to do':
      backgroundColor = '#6554C0'; // Purple
      break;
    default:
      backgroundColor = '#6B778C'; // Grey
  }
  
  return {
    backgroundColor,
    color: 'white',
    padding: '0.25rem 0.5rem',
    borderRadius: '3px',
    fontSize: '0.8rem',
    fontWeight: 'bold'
  };
};

export default JiraTaskList;