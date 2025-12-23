"""
rPPG Pulse Estimator Module for Lie-Dar System
===============================================
Estimates heart rate (BPM) from video using remote photoplethysmography (rPPG).
Analyzes subtle color changes in the forehead region caused by blood flow.

Key Features:
- Forehead ROI extraction using facial landmarks
- Green channel analysis (optimal for PPG signal)
- FFT-based BPM calculation
- Bandpass filtering (48-180 BPM range)
"""

import cv2
import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
from collections import deque
from typing import Tuple, Optional


class BPM_Estimator:
    """
    Estimates heart rate from video using remote photoplethysmography (rPPG).
    
    The rPPG technique exploits the fact that blood volume changes in facial
    blood vessels cause subtle color variations detectable by camera.
    """
    
    def __init__(self, fps: int = 30, buffer_seconds: int = 10):
        """
        Initialize the BPM estimator.
        
        Args:
            fps: Video frame rate (default: 30)
            buffer_seconds: Duration of signal buffer in seconds (default: 10)
        """
        self.fps = fps
        self.buffer_size = fps * buffer_seconds  # Number of frames to buffer
        
        # Signal buffer (stores mean green channel values over time)
        self.signal_buffer = deque(maxlen=self.buffer_size)
        
        # Bandpass filter parameters
        # Physiological heart rate range: 48-180 BPM = 0.8-3.0 Hz
        self.min_bpm = 48
        self.max_bpm = 180
        self.min_hz = self.min_bpm / 60.0
        self.max_hz = self.max_bpm / 60.0
        
        # Current BPM estimate
        self.current_bpm = 0.0
        self.bpm_history = deque(maxlen=10)  # Smooth BPM over last 10 estimates
        
    def _extract_forehead_roi(self, frame: np.ndarray, 
                              landmarks) -> Optional[np.ndarray]:
        """
        Extract forehead region of interest using facial landmarks.
        
        Mathematical Approach:
        - Use forehead landmarks from MediaPipe (landmarks 10, 338, 297, 332, 284, etc.)
        - Create bounding box around forehead area
        - Extract ROI with some padding
        
        Args:
            frame: Input BGR frame
            landmarks: MediaPipe facial landmarks
            
        Returns:
            Forehead ROI as numpy array, or None if extraction fails
        """
        if landmarks is None:
            return None
        
        img_height, img_width = frame.shape[:2]
        
        # Forehead landmark indices (top center of face, above eyebrows)
        # These represent a horizontal band across the forehead
        forehead_indices = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                           397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136]
        
        # Extract coordinates
        forehead_points = []
        for idx in forehead_indices:
            lm = landmarks.landmark[idx]
            x = int(lm.x * img_width)
            y = int(lm.y * img_height)
            forehead_points.append([x, y])
        
        forehead_points = np.array(forehead_points)
        
        # Calculate bounding box
        x_min = max(0, np.min(forehead_points[:, 0]) - 10)
        x_max = min(img_width, np.max(forehead_points[:, 0]) + 10)
        y_min = max(0, np.min(forehead_points[:, 1]) - 10)
        y_max = min(img_height, np.max(forehead_points[:, 1]) + 10)
        
        # Extract ROI
        roi = frame[y_min:y_max, x_min:x_max]
        
        if roi.size == 0:
            return None
        
        return roi
    
    def _extract_ppg_signal(self, roi: np.ndarray) -> float:
        """
        Extract PPG signal value from forehead ROI.
        
        Mathematical Approach:
        - Green channel is most sensitive to blood volume changes
        - Calculate spatial average of green channel in ROI
        - This represents the PPG signal for current frame
        
        Rationale:
        - Blood absorbs green light more than red/blue
        - As blood volume increases (systole), green intensity decreases
        - As blood volume decreases (diastole), green intensity increases
        
        Args:
            roi: Forehead region of interest
            
        Returns:
            Mean green channel intensity
        """
        # Extract green channel (index 1 in BGR)
        green_channel = roi[:, :, 1]
        
        # Calculate spatial mean
        mean_green = np.mean(green_channel)
        
        return mean_green
    
    def _apply_bandpass_filter(self, signal_data: np.ndarray) -> np.ndarray:
        """
        Apply bandpass filter to isolate heart rate frequencies.
        
        Mathematical Approach:
        - Use Butterworth bandpass filter
        - Passband: 0.8-3.0 Hz (48-180 BPM)
        - Remove low-frequency trends and high-frequency noise
        - Order 3 for balance between sharpness and ringing
        
        Args:
            signal_data: Raw PPG signal
            
        Returns:
            Filtered signal
        """
        # Design Butterworth bandpass filter
        nyquist = self.fps / 2.0  # Nyquist frequency
        low = self.min_hz / nyquist
        high = self.max_hz / nyquist
        
        # Ensure valid frequency range
        low = max(0.001, min(low, 0.999))
        high = max(0.001, min(high, 0.999))
        
        if low >= high:
            return signal_data  # Return unfiltered if invalid range
        
        # Create filter coefficients
        b, a = signal.butter(3, [low, high], btype='band')
        
        # Apply filter
        filtered_signal = signal.filtfilt(b, a, signal_data)
        
        return filtered_signal
    
    def _estimate_bpm_fft(self, signal_data: np.ndarray) -> float:
        """
        Estimate BPM using Fast Fourier Transform (FFT).
        
        Mathematical Approach:
        - Transform time-domain signal to frequency domain
        - Find frequency with maximum power in physiological range
        - Convert frequency (Hz) to BPM: BPM = frequency * 60
        
        Why FFT?
        - Efficiently identifies dominant periodic components
        - Heart rate manifests as peak in frequency spectrum
        
        Args:
            signal_data: Filtered PPG signal
            
        Returns:
            Estimated BPM
        """
        # Compute FFT
        N = len(signal_data)
        fft_vals = fft(signal_data)
        fft_freq = fftfreq(N, 1.0 / self.fps)
        
        # Only consider positive frequencies
        positive_mask = fft_freq > 0
        fft_freq = fft_freq[positive_mask]
        fft_power = np.abs(fft_vals[positive_mask]) ** 2
        
        # Filter to physiological range (0.8-3.0 Hz)
        valid_range = (fft_freq >= self.min_hz) & (fft_freq <= self.max_hz)
        valid_freq = fft_freq[valid_range]
        valid_power = fft_power[valid_range]
        
        if len(valid_power) == 0:
            return 0.0
        
        # Find frequency with maximum power
        max_idx = np.argmax(valid_power)
        dominant_freq = valid_freq[max_idx]
        
        # Convert to BPM
        bpm = dominant_freq * 60.0
        
        return bpm
    
    def process_frame(self, frame: np.ndarray, landmarks) -> Tuple[float, dict]:
        """
        Process a single video frame to update BPM estimate.
        
        Args:
            frame: BGR video frame
            landmarks: MediaPipe facial landmarks
            
        Returns:
            Tuple of (bpm, metrics_dict)
            - bpm: Current BPM estimate
            - metrics_dict: Diagnostic information
        """
        # Extract forehead ROI
        forehead_roi = self._extract_forehead_roi(frame, landmarks)
        
        if forehead_roi is None:
            return self.current_bpm, {"error": "Could not extract forehead ROI"}
        
        # Extract PPG signal value
        ppg_value = self._extract_ppg_signal(forehead_roi)
        
        # Add to buffer
        self.signal_buffer.append(ppg_value)
        
        # Need sufficient data for FFT (at least 5 seconds)
        min_buffer_size = self.fps * 5
        if len(self.signal_buffer) < min_buffer_size:
            progress = len(self.signal_buffer) / min_buffer_size * 100
            return 0.0, {"status": "buffering", "progress": progress}
        
        # Convert buffer to numpy array
        signal_data = np.array(self.signal_buffer)
        
        # Detrend signal (remove DC component and linear trends)
        signal_data = signal.detrend(signal_data)
        
        # Apply bandpass filter
        filtered_signal = self._apply_bandpass_filter(signal_data)
        
        # Estimate BPM using FFT
        bpm = self._estimate_bpm_fft(filtered_signal)
        
        # Smooth BPM estimate
        self.bpm_history.append(bpm)
        self.current_bpm = np.median(self.bpm_history)  # Use median for robustness
        
        # Calculate stress score based on BPM
        # Normal resting heart rate: 60-80 BPM
        # Elevated: 80-100 BPM (mild stress)
        # High: >100 BPM (significant stress)
        stress_score = 0.0
        if self.current_bpm > 90:
            stress_score = min(100.0, ((self.current_bpm - 90) / 40) * 100)
        elif self.current_bpm < 50:  # Abnormally low (may indicate measurement error)
            stress_score = 20.0
        
        metrics = {
            "bpm": self.current_bpm,
            "raw_bpm": bpm,
            "stress_score": stress_score,
            "buffer_size": len(self.signal_buffer),
            "signal_quality": "good" if 50 <= self.current_bpm <= 180 else "poor"
        }
        
        return self.current_bpm, metrics
    
    def get_stress_score(self) -> float:
        """
        Calculate stress score based on current BPM.
        
        Stress Indicators:
        - BPM > 90: Elevated heart rate (linear scaling to 100 at 130 BPM)
        - BPM < 50: Abnormally low (may indicate poor signal quality)
        
        Returns:
            Stress score (0-100)
        """
        if self.current_bpm == 0:
            return 0.0
        
        if self.current_bpm > 90:
            return min(100.0, ((self.current_bpm - 90) / 40) * 100)
        elif self.current_bpm < 50:
            return 20.0
        else:
            return 0.0
    
    def reset(self):
        """Reset all buffers and estimates."""
        self.signal_buffer.clear()
        self.bpm_history.clear()
        self.current_bpm = 0.0
