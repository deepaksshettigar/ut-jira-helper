// Enhanced conversational AI integration with backend LLM service
// Integrates with the backend's intelligent filtering and analysis

export class ConversationalHelper {
  constructor(tasks) {
    this.tasks = tasks || [];
    this.apiBaseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  }

  // Analyze query and provide conversational response using backend AI
  async getResponse(query) {
    try {
      // Try to use backend AI service first
      const response = await fetch(`${this.apiBaseUrl}/api/ai/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          context: 'Frontend search widget'
        })
      });

      if (response.ok) {
        const result = await response.json();
        return {
          text: result.response,
          taskCount: result.task_count,
          suggestedActions: result.suggested_actions,
          chartRecommendation: result.chart_recommendation
        };
      } else {
        // Fallback to local processing
        return this.getLocalResponse(query);
      }
    } catch (error) {
      console.warn('Backend AI service unavailable, using local processing:', error.message);
      // Fallback to local processing
      return this.getLocalResponse(query);
    }
  }

  // Local fallback processing (original implementation)
  getLocalResponse(query) {
    const lowerQuery = query.toLowerCase();
    
    // Task creation queries
    if (lowerQuery.includes('create') || lowerQuery.includes('add') || lowerQuery.includes('new task')) {
      return {
        text: this.getCreateTaskResponse(query),
        taskCount: 0,
        suggestedActions: ['Set assignee', 'Add description', 'Create task via API'],
        chartRecommendation: null
      };
    }
    
    // Task status queries
    if (lowerQuery.includes('in progress') || lowerQuery.includes('working on')) {
      const inProgressTasks = this.tasks.filter(task => task.status === 'In Progress');
      return {
        text: this.getInProgressResponse(),
        taskCount: inProgressTasks.length,
        suggestedActions: ['View task details', 'Update status', 'Mark as done'],
        chartRecommendation: 'timeline'
      };
    }
    
    if (lowerQuery.includes('to do') || lowerQuery.includes('todo') || lowerQuery.includes('pending')) {
      const todoTasks = this.tasks.filter(task => task.status === 'To Do');
      return {
        text: this.getToDoResponse(),
        taskCount: todoTasks.length,
        suggestedActions: ['Start working', 'Assign tasks', 'Prioritize'],
        chartRecommendation: 'table'
      };
    }
    
    if (lowerQuery.includes('done') || lowerQuery.includes('completed') || lowerQuery.includes('finished')) {
      const doneTasks = this.tasks.filter(task => task.status === 'Done');
      return {
        text: this.getDoneResponse(),
        taskCount: doneTasks.length,
        suggestedActions: ['View completed', 'Archive tasks', 'Generate report'],
        chartRecommendation: 'pie'
      };
    }
    
    // Summary queries
    if (lowerQuery.includes('summary') || lowerQuery.includes('overview') || lowerQuery.includes('status')) {
      return {
        text: this.getSummaryResponse(),
        taskCount: this.tasks.length,
        suggestedActions: ['Show pie chart', 'View detailed breakdown', 'Export data'],
        chartRecommendation: 'pie'
      };
    }
    
    // Assignee queries
    if (lowerQuery.includes('user1') || lowerQuery.includes('assigned to user1')) {
      const userTasks = this.tasks.filter(task => task.assignee?.includes('user1'));
      return {
        text: this.getAssigneeResponse('user1@example.com'),
        taskCount: userTasks.length,
        suggestedActions: ['View user tasks', 'Check workload', 'Reassign tasks'],
        chartRecommendation: 'bar'
      };
    }
    
    if (lowerQuery.includes('user2') || lowerQuery.includes('assigned to user2')) {
      const userTasks = this.tasks.filter(task => task.assignee?.includes('user2'));
      return {
        text: this.getAssigneeResponse('user2@example.com'),
        taskCount: userTasks.length,
        suggestedActions: ['View user tasks', 'Check workload', 'Reassign tasks'],
        chartRecommendation: 'bar'
      };
    }
    
    // Weekly resolved queries
    if (lowerQuery.includes('average resolved') || lowerQuery.includes('weekly resolved') || lowerQuery.includes('resolved per week')) {
      return this.handleWeeklyResolvedQuery(query);
    }
    
    // Workload queries
    if (lowerQuery.includes('workload') || lowerQuery.includes('how many') || lowerQuery.includes('count')) {
      return {
        text: this.getWorkloadResponse(),
        taskCount: this.tasks.length,
        suggestedActions: ['Show bar chart', 'Balance workload', 'View individual assignments'],
        chartRecommendation: 'bar'
      };
    }
    
    // Priority/urgent queries
    if (lowerQuery.includes('urgent') || lowerQuery.includes('priority') || lowerQuery.includes('important')) {
      return {
        text: this.getPriorityResponse(),
        taskCount: this.tasks.length,
        suggestedActions: ['Filter by priority', 'View urgent tasks', 'Sort by importance'],
        chartRecommendation: 'bar'
      };
    }
    
    // Help queries
    if (lowerQuery.includes('help') || lowerQuery.includes('what can') || lowerQuery.includes('?')) {
      return {
        text: this.getHelpResponse(),
        taskCount: this.tasks.length,
        suggestedActions: ['Try sample query', 'View task summary', 'Create new task'],
        chartRecommendation: null
      };
    }
    
    // Search fallback
    const searchResults = this.searchTasks(query);
    if (searchResults.length > 0) {
      return {
        text: this.getSearchResultsResponse(query, searchResults),
        taskCount: searchResults.length,
        suggestedActions: ['View task details', 'Refine search', 'Filter results'],
        chartRecommendation: 'table'
      };
    }
    
    return {
      text: this.getDefaultResponse(query),
      taskCount: 0,
      suggestedActions: ['Ask for help', 'Try different query', 'View all tasks'],
      chartRecommendation: null
    };
  }

  searchTasks(query) {
    return this.tasks.filter(task => 
      task.title.toLowerCase().includes(query.toLowerCase()) ||
      task.description?.toLowerCase().includes(query.toLowerCase()) ||
      task.id.toLowerCase().includes(query.toLowerCase()) ||
      task.status.toLowerCase().includes(query.toLowerCase()) ||
      task.assignee?.toLowerCase().includes(query.toLowerCase())
    );
  }

  getCreateTaskResponse(query) {
    // Extract potential task title from the query
    const createPatterns = [
      /create task[:\s]+([^.!?]*)/i,
      /add task[:\s]+([^.!?]*)/i,
      /new task[:\s]+([^.!?]*)/i,
      /create[:\s]+([^.!?]*)/i
    ];
    
    let taskTitle = '';
    for (const pattern of createPatterns) {
      const match = query.match(pattern);
      if (match && match[1]) {
        taskTitle = match[1].trim();
        break;
      }
    }
    
    if (taskTitle) {
      return `I'd be happy to help you create a task! Here's what I understood:

📝 Task Title: "${taskTitle}"

To create this task, you would need to use the task creation feature. In a real Jira integration, this would automatically create the task for you.

Would you like me to help you with anything else about this task, such as:
• Setting an assignee
• Adding a description  
• Setting the priority
• Checking similar existing tasks`;
    } else {
      return `I can help you create a new task! Try saying something like:
• "Create task: Fix the login bug"
• "Add task: Update documentation"
• "New task: Implement user dashboard"

What task would you like to create?`;
    }
  }

  getInProgressResponse() {
    const inProgressTasks = this.tasks.filter(task => task.status === 'In Progress');
    if (inProgressTasks.length === 0) {
      return "Great news! There are no tasks currently in progress. Everything is either completed or waiting to be started.";
    }
    
    const taskList = inProgressTasks.map(task => `• ${task.id}: ${task.title}`).join('\n');
    return `Currently, there ${inProgressTasks.length === 1 ? 'is' : 'are'} ${inProgressTasks.length} task${inProgressTasks.length === 1 ? '' : 's'} in progress:\n\n${taskList}`;
  }

  getToDoResponse() {
    const todoTasks = this.tasks.filter(task => task.status === 'To Do');
    if (todoTasks.length === 0) {
      return "Excellent! There are no pending tasks in your backlog. All tasks are either in progress or completed.";
    }
    
    const taskList = todoTasks.map(task => `• ${task.id}: ${task.title}`).join('\n');
    return `You have ${todoTasks.length} task${todoTasks.length === 1 ? '' : 's'} waiting to be started:\n\n${taskList}\n\nReady to tackle any of these?`;
  }

  getDoneResponse() {
    const doneTasks = this.tasks.filter(task => task.status === 'Done');
    if (doneTasks.length === 0) {
      return "No tasks are marked as completed yet. Keep working - you'll get there!";
    }
    
    const taskList = doneTasks.map(task => `• ${task.id}: ${task.title}`).join('\n');
    return `Well done! You've completed ${doneTasks.length} task${doneTasks.length === 1 ? '' : 's'}:\n\n${taskList}\n\n🎉 Keep up the great work!`;
  }

  getSummaryResponse() {
    const statusCounts = this.tasks.reduce((counts, task) => {
      counts[task.status] = (counts[task.status] || 0) + 1;
      return counts;
    }, {});
    
    const total = this.tasks.length;
    let summary = `Here's your project overview:\n\n📊 Total Tasks: ${total}\n`;
    
    Object.entries(statusCounts).forEach(([status, count]) => {
      const emoji = status === 'Done' ? '✅' : status === 'In Progress' ? '🔄' : '📋';
      summary += `${emoji} ${status}: ${count}\n`;
    });
    
    if (statusCounts['Done']) {
      const completion = Math.round((statusCounts['Done'] / total) * 100);
      summary += `\n🎯 Progress: ${completion}% complete`;
    }
    
    return summary;
  }

  getAssigneeResponse(assignee) {
    const userTasks = this.tasks.filter(task => task.assignee === assignee);
    if (userTasks.length === 0) {
      return `${assignee} doesn't have any tasks assigned currently.`;
    }
    
    const statusCounts = userTasks.reduce((counts, task) => {
      counts[task.status] = (counts[task.status] || 0) + 1;
      return counts;
    }, {});
    
    let response = `${assignee} has ${userTasks.length} task${userTasks.length === 1 ? '' : 's'} assigned:\n\n`;
    Object.entries(statusCounts).forEach(([status, count]) => {
      response += `• ${count} ${status}\n`;
    });
    
    return response;
  }

  getWorkloadResponse() {
    const assigneeCounts = this.tasks.reduce((counts, task) => {
      if (task.assignee) {
        counts[task.assignee] = (counts[task.assignee] || 0) + 1;
      }
      return counts;
    }, {});
    
    if (Object.keys(assigneeCounts).length === 0) {
      return "No tasks are currently assigned to anyone.";
    }
    
    let response = "Current workload distribution:\n\n";
    Object.entries(assigneeCounts).forEach(([assignee, count]) => {
      response += `• ${assignee}: ${count} task${count === 1 ? '' : 's'}\n`;
    });
    
    return response;
  }

  getPriorityResponse() {
    // Since we don't have priority field, we'll use status as proxy
    const urgentTasks = this.tasks.filter(task => task.status === 'In Progress');
    if (urgentTasks.length === 0) {
      return "No tasks are currently in progress, so nothing is immediately urgent. Consider starting on your 'To Do' items.";
    }
    
    return `The most urgent items are the ${urgentTasks.length} task${urgentTasks.length === 1 ? '' : 's'} currently in progress. Focus on completing these first!`;
  }

  getSearchResultsResponse(query, results) {
    if (results.length === 1) {
      const task = results[0];
      return `I found one task matching "${query}":\n\n${task.id}: ${task.title}\nStatus: ${task.status}\nAssigned to: ${task.assignee || 'Unassigned'}`;
    }
    
    const taskList = results.slice(0, 3).map(task => `• ${task.id}: ${task.title} (${task.status})`).join('\n');
    const remaining = results.length > 3 ? `\n...and ${results.length - 3} more` : '';
    
    return `I found ${results.length} task${results.length === 1 ? '' : 's'} matching "${query}":\n\n${taskList}${remaining}`;
  }

  getHelpResponse() {
    return `Hi! I'm here to help you with your Jira tasks. You can ask me things like:

📋 **Task Information:**
• "What's in progress?" - See current work
• "What needs to be done?" - View pending tasks  
• "Show me completed tasks" - See what's done
• "Give me a summary" - Project overview
• "What's user1 working on?" - User workload

🔍 **Search:**
• Search for specific tasks by name or ID
• "Find login tasks" - Search by keywords

💬 **Conversational:**
• "Create task: Fix navigation bug" - Task creation guidance
• "Show workload distribution" - Team insights
• Natural language queries about your project

Just type naturally and I'll do my best to help! 🤖

*Note: This is a demo AI assistant. In a full implementation, it would integrate with actual Jira APIs and could use local LLM models for enhanced capabilities.*`;
  }

  async handleWeeklyResolvedQuery(query) {
    try {
      const lowerQuery = query.toLowerCase();
      
      // Extract assignee from query if mentioned
      let assignee = null;
      if (lowerQuery.includes('user1') || lowerQuery.includes('for user1')) {
        assignee = 'user1@example.com';
      } else if (lowerQuery.includes('user2') || lowerQuery.includes('for user2')) {
        assignee = 'user2@example.com';
      }
      
      // Build API URL
      let apiUrl = `${this.apiBaseUrl}/api/tasks/analytics/weekly-resolved`;
      if (assignee) {
        apiUrl += `?assignee=${encodeURIComponent(assignee)}`;
      }
      
      // Fetch weekly analytics from backend
      const response = await fetch(apiUrl);
      if (!response.ok) {
        throw new Error('Failed to fetch analytics');
      }
      
      const analytics = await response.json();
      
      // Generate response text
      const assigneeText = assignee ? ` for ${assignee}` : '';
      const responseText = `Weekly Resolved Tasks Analysis${assigneeText}:

📊 **Average:** ${analytics.average_per_week} tasks per week
📈 **Total Resolved:** ${analytics.total_resolved} tasks in ${analytics.weeks_analyzed} weeks

**Weekly Breakdown:**
${Object.entries(analytics.weekly_breakdown)
  .map(([week, count]) => `• ${week}: ${count} task${count === 1 ? '' : 's'}`)
  .join('\n')}

${analytics.total_resolved > 0 ? 
  '🎯 Keep up the great work!' : 
  '💡 Consider reviewing task completion workflow.'}`;

      return {
        text: responseText,
        taskCount: analytics.total_resolved,
        suggestedActions: ['View detailed breakdown', 'Export analytics', 'Compare assignees'],
        chartRecommendation: 'weekly_trend',
        chartData: analytics
      };
    } catch (error) {
      console.error('Error fetching weekly analytics:', error);
      
      // Fallback response
      return {
        text: 'Sorry, I couldn\'t fetch the weekly resolved analytics right now. Please try again later.',
        taskCount: 0,
        suggestedActions: ['Try again', 'Check connection'],
        chartRecommendation: null
      };
    }
  }

  getDefaultResponse(query) {
    return `I'm not sure how to help with "${query}" specifically, but I can search your tasks or answer questions about task status, assignments, and progress. Try asking "help" to see what I can do!`;
  }
}