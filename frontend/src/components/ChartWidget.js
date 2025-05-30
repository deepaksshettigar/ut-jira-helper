import React from 'react';
import Widget from './Widget';

function ChartWidget({ data, chartType, title }) {
  const renderChart = () => {
    if (!data || data.length === 0) {
      return (
        <div style={emptyStateStyle}>
          <p>No data available for chart</p>
        </div>
      );
    }

    switch (chartType) {
      case 'pie':
        return renderPieChart(data);
      case 'bar':
        return renderBarChart(data);
      case 'timeline':
        return renderTimelineChart(data);
      case 'table':
        return renderTable(data);
      default:
        return renderTable(data);
    }
  };

  const renderPieChart = (data) => {
    // Simple pie chart visualization using CSS
    const total = Object.values(data).reduce((sum, value) => sum + value, 0);
    
    return (
      <div style={chartContainerStyle}>
        <h4 style={chartTitleStyle}>Status Distribution</h4>
        <div style={pieChartStyle}>
          {Object.entries(data).map(([key, value], index) => {
            const percentage = ((value / total) * 100).toFixed(1);
            const color = getStatusColor(key);
            
            return (
              <div key={key} style={{...pieSliceStyle, backgroundColor: color}}>
                <span style={pieSliceLabelStyle}>
                  {key}: {value} ({percentage}%)
                </span>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderBarChart = (data) => {
    const maxValue = Math.max(...Object.values(data));
    
    return (
      <div style={chartContainerStyle}>
        <h4 style={chartTitleStyle}>Distribution Comparison</h4>
        <div style={barChartStyle}>
          {Object.entries(data).map(([key, value]) => {
            const height = (value / maxValue) * 100;
            const color = getStatusColor(key);
            
            return (
              <div key={key} style={barContainerStyle}>
                <div style={barLabelStyle}>{key}</div>
                <div style={barStyle}>
                  <div 
                    style={{
                      ...barFillStyle, 
                      height: `${height}%`,
                      backgroundColor: color
                    }}
                  >
                    <span style={barValueStyle}>{value}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderTimelineChart = (data) => {
    return (
      <div style={chartContainerStyle}>
        <h4 style={chartTitleStyle}>Timeline View</h4>
        <div style={timelineStyle}>
          {Object.entries(data).map(([key, value], index) => (
            <div key={key} style={timelineItemStyle}>
              <div style={timelineDotStyle}></div>
              <div style={timelineContentStyle}>
                <strong>{key}</strong>: {value} tasks
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderTable = (data) => {
    return (
      <div style={chartContainerStyle}>
        <h4 style={chartTitleStyle}>Data Table</h4>
        <div style={tableContainerStyle}>
          <table style={tableStyle}>
            <thead>
              <tr style={tableHeaderRowStyle}>
                <th style={tableHeaderStyle}>Category</th>
                <th style={tableHeaderStyle}>Count</th>
                <th style={tableHeaderStyle}>Percentage</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(data).map(([key, value]) => {
                const total = Object.values(data).reduce((sum, val) => sum + val, 0);
                const percentage = ((value / total) * 100).toFixed(1);
                
                return (
                  <tr key={key} style={tableRowStyle}>
                    <td style={tableCellStyle}>{key}</td>
                    <td style={tableCellStyle}>{value}</td>
                    <td style={tableCellStyle}>{percentage}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'done':
        return '#36B37E';
      case 'in progress':
        return '#0052CC';
      case 'to do':
        return '#6554C0';
      default:
        return '#6B778C';
    }
  };

  return (
    <Widget title={title || 'Chart Visualization'}>
      {renderChart()}
    </Widget>
  );
}

// Styles
const emptyStateStyle = {
  textAlign: 'center',
  padding: '2rem',
  color: '#666'
};

const chartContainerStyle = {
  padding: '1rem'
};

const chartTitleStyle = {
  margin: '0 0 1rem 0',
  fontSize: '1rem',
  fontWeight: '600',
  color: '#333'
};

const pieChartStyle = {
  display: 'flex',
  flexDirection: 'column',
  gap: '0.5rem'
};

const pieSliceStyle = {
  padding: '0.5rem',
  borderRadius: '4px',
  color: 'white',
  fontWeight: 'bold',
  fontSize: '0.8rem'
};

const pieSliceLabelStyle = {
  display: 'block'
};

const barChartStyle = {
  display: 'flex',
  gap: '1rem',
  alignItems: 'end',
  height: '150px'
};

const barContainerStyle = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  flex: 1
};

const barLabelStyle = {
  fontSize: '0.8rem',
  marginBottom: '0.5rem',
  textAlign: 'center',
  fontWeight: '500'
};

const barStyle = {
  width: '100%',
  height: '120px',
  backgroundColor: '#f0f0f0',
  borderRadius: '4px',
  position: 'relative',
  display: 'flex',
  alignItems: 'end'
};

const barFillStyle = {
  width: '100%',
  borderRadius: '4px',
  position: 'relative',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: 'white',
  fontWeight: 'bold',
  fontSize: '0.8rem'
};

const barValueStyle = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)'
};

const timelineStyle = {
  display: 'flex',
  flexDirection: 'column',
  gap: '1rem'
};

const timelineItemStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '0.75rem'
};

const timelineDotStyle = {
  width: '12px',
  height: '12px',
  borderRadius: '50%',
  backgroundColor: '#0052CC',
  flexShrink: 0
};

const timelineContentStyle = {
  fontSize: '0.9rem'
};

const tableContainerStyle = {
  overflowX: 'auto'
};

const tableStyle = {
  width: '100%',
  borderCollapse: 'collapse',
  fontSize: '0.9rem'
};

const tableHeaderRowStyle = {
  backgroundColor: '#f5f5f5'
};

const tableHeaderStyle = {
  padding: '0.5rem',
  textAlign: 'left',
  fontWeight: '600',
  border: '1px solid #ddd'
};

const tableRowStyle = {
  borderBottom: '1px solid #eee'
};

const tableCellStyle = {
  padding: '0.5rem',
  border: '1px solid #ddd'
};

export default ChartWidget;