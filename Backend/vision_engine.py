# // [SYSTEM_CHECK]: GODS_EYE VISION ENGINE v2.0 - IDENTITY RECOGNITION
# // [CLASSIFICATION]: TACTICAL SURVEILLANCE MODULE + DEEPFACE
# // [STATUS]: ONLINE

"""
vision_engine.py - Core Visual Processing Unit for Mini God's Eye
Handles webcam capture, YOLOv8 inference, facial recognition via DeepFace.
"""

import cv2
import csv
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Generator, List, Tuple, Optional, Dict
from ultralytics import YOLO

# // [IMPORT]: DeepFace for facial recognition
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
    # // [SUPPRESS]: TensorFlow warnings
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("[WARNING] DeepFace not installed. Identity recognition disabled.")


class FaceDatabase:
    """
    // [MODULE]: FaceDatabase
    // [PURPOSE]: Manage known faces folder for DeepFace verification
    """
    
    def __init__(self, known_faces_dir: str = "known_faces"):
        """
        // [INIT]: Initialize face database
        
        Args:
            known_faces_dir: Path to folder containing face images
        """
        self.known_faces_dir = Path(known_faces_dir)
        self.known_faces: Dict[str, str] = {}  # name -> image_path
        
        self._load_known_faces()
    
    def _load_known_faces(self) -> None:
        """
        // [SYSTEM_LOG]: Scan known_faces folder and catalog images
        """
        if not DEEPFACE_AVAILABLE:
            print("[FACE_DB] DeepFace library not available")
            return
            
        if not self.known_faces_dir.exists():
            print(f"[FACE_DB] Creating known_faces directory: {self.known_faces_dir}")
            self.known_faces_dir.mkdir(parents=True, exist_ok=True)
            return
        
        # // [SCAN]: Process each image file in the directory
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        
        for image_path in self.known_faces_dir.iterdir():
            if image_path.suffix.lower() not in valid_extensions:
                continue
                
            # // [STORE]: Use filename (without extension) as identity name
            name = image_path.stem.replace("_", " ").title()
            self.known_faces[name] = str(image_path.absolute())
            print(f"[FACE_DB] ✓ Registered: {name}")
        
        print(f"[FACE_DB] Loaded {len(self.known_faces)} known identities")
    
    def identify_face(self, face_image) -> Tuple[str, float, bool]:
        """
        // [IDENTIFY]: Compare face image against known faces using DeepFace
        
        Returns:
            Tuple of (name, confidence, is_known)
        """
        if not self.known_faces or not DEEPFACE_AVAILABLE:
            return ("UNKNOWN", 0.0, False)
        
        try:
            # // [COMPARE]: Check against each known face
            for name, known_path in self.known_faces.items():
                try:
                    result = DeepFace.verify(
                        img1_path=face_image,
                        img2_path=known_path,
                        model_name="VGG-Face",
                        enforce_detection=False,
                        detector_backend="opencv"
                    )
                    
                    if result["verified"]:
                        confidence = 1.0 - result["distance"]
                        return (name, confidence, True)
                        
                except Exception:
                    continue
            
            return ("UNKNOWN", 0.0, False)
            
        except Exception as e:
            print(f"[FACE_DB] Verification error: {e}")
            return ("ERROR", 0.0, False)


