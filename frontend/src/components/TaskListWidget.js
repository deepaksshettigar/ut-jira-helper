import React from 'react';
import Widget from './Widget';

function TaskListWidget({ tasks, title = "Recent Tasks", maxTasks = 5 }) {
  const displayTasks = (tasks || []).slice(0, maxTasks);

  // Helper function to format dates
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  if (!tasks || tasks.length === 0) {
    return (
      <Widget title={title}>
        <p style={emptyStateStyle}>No tasks found.</p>
      </Widget>
    );
  }

  return (
    <Widget title={title}>
      <ul style={listStyle}>
        {displayTasks.map(task => (
          <li key={task.id} style={taskItemStyle}>
            <div style={taskHeaderStyle}>
              <span style={taskIdStyle}>{task.id}</span>
              <span style={getStatusStyle(task.status)}>{task.status}</span>
            </div>
            <h4 style={taskTitleStyle}>{task.title}</h4>
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
            </div>
          </li>
        ))}
      </ul>
      
      {tasks.length > maxTasks && (
        <div style={showMoreStyle}>
          <span>Showing {maxTasks} of {tasks.length} tasks</span>
        </div>
      )}
    </Widget>
  );
}

// Styles
const listStyle = {
  listStyle: 'none',
  padding: 0,
  margin: 0
};

const taskItemStyle = {
  border: '1px solid #e6e6e6',
  borderRadius: '4px',
  padding: '0.75rem',
  marginBottom: '0.75rem',
  backgroundColor: '#fafafa',
  transition: 'background-color 0.2s ease'
};

const taskHeaderStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '0.5rem'
};

const taskIdStyle = {
  color: '#0052CC',
  fontWeight: 'bold',
  fontSize: '0.9rem'
};

const taskTitleStyle = {
  margin: '0 0 0.5rem 0',
  fontSize: '1rem',
  color: '#333',
  lineHeight: 1.3
};

const assigneeStyle = {
  margin: 0,
  fontSize: '0.8rem',
  color: '#666'
};

const emptyStateStyle = {
  textAlign: 'center',
  color: '#666',
  fontStyle: 'italic',
  margin: 0
};

const showMoreStyle = {
  textAlign: 'center',
  marginTop: '0.75rem',
  paddingTop: '0.75rem',
  borderTop: '1px solid #e6e6e6',
  fontSize: '0.8rem',
  color: '#666'
};

const taskDatesStyle = {
  display: 'flex',
  flexDirection: 'column',
  gap: '0.25rem',
  marginTop: '0.5rem'
};

const dateItemStyle = {
  fontSize: '0.7rem',
  color: '#666',
  display: 'flex',
  alignItems: 'center',
  gap: '0.25rem'
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
    padding: '0.2rem 0.4rem',
    borderRadius: '3px',
    fontSize: '0.7rem',
    fontWeight: 'bold'
  };
};

export default TaskListWidget;