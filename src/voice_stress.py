"""
Voice Stress Analysis Module for Lie-Dar System
================================================
Analyzes acoustic features from microphone input to detect vocal stress indicators.

Key Features:
- Real-time audio capture from microphone
- Pitch (F0) variation analysis
- Jitter measurement (frequency perturbation)
- Shimmer measurement (amplitude perturbation)
- RMS energy analysis
"""

import numpy as np
import pyaudio
import librosa
from collections import deque
from typing import Tuple, Optional
import threading
import time


class VoiceStress:
    """
    Analyzes voice acoustic features to detect stress indicators.
    
    Stress manifests in voice through:
    - Increased pitch variation
    - Higher jitter (vocal cord tension)
    - Higher shimmer (amplitude instability)
    - Changed energy levels
    """
    
    def __init__(self, sample_rate: int = 16000, chunk_duration: float = 1.0):
        """
        Initialize the voice stress analyzer.
        
        Args:
            sample_rate: Audio sampling rate in Hz (default: 16000)
            chunk_duration: Duration of audio chunks to analyze in seconds (default: 1.0)
        """
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_size = int(sample_rate * chunk_duration)
        
        # PyAudio configuration
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
        # Audio buffer
        self.audio_buffer = deque(maxlen=sample_rate * 5)  # 5 seconds of audio
        
        # Feature history for baseline calculation
        self.pitch_history = deque(maxlen=30)
        self.jitter_history = deque(maxlen=30)
        self.shimmer_history = deque(maxlen=30)
        self.energy_history = deque(maxlen=30)
        
        # Current measurements
        self.current_metrics = {
            "pitch_mean": 0.0,
            "pitch_std": 0.0,
            "jitter": 0.0,
            "shimmer": 0.0,
            "energy": 0.0,
            "stress_score": 0.0
        }
        
        # Threading for async audio capture
        self.is_recording = False
        self.record_thread = None
        
    def start_recording(self):
        """Start asynchronous audio recording from microphone."""
        if self.is_recording:
            return
        
        try:
            # Open audio stream
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=1024,
                stream_callback=self._audio_callback
            )
            
            self.is_recording = True
            self.stream.start_stream()
            
        except Exception as e:
            print(f"Error starting audio recording: {e}")
            self.is_recording = False
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for PyAudio stream to capture audio data."""
        if in_data:
            # Convert bytes to numpy array
            audio_data = np.frombuffer(in_data, dtype=np.float32)
            self.audio_buffer.extend(audio_data)
        
        return (None, pyaudio.paContinue)
    
    def stop_recording(self):
        """Stop audio recording."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.is_recording = False
    
    def _extract_pitch(self, audio_chunk: np.ndarray) -> Tuple[float, float]:
        """
        Extract pitch (fundamental frequency F0) statistics.
        
        Mathematical Approach:
        - Use librosa's pyin algorithm (probabilistic YIN)
        - YIN is autocorrelation-based pitch detection
        - Calculate mean and std deviation of pitch over chunk
        
        Stress Indicators:
        - Increased pitch variation (higher std)
        - Elevated baseline pitch (higher mean)
        
        Args:
            audio_chunk: Audio signal array
            
        Returns:
            Tuple of (pitch_mean, pitch_std) in Hz
        """
        # Extract pitch using probabilistic YIN algorithm
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio_chunk,
            fmin=librosa.note_to_hz('C2'),  # ~65 Hz (low male voice)
            fmax=librosa.note_to_hz('C7'),  # ~2093 Hz (high female voice)
            sr=self.sample_rate
        )
        
        # Filter out unvoiced frames
        voiced_f0 = f0[voiced_flag]
        
        if len(voiced_f0) == 0:
            return 0.0, 0.0
        
        # Remove NaN values
        voiced_f0 = voiced_f0[~np.isnan(voiced_f0)]
        
        if len(voiced_f0) == 0:
            return 0.0, 0.0
        
        pitch_mean = np.mean(voiced_f0)
        pitch_std = np.std(voiced_f0)
        
        return pitch_mean, pitch_std
    
    def _calculate_jitter(self, audio_chunk: np.ndarray) -> float:
        """
        Calculate jitter (pitch period perturbation).
        
        Mathematical Definition:
        Jitter = (1/N) * Σ|T_i - T_(i+1)| / mean(T)
        
        Where:
        - T_i is the i-th pitch period duration
        - N is number of periods
        
        Measures cycle-to-cycle variation in fundamental frequency.
        Higher jitter indicates vocal cord tension (stress indicator).
        
        Normal jitter: <1%
        Stressed voice: >2%
        
        Args:
            audio_chunk: Audio signal array
            
        Returns:
            Jitter percentage (0-100)
        """
        # Extract pitch periods using autocorrelation
        try:
            f0, _, _ = librosa.pyin(
                audio_chunk,
                fmin=librosa.note_to_hz('C2'),
                fmax=librosa.note_to_hz('C7'),
                sr=self.sample_rate
            )
            
            # Remove NaN values
            f0 = f0[~np.isnan(f0)]
            
            if len(f0) < 2:
                return 0.0
            
            # Convert frequency to period (T = 1/f)
            periods = 1.0 / (f0 + 1e-6)  # Add epsilon to avoid division by zero
            
            # Calculate absolute differences between consecutive periods
            period_diffs = np.abs(np.diff(periods))
            
            # Calculate jitter
            mean_period = np.mean(periods)
            jitter = (np.mean(period_diffs) / mean_period) * 100.0
            
            return min(jitter, 100.0)  # Cap at 100%
            
        except Exception:
            return 0.0
    
    def _calculate_shimmer(self, audio_chunk: np.ndarray) -> float:
        """
        Calculate shimmer (amplitude perturbation).
        
        Mathematical Definition:
        Shimmer = (1/N) * Σ|A_i - A_(i+1)| / mean(A)
        
        Where:
        - A_i is the i-th peak amplitude
        - N is number of periods
        
        Measures cycle-to-cycle variation in amplitude.
        Higher shimmer indicates vocal instability (stress indicator).
        
        Normal shimmer: <3%
        Stressed voice: >5%
        
        Args:
            audio_chunk: Audio signal array
            
        Returns:
            Shimmer percentage (0-100)
        """
        # Calculate frame-wise RMS amplitude
        frame_length = 512
        hop_length = 256
        
        rms = librosa.feature.rms(
            y=audio_chunk,
            frame_length=frame_length,
            hop_length=hop_length
        )[0]
        
        if len(rms) < 2:
            return 0.0
        
        # Calculate absolute differences between consecutive amplitudes
        amplitude_diffs = np.abs(np.diff(rms))
        
        # Calculate shimmer
        mean_amplitude = np.mean(rms)
        if mean_amplitude < 1e-6:
            return 0.0
        
        shimmer = (np.mean(amplitude_diffs) / mean_amplitude) * 100.0
        
        return min(shimmer, 100.0)  # Cap at 100%
    
    def _calculate_energy(self, audio_chunk: np.ndarray) -> float:
        """
        Calculate RMS energy of audio signal.
        
        Mathematical Definition:
        RMS = sqrt((1/N) * Σ(x_i^2))
        
        Energy changes can indicate stress (often reduced during deception).
        
        Args:
            audio_chunk: Audio signal array
            
        Returns:
            RMS energy
        """
        rms_energy = np.sqrt(np.mean(audio_chunk ** 2))
        return rms_energy
    
    def analyze_audio(self) -> Tuple[float, dict]:
        """
        Analyze current audio buffer for stress indicators.
        
        Returns:
            Tuple of (stress_score, metrics_dict)
            - stress_score: Overall voice stress score (0-100)
            - metrics_dict: Detailed acoustic features
        """
        if len(self.audio_buffer) < self.chunk_size:
            progress = len(self.audio_buffer) / self.chunk_size * 100
            return 0.0, {"status": "buffering", "progress": progress}
        
        # Get recent audio chunk
        audio_chunk = np.array(list(self.audio_buffer)[-self.chunk_size:])
        
        # Normalize audio
        if np.max(np.abs(audio_chunk)) > 0:
            audio_chunk = audio_chunk / np.max(np.abs(audio_chunk))
        
        # Extract features
        pitch_mean, pitch_std = self._extract_pitch(audio_chunk)
        jitter = self._calculate_jitter(audio_chunk)
        shimmer = self._calculate_shimmer(audio_chunk)
        energy = self._calculate_energy(audio_chunk)
        
        # Update history
        if pitch_mean > 0:  # Only add valid measurements
            self.pitch_history.append(pitch_std)
            self.jitter_history.append(jitter)
            self.shimmer_history.append(shimmer)
            self.energy_history.append(energy)
        
        # Calculate stress indicators
        stress_components = []
        
        # 1. Pitch variation stress (higher std indicates stress)
        if len(self.pitch_history) > 5:
            baseline_pitch_std = np.median(self.pitch_history)
            if baseline_pitch_std > 0:
                pitch_stress = min(100.0, (pitch_std / baseline_pitch_std) * 50)
                stress_components.append(pitch_stress)
        
        # 2. Jitter stress (>2% indicates stress)
        jitter_stress = min(100.0, (jitter / 2.0) * 100)
        stress_components.append(jitter_stress)
        
        # 3. Shimmer stress (>5% indicates stress)
        shimmer_stress = min(100.0, (shimmer / 5.0) * 100)
        stress_components.append(shimmer_stress)
        
        # Overall stress score (weighted average)
        if len(stress_components) > 0:
            stress_score = np.mean(stress_components)
        else:
            stress_score = 0.0
        
        # Update current metrics
        self.current_metrics = {
            "pitch_mean": pitch_mean,
            "pitch_std": pitch_std,
            "jitter": jitter,
            "shimmer": shimmer,
            "energy": energy,
            "stress_score": stress_score
        }
        
        return stress_score, self.current_metrics
    
    def get_stress_score(self) -> float:
        """Get current voice stress score."""
        return self.current_metrics["stress_score"]
    
    def reset(self):
        """Reset all buffers and history."""
        self.audio_buffer.clear()
        self.pitch_history.clear()
        self.jitter_history.clear()
        self.shimmer_history.clear()
        self.energy_history.clear()
        self.current_metrics = {
            "pitch_mean": 0.0,
            "pitch_std": 0.0,
            "jitter": 0.0,
            "shimmer": 0.0,
            "energy": 0.0,
            "stress_score": 0.0
        }
    
    def __del__(self):
        """Cleanup audio resources."""
        self.stop_recording()
        if hasattr(self, 'audio'):
            self.audio.terminate()
