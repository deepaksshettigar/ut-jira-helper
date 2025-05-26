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

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
