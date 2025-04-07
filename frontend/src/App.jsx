import React, { useState } from 'react';
import ChannelForm from './components/ChannelForm';
import ProgressBar from './components/ProgressBar';
import Results from './components/Results';
import './App.css';

function App() {
  const [analysisInProgress, setAnalysisInProgress] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalysisStart = () => {
    // Reset state when analysis starts
    setAnalysisInProgress(true);
    setProgress(0);
    setResults(null);
    setError(null);
  };

  const handleProgress = (newProgress) => {
    setProgress(newProgress);
  };

  const handleAnalysisComplete = (data) => {
    setAnalysisInProgress(false);
    setProgress(100);
    setResults(data);
  };

  const handleError = (errorMessage) => {
    setAnalysisInProgress(false);
    setError(errorMessage);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>CrowdWork</h1>
        <p className="app-tagline">
          Analyze how much of a comedian's stand-up is crowdwork vs. prepared material
        </p>
      </header>

      <main className="app-main">
        <ChannelForm 
          onAnalysisStart={handleAnalysisStart}
          onProgress={handleProgress}
          onAnalysisComplete={handleAnalysisComplete}
          onError={handleError}
        />

        {analysisInProgress && (
          <div className="analysis-status">
            <h3>Analyzing Channel</h3>
            <ProgressBar progress={progress} />
            <p className="progress-text">Progress: {Math.round(progress)}%</p>
          </div>
        )}

        {error && (
          <div className="error-container">
            <h3>Error</h3>
            <p className="error-message">{error}</p>
          </div>
        )}

        {results && <Results results={results} />}
      </main>

      <footer className="app-footer">
        <p>
          CrowdWork - Understanding Comedy Performance Analytics
        </p>
      </footer>
    </div>
  );
}

export default App; 