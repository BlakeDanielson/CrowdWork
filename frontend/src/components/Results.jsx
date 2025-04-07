import React, { useState } from 'react';
import '../styles/Results.css';

// Helper function to format timestamps
const formatTime = (seconds) => {
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
};

const Results = ({ results }) => {
  const [activeTab, setActiveTab] = useState('summary');
  const [expandedSegments, setExpandedSegments] = useState({});

  if (!results || Object.keys(results).length === 0) {
    return null;
  }

  const {
    channel_title,
    videos_analyzed,
    total_videos,
    total_duration,
    crowdwork_duration,
    material_duration,
    crowdwork_percentage,
    material_percentage,
    videos = []
  } = results;

  const toggleSegmentExpand = (videoId, segmentIndex) => {
    const key = `${videoId}-${segmentIndex}`;
    setExpandedSegments(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const renderSummary = () => (
    <div className="summary-container">
      <div className="summary-header">
        <h3>Analysis Summary for {channel_title}</h3>
        <p className="videos-count">
          {videos_analyzed} of {total_videos} videos analyzed
        </p>
      </div>

      <div className="summary-stats">
        <div className="stat-card">
          <h4>Total Duration</h4>
          <p className="stat-value">{formatTime(total_duration)}</p>
        </div>
        <div className="stat-card">
          <h4>Crowdwork</h4>
          <p className="stat-value">{crowdwork_percentage.toFixed(1)}%</p>
          <p className="stat-subvalue">{formatTime(crowdwork_duration)}</p>
        </div>
        <div className="stat-card">
          <h4>Material</h4>
          <p className="stat-value">{material_percentage.toFixed(1)}%</p>
          <p className="stat-subvalue">{formatTime(material_duration)}</p>
        </div>
      </div>

      <div className="visualization-container">
        <div className="percentage-bar">
          <div 
            className="crowdwork-bar" 
            style={{ width: `${crowdwork_percentage}%` }}
            title={`Crowdwork: ${crowdwork_percentage.toFixed(1)}%`}
          >
            {crowdwork_percentage > 8 ? `${crowdwork_percentage.toFixed(1)}%` : ''}
          </div>
          <div 
            className="material-bar" 
            style={{ width: `${material_percentage}%` }}
            title={`Material: ${material_percentage.toFixed(1)}%`}
          >
            {material_percentage > 8 ? `${material_percentage.toFixed(1)}%` : ''}
          </div>
        </div>
        <div className="bar-labels">
          <span>Crowdwork</span>
          <span>Material</span>
        </div>
      </div>
    </div>
  );

  const renderVideoDetails = () => (
    <div className="videos-details">
      <h3>Analyzed Videos ({videos.length})</h3>
      
      {videos.map((video, videoIndex) => (
        <div key={videoIndex} className="video-card">
          <div className="video-header">
            <h4>{video.title}</h4>
            <a href={`https://www.youtube.com/watch?v=${video.video_id}`} target="_blank" rel="noopener noreferrer" className="video-link">
              Watch Video
            </a>
          </div>
          
          <div className="video-stats">
            <div className="video-stats-item">
              <span>Duration:</span> {formatTime(video.duration)}
            </div>
            <div className="video-stats-item">
              <span>Crowdwork:</span> {video.crowdwork_percentage.toFixed(1)}% ({formatTime(video.crowdwork_duration)})
            </div>
            <div className="video-stats-item">
              <span>Material:</span> {video.material_percentage.toFixed(1)}% ({formatTime(video.material_duration)})
            </div>
          </div>

          <div className="video-visualization">
            <div className="percentage-bar">
              <div 
                className="crowdwork-bar" 
                style={{ width: `${video.crowdwork_percentage}%` }}
                title={`Crowdwork: ${video.crowdwork_percentage.toFixed(1)}%`}
              ></div>
              <div 
                className="material-bar" 
                style={{ width: `${video.material_percentage}%` }}
                title={`Material: ${video.material_percentage.toFixed(1)}%`}
              ></div>
            </div>
          </div>

          {video.segment_classifications && video.segment_classifications.length > 0 && (
            <div className="segments-container">
              <h5 className="segments-header">
                Transcript Segments ({video.segment_classifications.length})
              </h5>
              <div className="segments-list">
                {video.segment_classifications.map((segment, segmentIndex) => {
                  const isExpanded = expandedSegments[`${video.video_id}-${segmentIndex}`];
                  const segmentType = segment.is_crowdwork ? 'crowdwork' : 'material';
                  const confidence = Math.round(segment.confidence * 100);
                  
                  return (
                    <div 
                      key={segmentIndex} 
                      className={`segment-item ${segmentType}`}
                      onClick={() => toggleSegmentExpand(video.video_id, segmentIndex)}
                    >
                      <div className="segment-header">
                        <div className="segment-time">
                          {formatTime(segment.start_time)} ({formatTime(segment.duration)})
                        </div>
                        <div className={`segment-type ${segmentType}`}>
                          {segment.is_crowdwork ? 'Crowdwork' : 'Material'} ({confidence}%)
                        </div>
                        <div className="segment-expand">
                          {isExpanded ? '▼' : '►'}
                        </div>
                      </div>
                      
                      {isExpanded && (
                        <div className="segment-details">
                          <div className="segment-text">{segment.text}</div>
                          
                          {segment.matched_patterns && segment.matched_patterns.length > 0 && (
                            <div className="matched-patterns">
                              <h6>Matched Patterns:</h6>
                              <ul>
                                {segment.matched_patterns.map((match, matchIndex) => (
                                  <li key={matchIndex}>
                                    <span className="matched-text">{match.matched_text}</span>
                                    <span className="pattern-info">({match.pattern})</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );

  return (
    <div className="results-container">
      <h2 className="results-title">Analysis Results</h2>
      
      <div className="results-tabs">
        <button 
          className={`tab-button ${activeTab === 'summary' ? 'active' : ''}`}
          onClick={() => setActiveTab('summary')}
        >
          Summary
        </button>
        <button 
          className={`tab-button ${activeTab === 'videos' ? 'active' : ''}`}
          onClick={() => setActiveTab('videos')}
        >
          Videos ({videos.length})
        </button>
      </div>
      
      <div className="tab-content">
        {activeTab === 'summary' ? renderSummary() : renderVideoDetails()}
      </div>
    </div>
  );
};

export default Results; 