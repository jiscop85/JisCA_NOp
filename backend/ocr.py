"""EasyOCR Text Recognition Module with Advanced Preprocessing"""
import cv2
import numpy as np
import easyocr
from typing import Optional, Tuple, List
import logging
import re
from preprocessing import get_preprocessor

logger = logging.getLogger(__name__)

class PlateOCR:
    """OCR for license plate text recognition with advanced preprocessing"""
    
    def __init__(self, languages: list = None, fast_mode: bool = False):
        """
        Initialize EasyOCR reader
        
        Args:
            languages: List of language codes (default: ['en'])
            fast_mode: Use fast preprocessing (default: False for accuracy)
        """
        self.languages = languages or ['en']
        self.reader = None
        self.is_loaded = False
        self.fast_mode = fast_mode
        
        # Initialize appropriate preprocessor
        self.preprocessor = get_preprocessor('fast' if fast_mode else 'advanced')
    
    def load_reader(self) -> bool:
        """Load the EasyOCR reader"""
        try:
            logger.info(f"Loading EasyOCR with languages: {self.languages}")
            self.reader = easyocr.Reader(self.languages, gpu=False)
            self.is_loaded = True
            logger.info("EasyOCR loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading EasyOCR: {e}")
            self.is_loaded = False
            return False
    
    def read_plate(self, plate_img: np.ndarray, use_ensemble: bool = True) -> Tuple[str, float]:
        """
        Read text from license plate image with advanced preprocessing
        
        Args:
            plate_img: Cropped plate image
            use_ensemble: Use ensemble of preprocessing methods (default: True)
            
        Returns:
            Tuple of (plate_text, confidence)
        """
        if not self.is_loaded:
            if not self.load_reader():
                return "", 0.0
        
        try:
            if use_ensemble and not self.fast_mode:
                # Use multiple preprocessing methods and pick best result
                return self._ensemble_read(plate_img)
            else:
                # Single-pass reading with advanced preprocessing
                return self._single_read(plate_img)
            
        except Exception as e:
            logger.error(f"Error during OCR: {e}")
            return "", 0.0
    
    def _single_read(self, plate_img: np.ndarray) -> Tuple[str, float]:
        """Single-pass OCR with advanced preprocessing"""
        # Apply advanced preprocessing
        if self.fast_mode:
            from preprocessing import FastPreprocessor
            processed = FastPreprocessor.quick_ocr_prep(plate_img)
        else:
            gray, binary = self.preprocessor.preprocess_for_ocr(plate_img)
            
            # Try to deskew
            gray = self.preprocessor.deskew_plate(gray)
            
            # Use binary for OCR
            processed = binary
        
        # Run OCR
        results = self.reader.readtext(processed)
        
        if not results:
            # Fallback: try on grayscale
            gray_only = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY) if len(plate_img.shape) == 3 else plate_img
            results = self.reader.readtext(gray_only)
            
            if not results:
                logger.warning("No text detected in plate image")
                return "", 0.0
        
        # Get best result
        best_result = max(results, key=lambda x: x[2])
        text = best_result[1]
        confidence = best_result[2]
        
        # Clean up the text
        text = self.clean_plate_text(text)
        
        logger.info(f"OCR Result: '{text}' (confidence: {confidence:.2f})")
        return text, confidence
    
    def _ensemble_read(self, plate_img: np.ndarray) -> Tuple[str, float]:
        """
        Ensemble OCR with multiple preprocessing methods
        Picks the result with highest confidence
        """
        results = []
        
        # Method 1: Advanced preprocessing with CLAHE
        try:
            gray, binary = self.preprocessor.preprocess_for_ocr(plate_img)
            ocr_results = self.reader.readtext(binary)
            if ocr_results:
                best = max(ocr_results, key=lambda x: x[2])
                results.append({
                    'text': self.clean_plate_text(best[1]),
                    'confidence': best[2],
                    'method': 'advanced'
                })
        except Exception as e:
            logger.debug(f"Method 1 failed: {e}")
        
        # Method 2: Grayscale with deskewing
        try:
            gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY) if len(plate_img.shape) == 3 else plate_img
            gray = self.preprocessor.deskew_plate(gray)
            ocr_results = self.reader.readtext(gray)
            if ocr_results:
                best = max(ocr_results, key=lambda x: x[2])
                results.append({
                    'text': self.clean_plate_text(best[1]),
                    'confidence': best[2],
                    'method': 'deskew'
                })
        except Exception as e:
            logger.debug(f"Method 2 failed: {e}")
        
        # Method 3: High contrast enhancement
        try:
            enhanced = self.preprocessor.enhance_plate_contrast(plate_img)
            ocr_results = self.reader.readtext(enhanced)
            if ocr_results:
                best = max(ocr_results, key=lambda x: x[2])
                results.append({
                    'text': self.clean_plate_text(best[1]),
                    'confidence': best[2],
                    'method': 'contrast'
                })
        except Exception as e:
            logger.debug(f"Method 3 failed: {e}")
        
        # Method 4: Border removal
        try:
            no_borders = self.preprocessor.remove_borders(plate_img)
            ocr_results = self.reader.readtext(no_borders)
            if ocr_results:
                best = max(ocr_results, key=lambda x: x[2])
                results.append({
                    'text': self.clean_plate_text(best[1]),
                    'confidence': best[2],
                    'method': 'no_borders'
                })
        except Exception as e:
            logger.debug(f"Method 4 failed: {e}")
        
        if not results:
            logger.warning("All preprocessing methods failed")
            return "", 0.0
        
        # Pick result with highest confidence
        best_result = max(results, key=lambda x: x['confidence'])
        
        logger.info(f"Ensemble OCR: '{best_result['text']}' from {best_result['method']} "
                   f"(confidence: {best_result['confidence']:.2f})")
        
        return best_result['text'], best_result['confidence']
    
    def clean_plate_text(self, text: str) -> str:
        """
        Clean and format plate text with smart corrections
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text
        """
        # Remove special characters and spaces
        text = re.sub(r'[^A-Z0-9]', '', text.upper())
        
        # Common OCR mistakes correction
        corrections = {
            'O': '0',  # O to 0 in numeric context
            'I': '1',  # I to 1 in numeric context
            'S': '5',  # S to 5 in numeric context (sometimes)
            'Z': '2',  # Z to 2 in numeric context (sometimes)
            'B': '8',  # B to 8 in numeric context (sometimes)
        }
        
        # Smart correction based on plate patterns
        # US plates typically: 3 letters + 4 numbers or 4 numbers + 3 letters
        if len(text) >= 6:
            # If first 3 chars are likely letters, don't correct them
            # If last 4 chars are likely numbers, correct them
            parts = []
            for i, char in enumerate(text):
                if i < 3:  # Likely letters
                    parts.append(char)
                else:  # Likely numbers
                    parts.append(corrections.get(char, char) if char in corrections else char)
            text = ''.join(parts)
        
        return text
    
    def batch_read_plates(self, plate_images: List[np.ndarray]) -> List[Tuple[str, float]]:
        """
        Batch process multiple plate images
        
        Args:
            plate_images: List of plate crop images
            
        Returns:
            List of (plate_text, confidence) tuples
        """
        if not self.is_loaded:
            if not self.load_reader():
                return [("", 0.0)] * len(plate_images)
        
        results = []
        for plate_img in plate_images:
            try:
                text, conf = self.read_plate(plate_img, use_ensemble=False)  # Fast mode for batch
                results.append((text, conf))
            except Exception as e:
                logger.error(f"Batch read error: {e}")
                results.append(("", 0.0))
        
        return results
