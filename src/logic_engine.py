"""
Logic Engine for Lie-Dar System
================================
Fuses multi-modal stress scores into a unified honesty assessment.

Key Features:
- Weighted score fusion from facial, voice, and pulse modalities
- Configurable weights per modality
- Honesty score calculation (0-100 scale)
- Alert level classification
"""

import numpy as np
from typing import Dict, Tuple
from enum import Enum


class AlertLevel(Enum):
    """Alert levels based on honesty score thresholds."""
    HIGH_STRESS = "high_stress"      # Score < 40 (likely deceptive)
    MEDIUM_STRESS = "medium_stress"  # Score 40-60 (uncertain)
    LOW_STRESS = "low_stress"        # Score > 60 (likely honest)


class LogicEngine:
    """
    Multi-modal fusion engine for lie detection.
    
    Combines stress indicators from:
    - Facial micro-expressions (40% weight)
    - Voice acoustic features (30% weight)
    - Heart rate (pulse) changes (30% weight)
    
    Produces a unified "Honesty Score" from 0-100:
    - 100 = Maximum honesty (no stress indicators)
    - 0 = Maximum deception indicators
    """
    
    def __init__(self, 
                 facial_weight: float = 0.40,
                 voice_weight: float = 0.30,
                 pulse_weight: float = 0.30):
        """
        Initialize the logic engine.
        
        Args:
            facial_weight: Weight for facial analysis (default: 0.40)
            voice_weight: Weight for voice analysis (default: 0.30)
            pulse_weight: Weight for pulse analysis (default: 0.30)
        """
        # Validate weights sum to 1.0
        total_weight = facial_weight + voice_weight + pulse_weight
        assert abs(total_weight - 1.0) < 0.01, "Weights must sum to 1.0"
        
        self.facial_weight = facial_weight
        self.voice_weight = voice_weight
        self.pulse_weight = pulse_weight
        
        # Score history for smoothing
        self.honesty_history = []
        self.max_history = 10
        
    def calculate_honesty_score(self,
                                facial_stress: float,
                                voice_stress: float,
                                pulse_stress: float) -> float:
        """
        Calculate unified honesty score from individual modality scores.
        
        Mathematical Formula:
        combined_stress = (w_f × S_f) + (w_v × S_v) + (w_p × S_p)
        honesty_score = 100 - combined_stress
        
        Where:
        - w_f, w_v, w_p are weights for facial, voice, pulse
        - S_f, S_v, S_p are stress scores for each modality (0-100)
        
        Rationale:
        - Higher stress scores indicate deception
        - Invert to get honesty score (100 = honest, 0 = deceptive)
        - Weighted average gives more importance to facial cues (most reliable)
        
        Args:
            facial_stress: Facial stress score (0-100)
            voice_stress: Voice stress score (0-100)
            pulse_stress: Pulse stress score (0-100)
            
        Returns:
            Honesty score (0-100)
        """
        # Validate inputs
        facial_stress = np.clip(facial_stress, 0, 100)
        voice_stress = np.clip(voice_stress, 0, 100)
        pulse_stress = np.clip(pulse_stress, 0, 100)
        
        # Calculate weighted combined stress
        combined_stress = (
            self.facial_weight * facial_stress +
            self.voice_weight * voice_stress +
            self.pulse_weight * pulse_stress
        )
        
        # Convert stress to honesty (inverse relationship)
        honesty_score = 100.0 - combined_stress
        
        # Add to history for smoothing
        self.honesty_history.append(honesty_score)
        if len(self.honesty_history) > self.max_history:
            self.honesty_history.pop(0)
        
        # Return smoothed score (moving average)
        smoothed_score = np.mean(self.honesty_history)
        
        return smoothed_score
    
    def get_alert_level(self, honesty_score: float) -> AlertLevel:
        """
        Classify alert level based on honesty score.
        
        Thresholds:
        - High Stress (< 40): Strong deception indicators
        - Medium Stress (40-60): Uncertain, mixed signals
        - Low Stress (> 60): Likely honest
        
        Args:
            honesty_score: Honesty score (0-100)
            
        Returns:
            AlertLevel enum
        """
        if honesty_score < 40:
            return AlertLevel.HIGH_STRESS
        elif honesty_score < 60:
            return AlertLevel.MEDIUM_STRESS
        else:
            return AlertLevel.LOW_STRESS
    
    def analyze(self,
               facial_stress: float,
               voice_stress: float,
               pulse_stress: float) -> Dict:
        """
        Perform complete multi-modal analysis.
        
        Args:
            facial_stress: Facial stress score (0-100)
            voice_stress: Voice stress score (0-100)
            pulse_stress: Pulse stress score (0-100)
            
        Returns:
            Dictionary containing:
            - honesty_score: Overall honesty assessment (0-100)
            - alert_level: Classification (HIGH/MEDIUM/LOW_STRESS)
            - component_scores: Individual modality contributions
            - interpretation: Human-readable description
        """
        # Calculate honesty score
        honesty_score = self.calculate_honesty_score(
            facial_stress, voice_stress, pulse_stress
        )
        
        # Determine alert level
        alert_level = self.get_alert_level(honesty_score)
        
        # Calculate component contributions (weighted scores)
        component_scores = {
            "facial_contribution": facial_stress * self.facial_weight,
            "voice_contribution": voice_stress * self.voice_weight,
            "pulse_contribution": pulse_stress * self.pulse_weight,
            "facial_raw": facial_stress,
            "voice_raw": voice_stress,
            "pulse_raw": pulse_stress
        }
        
        # Generate interpretation
        interpretation = self._generate_interpretation(honesty_score, alert_level)
        
        return {
            "honesty_score": honesty_score,
            "alert_level": alert_level.value,
            "component_scores": component_scores,
            "interpretation": interpretation,
            "weights": {
                "facial": self.facial_weight,
                "voice": self.voice_weight,
                "pulse": self.pulse_weight
            }
        }
    
    def _generate_interpretation(self, honesty_score: float, 
                                alert_level: AlertLevel) -> str:
        """
        Generate human-readable interpretation of results.
        
        Args:
            honesty_score: Honesty score
            alert_level: Alert level
            
        Returns:
            Interpretation string
        """
        if alert_level == AlertLevel.HIGH_STRESS:
            return (f"HIGH STRESS DETECTED (Score: {honesty_score:.1f}/100). "
                   "Multiple deception indicators present. Subject may be withholding truth.")
        elif alert_level == AlertLevel.MEDIUM_STRESS:
            return (f"MODERATE STRESS (Score: {honesty_score:.1f}/100). "
                   "Mixed signals detected. Possible nervousness or mild deception.")
        else:
            return (f"LOW STRESS (Score: {honesty_score:.1f}/100). "
                   "Minimal deception indicators. Subject appears truthful.")
    
    def reset(self):
        """Reset score history."""
        self.honesty_history.clear()
    
    def update_weights(self, facial: float = None, 
                      voice: float = None, 
                      pulse: float = None):
        """
        Update modality weights dynamically.
        
        Args:
            facial: New facial weight (optional)
            voice: New voice weight (optional)
            pulse: New pulse weight (optional)
        """
        if facial is not None:
            self.facial_weight = facial
        if voice is not None:
            self.voice_weight = voice
        if pulse is not None:
            self.pulse_weight = pulse
        
        # Normalize to sum to 1.0
        total = self.facial_weight + self.voice_weight + self.pulse_weight
        self.facial_weight /= total
        self.voice_weight /= total
        self.pulse_weight /= total
