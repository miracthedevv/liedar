"""
Visualization Module for Lie-Dar System
========================================
Real-time UI for displaying lie detection results.

Key Features:
- Live video feed with facial landmark overlay
- Honesty score bar chart (color-coded)
- Individual modality stress indicators
- BPM counter and metrics display
- Alert status visualization
"""

import cv2
import numpy as np
from typing import Dict, Optional


class Visualizer:
    """
    Handles real-time visualization of lie detection results.
    
    Displays:
    - Video feed with facial landmarks
    - Honesty score bar (green/yellow/red gradient)
    - Individual stress scores (facial, voice, pulse)
    - BPM and alert status
    """
    
    def __init__(self, window_name: str = "Lie-Dar - Real-Time Lie Detection"):
        """
        Initialize the visualizer.
        
        Args:
            window_name: Name of the display window
        """
        self.window_name = window_name
        
        # Color definitions (BGR format)
        self.COLOR_GREEN = (0, 255, 0)       # High honesty
        self.COLOR_YELLOW = (0, 255, 255)    # Medium
        self.COLOR_RED = (0, 0, 255)         # Low honesty (high stress)
        self.COLOR_WHITE = (255, 255, 255)
        self.COLOR_BLACK = (0, 0, 0)
        self.COLOR_GRAY = (128, 128, 128)
        
        # UI layout parameters
        self.info_panel_height = 250
        self.bar_height = 40
        self.margin = 20
        
    def _get_color_for_score(self, score: float) -> tuple:
        """
        Get color based on honesty score.
        
        Color gradient:
        - 0-40: Red (high stress)
        - 40-60: Yellow (medium stress)
        - 60-100: Green (low stress)
        
        Args:
            score: Honesty score (0-100)
            
        Returns:
            BGR color tuple
        """
        if score < 40:
            # Red zone
            return self.COLOR_RED
        elif score < 60:
            # Yellow zone (interpolate between red and yellow)
            ratio = (score - 40) / 20
            return (
                0,
                int(255 * ratio),
                int(255 * (1 - ratio))
            )
        else:
            # Green zone (interpolate between yellow and green)
            ratio = (score - 60) / 40
            return (
                0,
                255,
                int(255 * (1 - ratio))
            )
    
    def _draw_bar(self, img: np.ndarray, x: int, y: int, 
                 width: int, height: int, 
                 value: float, max_value: float,
                 label: str, color: tuple):
        """
        Draw a horizontal bar chart.
        
        Args:
            img: Image to draw on
            x, y: Top-left corner position
            width, height: Bar dimensions
            value: Current value
            max_value: Maximum value (for normalization)
            label: Text label
            color: Bar color (BGR)
        """
        # Draw background
        cv2.rectangle(img, (x, y), (x + width, y + height), 
                     self.COLOR_GRAY, 2)
        
        # Draw filled portion
        fill_width = int((value / max_value) * width)
        cv2.rectangle(img, (x, y), (x + fill_width, y + height), 
                     color, -1)
        
        # Draw label and value
        label_text = f"{label}: {value:.1f}/{max_value:.0f}"
        cv2.putText(img, label_text, (x, y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.COLOR_WHITE, 2)
    
    def _draw_metric(self, img: np.ndarray, x: int, y: int,
                    label: str, value: str, color: tuple):
        """
        Draw a text metric.
        
        Args:
            img: Image to draw on
            x, y: Text position
            label: Metric label
            value: Metric value
            color: Text color
        """
        text = f"{label}: {value}"
        cv2.putText(img, text, (x, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    def render_frame(self,
                    video_frame: np.ndarray,
                    honesty_score: float,
                    component_scores: Dict,
                    bpm: float,
                    alert_level: str,
                    facial_metrics: Optional[Dict] = None,
                    voice_metrics: Optional[Dict] = None) -> np.ndarray:
        """
        Render complete visualization frame.
        
        Args:
            video_frame: Video frame (possibly with landmarks)
            honesty_score: Overall honesty score (0-100)
            component_scores: Individual modality scores
            bpm: Current heart rate
            alert_level: Alert status string
            facial_metrics: Optional facial analysis metrics
            voice_metrics: Optional voice analysis metrics
            
        Returns:
            Combined visualization frame
        """
        frame_height, frame_width = video_frame.shape[:2]
        
        # Create extended canvas for info panel
        canvas_height = frame_height + self.info_panel_height
        canvas = np.zeros((canvas_height, frame_width, 3), dtype=np.uint8)
        
        # Place video frame on top
        canvas[0:frame_height, 0:frame_width] = video_frame
        
        # Info panel background (dark gray)
        cv2.rectangle(canvas, 
                     (0, frame_height), 
                     (frame_width, canvas_height),
                     (40, 40, 40), -1)
        
        # Calculate positions for UI elements
        panel_y = frame_height + self.margin
        
        # 1. Main Honesty Score Bar
        bar_width = frame_width - 2 * self.margin
        honesty_color = self._get_color_for_score(honesty_score)
        
        self._draw_bar(
            canvas,
            self.margin,
            panel_y,
            bar_width,
            self.bar_height,
            honesty_score,
            100.0,
            "HONESTY SCORE",
            honesty_color
        )
        
        panel_y += self.bar_height + 30
        
        # 2. Individual Component Scores
        component_bar_width = (frame_width - 4 * self.margin) // 3
        component_bar_height = 25
        
        # Facial stress
        facial_stress = component_scores.get("facial_raw", 0)
        self._draw_bar(
            canvas,
            self.margin,
            panel_y,
            component_bar_width,
            component_bar_height,
            facial_stress,
            100.0,
            "Facial",
            (255, 100, 0)  # Blue-ish
        )
        
        # Voice stress
        voice_stress = component_scores.get("voice_raw", 0)
        self._draw_bar(
            canvas,
            self.margin * 2 + component_bar_width,
            panel_y,
            component_bar_width,
            component_bar_height,
            voice_stress,
            100.0,
            "Voice",
            (0, 165, 255)  # Orange
        )
        
        # Pulse stress
        pulse_stress = component_scores.get("pulse_raw", 0)
        self._draw_bar(
            canvas,
            self.margin * 3 + component_bar_width * 2,
            panel_y,
            component_bar_width,
            component_bar_height,
            pulse_stress,
            100.0,
            "Pulse",
            (147, 20, 255)  # Pink
        )
        
        panel_y += component_bar_height + 30
        
        # 3. BPM and Alert Status
        col1_x = self.margin
        col2_x = frame_width // 2
        
        # BPM indicator
        bpm_color = self.COLOR_GREEN if 60 <= bpm <= 90 else self.COLOR_YELLOW
        self._draw_metric(canvas, col1_x, panel_y, 
                         "BPM", f"{bpm:.0f}", bpm_color)
        
        # Alert level
        alert_color = {
            "high_stress": self.COLOR_RED,
            "medium_stress": self.COLOR_YELLOW,
            "low_stress": self.COLOR_GREEN
        }.get(alert_level, self.COLOR_WHITE)
        
        self._draw_metric(canvas, col2_x, panel_y,
                         "Alert", alert_level.upper().replace("_", " "),
                         alert_color)
        
        panel_y += 40
        
        # 4. Additional Metrics (if available)
        if facial_metrics:
            blink_rate = facial_metrics.get("blink_rate", 0)
            self._draw_metric(canvas, col1_x, panel_y,
                            "Blink Rate", f"{blink_rate:.1f}/min",
                            self.COLOR_WHITE)
        
        if voice_metrics and voice_metrics.get("jitter", 0) > 0:
            jitter = voice_metrics.get("jitter", 0)
            self._draw_metric(canvas, col2_x, panel_y,
                            "Voice Jitter", f"{jitter:.2f}%",
                            self.COLOR_WHITE)
        
        # Add header text
        header_text = "LIE-DAR: Real-Time Deception Detection System"
        cv2.putText(canvas, header_text, (self.margin, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.COLOR_WHITE, 2)
        
        # Add instruction text
        instruction = "Press 'Q' to quit | 'R' to reset"
        cv2.putText(canvas, instruction, (self.margin, frame_height - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_WHITE, 1)
        
        return canvas
    
    def show(self, frame: np.ndarray) -> int:
        """
        Display frame and handle keyboard input.
        
        Args:
            frame: Frame to display
            
        Returns:
            Key code pressed (or -1 if no key)
        """
        cv2.imshow(self.window_name, frame)
        return cv2.waitKey(1) & 0xFF
    
    def close(self):
        """Close visualization window."""
        cv2.destroyAllWindows()
