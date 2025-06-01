import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  LineController,
  BarController,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  LineController,
  BarController,
  Title,
  Tooltip,
  Legend,
  Filler
);

const IssuesPage = () => {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [chatQuery, setChatQuery] = useState('');
  const [jqlQuery, setJqlQuery] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('table'); // Add tab state
  const [chartGroupBy, setChartGroupBy] = useState('duedate'); // Chart grouping selection
  const [totalCount, setTotalCount] = useState(0); // Store total count from backend

  const chatEndRef = useRef(null);
  const apiBaseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  // Load initial data
  useEffect(() => {
    const loadInitialData = () => {
      handleNaturalLanguageQuery('Show me all issues');
    };
    loadInitialData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
        max_results: 50,
        start_at: 0
      });

      const data = response.data;
      
      // Update state with results
      setIssues(data.issues);
      setJqlQuery(data.jql_query);
      setTotalCount(data.total_count);
      setError('');
      
      // Add assistant response to chat
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: data.total_count > data.issues.length 
          ? `Found ${data.total_count} issues (showing first ${data.issues.length}).`
          : `Found ${data.issues.length} issues.`,
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
        max_results: 50,
        start_at: 0
      });

      const data = response.data;
      
      setIssues(data.issues);
      setJqlQuery(data.jql_query);
      setTotalCount(data.total_count);
      setError('');

    } catch (err) {
      console.error('Error executing JQL:', err);
      setError('Failed to execute JQL query. Please check your syntax.');
    } finally {
      setLoading(false);
    }
  };

  const handleChatSubmit = (e) => {
    e.preventDefault();
    if (chatQuery.trim()) {
      handleNaturalLanguageQuery(chatQuery);
      setChatQuery('');
    }
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

  // Add function to prepare chart data based on grouping selection
  const prepareChartData = () => {
    if (!issues || issues.length === 0) return null;

    const now = new Date();
    let buckets = [];
    let labels = [];
    let chartTitle = '';
    let yAxisLabel = 'Number of Issues';

    switch (chartGroupBy) {
      case 'duedate':
        // Due date grouping (4 weeks)
        for (let i = 3; i >= 0; i--) {
          const weekStart = new Date(now.getTime() - (i * 7 * 24 * 60 * 60 * 1000));
          const weekLabel = weekStart.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric' 
          });
          labels.push(weekLabel);
          buckets.push(0);
        }

        issues.forEach(issue => {
          if (issue.due_date) {
            const dueDate = new Date(issue.due_date);
            for (let i = 0; i < 4; i++) {
              const weekStart = new Date(now.getTime() - ((3 - i) * 7 * 24 * 60 * 60 * 1000));
              const weekEnd = new Date(weekStart.getTime() + (7 * 24 * 60 * 60 * 1000));
              
              if (dueDate >= weekStart && dueDate < weekEnd) {
                buckets[i]++;
                break;
              }
            }
          }
        });

        chartTitle = 'Issues Due by Week';
        break;

      case 'startdate':
        // Start date grouping (4 weeks)
        for (let i = 3; i >= 0; i--) {
          const weekStart = new Date(now.getTime() - (i * 7 * 24 * 60 * 60 * 1000));
          const weekLabel = weekStart.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric' 
          });
          labels.push(weekLabel);
          buckets.push(0);
        }

        issues.forEach(issue => {
          if (issue.start_date) {
            const startDate = new Date(issue.start_date);
            for (let i = 0; i < 4; i++) {
              const weekStart = new Date(now.getTime() - ((3 - i) * 7 * 24 * 60 * 60 * 1000));
              const weekEnd = new Date(weekStart.getTime() + (7 * 24 * 60 * 60 * 1000));
              
              if (startDate >= weekStart && startDate < weekEnd) {
                buckets[i]++;
                break;
              }
            }
          }
        });

        chartTitle = 'Issues Starting by Week';
        break;

      case 'created':
        // Created date grouping (4 weeks)
        for (let i = 3; i >= 0; i--) {
          const weekStart = new Date(now.getTime() - (i * 7 * 24 * 60 * 60 * 1000));
          const weekLabel = weekStart.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric' 
          });
          labels.push(weekLabel);
          buckets.push(0);
        }

        issues.forEach(issue => {
          if (issue.created_date) {
            const createdDate = new Date(issue.created_date);
            for (let i = 0; i < 4; i++) {
              const weekStart = new Date(now.getTime() - ((3 - i) * 7 * 24 * 60 * 60 * 1000));
              const weekEnd = new Date(weekStart.getTime() + (7 * 24 * 60 * 60 * 1000));
              
              if (createdDate >= weekStart && createdDate < weekEnd) {
                buckets[i]++;
                break;
              }
            }
          }
        });

        chartTitle = 'Issues Created by Week';
        break;

      case 'updated':
        // Updated date grouping (4 weeks)
        for (let i = 3; i >= 0; i--) {
          const weekStart = new Date(now.getTime() - (i * 7 * 24 * 60 * 60 * 1000));
          const weekLabel = weekStart.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric' 
          });
          labels.push(weekLabel);
          buckets.push(0);
        }

        issues.forEach(issue => {
          if (issue.updated_date) {
            const updatedDate = new Date(issue.updated_date);
            for (let i = 0; i < 4; i++) {
              const weekStart = new Date(now.getTime() - ((3 - i) * 7 * 24 * 60 * 60 * 1000));
              const weekEnd = new Date(weekStart.getTime() + (7 * 24 * 60 * 60 * 1000));
              
              if (updatedDate >= weekStart && updatedDate < weekEnd) {
                buckets[i]++;
                break;
              }
            }
          }
        });

        chartTitle = 'Issues Updated by Week';
        break;

      case 'resolved':
        // Resolved date grouping (4 weeks)
        for (let i = 3; i >= 0; i--) {
          const weekStart = new Date(now.getTime() - (i * 7 * 24 * 60 * 60 * 1000));
          const weekLabel = weekStart.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric' 
          });
          labels.push(weekLabel);
          buckets.push(0);
        }

        issues.forEach(issue => {
          if (issue.resolved_date) {
            const resolvedDate = new Date(issue.resolved_date);
            for (let i = 0; i < 4; i++) {
              const weekStart = new Date(now.getTime() - ((3 - i) * 7 * 24 * 60 * 60 * 1000));
              const weekEnd = new Date(weekStart.getTime() + (7 * 24 * 60 * 60 * 1000));
              
              if (resolvedDate >= weekStart && resolvedDate < weekEnd) {
                buckets[i]++;
                break;
              }
            }
          }
        });

        chartTitle = 'Issues Resolved by Week';
        break;

      case 'status':
        // Status grouping
        const statusCounts = {};
        issues.forEach(issue => {
          const status = issue.status || 'Unknown';
          statusCounts[status] = (statusCounts[status] || 0) + 1;
        });

        labels = Object.keys(statusCounts);
        buckets = Object.values(statusCounts);
        chartTitle = 'Issues by Status';
        break;

      case 'assignee':
        // Assignee grouping
        const assigneeCounts = {};
        issues.forEach(issue => {
          const assignee = issue.assignee || 'Unassigned';
          const displayName = assignee.includes('@') ? assignee.split('@')[0] : assignee;
          assigneeCounts[displayName] = (assigneeCounts[displayName] || 0) + 1;
        });

        labels = Object.keys(assigneeCounts);
        buckets = Object.values(assigneeCounts);
        chartTitle = 'Issues by Assignee';
        break;

      case 'priority':
        // Priority grouping
        const priorityCounts = {};
        issues.forEach(issue => {
          const priority = issue.priority || 'No Priority';
          priorityCounts[priority] = (priorityCounts[priority] || 0) + 1;
        });

        labels = Object.keys(priorityCounts);
        buckets = Object.values(priorityCounts);
        chartTitle = 'Issues by Priority';
        break;

      default:
        return null;
    }

    // Calculate average for time-based charts
    const average = (chartGroupBy === 'duedate' || chartGroupBy === 'created' || 
                    chartGroupBy === 'startdate' || chartGroupBy === 'updated' || 
                    chartGroupBy === 'resolved') 
      ? buckets.reduce((sum, count) => sum + count, 0) / buckets.length 
      : 0;

    // Prepare data for chart
    const datasets = [
      {
        label: 'Issues',
        data: buckets,
        borderColor: '#0052CC',
        backgroundColor: 'rgba(0, 82, 204, 0.1)',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointRadius: 5,
        pointHoverRadius: 7
      }
    ];

    // Add average line for time-based charts
    if (chartGroupBy === 'duedate' || chartGroupBy === 'created' || 
        chartGroupBy === 'startdate' || chartGroupBy === 'updated' || 
        chartGroupBy === 'resolved') {
      datasets.push({
        label: `Average (${average.toFixed(1)})`,
        data: new Array(buckets.length).fill(average),
        borderColor: '#FF5722',
        backgroundColor: 'transparent',
        borderWidth: 2,
        borderDash: [8, 4],
        pointRadius: 0,
        fill: false
      });
    }

    return {
      labels,
      datasets,
      title: chartTitle,
      yAxisLabel
    };
  };

  return (
    <div style={pageStyle}>
      <div style={headerStyle}>
        <h1>Jira Issues</h1>
        <p>Use natural language to search and filter Jira issues</p>
      </div>

      <div style={mainContentStyle}>
        {/* Chat Panel */}
        <div style={chatPanelStyle}>
          <div style={chatHeaderStyle}>
            <h3>Natural Language Query</h3>
            <button 
              onClick={() => setEditMode(!editMode)}
              style={toggleButtonStyle}
            >
              {editMode ? 'Hide JQL' : 'Show JQL'}
            </button>
          </div>

          {/* JQL Editor (conditional) */}
          {editMode && (
            <div style={jqlEditorStyle}>
              <textarea
                value={jqlQuery}
                onChange={(e) => setJqlQuery(e.target.value)}
                placeholder="Enter JQL query directly..."
                style={jqlTextareaStyle}
              />
              <button 
                onClick={() => handleDirectJQL(jqlQuery)}
                style={executeButtonStyle}
                disabled={loading}
              >
                Execute JQL
              </button>
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
              value={chatQuery}
              onChange={(e) => setChatQuery(e.target.value)}
              placeholder="Ask me about your issues... (e.g., 'Show me high priority bugs assigned to John')"
              style={chatInputStyle}
              disabled={loading}
            />
            <button 
              type="submit" 
              style={sendButtonStyle}
              disabled={loading || !chatQuery.trim()}
            >
              {loading ? '...' : 'Send'}
            </button>
          </form>

          {/* Suggestions */}
          {error && (
            <div style={errorStyle}>
              {error}
            </div>
          )}
        </div>

        {/* Issues Display Panel */}
        <div style={issuesPanelStyle}>
          {/* Tab Navigation */}
          <div style={tabNavigationStyle}>
            <button
              style={{
                ...tabButtonStyle,
                ...(activeTab === 'table' ? activeTabButtonStyle : {})
              }}
              onClick={() => setActiveTab('table')}
            >
              Issues Table
            </button>
            <button
              style={{
                ...tabButtonStyle,
                ...(activeTab === 'chart' ? activeTabButtonStyle : {})
              }}
              onClick={() => setActiveTab('chart')}
            >
              Data Trends
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'table' && (
            <div>
              {/* Issues Count */}
              <div style={issuesCountStyle}>
                {loading ? 'Loading...' : 
                  `Showing ${issues.length} of ${issues.length} issues${totalCount > issues.length ? ` (${totalCount} total found)` : ''}`
                }
                {jqlQuery && (
                  <div style={jqlDisplayStyle}>
                    <strong>JQL:</strong> {jqlQuery}
                  </div>
                )}
              </div>

              {/* Error Message */}
              {error && (
                <div style={errorStyle}>
                  {error}
                </div>
              )}

              {/* Issues Table */}
              {!loading && issues.length > 0 && (
                <div style={tableContainerStyle}>
                  <table style={tableStyle}>
                    <thead>
                      <tr style={tableHeaderRowStyle}>
                        <th style={tableHeaderStyle}>Issue</th>
                        <th style={tableHeaderStyle}>Title</th>
                        <th style={tableHeaderStyle}>Status</th>
                        <th style={tableHeaderStyle}>Assignee</th>
                        <th style={tableHeaderStyle}>Priority</th>
                        <th style={tableHeaderStyle}>Created</th>
                        <th style={tableHeaderStyle}>Updated</th>
                        <th style={tableHeaderStyle}>Start Date</th>
                        <th style={tableHeaderStyle}>Due Date</th>
                        <th style={tableHeaderStyle}>Resolved</th>
                        <th style={tableHeaderStyle}>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {issues.map((issue) => (
                        <tr 
                          key={issue.id} 
                          style={tableRowStyle}
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
                            <span style={dateStyle}>
                              {formatDate(issue.updated_date)}
                            </span>
                          </td>
                          <td style={tableCellStyle}>
                            <span style={dateStyle}>
                              {formatDate(issue.start_date)}
                            </span>
                          </td>
                          <td style={tableCellStyle}>
                            <span style={dateStyle}>
                              {formatDate(issue.due_date)}
                            </span>
                          </td>
                          <td style={tableCellStyle}>
                            <span style={dateStyle}>
                              {formatDate(issue.resolved_date)}
                            </span>
                          </td>
                          <td style={tableCellStyle}>
                            <a
                              href={getJiraUrl(issue.id)}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={jiraLinkStyle}
                            >
                              Open in Jira ↗
                            </a>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* No Issues Message */}
              {!loading && issues.length === 0 && !error && (
                <div style={noIssuesStyle}>
                  No issues found. Try a different search query.
                </div>
              )}
            </div>
          )}

          {activeTab === 'chart' && (
            <div style={chartTabStyle}>
              {/* Chart Controls */}
              <div style={chartControlsStyle}>
                <h3 style={chartTitleStyle}>Data Trends</h3>
                <div style={groupByContainerStyle}>
                  <label style={groupByLabelStyle}>Group by:</label>
                  <select 
                    value={chartGroupBy} 
                    onChange={(e) => setChartGroupBy(e.target.value)}
                    style={groupBySelectStyle}
                  >
                    <option value="duedate">Due Date (4 weeks)</option>
                    <option value="startdate">Start Date (4 weeks)</option>
                    <option value="created">Created Date (4 weeks)</option>
                    <option value="updated">Updated Date (4 weeks)</option>
                    <option value="resolved">Resolved Date (4 weeks)</option>
                    <option value="status">Status</option>
                    <option value="assignee">Assignee</option>
                    <option value="priority">Priority</option>
                  </select>
                </div>
              </div>

              {!loading && issues.length > 0 ? (
                <div style={chartContainerStyle}>
                  <TrendChart data={prepareChartData()} />
                </div>
              ) : (
                <div style={noDataStyle}>
                  {loading ? 'Loading chart data...' : 'No data available for chart. Please search for issues first.'}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Add the chart component
const TrendChart = ({ data }) => {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!data || !canvasRef.current) return;

    // Destroy existing chart
    if (chartRef.current) {
      chartRef.current.destroy();
    }

    // Determine chart type based on data structure
    const chartType = (data.labels && data.labels.length <= 6) ? 'bar' : 'line';

    // Create new chart
    const ctx = canvasRef.current.getContext('2d');
    chartRef.current = new ChartJS(ctx, {
      type: chartType,
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: data.title || 'Data Trends',
            font: { size: 16 }
          },
          legend: {
            display: true,
            position: 'top'
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: data.yAxisLabel || 'Count'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Categories'
            }
          }
        },
        interaction: {
          intersect: false,
          mode: 'index'
        }
      }
    });

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, [data]);

  return <canvas ref={canvasRef} />;
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
  maxHeight: '100%',
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

const issuesPanelStyle = {
  backgroundColor: 'white',
  borderRadius: '8px',
  padding: '1.5rem',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
};

const tabNavigationStyle = {
  display: 'flex',
  borderBottom: '1px solid #ddd',
  marginBottom: '1rem'
};

const tabButtonStyle = {
  padding: '0.75rem 1.5rem',
  border: 'none',
  backgroundColor: 'transparent',
  cursor: 'pointer',
  borderBottom: '2px solid transparent',
  fontSize: '1rem',
  fontWeight: '500',
  color: '#666'
};

const activeTabButtonStyle = {
  color: '#0052CC',
  borderBottomColor: '#0052CC'
};

const issuesCountStyle = {
  marginBottom: '1rem',
  fontSize: '1rem',
  color: '#333'
};

const chartTabStyle = {
  padding: '1rem 0'
};

const chartControlsStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '1rem',
  padding: '1rem',
  backgroundColor: '#f8f9fa',
  borderRadius: '8px',
  border: '1px solid #dee2e6'
};

const groupByContainerStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '0.5rem'
};

const groupByLabelStyle = {
  fontWeight: '500',
  color: '#333',
  fontSize: '0.9rem'
};

const groupBySelectStyle = {
  padding: '0.5rem',
  border: '1px solid #ddd',
  borderRadius: '4px',
  backgroundColor: 'white',
  fontSize: '0.9rem',
  minWidth: '200px',
  cursor: 'pointer'
};

const chartTitleStyle = {
  margin: '0',
  color: '#333',
  fontSize: '1.2rem'
};

const chartContainerStyle = {
  height: '400px',
  backgroundColor: 'white',
  padding: '1rem',
  borderRadius: '8px',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
};

const noDataStyle = {
  textAlign: 'center',
  padding: '3rem',
  color: '#666',
  fontSize: '1.1rem'
};

const noIssuesStyle = {
  textAlign: 'center',
  padding: '3rem',
  color: '#666',
  fontSize: '1.1rem',
  backgroundColor: '#f8f9fa',
  borderRadius: '8px'
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

const errorStyle = {
  padding: '1rem',
  backgroundColor: '#ffebee',
  color: '#c62828',
  borderRadius: '4px',
  border: '1px solid #ffcdd2',
  margin: '1rem 0',
  fontSize: '0.9rem'
};

const tableContainerStyle = {
  overflowX: 'auto',
  marginTop: '1rem',
  borderRadius: '8px',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
};

export default IssuesPage;
