import React from 'react';

function Results({ results }) {
  if (!results) {
    return <p>No results available.</p>;
  }

  if (results.error) {
    return <p className="error">{results.error}</p>;
  }

  return (
    <div>
      <div className="results">
        <div className="result-item">
          <div className="percentage crowdwork">
            {results.crowdwork_percentage}%
          </div>
          <div className="label">Crowdwork</div>
        </div>
        
        <div className="result-item">
          <div className="percentage material">
            {results.material_percentage}%
          </div>
          <div className="label">Prepared Material</div>
        </div>
      </div>
      
      {results.videos_analyzed > 0 && (
        <div className="section">
          <h3>Videos Analyzed: {results.videos_analyzed}</h3>
          
          {results.per_video_results && results.per_video_results.length > 0 && (
            <div className="card">
              <h4>Breakdown by Video</h4>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={tableHeaderStyle}>Video</th>
                    <th style={tableHeaderStyle}>Crowdwork</th>
                    <th style={tableHeaderStyle}>Material</th>
                  </tr>
                </thead>
                <tbody>
                  {results.per_video_results.map((video, index) => (
                    <tr key={index}>
                      <td style={tableCellStyle}>
                        <a 
                          href={`https://www.youtube.com/watch?v=${video.video_id}`}
                          target="_blank" 
                          rel="noopener noreferrer"
                          style={{ color: 'var(--secondary-color)' }}
                        >
                          {video.title}
                        </a>
                      </td>
                      <td style={tableCellStyle}>
                        {video.crowdwork_percentage.toFixed(1)}%
                      </td>
                      <td style={tableCellStyle}>
                        {video.material_percentage.toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
      
      <div style={{ marginTop: '1.5rem', fontSize: '0.9rem', color: '#666' }}>
        <p><strong>Note:</strong> This analysis is based on automatic detection of audience interactions and may not be 100% accurate.</p>
      </div>
    </div>
  );
}

const tableHeaderStyle = {
  textAlign: 'left',
  padding: '8px',
  borderBottom: '1px solid #ddd',
  backgroundColor: 'var(--light-gray)',
};

const tableCellStyle = {
  padding: '8px',
  borderBottom: '1px solid #ddd',
};

export default Results; 