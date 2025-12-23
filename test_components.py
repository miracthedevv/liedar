"""
Simple Test Script for Lie-Dar Components
==========================================
Tests individual modules without requiring full system setup.
Useful for verifying installation and component functionality.
"""

import sys
import numpy as np

def test_imports():
    """Test that all required libraries can be imported."""
    print("Testing imports...")
    
    try:
        import cv2
        print("✓ OpenCV imported successfully")
    except ImportError as e:
        print(f"✗ OpenCV import failed: {e}")
        return False
    
    try:
        import mediapipe
        print("✓ MediaPipe imported successfully")
    except ImportError as e:
        print(f"✗ MediaPipe import failed: {e}")
        return False
    
    try:
        import numpy
        print("✓ NumPy imported successfully")
    except ImportError as e:
        print(f"✗ NumPy import failed: {e}")
        return False
    
    try:
        import scipy
        print("✓ SciPy imported successfully")
    except ImportError as e:
        print(f"✗ SciPy import failed: {e}")
        return False
    
    try:
        import librosa
        print("✓ librosa imported successfully")
    except ImportError as e:
        print(f"✗ librosa import failed: {e}")
        return False
    
    try:
        import pyaudio
        print("✓ PyAudio imported successfully")
    except ImportError as e:
        print(f"✗ PyAudio import failed: {e}")
        print("  Note: PyAudio installation can be tricky. See README for platform-specific instructions.")
        return False
    
    return True


def test_modules():
    """Test that all Lie-Dar modules can be imported."""
    print("\nTesting Lie-Dar modules...")
    
    try:
        from src.facial_analysis import FacialAnalysis
        print("✓ FacialAnalysis module imported")
    except ImportError as e:
        print(f"✗ FacialAnalysis import failed: {e}")
        return False
    
    try:
        from src.bpm_estimator import BPM_Estimator
        print("✓ BPM_Estimator module imported")
    except ImportError as e:
        print(f"✗ BPM_Estimator import failed: {e}")
        return False
    
    try:
        from src.voice_stress import VoiceStress
        print("✓ VoiceStress module imported")
    except ImportError as e:
        print(f"✗ VoiceStress import failed: {e}")
        return False
    
    try:
        from src.logic_engine import LogicEngine
        print("✓ LogicEngine module imported")
    except ImportError as e:
        print(f"✗ LogicEngine import failed: {e}")
        return False
    
    try:
        from src.visualizer import Visualizer
        print("✓ Visualizer module imported")
    except ImportError as e:
        print(f"✗ Visualizer import failed: {e}")
        return False
    
    return True


def test_logic_engine():
    """Test the logic engine with dummy data."""
    print("\nTesting Logic Engine...")
    
    try:
        from src.logic_engine import LogicEngine
        
        engine = LogicEngine(facial_weight=0.4, voice_weight=0.3, pulse_weight=0.3)
        print("✓ Logic engine initialized")
        
        # Test with dummy scores
        result = engine.analyze(
            facial_stress=30.0,
            voice_stress=25.0,
            pulse_stress=20.0
        )
        
        print(f"  Honesty Score: {result['honesty_score']:.1f}/100")
        print(f"  Alert Level: {result['alert_level']}")
        print(f"  Components: Facial={result['component_scores']['facial_raw']:.1f}, "
              f"Voice={result['component_scores']['voice_raw']:.1f}, "
              f"Pulse={result['component_scores']['pulse_raw']:.1f}")
        
        # Verify calculation
        expected_combined = 0.4 * 30 + 0.3 * 25 + 0.3 * 20
        expected_honesty = 100 - expected_combined
        
        if abs(result['honesty_score'] - expected_honesty) < 0.1:
            print("✓ Logic engine calculations correct")
            return True
        else:
            print(f"✗ Logic engine calculation error. Expected {expected_honesty}, got {result['honesty_score']}")
            return False
            
    except Exception as e:
        print(f"✗ Logic engine test failed: {e}")
        return False


def test_camera():
    """Test camera access."""
    print("\nTesting camera access...")
    
    try:
        import cv2
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("✗ Could not open camera")
            return False
        
        ret, frame = cap.read()
        cap.release()
        
        if ret and frame is not None:
            print(f"✓ Camera accessible (resolution: {frame.shape[1]}x{frame.shape[0]})")
            return True
        else:
            print("✗ Could not read frame from camera")
            return False
            
    except Exception as e:
        print(f"✗ Camera test failed: {e}")
        return False


def test_mediapipe():
    """Test MediaPipe facial landmark detection."""
    print("\nTesting MediaPipe facial landmarks...")
    
    try:
        import cv2
        import mediapipe as mp
        
        # Create a dummy black image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        
        results = face_mesh.process(cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB))
        face_mesh.close()
        
        print("✓ MediaPipe initialized successfully")
        return True
        
    except Exception as e:
        print(f"✗ MediaPipe test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Lie-Dar System - Component Test Suite")
    print("=" * 60)
    
    results = {
        "Imports": test_imports(),
        "Modules": test_modules(),
        "Logic Engine": test_logic_engine(),
        "MediaPipe": test_mediapipe(),
        "Camera": test_camera()
    }
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:20s}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All tests passed! System is ready to run.")
        print("\nRun the full system with: python main.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        print("\nCommon issues:")
        print("- PyAudio: See README for platform-specific installation")
        print("- Camera: Ensure no other app is using the webcam")
        return 1


if __name__ == "__main__":
    sys.exit(main())
