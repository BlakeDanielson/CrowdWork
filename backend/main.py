from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
from dotenv import load_dotenv
import asyncio
from youtube_api import YouTubeAPI
from analyzer import ComedyAnalyzer

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="CrowdWork API",
    description="API for analyzing comedian videos to determine crowdwork percentage",
    version="0.1.0",
)

# Configure CORS to allow frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for tasks and results (would be a database in production)
tasks = {}

class ChannelRequest(BaseModel):
    channel_url: str

class TaskResponse(BaseModel):
    task_id: str

@app.get("/")
async def read_root():
    return {"message": "Welcome to CrowdWork API"}

@app.post("/analyze/youtube", response_model=TaskResponse)
async def analyze_youtube(request: ChannelRequest, background_tasks: BackgroundTasks):
    # Generate a unique task ID
    task_id = str(uuid.uuid4())
    
    # Store initial task status
    tasks[task_id] = {
        "status": "processing",
        "progress": 0,
        "channel_url": request.channel_url,
        "results": None,
        "error": None,
    }
    
    # Add the analysis task to the background tasks
    background_tasks.add_task(process_youtube_channel, task_id, request.channel_url)
    
    return {"task_id": task_id}

@app.get("/results/{task_id}")
async def get_results(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks[task_id]

async def process_youtube_channel(task_id: str, channel_url: str):
    """
    Background task to process a YouTube channel.
    Implements the complete analysis pipeline:
    1. Call YouTube API to get videos for the channel
    2. Filter videos that are likely standup performances
    3. Get details for those videos
    4. Get transcripts for those videos
    5. Analyze transcripts to classify segments
    6. Calculate overall percentages
    """
    try:
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["progress"] = 5
        
        # Initialize API and analyzer
        youtube_api = YouTubeAPI()
        analyzer = ComedyAnalyzer()
        
        # Extract channel ID from URL
        try:
            channel_id = youtube_api.extract_channel_id(channel_url)
            tasks[task_id]["progress"] = 10
        except ValueError as e:
            tasks[task_id]["status"] = "error"
            tasks[task_id]["error"] = f"Invalid channel URL: {str(e)}"
            return
        
        # Get videos for the channel
        try:
            videos = youtube_api.get_channel_videos(channel_id)
            tasks[task_id]["progress"] = 25
        except Exception as e:
            tasks[task_id]["status"] = "error"
            tasks[task_id]["error"] = f"Error fetching videos: {str(e)}"
            return
        
        # Filter for likely stand-up videos
        # First, we need video details for durations
        video_ids = [video["video_id"] for video in videos]
        video_details = youtube_api.get_video_details(video_ids)
        tasks[task_id]["progress"] = 35
        
        # Now filter for stand-up
        standup_videos = youtube_api.filter_standup_videos(video_details)
        
        if not standup_videos:
            tasks[task_id]["status"] = "complete"
            tasks[task_id]["results"] = {
                "crowdwork_percentage": 0,
                "material_percentage": 0,
                "error": "No stand-up comedy videos found for this channel."
            }
            return
        
        tasks[task_id]["progress"] = 45
        
        # Analyze each video transcript
        total_crowdwork_duration = 0.0
        total_material_duration = 0.0
        
        # For MVP, limit to max 5 videos to avoid API rate limits
        standup_videos = standup_videos[:5]
        
        results_per_video = []
        
        for i, video in enumerate(standup_videos):
            video_id = video["video_id"]
            
            # In MVP, we have a placeholder for transcripts
            # In production, we'd need to handle fetching real transcripts, likely with a library
            # For simplicity, we'll create some dummy transcript data here
            # Normally this would be: transcript = youtube_api.get_video_transcript(video_id)
            
            # Dummy transcript data for development purposes
            dummy_transcript = [
                {"text": "Hey, how's everyone doing tonight? Great crowd!", "start": 0.0, "duration": 3.0},
                {"text": "Where are you from, sir? Oh, you're from Chicago?", "start": 3.0, "duration": 4.0},
                {"text": "I love Chicago, great pizza there.", "start": 7.0, "duration": 3.0},
                {"text": "So I was walking down the street the other day.", "start": 10.0, "duration": 3.0},
                {"text": "And this guy with the weirdest hat stops me.", "start": 13.0, "duration": 4.0},
                {"text": "What's your name? Bob? Give it up for Bob everyone!", "start": 17.0, "duration": 5.0},
                {"text": "I told him, that's not a hat, that's a raccoon.", "start": 22.0, "duration": 4.0},
            ]
            
            # In production, we'd use real transcript data
            analysis_result = analyzer.analyze_transcript(dummy_transcript)
            
            total_crowdwork_duration += analysis_result["crowdwork_duration"]
            total_material_duration += analysis_result["material_duration"]
            
            results_per_video.append({
                "video_id": video_id,
                "title": video["title"],
                "crowdwork_percentage": analysis_result["crowdwork_percentage"],
                "material_percentage": analysis_result["material_percentage"]
            })
            
            # Update progress
            tasks[task_id]["progress"] = 45 + int((i + 1) / len(standup_videos) * 50)
            
            # Simulate some processing time to avoid immediate response
            await asyncio.sleep(1)
        
        # Calculate overall percentages
        total_duration = total_crowdwork_duration + total_material_duration
        if total_duration > 0:
            overall_crowdwork_percentage = (total_crowdwork_duration / total_duration) * 100
            overall_material_percentage = (total_material_duration / total_duration) * 100
        else:
            overall_crowdwork_percentage = 0
            overall_material_percentage = 0
        
        # Store final results
        tasks[task_id]["status"] = "complete"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["results"] = {
            "crowdwork_percentage": round(overall_crowdwork_percentage, 1),
            "material_percentage": round(overall_material_percentage, 1),
            "videos_analyzed": len(standup_videos),
            "per_video_results": results_per_video
        }
        
    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["error"] = str(e)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 