# UT Jira Helper

A comprehensive Jira Dashboard clone with advanced widget system and conversational AI capabilities. This application provides an intuitive interface for managing Jira tasks with modern features like natural language queries, real-time search, and intelligent project insights.

## 🚀 Key Features

### 🔗 **Real Jira Integration**
- **Live Data Connection**: Connect to your actual Jira instance using API tokens
- **Full CRUD Operations**: Read, create, and manage tasks directly through Jira API
- **Automatic Fallback**: Works with mock data when Jira is not configured
- **Project Filtering**: Filter tasks by project, status, and assignee

### 🤖 **Local LLM Conversational AI**
- **GGUF Model Support**: Run local LLM models (.gguf files) for enhanced conversational capabilities
- **Intelligent Responses**: Context-aware responses based on actual task data
- **Pattern Matching Fallback**: Works with basic pattern matching when LLM is not available
- **Natural Language Processing**: Handle complex queries about projects, tasks, and team workload

### 🎛️ Interactive Dashboard
- **Responsive Grid Layout**: Clean, modern dashboard that adapts to all screen sizes
- **Modular Widget System**: Extensible architecture for adding new widgets
- **Jira-Inspired Design**: Professional interface matching Jira's design language
- **Real-time Updates**: Dynamic content updates based on user interactions

### 📊 Smart Widgets

#### Task Summary Widget
- Visual overview of task counts by status (To Do, In Progress, Done)
- Color-coded status indicators for quick identification
- Progress calculation and completion tracking
- Empty state handling with helpful messages

#### Advanced Search & Chat Widget
- **Natural Language Search**: Query tasks using conversational language
- **Real-time Filtering**: Instant search results across all task fields
- **AI-Powered Assistant**: Conversational interface for task management
- **Search History**: Track and reuse previous queries
- **Quick Actions**: Pre-built buttons for common queries

#### Task List Widget
- Dynamic task display with configurable limits
- Status badges and assignee information
- Responsive design with mobile optimization
- Integration with search and filter results

### 🤖 Conversational AI System

#### Local LLM Integration
- **GGUF Model Support**: Direct integration with local .gguf model files
- **High Performance**: Runs entirely offline with llama-cpp-python
- **Context-Aware Responses**: Uses current task data to provide relevant insights
- **Configurable Parameters**: Adjustable temperature, context size, and token limits

#### Real Jira API Integration  
- **Live Data Processing**: Queries work with actual Jira tasks and projects
- **API Token Authentication**: Secure connection using Jira API tokens
- **Project-Specific Filtering**: Automatic filtering by configured project keys
- **Real-time Task Management**: Create, read, and analyze tasks directly from Jira

#### AI Response Capabilities
- Natural language query processing with actual task context
- Support for complex queries like:
  - "What's in progress for Project X?"
  - "Give me a summary of John's workload"
  - "Show tasks that need attention"
  - "Create task: Implement new feature"
  - "Which team member has the most open tasks?"

#### Fallback Systems
- **Pattern Matching**: Works without LLM using intelligent pattern recognition
- **Mock Data**: Functions with sample data when Jira is not configured
- **Graceful Degradation**: Maintains functionality across all configuration states

### 🔌 API Integration

#### Jira API Endpoints
- **Real Jira Connection**: Direct integration with Atlassian Jira Cloud/Server
- **Authentication**: API token-based secure authentication
- **Task Operations**: Full CRUD operations on Jira issues
- **JQL Support**: Advanced queries using Jira Query Language
- **Project Filtering**: Automatic project and status-based filtering

#### Task Management Endpoints
- `GET /api/tasks` - Retrieve tasks from Jira with filtering options
- `GET /api/tasks/{id}` - Get specific task details from Jira
- `POST /api/tasks` - Create new tasks directly in Jira

#### Conversational AI Endpoints
- `POST /api/ai/query` - Process natural language queries with LLM or pattern matching
- `GET /api/ai/analyze` - Get AI-powered project analysis from real Jira data
- `GET /api/ai/history` - Retrieve conversation history
- `DELETE /api/ai/history` - Clear conversation history
- `GET /api/ai/status` - Check LLM and Jira integration status

