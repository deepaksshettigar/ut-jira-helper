import React, { useState } from 'react';
import TaskSummaryWidget from './TaskSummaryWidget';
import TaskListWidget from './TaskListWidget';
import SearchWidget from './SearchWidget';
import ChartWidget from './ChartWidget';

function Dashboard({ tasks }) {
  const [searchResults, setSearchResults] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [chartType, setChartType] = useState(null);

  const handleSearch = (query, results) => {
    setSearchResults({ query, results });
  };

  const handleChartRecommendation = (data, type) => {
    setChartData(data);
    setChartType(type);
  };

  // Prepare chart data based on current tasks or search results
  const prepareChartData = () => {
    const currentTasks = searchResults ? searchResults.results : tasks;
    const statusData = {};
    
    currentTasks.forEach(task => {
      const status = task.status || 'Unknown';
      statusData[status] = (statusData[status] || 0) + 1;
    });
    
    return statusData;
  };

  return (
    <div style={dashboardStyle}>
      <div style={headerStyle}>
        <h1>Jira Dashboard</h1>
        <p>Your project overview and widgets with AI-powered insights</p>
      </div>
      
      <div style={widgetGridStyle}>
        {/* Task Summary Widget */}
        <TaskSummaryWidget tasks={tasks} />
        
        {/* Search Widget */}
        <SearchWidget 
          tasks={tasks} 
          onSearch={handleSearch}
          onChartRecommendation={handleChartRecommendation}
        />
        
        {/* Dynamic Chart Widget */}
        {(chartData || chartType) && (
          <ChartWidget 
            data={chartData || prepareChartData()}
            chartType={chartType || 'pie'}
            title={`${chartType ? chartType.charAt(0).toUpperCase() + chartType.slice(1) : 'Summary'} Chart`}
          />
        )}
        
        {/* Task List Widget - shows search results if available, otherwise recent tasks */}
        <div style={taskListContainerStyle}>
          <TaskListWidget 
            tasks={searchResults ? searchResults.results : tasks} 
            title={searchResults ? `Search Results for "${searchResults.query}"` : "Recent Tasks"}
            maxTasks={searchResults ? 10 : 5}
          />
        </div>
      </div>
    </div>
  );
}

// Dashboard styles
const dashboardStyle = {
  padding: '1rem',
  backgroundColor: '#f5f5f5',
  minHeight: '100vh'
};

const headerStyle = {
  marginBottom: '2rem',
  textAlign: 'center'
};

const widgetGridStyle = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
  gap: '1.5rem',
  maxWidth: '1200px',
  margin: '0 auto'
};

const taskListContainerStyle = {
  gridColumn: '1 / -1', // Make task list span full width on larger screens
  maxWidth: '100%'
};

export default Dashboard;