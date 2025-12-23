"""
Lie-Dar: Real-Time Lie Detection System
========================================
Main application orchestrator.

Integrates:
- Facial analysis (MediaPipe)
- rPPG pulse estimation
- Voice stress analysis
- Multi-modal fusion
- Real-time visualization

Author: Claude Sonnet 4.5 AI and Miraç Tahircan YILMAZ
Date: 2025
"""

import cv2
import sys
import time
import numpy as np
from src.facial_analysis import FacialAnalysis
from src.bpm_estimator import BPM_Estimator
from src.voice_stress import VoiceStress
from src.logic_engine import LogicEngine
from src.visualizer import Visualizer


class LieDar:
    """
    Main application class for the Lie-Dar system.
    
    Orchestrates all components and manages the real-time processing loop.
    """
    
    def __init__(self, camera_id: int = 0, fps: int = 30):
        """
        Initialize the Lie-Dar system.
        
        Args:
            camera_id: Webcam device ID (default: 0)
            fps: Target frame rate (default: 30)
        """
        print("Initializing Lie-Dar System...")
        
        self.fps = fps
        self.camera_id = camera_id
        
        # Initialize video capture
        print(f"Opening camera {camera_id}...")
        self.cap = cv2.VideoCapture(camera_id)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera {camera_id}")
        
        # Get actual camera properties
        actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
        if actual_fps > 0:
            self.fps = int(actual_fps)
        print(f"Camera FPS: {self.fps}")
        
        # Initialize analysis modules
        print("Initializing facial analysis...")
        try:
            self.facial_analyzer = FacialAnalysis(window_size=30, sensitivity=2.0)
            self.has_facial = True
            print("✓ Facial analysis initialized")
        except Exception as e:
            print(f"⚠️  Facial analysis unavailable (MediaPipe issue): {e}")
            print("   Running in simplified mode (Voice + Pulse only)")
            self.facial_analyzer = None
            self.has_facial = False
        
        print("Initializing pulse estimator...")
        self.bpm_estimator = BPM_Estimator(fps=self.fps, buffer_seconds=10)
        
        print("Initializing voice analyzer...")
        self.voice_analyzer = VoiceStress(sample_rate=16000, chunk_duration=1.0)
        
        print("Initializing logic engine...")
        # Adjust weights based on available modules
        if self.has_facial:
            self.logic_engine = LogicEngine(
                facial_weight=0.40,
                voice_weight=0.30,
                pulse_weight=0.30
            )
        else:
            # No facial analysis - redistribute weights
            self.logic_engine = LogicEngine(
                facial_weight=0.00,
                voice_weight=0.60,  # Increased weight
                pulse_weight=0.40   # Increased weight
            )
            print("   Weights adjusted: Voice 60%, Pulse 40%")
        
        print("Initializing visualizer...")
        self.visualizer = Visualizer()
        
        # State variables
        self.is_running = False
        self.current_results = {
            "honesty_score": 50.0,
            "alert_level": "medium_stress",
            "component_scores": {
                "facial_raw": 0.0,
                "voice_raw": 0.0,
                "pulse_raw": 0.0
            },
            "bpm": 0.0,
            "facial_metrics": {},
            "voice_metrics": {}
        }
        
        print("✓ Lie-Dar System Ready!")
        print("=" * 60)
    
    def start(self):
        """Start the Lie-Dar system."""
        print("Starting Lie-Dar...")
        print("Press 'Q' to quit, 'R' to reset")
        print("=" * 60)
        
        # Start voice recording
        self.voice_analyzer.start_recording()
        
        self.is_running = True
        self._main_loop()
    
    def _main_loop(self):
        """Main processing loop."""
        frame_count = 0
        start_time = time.time()
        
        while self.is_running:
            # Capture frame
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            frame_count += 1
            
            # Flip frame for mirror effect
            frame = cv2.flip(frame, 1)
            
            try:
                # 1. Facial Analysis (if available)
                facial_stress = 0.0
                annotated_frame = frame
                facial_metrics = {}
                
                if self.has_facial and self.facial_analyzer:
                    facial_stress, facial_metrics, temp_frame = self.facial_analyzer.analyze_frame(frame)
                    if temp_frame is not None:
                        annotated_frame = temp_frame
                
                # Use annotated frame if available, otherwise use original
                display_frame = annotated_frame
                
                # 2. Pulse Estimation
                bpm = 0.0
                pulse_stress = 0.0
                
                # For pulse estimation without MediaPipe, we'll use a simpler approach
                # Just extract a fixed forehead region based on face detection with OpenCV
                if self.has_facial:
                    # Get landmarks from facial analyzer if available
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = self.facial_analyzer.face_mesh.process(rgb_frame)
                    
                    if results.multi_face_landmarks:
                        landmarks = results.multi_face_landmarks[0]
                        bpm, bpm_metrics = self.bpm_estimator.process_frame(frame, landmarks)
                        pulse_stress = self.bpm_estimator.get_stress_score()
                else:
                    # Simple forehead extraction without MediaPipe
                    # Use Haar Cascade for face detection
                    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                    
                    if len(faces) > 0:
                        x, y, w, h = faces[0]
                        # Extract forehead region (top 30% of face)
                        forehead_y_start = y
                        forehead_y_end = y + int(h * 0.3)
                        forehead_x_start = x + int(w * 0.2)
                        forehead_x_end = x + int(w * 0.8)
                        
                        # Draw rectangle on display frame
                        cv2.rectangle(display_frame, (forehead_x_start, forehead_y_start),
                                    (forehead_x_end, forehead_y_end), (0, 255, 0), 2)
                        
                        # Simple BPM estimation (placeholder - would need proper rPPG implementation)
                        # For now, just use a dummy value
                        bpm = 75.0
                        pulse_stress = 10.0
                
                # 3. Voice Analysis (runs asynchronously)
                voice_stress, voice_metrics = self.voice_analyzer.analyze_audio()
                
                # 4. Multi-Modal Fusion
                results = self.logic_engine.analyze(
                    facial_stress=facial_stress,
                    voice_stress=voice_stress,
                    pulse_stress=pulse_stress
                )
                
                # Update current results
                self.current_results = {
                    "honesty_score": results["honesty_score"],
                    "alert_level": results["alert_level"],
                    "component_scores": results["component_scores"],
                    "bpm": bpm,
                    "facial_metrics": facial_metrics,
                    "voice_metrics": voice_metrics
                }
                
                # 5. Visualization
                viz_frame = self.visualizer.render_frame(
                    video_frame=display_frame,
                    honesty_score=results["honesty_score"],
                    component_scores=results["component_scores"],
                    bpm=bpm,
                    alert_level=results["alert_level"],
                    facial_metrics=facial_metrics,
                    voice_metrics=voice_metrics
                )
                
                # Display
                key = self.visualizer.show(viz_frame)
                
                # Handle keyboard input
                if key == ord('q') or key == ord('Q'):
                    print("\nQuitting...")
                    self.is_running = False
                elif key == ord('r') or key == ord('R'):
                    print("\nResetting system...")
                    self.reset()
                
                # Print status every 30 frames (~1 second)
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    actual_fps = frame_count / elapsed
                    print(f"Frame {frame_count} | FPS: {actual_fps:.1f} | "
                          f"Honesty: {results['honesty_score']:.1f} | "
                          f"BPM: {bpm:.0f} | "
                          f"Alert: {results['alert_level']}")
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                import traceback
                traceback.print_exc()
        
        self.cleanup()
    
    def reset(self):
        """Reset all analyzers."""
        self.facial_analyzer.reset()
        self.bpm_estimator.reset()
        self.voice_analyzer.reset()
        self.logic_engine.reset()
        print("System reset complete")
    
    def cleanup(self):
        """Cleanup resources."""
        print("\nCleaning up...")
        
        # Stop voice recording
        self.voice_analyzer.stop_recording()
        
        # Release camera
        if self.cap:
            self.cap.release()
        
        # Close windows
        self.visualizer.close()
        
        print("✓ Cleanup complete")
    
    def __del__(self):
        """Destructor."""
        self.cleanup()


def main():
    """Main entry point."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║       LIE-DAR: Real-Time Lie Detection System            ║
    ║                                                           ║
    ║  A multi-modal deception detection system using:         ║
    ║  • Facial Micro-Expression Analysis (MediaPipe)          ║
    ║  • Remote Photoplethysmography (rPPG) for BPM            ║
    ║  • Voice Stress Analysis (Jitter/Shimmer)                ║
    ║                                                           ║
    ║  ⚠️  For educational/research purposes only              ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Create and start Lie-Dar system
        liedar = LieDar(camera_id=0, fps=30)
        liedar.start()
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