## 🛠️ Tech Stack

- **Frontend**: React.js with modern hooks and component architecture
- **Backend**: Python FastAPI with Pydantic models
- **State Management**: React Context and component-level state
- **Styling**: CSS3 with Flexbox and Grid layouts
- **API**: RESTful services with comprehensive OpenAPI documentation

## 📁 Project Structure

```
ut-jira-helper/
├── frontend/                    # React.js frontend application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   │   ├── Dashboard.js    # Main dashboard container
│   │   │   ├── Widget.js       # Base widget component
│   │   │   ├── TaskSummaryWidget.js
│   │   │   ├── TaskListWidget.js
│   │   │   └── SearchWidget.js
│   │   ├── utils/
│   │   │   └── conversationalHelper.js  # Frontend AI logic
│   │   ├── App.js              # Main application component
│   │   └── App.css             # Application styling
│   └── package.json            # Frontend dependencies
├── backend/                     # Python FastAPI backend service
│   ├── app/
│   │   ├── api/               # API route handlers
│   │   │   ├── tasks.py       # Task management endpoints
│   │   │   └── conversation.py # AI conversation endpoints
│   │   ├── models/            # Pydantic data models
│   │   │   ├── task.py        # Task-related models
│   │   │   └── conversation.py # AI conversation models
│   │   └── main.py            # FastAPI application setup
│   └── pyproject.toml         # Backend dependencies
└── README.md                  # This file
```

## 🚀 Setup Instructions

### Prerequisites

- **Node.js** (v14 or later)
- **npm** or **yarn** package manager
- **Python** (v3.8 or later)
- **pip** package manager
- **Jira Instance** (Cloud or Server) with API access
- **LLM Model** (optional .gguf file for enhanced AI)

### Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd ut-jira-helper
   ```

2. **Configure Environment**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your Jira credentials and LLM model path
   ```

3. **Install Backend Dependencies**
   ```bash
   cd backend
   pip install fastapi uvicorn pydantic pydantic-settings jira python-dotenv httpx python-multipart aiofiles llama-cpp-python
   ```

4. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```

5. **Start the Application**
   ```bash
   # Terminal 1: Start backend
   cd backend
   uvicorn app.main:app --reload
   
   # Terminal 2: Start frontend
   cd frontend
   npm start
   ```

### Configuration

#### Jira Integration Setup

1. **Get Jira API Token**:
   - Log in to your Jira instance
   - Go to Account Settings > Security > API tokens
   - Create a new token and copy it

2. **Configure Environment Variables**:
   ```bash
   JIRA_SERVER=https://your-company.atlassian.net
   JIRA_USERNAME=your-email@example.com
   JIRA_API_TOKEN=your-jira-api-token
   JIRA_PROJECT_KEY=YOUR_PROJECT
   ```

#### Local LLM Setup (Optional)

1. **Download GGUF Model**:
   ```bash
   mkdir -p backend/models
   # Download your preferred .gguf model file
   # Example: Code Llama, Llama 2, Mistral, etc.
   ```

2. **Configure LLM Settings**:
   ```bash
   LLM_MODEL_PATH=./models/your-model.gguf
   LLM_CONTEXT_SIZE=4096
   LLM_MAX_TOKENS=512
   LLM_TEMPERATURE=0.7
   ```

### Verification

Check integration status:
```bash
curl http://localhost:8000/ai/status
```

Should return:
```json
{
  "llm_available": true,
  "jira_configured": true,
  "status": "ready"
}
```

## 📖 Usage Examples

### 💬 Natural Language Queries

The AI assistant supports conversational queries across various categories:

#### Project Status Queries
```
"What's in progress?"
"Show me completed tasks"
"Give me a project summary"
"How many tasks are pending?"
```

#### Team & Assignment Queries
```
"What's user1 working on?"
"Show workload distribution"
"Who is assigned to task JIRA-1?"
"Which tasks are unassigned?"
```

#### Task Creation & Management
```
"Create task: Fix login bug"
"Add task: Update documentation"
"New task: Implement user dashboard"
```

#### Search & Discovery
```
"Find tasks about login"
"Show tasks assigned to user2"
"Search for JIRA-123"
"Find urgent tasks"
```

### 🔍 Advanced Search Features

The search widget provides powerful filtering capabilities with real Jira data:

- **Full-text search** across task titles, descriptions, and IDs
- **Status filtering** with visual indicators
- **Assignee-based searches** for team management
- **JQL Integration** for advanced Jira queries
- **Real-time results** with instant feedback
- **Search history** for repeated queries

### 🤖 Conversational AI Examples

#### With Local LLM Model
```
"What tasks are overdue in Project ABC?"
"Show me John's current workload and suggest redistributions"
"Generate a weekly status report for the development team"
"What are the common themes in our bug reports this month?"
```

#### Basic Pattern Matching (Fallback)
```
"What's in progress?"
"Show me completed tasks"
"Give me a project summary"
"What's user1 working on?"
```

### 📊 Dashboard Widgets

#### Task Summary Widget
- Real-time task counts from Jira
- Visual status distribution with Jira-accurate colors
- Progress calculations based on actual project data
- Drill-down capabilities to detailed views

#### Task List Widget
- Dynamic display of actual Jira tasks
- Live status updates and assignee information
- Configurable filters and sorting options
- Responsive design for mobile devices

## 🔮 Advanced Features

### Real-Time Jira Integration
The application connects directly to your Jira instance for live data:

- **Automatic Task Sync**: Real-time updates from your Jira projects
- **Bidirectional Sync**: Changes made through the app reflect in Jira
- **Project Filtering**: Automatically filters by your configured project keys
- **Status Mapping**: Accurate status representation matching your Jira workflow

### Local LLM Processing
Enhanced conversational AI using local GGUF models:

- **Privacy-First**: All AI processing happens locally, no data sent to external services  
- **Model Flexibility**: Support for various GGUF models (Llama 2, Code Llama, Mistral, etc.)
- **Context-Aware**: Uses actual project data for intelligent responses
- **Performance Optimized**: Efficient inference with llama-cpp-python

### Intelligent Fallbacks
Robust operation across different configuration scenarios:

- **LLM Fallback**: Pattern matching when local model isn't available
- **Jira Fallback**: Mock data mode for development and testing
- **Graceful Degradation**: Full functionality maintained regardless of configuration
- **Status Monitoring**: Real-time status of all integrations

## 🔧 API Documentation

### Interactive Documentation

Once the backend is running, access comprehensive API documentation at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

#### Task Management
- `GET /api/tasks` - List all tasks with optional filtering
- `GET /api/tasks/{task_id}` - Retrieve specific task details
- `POST /api/tasks` - Create a new task

#### Conversational AI
- `POST /api/ai/query` - Process natural language queries
- `GET /api/ai/analyze` - Get intelligent project analysis
- `GET /api/ai/history` - Retrieve conversation history
- `DELETE /api/ai/history` - Clear conversation history

### Example API Usage

```javascript
// Query the AI assistant
const response = await fetch('/api/ai/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "What tasks are in progress?",
    context: "Sprint planning meeting"
  })
});

const result = await response.json();
console.log(result.response); // AI-generated response
console.log(result.suggested_actions); // Follow-up actions
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
poetry run pytest
# or
python -m pytest
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Integration Testing
```bash
# Start backend
cd backend && uvicorn app.main:app --reload &

# Start frontend
cd frontend && npm start &

# Run end-to-end tests
npm run test:e2e
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow existing code style and conventions
- Add tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by Jira's user interface and workflow concepts
- Built with modern web technologies for optimal performance
- Designed with extensibility and maintainability in mind

---

**Note**: This is a demonstration application showcasing modern web development practices and conversational AI integration. The AI assistant currently uses pattern matching and can be extended with actual LLM models for enhanced capabilities.
