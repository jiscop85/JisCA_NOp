"""Utility functions for ANPR system"""
import cv2
import numpy as np
from typing import List, Tuple
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

def draw_detections(image: np.ndarray, detections: List[dict], plate_texts: List[str] = None) -> np.ndarray:
    """
    Draw bounding boxes and text on image
    
    Args:
        image: Input image
        detections: List of detection dicts with bbox and confidence
        plate_texts: Optional list of recognized plate texts
        
    Returns:
        Annotated image
    """
    annotated = image.copy()
    
    for i, det in enumerate(detections):
        bbox = det['bbox']
        confidence = det['confidence']
        x1, y1, x2, y2 = bbox
        
        # Draw bounding box (cyan color for the cyberpunk theme)
        color = (255, 240, 0)  # Cyan in BGR
        thickness = 3
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, thickness)
        
        # Prepare label
        if plate_texts and i < len(plate_texts):
            label = f"{plate_texts[i]} ({confidence:.2f})"
        else:
            label = f"Plate {confidence:.2f}"
        
        # Draw label background
        (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.rectangle(annotated, (x1, y1 - text_h - 10), (x1 + text_w, y1), color, -1)
        
        # Draw label text
        cv2.putText(annotated, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.7, (0, 0, 0), 2, cv2.LINE_AA)
    
    return annotated

def save_image(image: np.ndarray, save_path: str) -> bool:
    """
    Save image to file
    
    Args:
        image: Image to save
        save_path: Destination path
        
    Returns:
        Success status
    """
    try:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(save_path, image)
        logger.info(f"Image saved to {save_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving image: {e}")
        return False

def encode_image_base64(image: np.ndarray) -> str:
    """
    Encode image to base64 string
    
    Args:
        image: Image as numpy array
        
    Returns:
        Base64 encoded string
    """
    import base64
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')

def decode_image_base64(base64_str: str) -> np.ndarray:
    """
    Decode base64 string to image
    
    Args:
        base64_str: Base64 encoded image string
        
    Returns:
        Image as numpy array
    """
    import base64
    img_bytes = base64.b64decode(base64_str)
    nparr = np.frombuffer(img_bytes, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def calculate_confidence_level(confidence: float) -> str:
    """
    Categorize confidence level
    
    Args:
        confidence: Confidence score (0-1)
        
    Returns:
        Category: 'high', 'medium', or 'low'
    """
    if confidence >= 0.7:
        return 'high'
    elif confidence >= 0.4:
        return 'medium'
    else:
        return 'low'

def format_timestamp(dt: datetime = None) -> str:
    """
    Format datetime for display
    
    Args:
        dt: Datetime object (default: now)
        
    Returns:
        Formatted string
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")
