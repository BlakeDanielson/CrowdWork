import React, { useState } from 'react';

function ChannelForm({ onSubmit }) {
  const [channelUrl, setChannelUrl] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [inputError, setInputError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Basic validation
    if (!channelUrl.trim()) {
      setInputError('Please enter a YouTube channel URL or handle');
      return;
    }
    
    // Check if it's a YouTube URL or handle
    if (!isValidYouTubeInput(channelUrl)) {
      setInputError('Please enter a valid YouTube channel URL or handle (e.g., https://www.youtube.com/c/ChannelName or @ChannelHandle)');
      return;
    }
    
    setInputError('');
    setIsSubmitting(true);
    
    try {
      await onSubmit(channelUrl);
    } catch (error) {
      console.error('Error submitting form:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const isValidYouTubeInput = (input) => {
    // This is a basic validation - the backend will handle more complex parsing
    const youtubeUrlPattern = /youtube\.com|youtu\.be/i;
    const handlePattern = /^@[\w.-]+$/;
    
    return (
      youtubeUrlPattern.test(input) || // URL containing youtube.com or youtu.be
      handlePattern.test(input) || // @handle format
      input.startsWith('UC') // Channel ID format starting with UC
    );
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Enter YouTube Channel</h2>
      <p>
        Input a YouTube channel URL, handle, or ID to analyze their stand-up comedy videos.
      </p>
      
      <div>
        <label htmlFor="channelUrl">YouTube Channel URL or Handle:</label>
        <input
          type="text"
          id="channelUrl"
          value={channelUrl}
          onChange={(e) => setChannelUrl(e.target.value)}
          placeholder="https://www.youtube.com/c/ChannelName or @ChannelHandle"
          disabled={isSubmitting}
        />
        {inputError && <p className="error">{inputError}</p>}
      </div>
      
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Analyze Channel'}
      </button>
      
      <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#666' }}>
        <p>Examples:</p>
        <ul style={{ marginLeft: '1.5rem' }}>
          <li>https://www.youtube.com/c/ComedianName</li>
          <li>https://www.youtube.com/channel/UC1234567890abcdefghij</li>
          <li>@ComedianHandle</li>
        </ul>
      </div>
    </form>
  );
}

export default ChannelForm; 