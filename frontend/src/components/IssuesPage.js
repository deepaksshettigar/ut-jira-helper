import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const IssuesPage = () => {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [currentJQL, setCurrentJQL] = useState('');
  const [explanation, setExplanation] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showJQLEditor, setShowJQLEditor] = useState(false);
  const [totalCount, setTotalCount] = useState(0);
  const [startAt, setStartAt] = useState(0);
  const [maxResults] = useState(50);
  
  const chatEndRef = useRef(null);
  const apiBaseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  // Load initial data
  useEffect(() => {
    handleNaturalLanguageQuery('Show me all issues');
  }, []);

  const handleNaturalLanguageQuery = async (query) => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    
    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: query,
      timestamp: new Date()
    };
    setChatHistory(prev => [...prev, userMessage]);

    try {
      const response = await axios.post(`${apiBaseUrl}/api/jql/convert`, {
        natural_language: query,
        context: 'Jira Issues List',
        max_results: maxResults,
        start_at: startAt
      });

      const data = response.data;
      
      // Update state with results
      setIssues(data.issues);
      setCurrentJQL(data.jql_query);
      setExplanation(data.explanation);
      setSuggestions(data.suggestions || []);
      setTotalCount(data.total_count);
      
      // Add assistant response to chat
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: `Found ${data.total_count} issues. ${data.explanation}`,
        jql: data.jql_query,
        timestamp: new Date()
      };
      setChatHistory(prev => [...prev, assistantMessage]);

    } catch (err) {
      console.error('Error processing natural language query:', err);
      setError('Failed to process your query. Please try again.');
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'Sorry, I couldn\'t process that query. Please try rephrasing it.',
        timestamp: new Date()
      };
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleDirectJQL = async (jqlQuery) => {
    if (!jqlQuery.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${apiBaseUrl}/api/jql/execute`, {
        jql: jqlQuery,
        max_results: maxResults,
        start_at: startAt
      });

      const data = response.data;
      
      setIssues(data.issues);
      setCurrentJQL(data.jql_query);
      setExplanation(data.explanation);
      setTotalCount(data.total_count);

    } catch (err) {
      console.error('Error executing JQL:', err);
      setError('Failed to execute JQL query. Please check your syntax.');
    } finally {
      setLoading(false);
    }
  };

  const handleChatSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      handleNaturalLanguageQuery(inputValue);
      setInputValue('');
    }
  };

  const handleSuggestionClick = (suggestion) => {
    handleNaturalLanguageQuery(suggestion);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusColor = (status) => {
    const statusColors = {
      'To Do': '#42526E',
      'In Progress': '#0052CC',
      'Done': '#00875A',
      'Closed': '#5E6C84',
      'Resolved': '#00875A'
    };
    return statusColors[status] || '#42526E';
  };

  const getPriorityIcon = (priority) => {
    const priorityIcons = {
      'Highest': '🔴',
      'High': '🟠', 
      'Medium': '🟡',
      'Low': '🔵',
      'Lowest': '⚪'
    };
    return priorityIcons[priority] || '⚪';
  };

  const getJiraUrl = (issueKey) => {
    // Extract base URL from issue key or use a default
    // In a real implementation, this would come from configuration
    const baseUrl = process.env.REACT_APP_JIRA_URL || 'https://your-domain.atlassian.net';
    return `${baseUrl}/browse/${issueKey}`;
  };

  return (
    <div style={pageStyle}>
      {/* Header */}
      <div style={headerStyle}>
        <h1>Jira Issues</h1>
        <p>Use natural language to search and filter your Jira issues</p>
      </div>

      {/* Main Content */}
      <div style={mainContentStyle}>
        {/* Chat Interface */}
        <div style={chatPanelStyle}>
          <div style={chatHeaderStyle}>
            <h3>Natural Language Query</h3>
            <button 
              onClick={() => setShowJQLEditor(!showJQLEditor)}
              style={toggleButtonStyle}
            >
              {showJQLEditor ? 'Hide JQL' : 'Show JQL'}
            </button>
          </div>

          {/* JQL Editor (conditional) */}
          {showJQLEditor && (
            <div style={jqlEditorStyle}>
              <textarea
                value={currentJQL}
                onChange={(e) => setCurrentJQL(e.target.value)}
                placeholder="Enter JQL query directly..."
                style={jqlTextareaStyle}
              />
              <button 
                onClick={() => handleDirectJQL(currentJQL)}
                style={executeButtonStyle}
                disabled={loading}
              >
                Execute JQL
              </button>
              {explanation && (
                <div style={explanationStyle}>
                  <strong>Explanation:</strong> {explanation}
                </div>
              )}
            </div>
          )}

          {/* Chat History */}
          <div style={chatHistoryStyle}>
            {chatHistory.map((message) => (
              <div 
                key={message.id} 
                style={{
                  ...messageStyle,
                  ...(message.type === 'user' ? userMessageStyle : 
                      message.type === 'error' ? errorMessageStyle : assistantMessageStyle)
                }}
              >
                <div style={messageContentStyle}>
                  <strong>{message.type === 'user' ? 'You' : message.type === 'error' ? 'Error' : 'Assistant'}:</strong>
                  <p>{message.content}</p>
                  {message.jql && (
                    <div style={jqlDisplayStyle}>
                      <code>{message.jql}</code>
                    </div>
                  )}
                  <small style={timestampStyle}>
                    {message.timestamp.toLocaleTimeString()}
                  </small>
                </div>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          {/* Input Form */}
          <form onSubmit={handleChatSubmit} style={inputFormStyle}>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask me about your issues... (e.g., 'Show me high priority bugs assigned to John')"
              style={chatInputStyle}
              disabled={loading}
            />
            <button 
              type="submit" 
              style={sendButtonStyle}
              disabled={loading || !inputValue.trim()}
            >
              {loading ? '...' : 'Send'}
            </button>
          </form>

          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div style={suggestionsStyle}>
              <strong>Suggestions:</strong>
              <div style={suggestionButtonsStyle}>
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(suggestion)}
                    style={suggestionButtonStyle}
                    disabled={loading}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Issues List */}
        <div style={issuesListStyle}>
          <div style={listHeaderStyle}>
            <h3>Issues ({totalCount} total)</h3>
            {loading && <div style={loadingIndicatorStyle}>Loading...</div>}
          </div>

          {error && (
            <div style={errorStyle}>
              {error}
            </div>
          )}

          <div style={issuesContainerStyle}>
            {issues.length > 0 ? (
              <table style={tableStyle}>
                <thead>
                  <tr style={tableHeaderRowStyle}>
                    <th style={tableHeaderStyle}>Issue</th>
                    <th style={tableHeaderStyle}>Title</th>
                    <th style={tableHeaderStyle}>Status</th>
                    <th style={tableHeaderStyle}>Assignee</th>
                    <th style={tableHeaderStyle}>Priority</th>
                    <th style={tableHeaderStyle}>Created</th>
                    <th style={tableHeaderStyle}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {issues.map((issue) => (
                    <tr 
                      key={issue.id} 
                      style={tableRowStyle}
                      onMouseEnter={(e) => e.target.parentElement.style.backgroundColor = '#f8f9fa'}
                      onMouseLeave={(e) => e.target.parentElement.style.backgroundColor = 'transparent'}
                    >
                      <td style={tableCellStyle}>
                        <span style={issueKeyStyle}>{issue.id}</span>
                      </td>
                      <td style={tableCellStyle}>
                        <div style={issueTitleCellStyle}>
                          <strong>{issue.title}</strong>
                          {issue.description && (
                            <div style={issueDescriptionCellStyle}>
                              {issue.description.length > 100 ? 
                                issue.description.substring(0, 100) + '...' : 
                                issue.description
                              }
                            </div>
                          )}
                        </div>
                      </td>
                      <td style={tableCellStyle}>
                        <span 
                          style={{
                            ...statusBadgeStyle,
                            backgroundColor: getStatusColor(issue.status)
                          }}
                        >
                          {issue.status}
                        </span>
                      </td>
                      <td style={tableCellStyle}>
                        <span style={assigneeStyle}>
                          👤 {issue.assignee || 'Unassigned'}
                        </span>
                      </td>
                      <td style={tableCellStyle}>
                        {issue.priority && (
                          <span style={priorityStyle}>
                            {getPriorityIcon(issue.priority)} {issue.priority}
                          </span>
                        )}
                      </td>
                      <td style={tableCellStyle}>
                        <span style={dateStyle}>
                          {formatDate(issue.created_date)}
                        </span>
                      </td>
                      <td style={tableCellStyle}>
                        <a
                          href={getJiraUrl(issue.id)}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={jiraLinkStyle}
                          onMouseEnter={(e) => {
                            e.target.style.backgroundColor = '#0052CC';
                            e.target.style.color = 'white';
                          }}
                          onMouseLeave={(e) => {
                            e.target.style.backgroundColor = '#f8f9fa';
                            e.target.style.color = '#0052CC';
                          }}
                        >
                          Open in Jira ↗
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div style={noIssuesStyle}>
                {loading ? 'Loading issues...' : 'No issues found. Try a different search query.'}
              </div>
            )}
          </div>

          {/* Pagination */}
          {totalCount > maxResults && (
            <div style={paginationStyle}>
              <button
                onClick={() => {
                  const newStartAt = Math.max(0, startAt - maxResults);
                  setStartAt(newStartAt);
                  if (currentJQL) {
                    handleDirectJQL(currentJQL);
                  }
                }}
                disabled={startAt === 0 || loading}
                style={pageButtonStyle}
              >
                Previous
              </button>
              
              <span style={pageInfoStyle}>
                {startAt + 1} - {Math.min(startAt + maxResults, totalCount)} of {totalCount}
              </span>
              
              <button
                onClick={() => {
                  const newStartAt = startAt + maxResults;
                  if (newStartAt < totalCount) {
                    setStartAt(newStartAt);
                    if (currentJQL) {
                      handleDirectJQL(currentJQL);
                    }
                  }
                }}
                disabled={startAt + maxResults >= totalCount || loading}
                style={pageButtonStyle}
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Styles
const pageStyle = {
  padding: '1rem',
  backgroundColor: '#f5f5f5',
  minHeight: '100vh'
};

const headerStyle = {
  textAlign: 'center',
  marginBottom: '2rem',
  backgroundColor: 'white',
  padding: '2rem',
  borderRadius: '8px',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
};

const mainContentStyle = {
  display: 'grid',
  gridTemplateColumns: '400px 1fr',
  gap: '2rem',
  maxWidth: '1600px',
  margin: '0 auto'
};

const chatPanelStyle = {
  backgroundColor: 'white',
  borderRadius: '8px',
  padding: '1rem',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  height: 'fit-content',
  maxHeight: '80vh',
  display: 'flex',
  flexDirection: 'column'
};

const chatHeaderStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '1rem',
  paddingBottom: '1rem',
  borderBottom: '1px solid #eee'
};

const toggleButtonStyle = {
  padding: '0.5rem 1rem',
  backgroundColor: '#0052CC',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
  fontSize: '0.9rem'
};

const jqlEditorStyle = {
  marginBottom: '1rem',
  padding: '1rem',
  backgroundColor: '#f8f9fa',
  borderRadius: '4px'
};

const jqlTextareaStyle = {
  width: '100%',
  height: '100px',
  padding: '0.5rem',
  border: '1px solid #ddd',
  borderRadius: '4px',
  fontFamily: 'monospace',
  fontSize: '0.9rem',
  resize: 'vertical'
};

const executeButtonStyle = {
  marginTop: '0.5rem',
  padding: '0.5rem 1rem',
  backgroundColor: '#00875A',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer'
};

const explanationStyle = {
  marginTop: '0.5rem',
  padding: '0.5rem',
  backgroundColor: '#e3fcef',
  borderRadius: '4px',
  fontSize: '0.9rem'
};

const chatHistoryStyle = {
  flex: 1,
  maxHeight: '400px',
  overflowY: 'auto',
  marginBottom: '1rem',
  border: '1px solid #eee',
  borderRadius: '4px',
  padding: '1rem'
};

const messageStyle = {
  marginBottom: '1rem',
  padding: '0.75rem',
  borderRadius: '8px'
};

const userMessageStyle = {
  backgroundColor: '#e3f2fd',
  marginLeft: '20%'
};

const assistantMessageStyle = {
  backgroundColor: '#f1f8e9',
  marginRight: '20%'
};

const errorMessageStyle = {
  backgroundColor: '#ffebee',
  marginRight: '20%'
};

const messageContentStyle = {
  margin: 0
};

const jqlDisplayStyle = {
  marginTop: '0.5rem',
  padding: '0.5rem',
  backgroundColor: '#f5f5f5',
  borderRadius: '4px',
  fontFamily: 'monospace',
  fontSize: '0.8rem'
};

const timestampStyle = {
  color: '#666',
  fontSize: '0.8rem'
};

const inputFormStyle = {
  display: 'flex',
  gap: '0.5rem'
};

const chatInputStyle = {
  flex: 1,
  padding: '0.75rem',
  border: '1px solid #ddd',
  borderRadius: '4px',
  fontSize: '1rem'
};

const sendButtonStyle = {
  padding: '0.75rem 1.5rem',
  backgroundColor: '#0052CC',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
  fontSize: '1rem'
};

const suggestionsStyle = {
  marginTop: '1rem',
  padding: '1rem',
  backgroundColor: '#f8f9fa',
  borderRadius: '4px'
};

const suggestionButtonsStyle = {
  display: 'flex',
  flexDirection: 'column',
  gap: '0.5rem',
  marginTop: '0.5rem'
};

const suggestionButtonStyle = {
  padding: '0.5rem',
  backgroundColor: 'white',
  border: '1px solid #ddd',
  borderRadius: '4px',
  cursor: 'pointer',
  textAlign: 'left',
  fontSize: '0.9rem'
};

const issuesListStyle = {
  backgroundColor: 'white',
  borderRadius: '8px',
  padding: '1.5rem',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
};

const listHeaderStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '1.5rem',
  paddingBottom: '1rem',
  borderBottom: '1px solid #eee'
};

const loadingIndicatorStyle = {
  color: '#666',
  fontStyle: 'italic'
};

const errorStyle = {
  backgroundColor: '#ffebee',
  color: '#c62828',
  padding: '1rem',
  borderRadius: '4px',
  marginBottom: '1rem'
};

const issuesContainerStyle = {
  overflowX: 'auto'
};

// Table styles
const tableStyle = {
  width: '100%',
  borderCollapse: 'collapse',
  backgroundColor: 'white',
  borderRadius: '8px',
  overflow: 'hidden',
  boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
};

const tableHeaderRowStyle = {
  backgroundColor: '#f8f9fa',
  borderBottom: '2px solid #dee2e6'
};

const tableHeaderStyle = {
  padding: '1rem',
  textAlign: 'left',
  fontWeight: '600',
  color: '#495057',
  fontSize: '0.9rem',
  borderBottom: '1px solid #dee2e6'
};

const tableRowStyle = {
  borderBottom: '1px solid #e9ecef',
  transition: 'background-color 0.2s'
};

const tableCellStyle = {
  padding: '1rem',
  verticalAlign: 'top',
  borderBottom: '1px solid #e9ecef'
};

const issueKeyStyle = {
  fontWeight: 'bold',
  color: '#0052CC',
  fontSize: '0.95rem'
};

const issueTitleCellStyle = {
  maxWidth: '300px'
};

const issueDescriptionCellStyle = {
  color: '#666',
  fontSize: '0.85rem',
  marginTop: '0.25rem',
  lineHeight: '1.4'
};

const assigneeStyle = {
  color: '#666',
  fontSize: '0.9rem'
};

const priorityStyle = {
  fontSize: '0.9rem'
};

const dateStyle = {
  color: '#666',
  fontSize: '0.85rem'
};

const jiraLinkStyle = {
  color: '#0052CC',
  textDecoration: 'none',
  fontWeight: '500',
  fontSize: '0.9rem',
  padding: '0.5rem 1rem',
  backgroundColor: '#f8f9fa',
  borderRadius: '4px',
  border: '1px solid #dee2e6',
  display: 'inline-block',
  transition: 'all 0.2s'
};

const statusBadgeStyle = {
  color: 'white',
  padding: '0.25rem 0.75rem',
  borderRadius: '12px',
  fontSize: '0.8rem',
  fontWeight: 'bold'
};

const noIssuesStyle = {
  textAlign: 'center',
  padding: '3rem',
  color: '#666',
  fontSize: '1.1rem',
  backgroundColor: '#f8f9fa',
  borderRadius: '8px'
};

const paginationStyle = {
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  gap: '1rem',
  marginTop: '2rem',
  padding: '1rem'
};

const pageButtonStyle = {
  padding: '0.5rem 1rem',
  backgroundColor: '#0052CC',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer'
};

const pageInfoStyle = {
  color: '#666',
  fontSize: '0.9rem'
};

export default IssuesPage;