class VisionEngine:
    """
    // [MODULE]: VisionEngine v2.0
    // [PURPOSE]: Real-time human detection + facial recognition via DeepFace
    """
    
    # // [CONFIG]: Visual theme constants
    HUD_COLOR_GREEN = (0, 255, 0)        # BGR - Known identity
    HUD_COLOR_RED = (0, 0, 255)          # BGR - Unknown subject
    HUD_COLOR_ORANGE = (0, 99, 255)      # BGR - BO6 Orange (#FF6300)
    HUD_COLOR_CYAN = (255, 255, 0)       # BGR - Cyan accent
    BOX_THICKNESS = 2
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    FONT_SCALE = 0.5
    FONT_THICKNESS = 1
    
    # // [CONFIG]: Performance tuning
    SKIP_FRAMES = 5  # Run YOLO inference every Nth frame
    FACE_SKIP_FRAMES = 10  # Run face recognition every Nth detection frame (DeepFace is slower)
    PERSON_CLASS_ID = 0  # YOLO class ID for 'person'
    
    def __init__(
        self, 
        camera_index: int = 0, 
        log_file: str = "detection_history.csv",
        known_faces_dir: str = "known_faces"
    ):
        """
        // [INIT]: Initialize the Vision Engine with Face Recognition
        """
        # // [SYSTEM_LOG]: Loading neural network model...
        print("[GODS_EYE] Loading YOLOv8n model...")
        self.model = YOLO("yolov8n.pt")
        
        # // [SYSTEM_LOG]: Initialize face database
        print("[GODS_EYE] Loading face database...")
        self.face_db = FaceDatabase(known_faces_dir)
        
        # // [SYSTEM_LOG]: Initializing camera feed...
        self.cap: Optional[cv2.VideoCapture] = None
        self.camera_index = camera_index
        
        # // [STATE]: Detection tracking
        self.last_detections: List[Dict] = []
        self.frame_count = 0
        self.face_frame_count = 0
        self.person_detected = False
        self.identified_count = 0
        self.detection_logs: List[dict] = []
        
        # // [CACHE]: Store last identification results
        self.identity_cache: Dict[str, Tuple[str, float, bool]] = {}
        
        # // [PERSISTENCE]: CSV log file
        self.log_file = Path(log_file)
        self._init_csv_log()
        
        # // [THREADING]: Lock for thread-safe operations
        self._lock = threading.Lock()
        
    def _init_csv_log(self) -> None:
        """Initialize CSV log file"""
        if not self.log_file.exists():
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'num_persons', 'identified', 'names'])
                
    def _log_detection(self, num_persons: int, identified: int, names: List[str]) -> None:
        """Write detection to CSV and memory log"""
        timestamp = datetime.now().isoformat()
        names_str = ", ".join(names) if names else "UNKNOWN"
        
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, num_persons, identified, names_str])
        
        with self._lock:
            self.detection_logs.append({
                "timestamp": timestamp,
                "num_persons": num_persons,
                "identified": identified,
                "names": names
            })
            if len(self.detection_logs) > 1000:
                self.detection_logs = self.detection_logs[-1000:]
    
    def _draw_hud_box(
        self, 
        frame, 
        x1: int, y1: int, x2: int, y2: int,
        identity: str, confidence: float, is_known: bool
    ) -> None:
        """Draw tactical HUD-style bounding box"""
        color = self.HUD_COLOR_GREEN if is_known else self.HUD_COLOR_RED
        
        # // [DRAW]: Main bounding rectangle
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, self.BOX_THICKNESS)
        
        # // [DRAW]: Corner accents
        corner_length = 15
        thickness = self.BOX_THICKNESS + 1
        cv2.line(frame, (x1, y1), (x1 + corner_length, y1), color, thickness)
        cv2.line(frame, (x1, y1), (x1, y1 + corner_length), color, thickness)
        cv2.line(frame, (x2, y1), (x2 - corner_length, y1), color, thickness)
        cv2.line(frame, (x2, y1), (x2, y1 + corner_length), color, thickness)
        cv2.line(frame, (x1, y2), (x1 + corner_length, y2), color, thickness)
        cv2.line(frame, (x1, y2), (x1, y2 - corner_length), color, thickness)
        cv2.line(frame, (x2, y2), (x2 - corner_length, y2), color, thickness)
        cv2.line(frame, (x2, y2), (x2, y2 - corner_length), color, thickness)
        
        # // [LABEL]: Identity text
        if is_known:
            label = f"IDENTITY: {identity.upper()} [{int(confidence * 100)}%]"
        else:
            label = "UNKNOWN SUBJECT"
        
        label_size = cv2.getTextSize(label, self.FONT, self.FONT_SCALE, self.FONT_THICKNESS)[0]
        cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), (x1 + label_size[0] + 4, y1 - 2), (0, 0, 0), -1)
        cv2.putText(frame, label, (x1 + 2, y1 - 6), self.FONT, self.FONT_SCALE, color, self.FONT_THICKNESS)
    
    def _draw_hud_overlay(self, frame) -> None:
        """Draw tactical HUD overlay"""
        height, width = frame.shape[:2]
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, f"[GODS_EYE v2.0] {timestamp}", (10, 25), self.FONT, 0.5, self.HUD_COLOR_ORANGE, 1)
        
        db_status = f"FACE_DB: {len(self.face_db.known_faces)} IDENTITIES"
        cv2.putText(frame, db_status, (10, 45), self.FONT, 0.4, self.HUD_COLOR_CYAN, 1)
        
        if self.identified_count > 0:
            status = f"IDENTIFIED: {self.identified_count}"
            status_color = self.HUD_COLOR_GREEN
        elif self.person_detected:
            status = "UNKNOWN SUBJECTS DETECTED"
            status_color = self.HUD_COLOR_RED
        else:
            status = "SEARCHING..."
            status_color = self.HUD_COLOR_CYAN
            
        cv2.putText(frame, f"STATUS: {status}", (10, height - 15), self.FONT, 0.6, status_color, 2)
        cv2.putText(frame, f"FRAME: {self.frame_count}", (width - 120, 25), self.FONT, 0.4, self.HUD_COLOR_ORANGE, 1)
    
    def _identify_person(self, frame, x1: int, y1: int, x2: int, y2: int) -> Tuple[str, float, bool]:
        """Extract face from person crop and identify via DeepFace"""
        if not DEEPFACE_AVAILABLE:
            return ("N/A", 0.0, False)
        
        try:
            h, w = frame.shape[:2]
            pad = 10
            crop_y1 = max(0, y1 - pad)
            crop_y2 = min(h, y2 + pad)
            crop_x1 = max(0, x1 - pad)
            crop_x2 = min(w, x2 + pad)
            
            person_crop = frame[crop_y1:crop_y2, crop_x1:crop_x2]
            
            if person_crop.size == 0:
                return ("UNKNOWN", 0.0, False)
            
            # // [IDENTIFY]: Use DeepFace to match against known faces
            return self.face_db.identify_face(person_crop)
            
        except Exception as e:
            print(f"[IDENTIFY] Error: {e}")
            return ("ERROR", 0.0, False)
    
    def _run_detection(self, frame) -> List[Dict]:
        """Run YOLOv8 detection + facial recognition"""
        results = self.model(frame, verbose=False)
        detections = []
        
        self.face_frame_count += 1
        run_face_recognition = (self.face_frame_count % self.FACE_SKIP_FRAMES == 0)
        
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
                
            for box in boxes:
                cls = int(box.cls[0])
                if cls == self.PERSON_CLASS_ID:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    yolo_confidence = float(box.conf[0])
                    
                    # // [CACHE_KEY]: Use bbox center as cache key
                    cache_key = f"{(x1+x2)//50}_{(y1+y2)//50}"
                    
                    if run_face_recognition and DEEPFACE_AVAILABLE and len(self.face_db.known_faces) > 0:
                        identity, face_conf, is_known = self._identify_person(frame, x1, y1, x2, y2)
                        self.identity_cache[cache_key] = (identity, face_conf, is_known)
                    elif cache_key in self.identity_cache:
                        identity, face_conf, is_known = self.identity_cache[cache_key]
                    else:
                        identity, face_conf, is_known = "SCANNING...", 0.0, False
                    
                    detections.append({
                        "bbox": (x1, y1, x2, y2),
                        "yolo_conf": yolo_confidence,
                        "identity": identity,
                        "face_conf": face_conf,
                        "is_known": is_known
                    })
        
        return detections
    
    def process_frame(self, frame):
        """Process a single frame with detection/recognition/annotation"""
        self.frame_count += 1
        
        if self.frame_count % self.SKIP_FRAMES == 0:
            self.last_detections = self._run_detection(frame)
            
            if self.last_detections:
                self.person_detected = True
                known_names = [d["identity"] for d in self.last_detections if d["is_known"]]
                self.identified_count = len(known_names)
                self._log_detection(len(self.last_detections), self.identified_count, known_names)
            else:
                self.person_detected = False
                self.identified_count = 0
        
        for detection in self.last_detections:
            x1, y1, x2, y2 = detection["bbox"]
            self._draw_hud_box(frame, x1, y1, x2, y2, detection["identity"], detection["face_conf"], detection["is_known"])
        
        self._draw_hud_overlay(frame)
        return frame
    
    def generate_frames(self) -> Generator[bytes, None, None]:
        """Generator yielding JPEG-encoded frames for MJPEG streaming"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                raise RuntimeError(f"[CRITICAL] Failed to open camera {self.camera_index}")
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            print(f"[GODS_EYE] Camera {self.camera_index} initialized successfully")
            
            while True:
                success, frame = self.cap.read()
                
                if not success:
                    continue
                
                processed_frame = self.process_frame(frame)
                _, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                       
        except Exception as e:
            print(f"[CRITICAL] Vision Engine error: {e}")
            raise
        finally:
            if self.cap is not None:
                self.cap.release()
                print("[GODS_EYE] Camera released successfully")
    
    def get_logs(self, limit: int = 50) -> List[dict]:
        with self._lock:
            return self.detection_logs[-limit:]
    
    def get_status(self) -> dict:
        return {
            "person_detected": self.person_detected,
            "identified_count": self.identified_count,
            "frame_count": self.frame_count,
            "detections_count": len(self.last_detections),
            "known_faces_loaded": len(self.face_db.known_faces),
            "deepface_available": DEEPFACE_AVAILABLE
        }
    
    def cleanup(self) -> None:
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
            print("[GODS_EYE] Vision Engine shutdown complete")
