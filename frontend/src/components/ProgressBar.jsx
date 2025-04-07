import React from 'react';

function ProgressBar({ progress }) {
  return (
    <div>
      <div className="progress-bar">
        <div 
          className="progress-bar-fill" 
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <div style={{ textAlign: 'center' }}>
        {progress}% Complete
      </div>
    </div>
  );
}

export default ProgressBar; 