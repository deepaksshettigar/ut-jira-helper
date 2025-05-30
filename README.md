# UT Jira Helper

A utility tool for enhancing and streamlining Jira workflows. This application provides helpful features for Jira users to increase productivity and simplify common tasks.

## Tech Stack

- **Frontend**: ReactJS
- **Backend**: Python with FastAPI

## Project Structure

```
ut-jira-helper/
├── frontend/     # ReactJS frontend application
├── backend/      # Python FastAPI backend service
```

## Setup Instructions

### Prerequisites

- Node.js (v14 or later)
- npm or yarn
- Python (v3.8 or later)
- pip

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm start
```

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Poetry if not already installed
# pip install poetry

# Install dependencies
poetry install

# Run the FastAPI server (option 1)
poetry run start

# Alternatively, you can still run with uvicorn directly (option 2)
# poetry run uvicorn app.main:app --reload
```

## API Documentation

Once the backend server is running, you can access the API documentation at:

```
http://localhost:8000/docs
```

## Features

### Jira Dashboard Clone

The application now includes a comprehensive dashboard with multiple widgets:

#### 🎛️ **Dashboard Layout**
- Responsive grid layout for widgets
- Clean, Jira-inspired design
- Mobile-friendly interface

#### 📊 **Task Summary Widget**
- Visual overview of task counts by status
- Total task counter with progress indicators
- Color-coded status indicators (To Do, In Progress, Done)

#### 🔍 **Search & Chat Widget**
- Natural language search across all task fields
- Conversational AI assistant for task queries
- Quick action buttons for common questions
- Search history tracking

#### 📋 **Task List Widget**
- Dynamic task display based on search results
- Compact view with essential task information
- Status badges and assignee information
- Configurable task limits

#### 🤖 **Conversational Features**
- AI-powered responses to natural language queries
- Support for questions like:
  - "What's in progress?"
  - "Give me a summary"
  - "Show workload distribution"
  - "Create task: Fix login bug"
- Context-aware responses based on current task data
- Future-ready for LLM integration (GGUF models)

#### 🔧 **Technical Features**
- Modular widget system for easy extension
- Real-time search and filtering
- State management between widgets
- RESTful API integration
- Modern React architecture

### Usage Examples

1. **Getting a Project Overview:**
   - Click "Give me a summary" or type "summary" in the search box

2. **Finding Specific Tasks:**
   - Type keywords, task IDs, or assignee names in the search box

3. **Checking Team Workload:**
   - Ask "Show workload distribution" or "What's user1 working on?"

4. **Natural Language Queries:**
   - "What needs to be done?"
   - "What's completed?"
   - "How many tasks are in progress?"

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
