"""YOLOv8 License Plate Detection Module"""
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PlateDetector:
    """License plate detector using YOLOv8"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the detector with a YOLOv8 model
        
        Args:
            model_path: Path to YOLOv8 model weights (.pt file)
        """
        self.model_path = model_path or str(Path(__file__).parent / "models" / "best.pt")
        self.model = None
        self.is_loaded = False
        
    def load_model(self) -> bool:
        """Load the YOLOv8 model"""
        try:
            # Check if custom model exists, otherwise use a pre-trained YOLO model
            if Path(self.model_path).exists():
                logger.info(f"Loading custom model from {self.model_path}")
                self.model = YOLO(self.model_path)
            else:
                logger.warning(f"Custom model not found at {self.model_path}")
                logger.info("Using YOLOv8n as fallback (note: not trained for license plates)")
                self.model = YOLO('yolov8n.pt')  # Fallback to general object detection
                
            self.is_loaded = True
            logger.info("Model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.is_loaded = False
            return False
    
    def detect(self, image: np.ndarray, conf_threshold: float = 0.25) -> List[dict]:
        """
        Detect license plates in an image
        
        Args:
            image: Input image as numpy array (BGR format)
            conf_threshold: Confidence threshold for detections
            
        Returns:
            List of detection dictionaries with keys:
                - bbox: [x1, y1, x2, y2]
                - confidence: float
                - class_id: int
        """
        if not self.is_loaded:
            if not self.load_model():
                return []
        
        try:
            # Run inference
            results = self.model(image, conf=conf_threshold, verbose=False)
            
       
