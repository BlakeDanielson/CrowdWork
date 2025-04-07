from typing import List, Dict, Any, Tuple
import re

class ComedyAnalyzer:
    """
    Analyzer for classifying comedy transcript segments as crowdwork or prepared material.
    
    This MVP uses a rule-based approach to classify text. Future versions may use ML.
    """
    
    def __init__(self):
        # Crowdwork indicators: patterns that suggest interaction with the audience
        self.crowdwork_patterns = [
            # Direct questions to audience members
            r"\bwhere (?:are|is|you) .+ from\b",
            r"\bwhat(?:'s| is) your name\b",
            r"\bwhat do you do\b",
            r"\bhow old are you\b",
            r"\bwhat brings you\b",
            r"\banyone (?:here|from)\b", 
            r"\bwho(?:'s| is) (?:here|from)\b",
            r"\bhow many (?:of you|people|folks)\b",
            r"\bhow are you doing\b",
            r"\bguys in the (?:front|back)\b",
            r"\bgive it up for\b",
            
            # References to specific audience members
            r"\bthis (?:guy|lady|woman|man|person)\b",
            r"\byou in the\b",
            r"\byou right there\b",
            r"\byou with the\b",
            
            # Addressing the audience or location
            r"\b(city|town) name\b",  # Often replaced with actual city
            r"\blooks like\b",  # When describing audience member
            r"\bI see a\b",  # When describing audience member
            
            # Reactions to audience
            r"\b(?:thanks|thank you) for (?:that|laughing|the)\b",
            r"\bdidn't expect that\b",
            r"\bthat wasn't planned\b",
            r"\bI'm getting distracted\b",
            r"\bthat's? not (?:in|part of) (?:the|my) (?:script|act|show)\b",
            r"\bwhat's happening (?:over|back) there\b",
            r"\byou guys (?:are|seem)\b"
        ]
        
        # Compile regexes for faster matching
        self.crowdwork_regexes = [re.compile(pattern, re.IGNORECASE) for pattern in self.crowdwork_patterns]
        
    def analyze_transcript(self, transcript_segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze a transcript to determine crowdwork vs. prepared material.
        
        Args:
            transcript_segments: List of transcript segments with text, start time, and duration
            
        Returns:
            Dictionary with analysis results including classifications and percentages
        """
        total_duration = 0.0
        crowdwork_duration = 0.0
        
        # Generate classifications for each segment
        classifications = []
        
        for segment in transcript_segments:
            text = segment.get("text", "")
            duration = segment.get("duration", 1.0)
            start_time = segment.get("start", 0.0)
            
            is_crowdwork, confidence = self._classify_segment(text)
            
            total_duration += duration
            if is_crowdwork:
                crowdwork_duration += duration
            
            classifications.append({
                "text": text,
                "start_time": start_time,
                "duration": duration,
                "is_crowdwork": is_crowdwork,
                "confidence": confidence
            })
        
        # Calculate percentages
        material_duration = total_duration - crowdwork_duration
        
        if total_duration > 0:
            crowdwork_percentage = (crowdwork_duration / total_duration) * 100
            material_percentage = (material_duration / total_duration) * 100
        else:
            crowdwork_percentage = 0
            material_percentage = 0
        
        return {
            "total_duration": total_duration,
            "crowdwork_duration": crowdwork_duration,
            "material_duration": material_duration,
            "crowdwork_percentage": crowdwork_percentage,
            "material_percentage": material_percentage,
            "segment_classifications": classifications
        }
    
    def _classify_segment(self, text: str) -> Tuple[bool, float]:
        """
        Classify a text segment as crowdwork or prepared material.
        
        Args:
            text: The transcript text segment
            
        Returns:
            Tuple of (is_crowdwork, confidence)
        """
        # Count how many crowdwork patterns match
        match_count = sum(1 for regex in self.crowdwork_regexes if regex.search(text))
        
        # Simple heuristic: if any pattern matches, consider it crowdwork
        # Future: could use a more sophisticated approach with weighted patterns
        is_crowdwork = match_count > 0
        
        # Confidence is simplistic in this rule-based approach
        # More matches = higher confidence (capped at 0.95)
        confidence = min(0.5 + (match_count * 0.15), 0.95) if is_crowdwork else 0.75
        
        return is_crowdwork, confidence 