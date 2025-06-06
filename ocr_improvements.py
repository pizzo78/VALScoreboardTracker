"""
OCR Improvements Module
Enhanced OCR processing for better leet speak detection and highlighted player recognition
"""

import re
import cv2
import numpy as np
from typing import Dict, List, Tuple
import pytesseract

class EnhancedOCR:
    """Enhanced OCR with leet speak detection and highlighted player recognition"""
    
    def __init__(self):
        # Leet speak character mappings
        self.leet_mappings = {
            '0': 'o',
            '1': 'i',
            '3': 'e',
            '4': 'a',
            '5': 's',
            '6': 'g',
            '7': 't',
            '8': 'b',
            '9': 'g',
            '@': 'a',
            '!': 'i',
            '$': 's',
            '+': 't',
            '|': 'i',
            '()': 'o',
            '[]': 'o',
            '{}': 'o',
            '<>': 'o',
            '/\\': 'a',
            '\\/': 'v',
            '|_': 'l',
            '|-|': 'h',
            '|\\|': 'n',
            '|\\/|': 'm',
            '|_|': 'u',
            '\\|/': 'y',
            '\\_/': 'u',
            '><': 'x',
            '2': 'z',
        }
        
        # Common leet patterns
        self.leet_patterns = [
            (r'ph', 'f'),
            (r'ck', 'k'),
            (r'qu', 'kw'),
            (r'x', 'ks'),
            (r'z', 's'),
        ]
        
        # Enhanced OCR configurations
        self.ocr_configs = [
            # Standard configuration
            '-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/_ --psm 7',
            # Include special characters for leet speak
            '-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/_@!$+|()[]{}\\<>/- --psm 7',
            # More permissive for difficult text
            '--psm 8',
            # Single word mode
            '--psm 8 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/_@!$+|()[]{}\\<>/-',
        ]

    def detect_highlighted_player(self, image_colored: np.ndarray, cell_row: List) -> Tuple[bool, np.ndarray]:
        """
        Detect if a player row is highlighted (yellow background in VALORANT)
        Returns (is_highlighted, processed_image)
        """
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(image_colored, cv2.COLOR_BGR2HSV)
            
            # Define yellow color range for VALORANT highlight
            # Yellow in HSV: Hue 20-30, Saturation 100-255, Value 100-255
            lower_yellow = np.array([15, 50, 50])
            upper_yellow = np.array([35, 255, 255])
            
            # Create mask for yellow areas
            yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
            
            # Calculate percentage of yellow pixels
            total_pixels = yellow_mask.shape[0] * yellow_mask.shape[1]
            yellow_pixels = cv2.countNonZero(yellow_mask)
            yellow_percentage = (yellow_pixels / total_pixels) * 100
            
            # If more than 10% of the area is yellow, consider it highlighted
            is_highlighted = yellow_percentage > 10
            
            if is_highlighted:
                # For highlighted players, enhance contrast differently
                # Convert to grayscale
                gray = cv2.cvtColor(image_colored, cv2.COLOR_BGR2GRAY)
                
                # Apply adaptive threshold to handle yellow background
                processed = cv2.adaptiveThreshold(
                    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
                )
                
                # Invert if needed (text should be black on white)
                if np.mean(processed) < 127:
                    processed = cv2.bitwise_not(processed)
                
                return True, processed
            else:
                # Standard processing for non-highlighted players
                gray = cv2.cvtColor(image_colored, cv2.COLOR_BGR2GRAY)
                return False, gray
                
        except Exception as e:
            # Fallback to standard processing
            gray = cv2.cvtColor(image_colored, cv2.COLOR_BGR2GRAY)
            return False, gray

    def normalize_leet_speak(self, text: str) -> str:
        """Convert leet speak to normal text"""
        if not text:
            return text
            
        normalized = text.lower()
        
        # Apply character mappings
        for leet_char, normal_char in self.leet_mappings.items():
            normalized = normalized.replace(leet_char, normal_char)
        
        # Apply pattern replacements
        for leet_pattern, normal_pattern in self.leet_patterns:
            normalized = re.sub(leet_pattern, normal_pattern, normalized)
        
        return normalized

    def enhanced_ocr_name(self, image: np.ndarray, is_highlighted: bool = False) -> str:
        """
        Enhanced OCR for player names with leet speak support
        """
        best_result = ""
        best_confidence = 0
        
        # Try multiple OCR configurations
        for config in self.ocr_configs:
            try:
                # Get OCR result with confidence
                data = pytesseract.image_to_data(
                    image, 
                    config=config, 
                    lang='eng+kor+jpn+chi_sim',
                    output_type=pytesseract.Output.DICT
                )
                
                # Extract text and calculate average confidence
                words = []
                confidences = []
                
                for i, word in enumerate(data['text']):
                    if word.strip() and int(data['conf'][i]) > 30:  # Minimum confidence threshold
                        words.append(word.strip())
                        confidences.append(int(data['conf'][i]))
                
                if words and confidences:
                    result_text = ' '.join(words)
                    avg_confidence = sum(confidences) / len(confidences)
                    
                    # Bonus for highlighted players (they're usually more important)
                    if is_highlighted:
                        avg_confidence += 10
                    
                    if avg_confidence > best_confidence:
                        best_confidence = avg_confidence
                        best_result = result_text
                        
            except Exception as e:
                continue
        
        # If no good result, try basic OCR
        if not best_result or best_confidence < 40:
            try:
                basic_result = pytesseract.image_to_string(
                    image, 
                    config=self.ocr_configs[0], 
                    lang='eng+kor+jpn+chi_sim'
                ).strip()
                if basic_result:
                    best_result = basic_result
            except:
                pass
        
        # Clean up the result
        if best_result:
            # Remove common OCR artifacts
            best_result = re.sub(r'[^\w\s\-_\.\|@!$+]', '', best_result)
            best_result = re.sub(r'\s+', ' ', best_result).strip()
            
            # If result looks like leet speak, also store normalized version
            normalized = self.normalize_leet_speak(best_result)
            
            # Return both original and normalized if they're different
            if normalized != best_result.lower() and len(normalized) > 2:
                return f"{best_result} ({normalized})"
            
        return best_result if best_result else "err"

    def preprocess_name_image(self, image: np.ndarray, is_highlighted: bool = False) -> np.ndarray:
        """
        Enhanced preprocessing for name images
        """
        try:
            if len(image.shape) == 3:
                # Convert to grayscale if colored
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Resize for better OCR
            scale_factor = 3
            height, width = gray.shape
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            resized = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            if is_highlighted:
                # Special processing for highlighted text
                # Apply Gaussian blur to reduce noise
                blurred = cv2.GaussianBlur(resized, (3, 3), 0)
                
                # Use adaptive threshold for better contrast
                thresh = cv2.adaptiveThreshold(
                    blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 2
                )
                
                # Morphological operations to clean up
                kernel = np.ones((2, 2), np.uint8)
                cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
                cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
                
            else:
                # Standard processing for non-highlighted text
                # Apply bilateral filter to reduce noise while preserving edges
                filtered = cv2.bilateralFilter(resized, 9, 75, 75)
                
                # Apply threshold
                _, thresh = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                
                # Ensure text is black on white background
                if np.mean(thresh) < 127:
                    thresh = cv2.bitwise_not(thresh)
                
                cleaned = thresh
            
            # Add border for better OCR
            bordered = cv2.copyMakeBorder(
                cleaned, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=255
            )
            
            return bordered
            
        except Exception as e:
            # Fallback to simple processing
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Simple resize and threshold
            resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            _, thresh = cv2.threshold(resized, 127, 255, cv2.THRESH_BINARY)
            
            return thresh

# Global instance for use in other modules
enhanced_ocr = EnhancedOCR()