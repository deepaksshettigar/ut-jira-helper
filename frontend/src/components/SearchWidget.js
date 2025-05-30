import React, { useState } from 'react';
import Widget from './Widget';

function SearchWidget({ tasks, onSearch }) {
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searchHistory, setSearchHistory] = useState([]);

  const handleSearch = (searchQuery) => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    // Simple search logic - can be enhanced with LLM later
    const results = (tasks || []).filter(task => 
      task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.status.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.assignee?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    setSearchResults(results);
    
    // Add to search history
    if (!searchHistory.includes(searchQuery)) {
      setSearchHistory(prev => [searchQuery, ...prev.slice(0, 4)]);
    }

    // Call parent callback if provided
    if (onSearch) {
      onSearch(searchQuery, results);
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
              onClick={() => handleQuickSearch('in progress')}
              style={quickButtonStyle}
            >
              What's in progress?
            </button>
            <button 
              onClick={() => handleQuickSearch('to do')}
              style={quickButtonStyle}
            >
              What needs to be done?
            </button>
            <button 
              onClick={() => handleQuickSearch('done')}
              style={quickButtonStyle}
            >
              What's completed?
            </button>
          </div>
        </div>

        {/* Search Results */}
        {query && (
          <div style={resultsContainerStyle}>
            <h4 style={sectionTitleStyle}>
              Results for "{query}" ({searchResults.length} found)
            </h4>
            {searchResults.length > 0 ? (
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
            ) : (
              <p style={noResultsStyle}>
                No tasks found matching "{query}". Try a different search term.
              </p>
            )}
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

const noResultsStyle = {
  margin: 0,
  fontSize: '0.85rem',
  color: '#666',
  fontStyle: 'italic'
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