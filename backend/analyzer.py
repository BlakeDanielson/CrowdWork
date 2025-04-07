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
            r"\bround of applause\b",
            r"\bput your hands together\b",
            r"\blive here tonight\b",
            r"\bfolks? in the audience\b",
            r"\bwho here\b",
            r"\bhow's? (?:it going|everybody|everyone)\b",
            r"\bhow's? your night\b",
            r"\bshow of hands\b",
            
            # References to specific audience members
            r"\bthis (?:guy|lady|woman|man|person|dude|gentleman|fella)\b",
            r"\byou in the\b",
            r"\byou right there\b",
            r"\byou with the\b",
            r"\bfirst row\b",
            r"\bfront row\b",
            r"\bback row\b",
            r"\bfolks? over there\b",
            
            # Addressing the audience or location
            r"\b(?:this|the) (?:city|town)\b",
            r"\blooks like\b",  # When describing audience member
            r"\bI see a\b",  # When describing audience member
            r"\bI see you\b",
            r"\bI noticed you\b",
            r"\byou guys look\b",
            r"\bI can see that\b",
            r"\bI heard you\b",
            
            # Reactions to audience
            r"\b(?:thanks|thank you) for (?:that|laughing|the)\b",
            r"\bdidn't expect that\b",
            r"\bthat wasn't planned\b",
            r"\bI'm getting distracted\b",
            r"\bthat's? not (?:in|part of) (?:the|my) (?:script|act|show)\b",
            r"\bwhat's happening (?:over|back) there\b",
            r"\byou guys (?:are|seem)\b",
            r"\bthat's? funny\b",
            r"\bI appreciate that\b",
            r"\byeah exactly\b",
            r"\bI heard that\b",
            r"\bsome(?:body|one) said\b",
            r"\bwhat did you say\b",
            r"\bwait, what\?\b",
            r"\bheckl(?:er|ing)\b",
            
            # Local references that might indicate crowdwork
            r"\bhere in\b",
            r"\btonight in\b",
            r"\bthis (?:club|venue|theater|theatre)\b",
        ]
        
        # Patterns that often indicate prepared material
        self.prepared_patterns = [
            # Storytelling phrases
            r"\bonce upon a time\b",
            r"\bback when I was\b",
            r"\bI remember when\b",
            r"\bwhen I was a kid\b",
            r"\bgrowing up\b",
            r"\bmy (?:mom|dad|mother|father|parents|family|wife|husband|girlfriend|boyfriend)\b",
            
            # Common joke structures
            r"\bso I (?:was|went|had)\b", # Setting up a joke
            r"\banyway,?\b", # Transitioning
            r"\bthe thing is\b",
            r"\bthe point is\b",
            r"\bthe moral of the story\b",
            
            # Other prepared material indicators
            r"\bleaving that aside\b",
            r"\bI've been thinking\b",
            r"\bdo you ever notice\b", # Generic "you" rather than specific audience member
            r"\bhave you ever noticed\b",
        ]
        
        # Compile regexes for faster matching
        self.crowdwork_regexes = [re.compile(pattern, re.IGNORECASE) for pattern in self.crowdwork_patterns]
        self.prepared_regexes = [re.compile(pattern, re.IGNORECASE) for pattern in self.prepared_patterns]
        
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
        material_duration = 0.0
        
        # Generate classifications for each segment
        classifications = []
        
        for segment in transcript_segments:
            text = segment.get("text", "")
            duration = segment.get("duration", 1.0)
            start_time = segment.get("start", 0.0)
            
            is_crowdwork, confidence, classification_details = self._classify_segment(text)
            
            total_duration += duration
            if is_crowdwork:
                crowdwork_duration += duration
            else:
                material_duration += duration
            
            classifications.append({
                "text": text,
                "start_time": start_time,
                "duration": duration,
                "is_crowdwork": is_crowdwork,
                "confidence": confidence,
                "matched_patterns": classification_details.get("matched_patterns", [])
            })
        
        # Calculate percentages
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
    
    def _classify_segment(self, text: str) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Classify a text segment as crowdwork or prepared material.
        
        Args:
            text: The transcript text segment
            
        Returns:
            Tuple of (is_crowdwork, confidence, classification_details)
        """
        # Find all matching patterns
        matched_crowdwork_patterns = []
        for i, regex in enumerate(self.crowdwork_regexes):
            match = regex.search(text)
            if match:
                matched_crowdwork_patterns.append({
                    "pattern": self.crowdwork_patterns[i],
                    "matched_text": match.group(0)
                })
        
        matched_prepared_patterns = []
        for i, regex in enumerate(self.prepared_regexes):
            match = regex.search(text)
            if match:
                matched_prepared_patterns.append({
                    "pattern": self.prepared_patterns[i],
                    "matched_text": match.group(0)
                })
        
        # Count matches
        crowdwork_count = len(matched_crowdwork_patterns)
        prepared_count = len(matched_prepared_patterns)
        
        # Decision logic
        if crowdwork_count > 0 and prepared_count == 0:
            # Clear crowdwork indicators and no prepared indicators
            is_crowdwork = True
            confidence = min(0.5 + (crowdwork_count * 0.1), 0.95)
        elif prepared_count > 0 and crowdwork_count == 0:
            # Clear prepared indicators and no crowdwork indicators
            is_crowdwork = False
            confidence = min(0.5 + (prepared_count * 0.1), 0.95)
        elif crowdwork_count > prepared_count:
            # More crowdwork indicators than prepared indicators
            is_crowdwork = True
            confidence = 0.5 + ((crowdwork_count - prepared_count) * 0.08)
            confidence = min(confidence, 0.9) # Cap confidence lower due to mixed signals
        elif prepared_count > crowdwork_count:
            # More prepared indicators than crowdwork indicators
            is_crowdwork = False
            confidence = 0.5 + ((prepared_count - crowdwork_count) * 0.08)
            confidence = min(confidence, 0.9) # Cap confidence lower due to mixed signals
        elif crowdwork_count > 0 and crowdwork_count == prepared_count:
            # Equal indicators - slightly favor crowdwork as it's more distinctive
            is_crowdwork = True
            confidence = 0.55
        else:
            # No clear indicators - default to prepared material
            is_crowdwork = False
            confidence = 0.6
        
        # Prepare detailed results
        classification_details = {
            "matched_patterns": matched_crowdwork_patterns if is_crowdwork else matched_prepared_patterns,
            "crowdwork_pattern_count": crowdwork_count,
            "prepared_pattern_count": prepared_count
        }
        
        return is_crowdwork, confidence, classification_details 