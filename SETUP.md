# Setup Instructions

## Quick Start

### 1. Configure Environment

Copy the example environment file and edit it with your credentials:

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your actual values:

```bash
# Jira Configuration
JIRA_SERVER=https://your-company.atlassian.net
JIRA_USERNAME=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token
JIRA_PROJECT_KEY=YOUR_PROJECT

# LLM Configuration (optional)
LLM_MODEL_PATH=./models/your-model.gguf
LLM_CONTEXT_SIZE=4096
LLM_MAX_TOKENS=512
LLM_TEMPERATURE=0.7
```

### 2. Get Jira API Token

1. Log in to your Jira instance
2. Go to Account Settings > Security > API tokens
3. Create a new token and copy it
4. Use your email as JIRA_USERNAME and the token as JIRA_API_TOKEN

### 3. Download Local LLM Model (Optional)

Download a GGUF model file (e.g., from Hugging Face):

```bash
mkdir -p backend/models
# Example: Download a small model like Code Llama or similar
# wget https://huggingface.co/your-model/your-model.gguf -O backend/models/your-model.gguf
```

### 4. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
# or
pip install fastapi uvicorn pydantic pydantic-settings jira python-dotenv httpx python-multipart aiofiles llama-cpp-python
```

### 5. Run the Application

```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Frontend (in another terminal)
cd frontend
npm install
npm start
```

## Features

- **Real Jira Integration**: Connects to your actual Jira instance
- **Local LLM Support**: Uses .gguf models for conversational AI
- **Fallback Support**: Works with mock data and pattern matching if not configured
- **Status Monitoring**: Check configuration status via `/ai/status` endpoint

## API Endpoints

- `GET /ai/status` - Check AI and Jira integration status
- `POST /ai/query` - Conversational AI queries
- `GET /tasks` - Fetch tasks from Jira
- `POST /tasks` - Create new tasks

## Troubleshooting

1. **Jira Connection Issues**: Check your server URL, username, and API token
2. **LLM Model Not Loading**: Ensure the GGUF file path is correct and the file exists
3. **Dependencies**: Make sure all Python packages are installed correctly

The application will work with fallback data if Jira or LLM are not configured.