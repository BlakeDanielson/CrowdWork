import React, { useState } from 'react';
import ChannelForm from './components/ChannelForm';
import ProgressBar from './components/ProgressBar';
import Results from './components/Results';

function App() {
  const [taskId, setTaskId] = useState(null);
  const [status, setStatus] = useState(null); // null, 'processing', 'complete', 'error'
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (channelUrl) => {
    try {
      setStatus('processing');
      setProgress(0);
      setResults(null);
      setError(null);

      // Submit channel for analysis
      const response = await fetch('/api/analyze/youtube', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ channel_url: channelUrl }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit channel for analysis');
      }

      const data = await response.json();
      setTaskId(data.task_id);

      // Start polling for results
      pollResults(data.task_id);
    } catch (err) {
      setStatus('error');
      setError(err.message);
    }
  };

  const pollResults = async (taskId) => {
    try {
      const response = await fetch(`/api/results/${taskId}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch results');
      }
      
      const data = await response.json();
      
      // Update progress
      setProgress(data.progress || 0);
      
      // Update status
      if (data.status === 'error') {
        setStatus('error');
        setError(data.error || 'An unknown error occurred');
        return;
      }
      
      if (data.status === 'complete') {
        setStatus('complete');
        setResults(data.results);
        return;
      }
      
      // Continue polling
      setTimeout(() => pollResults(taskId), 1000);
    } catch (err) {
      setStatus('error');
      setError(err.message);
    }
  };

  const resetAnalysis = () => {
    setTaskId(null);
    setStatus(null);
    setProgress(0);
    setResults(null);
    setError(null);
  };

  return (
    <div className="container">
      <header>
        <h1>CrowdWork</h1>
        <p>Analyze a comedian's YouTube videos to determine the percentage of crowdwork vs. prepared material.</p>
      </header>

      <main>
        {!status && (
          <section className="section">
            <div className="card">
              <ChannelForm onSubmit={handleSubmit} />
            </div>
          </section>
        )}

        {status === 'processing' && (
          <section className="section">
            <div className="card">
              <h2>Analyzing Channel</h2>
              <ProgressBar progress={progress} />
              <p>Please wait while we analyze the channel. This may take a few minutes.</p>
            </div>
          </section>
        )}

        {status === 'complete' && results && (
          <section className="section">
            <div className="card">
              <h2>Analysis Results</h2>
              <Results results={results} />
              <button onClick={resetAnalysis}>Analyze Another Channel</button>
            </div>
          </section>
        )}

        {status === 'error' && (
          <section className="section">
            <div className="card">
              <h2>Error</h2>
              <p className="error">{error}</p>
              <button onClick={resetAnalysis}>Try Again</button>
            </div>
          </section>
        )}
      </main>

      <footer>
        <p>© {new Date().getFullYear()} CrowdWork - Analyze comedians' videos</p>
      </footer>
    </div>
  );
}

export default App; 