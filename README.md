# CrowdWork

A web application that analyzes comedians' stand-up videos to estimate the percentage of performance time dedicated to crowdwork versus prepared material.

## Overview

CrowdWork helps researchers, comedy enthusiasts, and performers gain insights into comedy techniques by analyzing YouTube videos of stand-up performances. The application:

1. Takes a YouTube channel URL as input
2. Analyzes videos from the channel to identify stand-up comedy performances
3. Retrieves video transcripts and processes them
4. Classifies segments as either "crowdwork" (interaction with the audience) or "prepared material"
5. Provides detailed visualizations and analytics of the results

## Key Features

- **Channel Analysis**: Analyze any YouTube comedy channel
- **Advanced Text Analysis**: Rule-based pattern matching to identify audience interactions
- **Transcript Processing**: Automatic retrieval and analysis of video transcripts
- **Detailed Classifications**: Segment-by-segment breakdown with confidence scores
- **Visualizations**: Interactive charts and breakdowns for both overall and per-video results
- **Batch Processing**: Analyze multiple videos from a channel simultaneously

## Setup Instructions

### Prerequisites

- Node.js (v14+)
- Python (v3.8+)
- A YouTube Data API key (get one from [Google Cloud Console](https://console.cloud.google.com/apis/credentials))

### Backend Setup

1. Clone the repository:
   ```
   git clone https://github.com/BlakeDanielson/CrowdWork.git
   cd CrowdWork
   ```

2. Set up the backend:
   ```
   cd backend
   python -m venv venv
   venv\Scripts\activate  # On Windows
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the `backend` directory based on `.env.example`:
   ```
   YOUTUBE_API_KEY=your_youtube_api_key_here
   ```

4. Start the backend server:
   ```
   uvicorn main:app --reload
   ```

### Frontend Setup

1. In a separate terminal, navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

4. Open your browser and navigate to `http://localhost:5173`

### Quick Start with PowerShell

For Windows users, you can use the included PowerShell script to start both servers:

```
.\dev.ps1
```

## Project Structure

```
CrowdWork/
├── backend/
│   ├── analyzer.py       # Contains the ComedyAnalyzer class
│   ├── main.py           # FastAPI application and endpoints
│   ├── requirements.txt  # Python dependencies
│   └── youtube_api.py    # YouTube API integration
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── styles/       # CSS styles
│   │   ├── App.jsx       # Main app component
│   │   └── main.jsx      # Entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── dev.ps1               # Development startup script
└── README.md
```

## How It Works

1. **Input**: Enter a YouTube channel URL and select how many videos to analyze
2. **Processing**: The backend fetches channel data, video details, and transcripts
3. **Analysis**: Each transcript segment is analyzed for patterns indicating crowdwork
4. **Results**: View a breakdown of crowdwork vs. prepared material percentages:
   - Overall channel statistics
   - Per-video analysis
   - Detailed segment classification with confidence scores
   - Interactive visualizations

## Development Notes

- The analyzer uses a rule-based approach with regex patterns to identify crowdwork
- Future versions may incorporate machine learning for more accurate classification
- Current analysis focuses on English language transcripts

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open-source software. 