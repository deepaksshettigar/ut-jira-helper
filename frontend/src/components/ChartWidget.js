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
      case 'weekly_resolved':
        return renderWeeklyResolvedChart(data);
      case 'weekly_trend':
        return renderWeeklyTrendChart(data);
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

  const renderWeeklyTrendChart = (data) => {
    // Handle weekly resolved data structure for trend chart
    const weeklyData = data.weekly_breakdown || data;
    const assigneeInfo = data.assignee ? ` for ${data.assignee}` : '';
    const averageInfo = data.average_per_week ? ` (Avg: ${data.average_per_week}/week)` : '';
    const averageValue = data.average_per_week || 0;
    
    const maxValue = Math.max(...Object.values(weeklyData), averageValue);
    const weekEntries = Object.entries(weeklyData);
    
    return (
      <div style={chartContainerStyle}>
        <h4 style={chartTitleStyle}>
          Weekly Resolved Tasks Trend{assigneeInfo}{averageInfo}
        </h4>
        <div style={trendChartStyle}>
          <svg width="100%" height="200" style={svgStyle}>
            {/* Background grid lines */}
            {[0, 25, 50, 75, 100].map(percent => (
              <line
                key={percent}
                x1="40"
                y1={30 + (percent / 100) * 140}
                x2="95%"
                y2={30 + (percent / 100) * 140}
                stroke="#f0f0f0"
                strokeWidth="1"
              />
            ))}
            
            {/* Y-axis labels */}
            {[0, 1, 2, 3, Math.ceil(maxValue)].map((value, index) => (
              <text
                key={value}
                x="30"
                y={175 - (value / maxValue) * 140}
                fontSize="10"
                fill="#666"
                textAnchor="end"
              >
                {value}
              </text>
            ))}
            
            {/* Average line */}
            {averageValue > 0 && (
              <>
                <line
                  x1="40"
                  y1={175 - (averageValue / maxValue) * 140}
                  x2="95%"
                  y2={175 - (averageValue / maxValue) * 140}
                  stroke="#ff6b35"
                  strokeWidth="2"
                  strokeDasharray="5,5"
                />
                <text
                  x="50"
                  y={170 - (averageValue / maxValue) * 140}
                  fontSize="10"
                  fill="#ff6b35"
                  fontWeight="bold"
                >
                  Avg: {averageValue}
                </text>
              </>
            )}
            
            {/* Data line and points */}
            {weekEntries.length > 1 && (
              <polyline
                points={weekEntries.map((week, index) => {
                  const x = 40 + (index / (weekEntries.length - 1)) * (300 - 80);
                  const y = 175 - (week[1] / maxValue) * 140;
                  return `${x},${y}`;
                }).join(' ')}
                fill="none"
                stroke="#0052CC"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            )}
            
            {/* Data points */}
            {weekEntries.map((week, index) => {
              const x = 40 + (index / Math.max(weekEntries.length - 1, 1)) * (300 - 80);
              const y = 175 - (week[1] / maxValue) * 140;
              
              return (
                <g key={week[0]}>
                  <circle
                    cx={x}
                    cy={y}
                    r="4"
                    fill="#0052CC"
                    stroke="white"
                    strokeWidth="2"
                  />
                  <text
                    x={x}
                    y={y - 10}
                    fontSize="10"
                    fill="#333"
                    textAnchor="middle"
                    fontWeight="bold"
                  >
                    {week[1]}
                  </text>
                </g>
              );
            })}
            
            {/* X-axis labels */}
            {weekEntries.map((week, index) => {
              const x = 40 + (index / Math.max(weekEntries.length - 1, 1)) * (300 - 80);
              const label = week[0].replace('Week ', 'W').replace(' ago', '');
              
              return (
                <text
                  key={week[0]}
                  x={x}
                  y={195}
                  fontSize="9"
                  fill="#666"
                  textAnchor="middle"
                >
                  {label}
                </text>
              );
            })}
            
            {/* Axis lines */}
            <line x1="40" y1="30" x2="40" y2="175" stroke="#ccc" strokeWidth="1" />
            <line x1="40" y1="175" x2="95%" y2="175" stroke="#ccc" strokeWidth="1" />
          </svg>
        </div>
        {data.total_resolved !== undefined && (
          <div style={weeklyStatsStyle}>
            <p><strong>Total Resolved:</strong> {data.total_resolved} tasks</p>
            <p><strong>Period:</strong> {data.weeks_analyzed} weeks</p>
            <p><strong>Trend:</strong> {averageValue > 0 ? 'Consistent progress' : 'No completions yet'}</p>
          </div>
        )}
      </div>
    );
  };

  const renderWeeklyResolvedChart = (data) => {
    // Handle weekly resolved data structure
    const weeklyData = data.weekly_breakdown || data;
    const assigneeInfo = data.assignee ? ` for ${data.assignee}` : '';
    const averageInfo = data.average_per_week ? ` (Avg: ${data.average_per_week}/week)` : '';
    
    const maxValue = Math.max(...Object.values(weeklyData));
    
    return (
      <div style={chartContainerStyle}>
        <h4 style={chartTitleStyle}>
          Weekly Resolved Tasks{assigneeInfo}{averageInfo}
        </h4>
        <div style={weeklyResolvedChartStyle}>
          {Object.entries(weeklyData).map(([week, count]) => {
            const height = maxValue > 0 ? (count / maxValue) * 100 : 0;
            
            return (
              <div key={week} style={weeklyBarContainerStyle}>
                <div style={weeklyBarLabelStyle}>{week}</div>
                <div style={weeklyBarStyle}>
                  <div 
                    style={{
                      ...weeklyBarFillStyle, 
                      height: `${height}%`,
                      backgroundColor: '#36B37E'
                    }}
                  >
                    <span style={weeklyBarValueStyle}>{count}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        {data.total_resolved !== undefined && (
          <div style={weeklyStatsStyle}>
            <p><strong>Total Resolved:</strong> {data.total_resolved} tasks</p>
            <p><strong>Period:</strong> {data.weeks_analyzed} weeks</p>
          </div>
        )}
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

// Weekly resolved chart styles
const weeklyResolvedChartStyle = {
  display: 'flex',
  gap: '1rem',
  alignItems: 'end',
  height: '150px',
  marginBottom: '1rem'
};

const weeklyBarContainerStyle = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  flex: 1,
  minWidth: '60px'
};

const weeklyBarLabelStyle = {
  fontSize: '0.7rem',
  marginBottom: '0.5rem',
  textAlign: 'center',
  fontWeight: '500',
  lineHeight: '1.2'
};

const weeklyBarStyle = {
  width: '100%',
  height: '120px',
  backgroundColor: '#f0f0f0',
  borderRadius: '4px',
  position: 'relative',
  display: 'flex',
  alignItems: 'end'
};

const weeklyBarFillStyle = {
  width: '100%',
  borderRadius: '4px',
  position: 'relative',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: 'white',
  fontWeight: 'bold',
  fontSize: '0.8rem',
  minHeight: '20px'
};

const weeklyBarValueStyle = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)'
};

const weeklyStatsStyle = {
  fontSize: '0.85rem',
  color: '#666',
  borderTop: '1px solid #eee',
  paddingTop: '0.75rem',
  marginTop: '0.75rem'
};

// Trend chart styles
const trendChartStyle = {
  marginBottom: '1rem',
  backgroundColor: '#fff',
  borderRadius: '4px',
  border: '1px solid #e0e0e0'
};

const svgStyle = {
  display: 'block',
  margin: '0 auto'
};

export default ChartWidget;