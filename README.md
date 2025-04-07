# CrowdWork: Comedian Analysis Web App

A web application that analyzes a comedian's publicly available stand-up videos from social media platforms (starting with YouTube) to estimate the percentage of performance time dedicated to crowdwork versus prepared material.

## Project Overview

This application allows users to:
- Input a YouTube channel URL or handle
- Analyze videos to identify stand-up comedy performances
- Process transcripts to classify content as crowdwork or prepared material
- View percentage breakdown of crowdwork vs. prepared material

## Repository Structure

- `/backend` - Python FastAPI backend
- `/frontend` - React (Vite) frontend

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- YouTube Data API v3 key

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On MacOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
# On Windows (PowerShell):
$env:YOUTUBE_API_KEY = "your-api-key-here"
# On MacOS/Linux:
# export YOUTUBE_API_KEY="your-api-key-here"

# Run development server
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## Development Status

This project is currently in MVP development stage, focused exclusively on YouTube integration.

## License

[MIT](LICENSE) 