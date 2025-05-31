import React, { useState } from 'react';
import Widget from './Widget';
import { ConversationalHelper } from '../utils/conversationalHelper';

function SearchWidget({ tasks, onSearch, onChartRecommendation }) {
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searchHistory, setSearchHistory] = useState([]);
  const [aiResponse, setAiResponse] = useState('');
  const [chartRecommendation, setChartRecommendation] = useState(null);
  const [suggestedActions, setSuggestedActions] = useState([]);

  const conversationalHelper = new ConversationalHelper(tasks);

  const handleSearch = async (searchQuery) => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      setAiResponse('');
      setChartRecommendation(null);
      setSuggestedActions([]);
      return;
    }

    try {
      // Get AI response (which may use backend or fallback to local)
      const response = await conversationalHelper.getResponse(searchQuery);
      
      // Update AI response state
      setAiResponse(response.text);
      setChartRecommendation(response.chartRecommendation);
      setSuggestedActions(response.suggestedActions || []);

      // Simple search logic for filtering tasks (local fallback)
      const results = conversationalHelper.searchTasks(searchQuery);
      setSearchResults(results);
      
      // Call chart recommendation callback if chart recommendation exists
      if (response.chartRecommendation && onChartRecommendation) {
        // Use chartData from response if available (for analytics), otherwise prepare from search results
        const chartData = response.chartData || prepareChartData(results);
        onChartRecommendation(chartData, response.chartRecommendation);
      }
      
      // Add to search history
      if (!searchHistory.includes(searchQuery)) {
        setSearchHistory(prev => [searchQuery, ...prev.slice(0, 4)]);
      }

      // Call parent callback if provided
      if (onSearch) {
        onSearch(searchQuery, results);
      }
    } catch (error) {
      console.error('Error in search:', error);
      // Fallback to basic search
      const results = conversationalHelper.searchTasks(searchQuery);
      setSearchResults(results);
      setAiResponse(`Found ${results.length} tasks matching "${searchQuery}"`);
    }
  };

  const handleInputChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    handleSearch(value);
  };

  const handleQuickSearch = (quickQuery) => {
    setQuery(quickQuery);
    handleSearch(quickQuery);
  };

  const clearSearch = () => {
    setQuery('');
    setSearchResults([]);
    setAiResponse('');
    setChartRecommendation(null);
    setSuggestedActions([]);
  };

  const prepareChartData = (results) => {
    const statusData = {};
    
    results.forEach(task => {
      const status = task.status || 'Unknown';
      statusData[status] = (statusData[status] || 0) + 1;
    });
    
    return statusData;
  };

  return (
    <Widget title="Search & Chat">
      <div style={searchContainerStyle}>
        {/* Search Input */}
        <div style={searchInputContainerStyle}>
          <input
            type="text"
            placeholder="Search tasks or ask a question..."
            value={query}
            onChange={handleInputChange}
            style={searchInputStyle}
          />
          {query && (
            <button onClick={clearSearch} style={clearButtonStyle}>
              ×
            </button>
          )}
        </div>

        {/* Quick Actions */}
        <div style={quickActionsStyle}>
          <h4 style={sectionTitleStyle}>Quick Questions:</h4>
          <div style={quickButtonsStyle}>
            <button 
              onClick={() => handleQuickSearch('help')}
              style={quickButtonStyle}
            >
              💬 What can you help me with?
            </button>
            <button 
              onClick={() => handleQuickSearch('summary')}
              style={quickButtonStyle}
            >
              📊 Give me a summary
            </button>
            <button 
              onClick={() => handleQuickSearch('in progress')}
              style={quickButtonStyle}
            >
              🔄 What's in progress?
            </button>
            <button 
              onClick={() => handleQuickSearch('workload')}
              style={quickButtonStyle}
            >
              👥 Show workload distribution
            </button>
            <button 
              onClick={() => handleQuickSearch('create task: ')}
              style={quickButtonStyle}
            >
              ➕ How to create a task?
            </button>
            <button 
              onClick={() => handleQuickSearch('average resolved per week')}
              style={quickButtonStyle}
            >
              📈 Show weekly resolved chart
            </button>
            <button 
              onClick={() => handleQuickSearch('weekly resolved for user1')}
              style={quickButtonStyle}
            >
              📊 User1 weekly resolved
            </button>
          </div>
        </div>

        {/* AI Response */}
        {aiResponse && (
          <div style={aiResponseContainerStyle}>
            <h4 style={sectionTitleStyle}>💬 AI Assistant:</h4>
            <div style={aiResponseStyle}>
              <pre style={aiResponseTextStyle}>{aiResponse}</pre>
              
              {/* Chart Recommendation */}
              {chartRecommendation && (
                <div style={chartRecommendationStyle}>
                  <span style={chartIconStyle}>📊</span>
                  <span>Recommended visualization: <strong>{chartRecommendation.charAt(0).toUpperCase() + chartRecommendation.slice(1)} Chart</strong></span>
                </div>
              )}
              
              {/* Suggested Actions */}
              {suggestedActions.length > 0 && (
                <div style={actionsContainerStyle}>
                  <h5 style={actionsHeaderStyle}>Suggested Actions:</h5>
                  <div style={actionsListStyle}>
                    {suggestedActions.slice(0, 3).map((action, index) => (
                      <button
                        key={index}
                        style={actionButtonStyle}
                        onClick={() => {
                          // Handle action click - for now just show in console
                          console.log('Action clicked:', action);
                        }}
                      >
                        {action}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Search Results */}
        {query && searchResults.length > 0 && (
          <div style={resultsContainerStyle}>
            <h4 style={sectionTitleStyle}>
              📋 Task Results ({searchResults.length} found)
            </h4>
            <ul style={resultsListStyle}>
              {searchResults.map(task => (
                <li key={task.id} style={resultItemStyle}>
                  <div style={resultHeaderStyle}>
                    <span style={resultIdStyle}>{task.id}</span>
                    <span style={getStatusBadgeStyle(task.status)}>
                      {task.status}
                    </span>
                  </div>
                  <p style={resultTitleStyle}>{task.title}</p>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Search History */}
        {!query && searchHistory.length > 0 && (
          <div style={historyContainerStyle}>
            <h4 style={sectionTitleStyle}>Recent Searches:</h4>
            <div style={historyItemsStyle}>
              {searchHistory.map((historyItem, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickSearch(historyItem)}
                  style={historyButtonStyle}
                >
                  {historyItem}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </Widget>
  );
}

// Styles
const searchContainerStyle = {
  padding: 0
};

const searchInputContainerStyle = {
  position: 'relative',
  marginBottom: '1rem'
};

const searchInputStyle = {
  width: '100%',
  padding: '0.75rem',
  border: '1px solid #ddd',
  borderRadius: '4px',
  fontSize: '0.9rem',
  boxSizing: 'border-box'
};

const clearButtonStyle = {
  position: 'absolute',
  right: '8px',
  top: '50%',
  transform: 'translateY(-50%)',
  background: 'none',
  border: 'none',
  fontSize: '1.2rem',
  cursor: 'pointer',
  color: '#666'
};

const sectionTitleStyle = {
  margin: '0 0 0.5rem 0',
  fontSize: '0.9rem',
  fontWeight: '600',
  color: '#333'
};

const quickActionsStyle = {
  marginBottom: '1rem'
};

const quickButtonsStyle = {
  display: 'flex',
  flexDirection: 'column',
  gap: '0.5rem'
};

const quickButtonStyle = {
  padding: '0.5rem 0.75rem',
  border: '1px solid #ddd',
  borderRadius: '4px',
  background: 'white',
  color: '#0052CC',
  fontSize: '0.8rem',
  cursor: 'pointer',
  textAlign: 'left',
  transition: 'background-color 0.2s ease'
};

const resultsContainerStyle = {
  marginBottom: '1rem'
};

const resultsListStyle = {
  listStyle: 'none',
  padding: 0,
  margin: 0
};

const resultItemStyle = {
  padding: '0.5rem',
  border: '1px solid #e6e6e6',
  borderRadius: '3px',
  marginBottom: '0.5rem',
  backgroundColor: '#f9f9f9'
};

const resultHeaderStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '0.25rem'
};

const resultIdStyle = {
  fontSize: '0.8rem',
  fontWeight: 'bold',
  color: '#0052CC'
};

const resultTitleStyle = {
  margin: 0,
  fontSize: '0.85rem',
  color: '#333'
};

const historyContainerStyle = {
  marginTop: '1rem'
};

const historyItemsStyle = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: '0.5rem'
};

const historyButtonStyle = {
  padding: '0.25rem 0.5rem',
  border: '1px solid #e0e0e0',
  borderRadius: '12px',
  background: '#f5f5f5',
  color: '#666',
  fontSize: '0.75rem',
  cursor: 'pointer'
};

const aiResponseContainerStyle = {
  marginBottom: '1rem'
};

const aiResponseStyle = {
  backgroundColor: '#f0f7ff',
  border: '1px solid #cce7ff',
  borderRadius: '6px',
  padding: '0.75rem',
  marginTop: '0.5rem'
};

const aiResponseTextStyle = {
  margin: 0,
  fontFamily: 'inherit',
  fontSize: '0.85rem',
  lineHeight: 1.4,
  color: '#333',
  whiteSpace: 'pre-wrap',
  wordWrap: 'break-word'
};

const chartRecommendationStyle = {
  marginTop: '0.75rem',
  padding: '0.5rem',
  backgroundColor: '#e8f4f8',
  border: '1px solid #b3d9e6',
  borderRadius: '4px',
  display: 'flex',
  alignItems: 'center',
  gap: '0.5rem',
  fontSize: '0.8rem'
};

const chartIconStyle = {
  fontSize: '1rem'
};

const actionsContainerStyle = {
  marginTop: '0.75rem'
};

const actionsHeaderStyle = {
  margin: '0 0 0.5rem 0',
  fontSize: '0.8rem',
  fontWeight: '600',
  color: '#333'
};

const actionsListStyle = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: '0.5rem'
};

const actionButtonStyle = {
  padding: '0.25rem 0.5rem',
  border: '1px solid #0052CC',
  borderRadius: '4px',
  background: 'white',
  color: '#0052CC',
  fontSize: '0.75rem',
  cursor: 'pointer',
  transition: 'all 0.2s ease'
};

const getStatusBadgeStyle = (status) => {
  let backgroundColor;
  
  switch(status.toLowerCase()) {
    case 'done':
      backgroundColor = '#36B37E';
      break;
    case 'in progress':
      backgroundColor = '#0052CC';
      break;
    case 'to do':
      backgroundColor = '#6554C0';
      break;
    default:
      backgroundColor = '#6B778C';
  }
  
  return {
    backgroundColor,
    color: 'white',
    padding: '0.15rem 0.3rem',
    borderRadius: '2px',
    fontSize: '0.7rem',
    fontWeight: 'bold'
  };
};

export default SearchWidget;