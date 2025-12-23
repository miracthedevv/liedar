"""
Facial Analysis Module for Lie-Dar System
==========================================
Tracks 468 facial landmarks using MediaPipe and detects micro-expressions
that may indicate stress or deception.

Key Features:
- Eyebrow movement analysis (vertical distance changes)
- Lip movement tracking (corner and center variations)
- Blink rate detection and anomaly identification
- Statistical anomaly scoring using rolling window baseline
"""

import cv2
import numpy as np
import mediapipe as mp
from collections import deque
from typing import List, Tuple, Optional


class FacialAnalysis:
    """
    Analyzes facial micro-expressions to detect potential stress indicators.
    
    Uses MediaPipe Face Mesh to track 468 landmarks and computes stress scores
    based on eyebrow movements, lip variations, and blink frequency.
    """
    
    def __init__(self, window_size: int = 30, sensitivity: float = 2.0):
        """
        Initialize the facial analysis system.
        
        Args:
            window_size: Number of frames for rolling baseline calculation (default: 30)
            sensitivity: Standard deviation multiplier for anomaly detection (default: 2.0)
        """
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=False,  # Changed to False to avoid MediaPipe bug
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Statistical parameters
        self.window_size = window_size
        self.sensitivity = sensitivity
        
        # Rolling windows for baseline calculation
        self.eyebrow_distances = deque(maxlen=window_size)
        self.lip_distances = deque(maxlen=window_size)
        self.blink_history = deque(maxlen=60)  # Track blinks over 60 frames (~2 seconds at 30fps)
        
        # Landmark indices for key facial regions
        # Eyebrow landmarks (left and right)
        self.LEFT_EYEBROW = [70, 63, 105, 66, 107]
        self.RIGHT_EYEBROW = [336, 296, 334, 293, 300]
        
        # Eye landmarks for blink detection
        self.LEFT_EYE_UPPER = [159, 145]
        self.LEFT_EYE_LOWER = [23, 145]
        self.RIGHT_EYE_UPPER = [386, 374]
        self.RIGHT_EYE_LOWER = [253, 374]
        
        # Lip landmarks
        self.LIP_UPPER = [13]  # Center upper lip
        self.LIP_LOWER = [14]  # Center lower lip
        self.LIP_LEFT_CORNER = [61]
        self.LIP_RIGHT_CORNER = [291]
        
        # State tracking
        self.frame_count = 0
        self.last_blink_state = False
        self.blink_count = 0
        
    def _euclidean_distance(self, point1: np.ndarray, point2: np.ndarray) -> float:
        """Calculate Euclidean distance between two points."""
        return np.linalg.norm(point1 - point2)
    
    def _get_landmark_coords(self, landmarks, indices: List[int], 
                            img_width: int, img_height: int) -> np.ndarray:
        """
        Extract coordinates for specified landmark indices.
        
        Args:
            landmarks: MediaPipe landmark results
            indices: List of landmark indices to extract
            img_width: Image width for denormalization
            img_height: Image height for denormalization
            
        Returns:
            Array of (x, y) coordinates
        """
        coords = []
        for idx in indices:
            lm = landmarks.landmark[idx]
            coords.append([lm.x * img_width, lm.y * img_height])
        return np.array(coords)
    
    def _compute_eyebrow_distance(self, landmarks, img_width: int, img_height: int) -> float:
        """
        Compute average vertical distance between eyebrows and eyes.
        
        Mathematical Approach:
        - Calculate mean position of eyebrow landmarks
        - Calculate mean position of eye landmarks
        - Compute vertical (y-axis) distance
        - Lower values indicate eyebrow lowering (common stress indicator)
        
        Returns:
            Average eyebrow-to-eye distance
        """
        left_eyebrow = self._get_landmark_coords(landmarks, self.LEFT_EYEBROW, img_width, img_height)
        right_eyebrow = self._get_landmark_coords(landmarks, self.RIGHT_EYEBROW, img_width, img_height)
        
        # Mean eyebrow position
        eyebrow_y = np.mean([left_eyebrow[:, 1].mean(), right_eyebrow[:, 1].mean()])
        
        # Mean eye position (using upper eyelid landmarks)
        left_eye = self._get_landmark_coords(landmarks, self.LEFT_EYE_UPPER, img_width, img_height)
        right_eye = self._get_landmark_coords(landmarks, self.RIGHT_EYE_UPPER, img_width, img_height)
        eye_y = np.mean([left_eye[:, 1].mean(), right_eye[:, 1].mean()])
        
        # Vertical distance (smaller = eyebrows closer to eyes, often indicates tension)
        return eye_y - eyebrow_y
    
    def _compute_lip_distance(self, landmarks, img_width: int, img_height: int) -> float:
        """
        Compute lip corner to center distance ratio.
        
        Mathematical Approach:
        - Measure distance between lip corners (mouth width)
        - Measure distance between upper and lower lip centers (mouth opening)
        - Ratio changes indicate lip tension or compression (stress indicator)
        
        Returns:
            Lip distance metric
        """
        upper_lip = self._get_landmark_coords(landmarks, self.LIP_UPPER, img_width, img_height)
        lower_lip = self._get_landmark_coords(landmarks, self.LIP_LOWER, img_width, img_height)
        left_corner = self._get_landmark_coords(landmarks, self.LIP_LEFT_CORNER, img_width, img_height)
        right_corner = self._get_landmark_coords(landmarks, self.LIP_RIGHT_CORNER, img_width, img_height)
        
        # Vertical distance (lip opening)
        vertical_dist = self._euclidean_distance(upper_lip[0], lower_lip[0])
        
        # Horizontal distance (lip width)
        horizontal_dist = self._euclidean_distance(left_corner[0], right_corner[0])
        
        # Return ratio (normalized metric)
        return vertical_dist / (horizontal_dist + 1e-6)  # Add epsilon to avoid division by zero
    
    def _detect_blink(self, landmarks, img_width: int, img_height: int) -> bool:
        """
        Detect eye blinks using eye aspect ratio (EAR).
        
        Mathematical Approach:
        - Eye Aspect Ratio (EAR) = (vertical_distance) / (horizontal_distance)
        - EAR drops significantly during a blink
        - Threshold: EAR < 0.2 indicates closed eye
        
        Stress Indicator:
        - Increased blink rate (>25 blinks/min) may indicate stress
        - Decreased blink rate (<10 blinks/min) may indicate concentration/deception
        
        Returns:
            True if blink detected in current frame
        """
        # Calculate left eye aspect ratio
        left_upper = self._get_landmark_coords(landmarks, self.LEFT_EYE_UPPER, img_width, img_height)
        left_lower = self._get_landmark_coords(landmarks, self.LEFT_EYE_LOWER, img_width, img_height)
        left_vertical = self._euclidean_distance(left_upper[0], left_lower[0])
        
        # Calculate right eye aspect ratio
        right_upper = self._get_landmark_coords(landmarks, self.RIGHT_EYE_UPPER, img_width, img_height)
        right_lower = self._get_landmark_coords(landmarks, self.RIGHT_EYE_LOWER, img_width, img_height)
        right_vertical = self._euclidean_distance(right_upper[0], right_lower[0])
        
        # Average vertical distance
        avg_vertical = (left_vertical + right_vertical) / 2.0
        
        # Use a threshold to detect blink (normalized value)
        # Typical EAR threshold is around 0.2-0.25
        blink_threshold = 5.0  # Pixel distance threshold (adjust based on resolution)
        
        return avg_vertical < blink_threshold
    
    def _compute_anomaly_score(self, current_value: float, 
                               history: deque, metric_name: str) -> float:
        """
        Compute anomaly score using z-score normalization.
        
        Mathematical Approach:
        - Calculate baseline: mean(history)
        - Calculate std deviation: std(history)
        - Z-score = |current_value - mean| / (std + epsilon)
        - Anomaly exists if z-score > sensitivity threshold (default: 2σ)
        - Score normalized to 0-100 range
        
        Args:
            current_value: Current measurement
            history: Historical measurements (rolling window)
            metric_name: Name of metric for debugging
            
        Returns:
            Anomaly score (0-100, higher = more anomalous)
        """
        if len(history) < 5:  # Need minimum history for statistics
            return 0.0
        
        baseline = np.mean(history)
        std_dev = np.std(history) + 1e-6  # Add epsilon to avoid division by zero
        
        # Z-score calculation
        z_score = abs(current_value - baseline) / std_dev
        
        # Normalize to 0-100 scale
        # Values beyond 2σ indicate significant anomaly
        anomaly_score = min(100.0, (z_score / self.sensitivity) * 100.0)
        
        return anomaly_score
    
    def analyze_frame(self, frame: np.ndarray) -> Tuple[float, dict, Optional[np.ndarray]]:
        """
        Analyze a single video frame for facial stress indicators.
        
        Args:
            frame: BGR image from video capture
            
        Returns:
            Tuple of (stress_score, metrics_dict, annotated_frame)
            - stress_score: Overall facial stress score (0-100)
            - metrics_dict: Detailed metrics for debugging
            - annotated_frame: Frame with landmarks drawn (or None if no face detected)
        """
        self.frame_count += 1
        img_height, img_width = frame.shape[:2]
        
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return 0.0, {"error": "No face detected"}, None
        
        landmarks = results.multi_face_landmarks[0]
        
        # Compute facial metrics
        eyebrow_dist = self._compute_eyebrow_distance(landmarks, img_width, img_height)
        lip_dist = self._compute_lip_distance(landmarks, img_width, img_height)
        is_blinking = self._detect_blink(landmarks, img_width, img_height)
        
        # Update history
        self.eyebrow_distances.append(eyebrow_dist)
        self.lip_distances.append(lip_dist)
        
        # Blink detection and counting
        if is_blinking and not self.last_blink_state:
            self.blink_count += 1
            self.blink_history.append(1)
        else:
            self.blink_history.append(0)
        
        self.last_blink_state = is_blinking
        
        # Calculate blink rate (blinks per minute)
        blink_rate = (sum(self.blink_history) / len(self.blink_history)) * 60 * 30  # Assuming 30fps
        
        # Compute anomaly scores for each metric
        eyebrow_anomaly = self._compute_anomaly_score(eyebrow_dist, self.eyebrow_distances, "eyebrow")
        lip_anomaly = self._compute_anomaly_score(lip_dist, self.lip_distances, "lip")
        
        # Blink rate anomaly (normal: 15-20 blinks/min)
        blink_anomaly = 0.0
        if blink_rate > 25:  # High blink rate
            blink_anomaly = min(100.0, ((blink_rate - 25) / 20) * 100)
        elif blink_rate < 10:  # Low blink rate (possible suppression)
            blink_anomaly = min(100.0, ((10 - blink_rate) / 10) * 100)
        
        # Overall facial stress score (weighted average)
        stress_score = (eyebrow_anomaly * 0.4 + lip_anomaly * 0.3 + blink_anomaly * 0.3)
        
        # Prepare metrics dictionary
        metrics = {
            "eyebrow_distance": eyebrow_dist,
            "eyebrow_anomaly": eyebrow_anomaly,
            "lip_distance": lip_dist,
            "lip_anomaly": lip_anomaly,
            "blink_rate": blink_rate,
            "blink_anomaly": blink_anomaly,
            "stress_score": stress_score
        }
        
        # Draw landmarks on frame
        annotated_frame = frame.copy()
        mp.solutions.drawing_utils.draw_landmarks(
            image=annotated_frame,
            landmark_list=landmarks,
            connections=self.mp_face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_tesselation_style()
        )
        
        return stress_score, metrics, annotated_frame
    
    def reset(self):
        """Reset all history and counters."""
        self.eyebrow_distances.clear()
        self.lip_distances.clear()
        self.blink_history.clear()
        self.frame_count = 0
        self.blink_count = 0
        self.last_blink_state = False
    
    def __del__(self):
        """Cleanup MediaPipe resources."""
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()
