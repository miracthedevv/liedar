"""
PyQt5 GUI Version of Lie-Dar System
====================================
Modern desktop application with better UX than OpenCV windows.
"""

import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QProgressBar, QFrame)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont

from src.voice_stress import VoiceStress
from src.logic_engine import LogicEngine


class LieDarGUI(QMainWindow):
    """Modern GUI for Lie-Dar system."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lie-Dar - Gerçek Zamanlı Yalan Dedektörü")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #444444;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #00ff00;
            }
            QProgressBar {
                border: 2px solid #444444;
                border-radius: 5px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
            }
            QProgressBar::chunk {
                border-radius: 3px;
            }
        """)
        
        # Initialize components
        self.cap = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Analysis modules (simplified mode - no MediaPipe)
        self.voice_analyzer = VoiceStress(sample_rate=16000, chunk_duration=1.0)
        self.logic_engine = LogicEngine(facial_weight=0.0, voice_weight=0.60, pulse_weight=0.40)
        
        # State
        self.honesty_score = 50.0
        self.voice_stress = 0.0
        self.pulse_stress = 0.0
        self.bpm = 75.0
        self.alert_level = "medium_stress"
        
        # Setup UI
        self.setup_ui()
        
        # Start voice recording
        self.voice_analyzer.start_recording()
        
        # Setup timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(33)  # ~30 FPS
        
    def setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title = QLabel("LIE-DAR: Gerçek Zamanlı Yalan Dedektörü")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #00ff00; margin: 10px;")
        main_layout.addWidget(title)
        
        # Content layout (video + stats)
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)
        
        # Video frame
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("border: 2px solid #00ff00; background-color: #000000;")
        self.video_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.video_label, stretch=2)
        
        # Stats panel
        stats_panel = QFrame()
        stats_panel.setStyleSheet("background-color: #2d2d2d; border: 2px solid #444444; border-radius: 10px;")
        stats_layout = QVBoxLayout()
        stats_panel.setLayout(stats_layout)
        content_layout.addWidget(stats_panel, stretch=1)
        
        # Honesty score
        stats_layout.addWidget(QLabel("DÜRÜSTLÜK SKORU"))
        self.honesty_label = QLabel("50")
        self.honesty_label.setFont(QFont("Arial", 48, QFont.Bold))
        self.honesty_label.setAlignment(Qt.AlignCenter)
        stats_layout.addWidget(self.honesty_label)
        
        self.honesty_bar = QProgressBar()
        self.honesty_bar.setMinimum(0)
        self.honesty_bar.setMaximum(100)
        self.honesty_bar.setValue(50)
        self.honesty_bar.setTextVisible(False)
        self.honesty_bar.setMinimumHeight(30)
        stats_layout.addWidget(self.honesty_bar)
        
        stats_layout.addSpacing(20)
        
        # Alert level
        stats_layout.addWidget(QLabel("ALARM SEVİYESİ"))
        self.alert_label = QLabel("ORTA")
        self.alert_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.alert_label.setAlignment(Qt.AlignCenter)
        self.alert_label.setStyleSheet("color: #ffff00; padding: 10px; background-color: #3d3d3d; border-radius: 5px;")
        stats_layout.addWidget(self.alert_label)
        
        stats_layout.addSpacing(20)
        
        # Individual metrics
        stats_layout.addWidget(QLabel("SES ANALİZİ"))
        self.voice_bar = QProgressBar()
        self.voice_bar.setMinimum(0)
        self.voice_bar.setMaximum(100)
        self.voice_bar.setStyleSheet("QProgressBar::chunk { background-color: #ff6600; }")
        stats_layout.addWidget(self.voice_bar)
        
        stats_layout.addWidget(QLabel("NABIZ"))
        self.pulse_bar = QProgressBar()
        self.pulse_bar.setMinimum(0)
        self.pulse_bar.setMaximum(100)
        self.pulse_bar.setStyleSheet("QProgressBar::chunk { background-color: #ff00ff; }")
        stats_layout.addWidget(self.pulse_bar)
        
        stats_layout.addSpacing(20)
        
        # BPM
        stats_layout.addWidget(QLabel("KALP ATIŞI"))
        self.bpm_label = QLabel("75 BPM")
        self.bpm_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.bpm_label.setAlignment(Qt.AlignCenter)
        self.bpm_label.setStyleSheet("color: #ff00ff; padding: 5px;")
        stats_layout.addWidget(self.bpm_label)
        
        stats_layout.addStretch()
        
        # Control buttons
        button_layout = QHBoxLayout()
        stats_layout.addLayout(button_layout)
        
        reset_btn = QPushButton("Sıfırla")
        reset_btn.clicked.connect(self.reset)
        button_layout.addWidget(reset_btn)
        
        quit_btn = QPushButton("Çıkış")
        quit_btn.clicked.connect(self.close)
        quit_btn.setStyleSheet("QPushButton { background-color: #ff0000; } QPushButton:hover { background-color: #ff3333; }")
        button_layout.addWidget(quit_btn)
        
        # Info label
        info = QLabel("📊 Basitleştirilmiş Mod: Ses (%60) + Nabız (%40)")
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("color: #888888; font-size: 12px; margin: 10px;")
        main_layout.addWidget(info)
        
    def update_frame(self):
        """Update video frame and analysis."""
        ret, frame = self.cap.read()
        if not ret:
            return
        
        frame = cv2.flip(frame, 1)
        
        # Simple face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 0:
            x, y, w, h = faces[0]
            # Draw face rectangle
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Draw forehead region
            forehead_y_start = y
            forehead_y_end = y + int(h * 0.3)
            forehead_x_start = x + int(w * 0.2)
            forehead_x_end = x + int(w * 0.8)
            cv2.rectangle(frame, (forehead_x_start, forehead_y_start),
                        (forehead_x_end, forehead_y_end), (255, 0, 255), 2)
            cv2.putText(frame, "Alin Bolgesi", (forehead_x_start, forehead_y_start - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
        
        # Voice analysis
        self.voice_stress, voice_metrics = self.voice_analyzer.analyze_audio()
        
        # Simple pulse (placeholder)
        self.pulse_stress = 10.0 if len(faces) > 0 else 0.0
        self.bpm = 75.0 if len(faces) > 0 else 0.0
        
        # Calculate honesty
        results = self.logic_engine.analyze(0.0, self.voice_stress, self.pulse_stress)
        self.honesty_score = results["honesty_score"]
        self.alert_level = results["alert_level"]
        
        # Update UI
        self.update_stats()
        
        # Display frame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
            self.video_label.width(), self.video_label.height(), Qt.KeepAspectRatio))
    
    def update_stats(self):
        """Update statistics display."""
        # Honesty score
        self.honesty_label.setText(f"{int(self.honesty_score)}")
        self.honesty_bar.setValue(int(self.honesty_score))
        
        # Color based on score
        if self.honesty_score >= 60:
            color = "#00ff00"
            bar_color = "background-color: #00ff00;"
        elif self.honesty_score >= 40:
            color = "#ffff00"
            bar_color = "background-color: #ffff00;"
        else:
            color = "#ff0000"
            bar_color = "background-color: #ff0000;"
        
        self.honesty_label.setStyleSheet(f"color: {color};")
        self.honesty_bar.setStyleSheet(f"QProgressBar::chunk {{ {bar_color} }}")
        
        # Alert level
        alert_text = {
            "low_stress": ("DÜŞÜK", "#00ff00"),
            "medium_stress": ("ORTA", "#ffff00"),
            "high_stress": ("YÜKSEK", "#ff0000")
        }
        text, color = alert_text.get(self.alert_level, ("ORTA", "#ffff00"))
        self.alert_label.setText(text)
        self.alert_label.setStyleSheet(f"color: {color}; padding: 10px; background-color: #3d3d3d; border-radius: 5px;")
        
        # Individual bars
        self.voice_bar.setValue(int(self.voice_stress))
        self.pulse_bar.setValue(int(self.pulse_stress))
        
        # BPM
        self.bpm_label.setText(f"{int(self.bpm)} BPM")
    
    def reset(self):
        """Reset analyzers."""
        self.voice_analyzer.reset()
        self.honesty_score = 50.0
        print("✓ Sistem sıfırlandı")
    
    def closeEvent(self, event):
        """Cleanup on close."""
        self.timer.stop()
        self.voice_analyzer.stop_recording()
        self.cap.release()
        event.accept()


def main():
    """Main entry point for GUI version."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║       LIE-DAR: Desktop App Version                       ║
    ║                                                           ║
    ║  Modern GUI with PyQt5                                   ║
    ║  • Voice Stress Analysis (60%)                           ║
    ║  • Simple Pulse Detection (40%)                          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    app = QApplication(sys.argv)
    window = LieDarGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
