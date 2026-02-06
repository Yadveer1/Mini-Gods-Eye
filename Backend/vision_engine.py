# // [SYSTEM_CHECK]: GODS_EYE VISION ENGINE INITIALIZED
# // [CLASSIFICATION]: TACTICAL SURVEILLANCE MODULE
# // [STATUS]: ONLINE

"""
vision_engine.py - Core Visual Processing Unit for Mini God's Eye
Handles webcam capture, YOLOv8 inference, and frame annotation.
"""

import cv2
import csv
import threading
from datetime import datetime
from pathlib import Path
from typing import Generator, List, Tuple, Optional
from ultralytics import YOLO


class VisionEngine:
    """
    // [MODULE]: VisionEngine
    // [PURPOSE]: Real-time human detection and tracking system
    """
    
    # // [CONFIG]: Visual theme constants
    HUD_COLOR_CYAN = (255, 255, 0)      # BGR format - Cyan
    HUD_COLOR_RED = (0, 0, 255)          # BGR format - Red  
    HUD_COLOR_ORANGE = (0, 99, 255)      # BGR format - BO6 Orange (#FF6300)
    BOX_THICKNESS = 2
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    FONT_SCALE = 0.5
    FONT_THICKNESS = 1
    
    # // [CONFIG]: Performance tuning
    SKIP_FRAMES = 5  # Run YOLO inference every Nth frame
    PERSON_CLASS_ID = 0  # YOLO class ID for 'person'
    
    def __init__(self, camera_index: int = 0, log_file: str = "detection_history.csv"):
        """
        // [INIT]: Initialize the Vision Engine
        
        Args:
            camera_index: Webcam device index (default 0)
            log_file: Path to CSV file for detection persistence
        """
        # // [SYSTEM_LOG]: Loading neural network model...
        self.model = YOLO("yolov8n.pt")
        
        # // [SYSTEM_LOG]: Initializing camera feed...
        self.cap: Optional[cv2.VideoCapture] = None
        self.camera_index = camera_index
        
        # // [STATE]: Detection tracking
        self.last_detections: List[Tuple[int, int, int, int, float]] = []
        self.frame_count = 0
        self.person_detected = False
        self.detection_logs: List[dict] = []
        
        # // [PERSISTENCE]: CSV log file
        self.log_file = Path(log_file)
        self._init_csv_log()
        
        # // [THREADING]: Lock for thread-safe operations
        self._lock = threading.Lock()
        
    def _init_csv_log(self) -> None:
        """
        // [SYSTEM_LOG]: Initialize CSV log file with headers if not exists
        """
        if not self.log_file.exists():
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'num_persons', 'confidence_avg'])
                
    def _log_detection(self, num_persons: int, avg_confidence: float) -> None:
        """
        // [DATA_PERSISTENCE]: Write detection to CSV and memory log
        """
        timestamp = datetime.now().isoformat()
        
        # // [WRITE]: Append to CSV file immediately
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, num_persons, f"{avg_confidence:.2f}"])
        
        # // [MEMORY]: Store in RAM for API access
        with self._lock:
            self.detection_logs.append({
                "timestamp": timestamp,
                "num_persons": num_persons,
                "confidence": round(avg_confidence, 2)
            })
            # // [CLEANUP]: Keep last 1000 entries in memory
            if len(self.detection_logs) > 1000:
                self.detection_logs = self.detection_logs[-1000:]
    
    def _draw_hud_box(
        self, 
        frame, 
        x1: int, 
        y1: int, 
        x2: int, 
        y2: int, 
        confidence: float
    ) -> None:
        """
        // [RENDER]: Draw tactical HUD-style bounding box with label
        """
        color = self.HUD_COLOR_ORANGE  # Using BO6 tactical orange
        
        # // [DRAW]: Main bounding rectangle
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, self.BOX_THICKNESS)
        
        # // [DRAW]: Corner accents for tactical feel
        corner_length = 15
        # Top-left corner
        cv2.line(frame, (x1, y1), (x1 + corner_length, y1), color, self.BOX_THICKNESS + 1)
        cv2.line(frame, (x1, y1), (x1, y1 + corner_length), color, self.BOX_THICKNESS + 1)
        # Top-right corner
        cv2.line(frame, (x2, y1), (x2 - corner_length, y1), color, self.BOX_THICKNESS + 1)
        cv2.line(frame, (x2, y1), (x2, y1 + corner_length), color, self.BOX_THICKNESS + 1)
        # Bottom-left corner
        cv2.line(frame, (x1, y2), (x1 + corner_length, y2), color, self.BOX_THICKNESS + 1)
        cv2.line(frame, (x1, y2), (x1, y2 - corner_length), color, self.BOX_THICKNESS + 1)
        # Bottom-right corner
        cv2.line(frame, (x2, y2), (x2 - corner_length, y2), color, self.BOX_THICKNESS + 1)
        cv2.line(frame, (x2, y2), (x2, y2 - corner_length), color, self.BOX_THICKNESS + 1)
        
        # // [LABEL]: Target acquisition text
        label = f"TARGET ACQUIRED: PERSON [Conf: {int(confidence * 100)}%]"
        label_size = cv2.getTextSize(label, self.FONT, self.FONT_SCALE, self.FONT_THICKNESS)[0]
        
        # // [DRAW]: Label background for readability
        cv2.rectangle(
            frame, 
            (x1, y1 - label_size[1] - 10), 
            (x1 + label_size[0] + 4, y1 - 2), 
            (0, 0, 0), 
            -1
        )
        
        # // [DRAW]: Label text
        cv2.putText(
            frame, 
            label, 
            (x1 + 2, y1 - 6), 
            self.FONT, 
            self.FONT_SCALE, 
            color, 
            self.FONT_THICKNESS
        )
    
    def _draw_hud_overlay(self, frame) -> None:
        """
        // [RENDER]: Draw tactical HUD overlay elements
        """
        height, width = frame.shape[:2]
        color = self.HUD_COLOR_ORANGE
        
        # // [DRAW]: Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, f"[GODS_EYE] {timestamp}", (10, 25), 
                    self.FONT, 0.5, color, 1)
        
        # // [DRAW]: Status indicator
        status = "TARGET ACQUIRED" if self.person_detected else "SEARCHING..."
        status_color = (0, 255, 0) if self.person_detected else (0, 165, 255)
        cv2.putText(frame, f"STATUS: {status}", (10, height - 15), 
                    self.FONT, 0.6, status_color, 2)
        
        # // [DRAW]: Frame counter
        cv2.putText(frame, f"FRAME: {self.frame_count}", (width - 120, 25), 
                    self.FONT, 0.4, color, 1)
    
    def _run_detection(self, frame) -> List[Tuple[int, int, int, int, float]]:
        """
        // [INFERENCE]: Run YOLOv8 detection on frame
        Returns list of (x1, y1, x2, y2, confidence) for persons only
        """
        results = self.model(frame, verbose=False)
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
                
            for box in boxes:
                cls = int(box.cls[0])
                if cls == self.PERSON_CLASS_ID:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    confidence = float(box.conf[0])
                    detections.append((x1, y1, x2, y2, confidence))
        
        return detections
    
    def process_frame(self, frame):
        """
        // [CORE]: Process a single frame with detection/annotation
        Implements frame skipping for performance optimization
        """
        self.frame_count += 1
        
        # // [OPTIMIZATION]: Only run YOLO on every Nth frame
        if self.frame_count % self.SKIP_FRAMES == 0:
            self.last_detections = self._run_detection(frame)
            
            # // [LOG]: Record detection if persons found
            if self.last_detections:
                self.person_detected = True
                avg_conf = sum(d[4] for d in self.last_detections) / len(self.last_detections)
                self._log_detection(len(self.last_detections), avg_conf)
            else:
                self.person_detected = False
        
        # // [RENDER]: Draw bounding boxes from last known detections
        for x1, y1, x2, y2, conf in self.last_detections:
            self._draw_hud_box(frame, x1, y1, x2, y2, conf)
        
        # // [RENDER]: Draw HUD overlay
        self._draw_hud_overlay(frame)
        
        return frame
    
    def generate_frames(self) -> Generator[bytes, None, None]:
        """
        // [STREAM]: Generator yielding JPEG-encoded frames for MJPEG streaming
        Implements robust camera handling with try/finally for stability
        """
        try:
            # // [INIT]: Open camera connection
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                raise RuntimeError(f"[CRITICAL] Failed to open camera {self.camera_index}")
            
            # // [CONFIG]: Camera settings for optimal performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # // [SYSTEM_LOG]: Camera feed initialized
            print(f"[GODS_EYE] Camera {self.camera_index} initialized successfully")
            
            while True:
                success, frame = self.cap.read()
                
                if not success:
                    print("[WARNING] Frame capture failed, retrying...")
                    continue
                
                # // [PROCESS]: Run detection and annotation
                processed_frame = self.process_frame(frame)
                
                # // [ENCODE]: Convert to JPEG for streaming
                _, buffer = cv2.imencode('.jpg', processed_frame, 
                                         [cv2.IMWRITE_JPEG_QUALITY, 80])
                frame_bytes = buffer.tobytes()
                
                # // [YIELD]: MJPEG multipart format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                       
        except Exception as e:
            print(f"[CRITICAL] Vision Engine error: {e}")
            raise
            
        finally:
            # // [CLEANUP]: ALWAYS release camera to prevent OS lock
            if self.cap is not None:
                self.cap.release()
                print("[GODS_EYE] Camera released successfully")
    
    def get_logs(self, limit: int = 50) -> List[dict]:
        """
        // [API]: Return recent detection logs
        """
        with self._lock:
            return self.detection_logs[-limit:]
    
    def get_status(self) -> dict:
        """
        // [API]: Return current detection status
        """
        return {
            "person_detected": self.person_detected,
            "frame_count": self.frame_count,
            "detections_count": len(self.last_detections)
        }
    
    def cleanup(self) -> None:
        """
        // [SHUTDOWN]: Clean shutdown of vision engine
        """
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
            print("[GODS_EYE] Vision Engine shutdown complete")
