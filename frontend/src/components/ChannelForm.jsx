import React, { useState } from 'react';
import '../styles/ChannelForm.css';

const ChannelForm = ({ onAnalysisStart, onProgress, onAnalysisComplete, onError }) => {
  const [channelUrl, setChannelUrl] = useState('');
  const [maxVideos, setMaxVideos] = useState(5);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationError, setValidationError] = useState('');
  
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  
  const validateChannelUrl = (url) => {
    // Basic validation for YouTube channel URL
    const youtubeChannelPattern = /youtube\.com\/(channel|c|user|@)/;
    return youtubeChannelPattern.test(url);
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setValidationError('');
    
    if (!channelUrl.trim()) {
      setValidationError('Please enter a YouTube channel URL');
      return;
    }
    
    if (!validateChannelUrl(channelUrl)) {
      setValidationError('Please enter a valid YouTube channel URL');
      return;
    }
    
    try {
      setIsSubmitting(true);
      onAnalysisStart();
      
      // Submit request to API
      const response = await fetch(`${API_URL}/analyze-channel/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          channel_url: channelUrl,
          max_videos: maxVideos
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to start analysis');
      }
      
      const data = await response.json();
      const taskId = data.task_id;
      
      // Poll for results
      await pollForResults(taskId);
      
    } catch (error) {
      console.error('Error submitting form:', error);
      onError(error.message);
      setIsSubmitting(false);
    }
  };
  
  const pollForResults = async (taskId) => {
    const pollInterval = 2000; // Poll every 2 seconds
    let timeoutId;
    
    const checkStatus = async () => {
      try {
        const response = await fetch(`${API_URL}/status/${taskId}`);
        
        if (!response.ok) {
          throw new Error('Failed to get analysis status');
        }
        
        const data = await response.json();
        
        // Update progress
        onProgress(data.progress);
        
        if (data.status === 'completed') {
          setIsSubmitting(false);
          onAnalysisComplete(data.result);
          return;
        } else if (data.status === 'failed') {
          throw new Error(data.result?.error || 'Analysis failed');
        }
        
        // Continue polling
        timeoutId = setTimeout(checkStatus, pollInterval);
      } catch (error) {
        console.error('Error polling for results:', error);
        onError(error.message);
        setIsSubmitting(false);
        clearTimeout(timeoutId);
      }
    };
    
    // Start polling
    await checkStatus();
  };
  
  return (
    <div className="channel-form-container">
      <h2>Analyze Comedy Stand-up Videos</h2>
      <form onSubmit={handleSubmit} className="channel-form">
        <div className="form-group">
          <label htmlFor="channelUrl">YouTube Channel URL</label>
          <input
            type="text"
            id="channelUrl"
            placeholder="https://www.youtube.com/channel/..."
            value={channelUrl}
            onChange={(e) => setChannelUrl(e.target.value)}
            disabled={isSubmitting}
            className={validationError ? 'error' : ''}
          />
          {validationError && <p className="error-message">{validationError}</p>}
        </div>
        
        <div className="form-group">
          <label htmlFor="maxVideos">Maximum Videos to Analyze</label>
          <select
            id="maxVideos"
            value={maxVideos}
            onChange={(e) => setMaxVideos(Number(e.target.value))}
            disabled={isSubmitting}
          >
            <option value="1">1 video</option>
            <option value="3">3 videos</option>
            <option value="5">5 videos</option>
            <option value="10">10 videos</option>
            <option value="20">20 videos (may take longer)</option>
          </select>
        </div>
        
        <button 
          type="submit" 
          className="submit-button" 
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Analyzing...' : 'Analyze Channel'}
        </button>
      </form>
      
      {isSubmitting && (
        <p className="info-message">
          Analysis in progress. This may take a few minutes depending on the number of videos.
        </p>
      )}
    </div>
  );
};

export default ChannelForm; 