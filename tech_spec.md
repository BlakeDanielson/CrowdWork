# Technical Specification: Comedian Analysis Web App

## 1. Project Goal

To create a web application that allows users to analyze a comedian's publicly available stand-up videos from specified social media platforms (starting with YouTube) to estimate the percentage of performance time dedicated to crowdwork versus prepared material.

## 2. MVP Scope (YouTube Only)

The initial Minimum Viable Product (MVP) will focus *exclusively* on analyzing videos from a single YouTube channel:

*   User inputs a YouTube channel URL or handle.
*   The application fetches publicly available videos from that channel.
*   Basic filtering is applied to identify likely stand-up comedy performances (based on keywords in title/description).
*   Available YouTube transcripts/captions are retrieved for filtered videos.
*   A rule-based analysis classifies segments of the transcript as "Crowdwork" or "Prepared Material".
*   The application calculates and displays the estimated percentage breakdown for the analyzed videos from that channel.
*   No user accounts or persistent storage of results beyond the current session.

## 3. Core Components

### 3.1. Frontend
*   **Purpose:** User interface for input and results display.
*   **Functionality:**
    *   Input field for YouTube channel URL/handle.
    *   Button to trigger analysis.
    *   Display area for progress/status updates.
    *   Display area for final percentage breakdown.
*   **Technology:** React (using Vite for build tooling).

### 3.2. Backend (API Server)
*   **Purpose:** Handles requests, orchestrates data fetching and analysis, serves results.
*   **Functionality:**
    *   API endpoint to receive analysis requests.
    *   Coordinates calls to Data Acquisition, Filtering, Transcription, and Analysis modules.
    *   Manages background tasks for long-running processes.
    *   API endpoint to serve results.
*   **Technology:** Python (using FastAPI framework).

### 3.3. Data Acquisition Module (MVP: YouTube)
*   **Purpose:** Fetches video metadata and transcripts from YouTube.
*   **Functionality:**
    *   Uses YouTube Data API v3 to find videos associated with a channel.
    *   Retrieves video details (ID, title, description, duration).
    *   Checks for and retrieves available captions/transcripts via the API.
*   **Technology:** Python (`google-api-python-client` library). Requires API key management.

### 3.4. Video Filtering Module
*   **Purpose:** Selects videos likely to be stand-up comedy performances.
*   **Functionality (MVP):**
    *   Filters based on keywords in video titles and descriptions (e.g., "stand up", "live", "comedy club", "special").
    *   Potentially filter by minimum duration (e.g., > 2 minutes).
*   **Technology:** Python logic within the backend.

### 3.5. Transcription Module (MVP: YouTube Priority)
*   **Purpose:** Obtains text transcripts of the videos.
*   **Functionality (MVP):**
    *   Prioritizes retrieving existing transcripts directly from YouTube via the Data API.
    *   *(Potential Fallback/Future)*: Integrate a Speech-to-Text service (like OpenAI Whisper API) if YouTube transcripts are unavailable or insufficient (Requires downloading video/audio streams).
*   **Technology:** Python logic using the YouTube API client.

### 3.6. Analysis Module (MVP: Rule-Based)
*   **Purpose:** Classifies transcript segments.
*   **Functionality (MVP):**
    *   Applies a set of predefined rules to the transcript text.
    *   Looks for patterns indicative of crowdwork (e.g., direct questions to audience: "Where are you from?", "What's your name?", audience member references) versus prepared material (e.g., setup/punchline structure, narrative flow).
    *   Calculates the duration/proportion of text classified under each category.
*   **Technology:** Python logic within the backend.

### 3.7. Results Calculation & Storage (MVP: Session-Based)
*   **Purpose:** Aggregates analysis results and formats for display.
*   **Functionality (MVP):**
    *   Sums up the time/amount classified as crowdwork vs. material across all analyzed videos for a given request.
    *   Calculates the final percentages.
    *   Stores results temporarily to be served back to the frontend for the current request. No long-term storage.
*   **Technology:** Python logic within the backend.

## 4. Technical Stack (MVP Summary)

*   **Frontend:** React (Vite), CSS (or a simple UI library like Mantine/Chakra UI)
*   **Backend:** Python 3.x, FastAPI
*   **API Communication:** RESTful JSON API
*   **YouTube Interaction:** `google-api-python-client`
*   **Background Tasks:** FastAPI `BackgroundTasks` (for initial simplicity)
*   **Deployment (Placeholder):** Frontend (Vercel/Netlify), Backend (Cloud Run/Heroku/Render)

## 5. Data Flow (MVP)

1.  User enters YouTube channel URL in React Frontend.
2.  Frontend sends POST request to Backend API (`/analyze/youtube`) with channel URL.
3.  Backend acknowledges request and starts a background task.
4.  **Background Task:**
    *   **Data Acquisition:** Calls YouTube API to get video list for the channel.
    *   **Filtering:** Filters video list for likely stand-up content.
    *   **Transcription:** For each filtered video, calls YouTube API to get transcripts.
    *   **Analysis:** Processes each transcript using the rule-based classifier.
    *   **Calculation:** Aggregates results across all processed videos.
5.  Backend stores results temporarily (e.g., in memory associated with a task ID).
6.  Frontend polls a results endpoint (`/results/{task_id}`) or uses WebSockets (future) to get status and final results.
7.  Backend serves the calculated percentages when ready.
8.  Frontend displays the results.

## 6. API Endpoints (Initial)

*   `POST /analyze/youtube`:
    *   Request Body: `{ "channel_url": "..." }`
    *   Response: `{ "task_id": "..." }` (Immediately returns an ID for polling)
*   `GET /results/{task_id}`:
    *   Response (Pending): `{ "status": "processing", "progress": 25 }`
    *   Response (Complete): `{ "status": "complete", "results": { "crowdwork_percentage": 15.5, "material_percentage": 84.5 } }`
    *   Response (Error): `{ "status": "error", "message": "..." }`

## 7. Key Challenges & Risks

*   **YouTube API Quotas:** Usage limits may be hit, requiring quota management or requests for increases.
*   **Filtering Accuracy:** Simple keyword filtering might include non-standup videos or exclude relevant ones.
*   **Transcript Availability/Quality:** Not all videos have transcripts; auto-generated ones can have errors affecting analysis.
*   **Analysis Subjectivity:** Defining and programmatically identifying "crowdwork" is inherently subjective and complex. The rule-based approach will have limitations.
*   **Processing Time:** Fetching and analyzing many videos can be slow; requires efficient background processing and clear user feedback.
*   **Scalability:** The MVP architecture might not scale to high traffic or very large channels without optimizations (e.g., more robust task queues like Celery/RQ, database storage).

## 8. Future Enhancements

*   **Improved Analysis:** Implement ML-based classification (requires labeled data).
*   **Other Platforms:** Add support for TikTok and Instagram (significant scraping challenges).
*   **Audio/Video Cues:** Incorporate analysis of audio tone, laughter tracks, or visual elements.
*   **User Accounts:** Allow users to save past results or track comedians.
*   **Database Storage:** Persist results and potentially intermediate data.
*   **More Robust Filtering:** Use ML or more sophisticated heuristics.
*   **Improved UI/UX:** More detailed results, visualizations.
*   **Error Handling:** More granular error reporting.
*   **WebSockets:** Real-time progress updates instead of polling. 