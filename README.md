# UT Jira Helper

A comprehensive Jira Dashboard clone with advanced widget system and conversational AI capabilities. This application provides an intuitive interface for managing Jira tasks with modern features like natural language queries, real-time search, and intelligent project insights.

## 🚀 Features

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

#### Frontend AI Features
- Natural language query processing
- Context-aware responses based on current task data
- Support for complex queries like:
  - "What's in progress?"
  - "Give me a summary"
  - "Show workload distribution"
  - "What's user1 working on?"
  - "Create task: Fix login bug"

#### Backend AI Services
- **RESTful AI Endpoints**: Structured API for conversational processing
- **Query Analysis**: Pattern matching and natural language understanding
- **Task Analytics**: Intelligent project insights and recommendations
- **Conversation History**: Track and analyze user interactions
- **Extensible Architecture**: Ready for local LLM integration (GGUF models)

### 🔌 API Integration

#### Task Management Endpoints
- `GET /api/tasks` - Retrieve tasks with filtering options
- `GET /api/tasks/{id}` - Get specific task details
- `POST /api/tasks` - Create new tasks

#### Conversational AI Endpoints
- `POST /api/ai/query` - Process natural language queries
- `GET /api/ai/analyze` - Get AI-powered project analysis
- `GET /api/ai/history` - Retrieve conversation history
- `DELETE /api/ai/history` - Clear conversation history

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

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Application will be available at http://localhost:3000
```

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Option 1: Using Poetry (recommended)
pip install poetry
poetry install
poetry run uvicorn app.main:app --reload

# Option 2: Using pip directly
pip install fastapi uvicorn pydantic
uvicorn app.main:app --reload

# API will be available at http://localhost:8000
# Interactive API docs at http://localhost:8000/docs
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

The search widget provides powerful filtering capabilities:

- **Full-text search** across task titles, descriptions, and IDs
- **Status filtering** with visual indicators
- **Assignee-based searches** for team management
- **Real-time results** with instant feedback
- **Search history** for repeated queries

### 📊 Dashboard Widgets

#### Task Summary Widget
- Provides at-a-glance project status
- Shows task distribution across statuses
- Calculates completion percentages
- Offers drill-down capabilities

#### Task List Widget
- Displays tasks in a clean, organized format
- Supports dynamic filtering and sorting
- Shows essential task information (ID, title, status, assignee)
- Responsive design for mobile devices

## 🔮 Future Enhancements

### Local LLM Integration
The backend architecture is designed to easily integrate with local LLM models:

```python
# Future LLM integration example
from llm_provider import LocalLLM

async def process_with_llm(query: str, context: str):
    llm = LocalLLM(model_path="path/to/gguf/model")
    response = await llm.generate_response(query, context)
    return response
```

### Advanced Jira API Features
- Real Jira API integration for live data
- Custom field support and advanced filtering
- Automated workflow management
- Integration with Jira webhooks for real-time updates

### Enhanced Conversational Capabilities
- Multi-turn conversations with context retention
- Task creation through natural language
- Automated project insights and recommendations
- Voice interface integration

### Additional Widget Types
- **Charts Widget**: Visual analytics and reporting
- **Calendar Widget**: Due date and timeline management
- **Team Widget**: Assignee management and workload visualization
- **Custom Filters Widget**: Advanced query building interface

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
