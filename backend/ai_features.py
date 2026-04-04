"""Advanced AI features for JisCA_NOp"""
import numpy as np
import cv2
from typing import Tuple, List, Optional
import re
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)

class VehicleClassifier:
    """Classify vehicle type from detection"""
    
    def classify(self, image: np.ndarray, bbox: List[int]) -> str:
        """
        Classify vehicle type based on aspect ratio and size
        
        Args:
            image: Full image
            bbox: Bounding box [x1, y1, x2, y2]
            
        Returns:
            Vehicle type: car, truck, motorcycle, bus, van, unknown
        """
        try:
            x1, y1, x2, y2 = bbox
            height = y2 - y1
            width = x2 - x1
            aspect_ratio = width / height if height > 0 else 0
            
            # Simple heuristic classification
            if aspect_ratio < 2.0:
                return "motorcycle"
            elif aspect_ratio > 5.0:
                return "truck"
            elif aspect_ratio > 4.0:
                return "bus"
            elif aspect_ratio > 3.5:
                return "van"
            else:
                return "car"
        except Exception as e:
            logger.error(f"Error classifying vehicle: {e}")
            return "unknown"

class PlateRegionDetector:
    """Detect plate country/region from format"""
    
    # Pattern examples (simplified)
    PATTERNS = {
        "USA": r'^[A-Z]{1,3}[0-9]{1,4}$|^[0-9]{1,4}[A-Z]{1,3}$',
        "UK": r'^[A-Z]{2}[0-9]{2}[A-Z]{3}$',
        "EU": r'^[A-Z]{1,2}[0-9]{1,4}[A-Z]{1,3}$',
    }
    
    def detect_region(self, plate_text: str) -> Optional[str]:
        """
        Detect plate region from text pattern
        
        Args:
            plate_text: Cleaned plate text
            
        Returns:
            Region code or None
        """
        try:
            for region, pattern in self.PATTERNS.items():
                if re.match(pattern, plate_text):
                    return region
            return None
        except Exception as e:
            logger.error(f"Error detecting region: {e}")
            return None

class SmartSearch:
    """Fuzzy search for plates with OCR errors"""
    
    @staticmethod
    def similarity(str1: str, str2: str) -> float:
        """Calculate similarity ratio between strings"""
        return SequenceMatcher(None, str1.upper(), str2.upper()).ratio()
    
    @staticmethod
    def fuzzy_match(query: str, plates: List[str], threshold: float = 0.8) -> List[Tuple[str, float]]:
        """
        Find plates matching query with fuzzy logic
        
        Args:
            query: Search query
            plates: List of plate texts
            threshold: Minimum similarity (0-1)
            
        Returns:
            List of (plate, similarity_score) tuples
        """
        results = []
        for plate in plates:
            score = SmartSearch.similarity(query, plate)
            if score >= threshold:
                results.append((plate, score))
        
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results

class DuplicateDetector:
    """Detect duplicate/similar plates"""
    
    @staticmethod
    def find_duplicates(plates: List[dict], time_window_hours: int = 24) -> List[dict]:
        """
        Find duplicate detections within time window
        
        Args:
            plates: List of detection dicts with plate_text and timestamp
            time_window_hours: Time window for duplicate check
            
        Returns:
            List of duplicate groups
        """
        from datetime import timedelta
        
        duplicates = []
        checked = set()
        
        for i, plate1 in enumerate(plates):
            if i in checked:
                continue
            
            group = [plate1]
            for j, plate2 in enumerate(plates[i+1:], start=i+1):
                if j in checked:
                    continue
                
                # Check if same plate
                if plate1['plate_text'] == plate2['plate_text']:
                    # Check time window
                    time_diff = abs((plate2['timestamp'] - plate1['timestamp']).total_seconds() / 3600)
                    if time_diff <= time_window_hours:
                        group.append(plate2)
                        checked.add(j)
            
            if len(group) > 1:
                duplicates.append(group)
                checked.add(i)
        
        return duplicates

class AnalyticsEngine:
    """Analytics and predictions"""
    
    @staticmethod
    def calculate_stats(detections: List[dict]) -> dict:
        """
        Calculate analytics from detections
        
        Args:
            detections: List of detection dicts
            
        Returns:
            Statistics dictionary
        """
        if not detections:
            return {
                "total": 0,
                "avg_confidence": 0.0,
                "high_confidence": 0,
                "medium_confidence": 0,
                "low_confidence": 0,
                "unique_plates": 0,
                "vehicle_types": {}
            }
        
        total = len(detections)
        confidences = [d['confidence'] for d in detections]
        avg_confidence = sum(confidences) / total
        
        high = sum(1 for c in confidences if c >= 0.7)
        medium = sum(1 for c in confidences if 0.4 <= c < 0.7)
        low = sum(1 for c in confidences if c < 0.4)
        
        unique_plates = len(set(d['plate_text'] for d in detections))
        
        # Vehicle types distribution
        vehicle_types = {}
        for d in detections:
            vtype = d.get('vehicle_type', 'unknown')
            vehicle_types[vtype] = vehicle_types.get(vtype, 0) + 1
        
        return {
            "total": total,
            "avg_confidence": avg_confidence,
            "high_confidence": high,
            "medium_confidence": medium,
            "low_confidence": low,
            "unique_plates": unique_plates,
            "vehicle_types": vehicle_types
        }
    
    @staticmethod
    def predict_busy_hours(detections: List[dict]) -> List[int]:
        """
        Predict busy hours based on detection patterns
        
        Args:
            detections: List of detection dicts with timestamp
            
        Returns:
            List of hours (0-23) sorted by detection count
        """
        hour_counts = {}
        for d in detections:
            hour = d['timestamp'].hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Sort by count descending
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        return [hour for hour, count in sorted_hours[:5]]  # Top 5 busy hours
