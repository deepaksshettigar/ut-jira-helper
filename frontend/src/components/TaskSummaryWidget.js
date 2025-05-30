import React from 'react';
import Widget from './Widget';

function TaskSummaryWidget({ tasks }) {
  // Calculate task counts by status
  const statusCounts = (tasks || []).reduce((counts, task) => {
    const status = task.status || 'Unknown';
    counts[status] = (counts[status] || 0) + 1;
    return counts;
  }, {});

  const totalTasks = tasks?.length || 0;

  return (
    <Widget title="Task Summary">
      <div style={summaryStyle}>
        <div style={totalCountStyle}>
          <span style={totalNumberStyle}>{totalTasks}</span>
          <span style={totalLabelStyle}>Total Tasks</span>
        </div>
        
        <div style={statusGridStyle}>
          {Object.entries(statusCounts).map(([status, count]) => (
            <div key={status} style={statusItemStyle}>
              <div style={getStatusIndicatorStyle(status)}></div>
              <div style={statusInfoStyle}>
                <span style={statusCountStyle}>{count}</span>
                <span style={statusLabelStyle}>{status}</span>
              </div>
            </div>
          ))}
        </div>
        
        {totalTasks === 0 && (
          <div style={emptyStateStyle}>
            <p>No tasks found</p>
          </div>
        )}
      </div>
    </Widget>
  );
}

// Styles
const summaryStyle = {
  padding: 0
};

const totalCountStyle = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  marginBottom: '1.5rem',
  padding: '1rem',
  backgroundColor: '#f8f9fa',
  borderRadius: '6px'
};

const totalNumberStyle = {
  fontSize: '2.5rem',
  fontWeight: 'bold',
  color: '#0052CC',
  lineHeight: 1
};

const totalLabelStyle = {
  fontSize: '0.9rem',
  color: '#666',
  marginTop: '0.25rem'
};

const statusGridStyle = {
  display: 'flex',
  flexDirection: 'column',
  gap: '0.75rem'
};

const statusItemStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '0.75rem'
};

const statusInfoStyle = {
  display: 'flex',
  flexDirection: 'column'
};

const statusCountStyle = {
  fontSize: '1.2rem',
  fontWeight: 'bold',
  color: '#333'
};

const statusLabelStyle = {
  fontSize: '0.8rem',
  color: '#666'
};

const emptyStateStyle = {
  textAlign: 'center',
  color: '#666',
  fontStyle: 'italic'
};

// Function to get status indicator color
const getStatusIndicatorStyle = (status) => {
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
    width: '12px',
    height: '12px',
    borderRadius: '50%',
    backgroundColor
  };
};

export default TaskSummaryWidget;