from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import os
import uuid
from dotenv import load_dotenv
import asyncio
import logging
from youtube_api import YouTubeAPI
from analyzer import ComedyAnalyzer

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    max_videos: Optional[int] = 5

class AnalysisStatus(BaseModel):
    task_id: str
    status: str
    progress: float
    result: Optional[Dict[str, Any]] = None

@app.get("/")
async def read_root():
    return {"message": "Welcome to CrowdWork API"}

@app.post("/analyze-channel/", response_model=Dict[str, str])
async def analyze_channel(request: ChannelRequest, background_tasks: BackgroundTasks):
    task_id = f"task_{len(tasks) + 1}"
    
    # Initialize task status
    tasks[task_id] = {
        "status": "queued",
        "progress": 0,
        "result": None
    }
    
    # Add task to background
    background_tasks.add_task(
        process_youtube_channel, 
        task_id=task_id, 
        channel_url=request.channel_url,
        max_videos=request.max_videos
    )
    
    return {"task_id": task_id}

@app.get("/status/{task_id}", response_model=AnalysisStatus)
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task_id,
        **tasks[task_id]
    }

async def process_youtube_channel(task_id: str, channel_url: str, max_videos: int):
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
        # Update task status
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["progress"] = 0
        
        # Step 1: Extract channel ID from URL
        channel_id = YouTubeAPI().extract_channel_id(channel_url)
        if not channel_id:
            raise ValueError(f"Could not extract channel ID from URL: {channel_url}")
        
        # Step 2: Get channel info
        channel_info = YouTubeAPI().get_channel_info(channel_id)
        channel_title = channel_info.get("title", "Unknown Channel")
        
        # Update progress
        tasks[task_id]["progress"] = 10
        
        # Step 3: Get videos from channel
        videos = YouTubeAPI().get_channel_videos(channel_id, max_results=max_videos)
        if not videos:
            raise ValueError(f"No videos found for channel: {channel_title}")
        
        logger.info(f"Found {len(videos)} videos for channel '{channel_title}'")
        
        # Update progress
        tasks[task_id]["progress"] = 20
        
        # Step 4: Filter for stand-up performances
        # In a real implementation, you'd have more sophisticated filtering
        # For now, we'll assume all videos are stand-up performances
        standup_videos = videos[:max_videos]  # Limit to max_videos
        logger.info(f"Filtered to {len(standup_videos)} stand-up videos")
        
        # Update progress
        tasks[task_id]["progress"] = 30
        
        # Step 5: Get transcripts and analyze videos
        total_duration = 0
        crowdwork_duration = 0
        material_duration = 0
        video_results = []
        videos_with_transcripts = 0
        
        progress_per_video = 60 / max(len(standup_videos), 1)  # 60% of progress for processing videos
        
        for i, video in enumerate(standup_videos):
            video_id = video.get("video_id")
            video_title = video.get("title", f"Video {i+1}")
            video_duration = video.get("duration", 0)
            
            # Update progress for each video
            current_progress = 30 + (i * progress_per_video)
            tasks[task_id]["progress"] = current_progress
            
            try:
                # Get video transcript
                transcript = YouTubeAPI().get_video_transcript(video_id, ['en'])
                if not transcript:
                    logger.warning(f"No transcript for video: {video_title}")
                    continue
                
                videos_with_transcripts += 1
                
                # Update progress within video processing
                tasks[task_id]["progress"] = current_progress + (progress_per_video * 0.5)
                
                # Analyze transcript
                analysis_result = ComedyAnalyzer().analyze_transcript(transcript)
                
                # Add video-specific results
                video_result = {
                    "video_id": video_id,
                    "title": video_title,
                    "duration": video_duration,
                    "crowdwork_duration": analysis_result["crowdwork_duration"],
                    "material_duration": analysis_result["material_duration"],
                    "crowdwork_percentage": analysis_result["crowdwork_percentage"],
                    "material_percentage": analysis_result["material_percentage"],
                    "segment_classifications": analysis_result["segment_classifications"]
                }
                
                video_results.append(video_result)
                
                # Accumulate for overall stats
                total_duration += video_duration
                crowdwork_duration += analysis_result["crowdwork_duration"]
                material_duration += analysis_result["material_duration"]
                
                # Update progress after video is processed
                tasks[task_id]["progress"] = current_progress + progress_per_video
                
            except Exception as e:
                logger.error(f"Error processing video {video_title}: {str(e)}")
                continue
        
        # Calculate overall percentages
        if total_duration > 0:
            crowdwork_percentage = (crowdwork_duration / total_duration) * 100
            material_percentage = (material_duration / total_duration) * 100
        else:
            crowdwork_percentage = 0
            material_percentage = 0
        
        # Step 6: Prepare final results
        final_result = {
            "channel_id": channel_id,
            "channel_title": channel_title,
            "videos_analyzed": videos_with_transcripts,
            "total_videos": len(standup_videos),
            "total_duration": total_duration,
            "crowdwork_duration": crowdwork_duration,
            "material_duration": material_duration,
            "crowdwork_percentage": crowdwork_percentage,
            "material_percentage": material_percentage,
            "videos": video_results
        }
        
        # Update task with results
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["result"] = final_result
        
        logger.info(f"Analysis completed for {channel_title}")
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error processing channel: {error_message}")
        
        # Update task with error
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["result"] = {"error": error_message}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 