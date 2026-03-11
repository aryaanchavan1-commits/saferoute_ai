"""
SafeRoute AI - Hazard Detection Engine
======================================
OpenCV-based road hazard detection (simulating YOLOv8).
Uses thresholding, contour detection, and color analysis.
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional

from PIL import Image

from config import HAZARD_TYPES, MIN_CONTOUR_AREA


@dataclass
class Detection:
    """Data class for a detected hazard."""
    hazard_type: str
    confidence: float
    severity: str
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    
    def to_dict(self):
        return {
            "hazard_type": self.hazard_type,
            "confidence": self.confidence,
            "severity": self.severity,
            "bbox": self.bbox
        }


class HazardDetector:
    """
    OpenCV-based road hazard detection engine.
    
    Simulates YOLOv8 detection using:
    - Stage 1: cv2.threshold on grayscale → dark patches → Pothole / Road Crack
    - Stage 2: Blue channel dominance → Waterlogging
    - Stage 3: cv2.Canny edge density → Road Wear / Damage
    - Stage 4: Brightness variance → Debris
    - Stage 5: If nothing found → "Clear Road"
    """
    
    def __init__(self, confidence_threshold: float = 0.5):
        """
        Initialize the hazard detector.
        
        Args:
            confidence_threshold: Minimum confidence for detections
        """
        self.confidence_threshold = confidence_threshold
    
    def detect(self, pil_image: Image.Image) -> Tuple[Image.Image, List[Detection]]:
        """
        Detect hazards in an image.
        
        Args:
            pil_image: PIL Image object
            
        Returns:
            Tuple of (annotated PIL image, list of Detection objects)
        """
        # Convert PIL to OpenCV format
        cv_image = self._pil_to_cv2(pil_image)
        
        # Create annotated image (copy)
        annotated = cv_image.copy()
        
        # Run detection stages
        detections = []
        
        # Stage 1: Detect potholes and road cracks (dark patches)
        pothole_detections = self._detect_dark_patches(cv_image)
        detections.extend(pothole_detections)
        
        # Stage 2: Detect waterlogging (blue channel)
        waterlogging_detections = self._detect_waterlogging(cv_image)
        detections.extend(waterlogging_detections)
        
        # Stage 3: Detect road wear (edge density)
        road_wear_detections = self._detect_road_wear(cv_image)
        detections.extend(road_wear_detections)
        
        # Stage 4: Detect debris (brightness variance)
        debris_detections = self._detect_debris(cv_image)
        detections.extend(debris_detections)
        
        # If no hazards found, mark as clear road
        if not detections:
            h, w = cv_image.shape[:2]
            # Draw "Clear Road" message
            cv2.putText(
                annotated,
                "Clear Road - No hazards detected",
                (w // 4, h // 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                2
            )
        else:
            # Draw detections on annotated image
            for det in detections:
                self._draw_detection(annotated, det)
        
        # Convert back to PIL
        annotated_pil = self._cv2_to_pil(annotated)
        
        return annotated_pil, detections
    
    def _pil_to_cv2(self, pil_image: Image.Image) -> np.ndarray:
        """Convert PIL Image to OpenCV format."""
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    def _cv2_to_pil(self, cv_image: np.ndarray) -> Image.Image:
        """Convert OpenCV image to PIL Image."""
        return Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
    
    def _detect_dark_patches(self, image: np.ndarray) -> List[Detection]:
        """Detect potholes and road cracks using grayscale thresholding."""
        detections = []
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold to find dark patches
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > MIN_CONTOUR_AREA:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate confidence based on area and shape
                aspect_ratio = float(w) / h if h > 0 else 0
                extent = area / (w * h) if w * h > 0 else 0
                
                # Determine type based on shape
                if aspect_ratio > 2 or extent < 0.3:
                    hazard_type = "Road Crack"
                    confidence = min(0.95, 0.72 + (area / 10000))
                    severity = "Medium" if area < 5000 else "High"
                else:
                    hazard_type = "Pothole"
                    confidence = min(0.99, 0.75 + (area / 15000))
                    severity = "Medium" if area < 8000 else "High"
                
                if confidence >= self.confidence_threshold:
                    detections.append(Detection(
                        hazard_type=hazard_type,
                        confidence=round(confidence, 2),
                        severity=severity,
                        bbox=(x, y, w, h)
                    ))
        
        return detections
    
    def _detect_waterlogging(self, image: np.ndarray) -> List[Detection]:
        """Detect waterlogging using blue channel analysis."""
        detections = []
        
        # Split into BGR channels
        b, g, r = cv2.split(image)
        
        # Find areas where blue is dominant
        blue_dominant = cv2.bitwise_and(
            b,
            cv2.compare(b, g, cv2.CMP_GT),
            cv2.bitwise_and(b, r, cv2.compare(b, r, cv2.CMP_GT))
        )
        
        # Apply threshold
        _, thresh = cv2.threshold(blue_dominant, 50, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > MIN_CONTOUR_AREA * 1.5:
                x, y, w, h = cv2.boundingRect(contour)
                
                confidence = min(0.92, 0.70 + (area / 12000))
                severity = "Low" if area < 6000 else "Medium" if area < 12000 else "High"
                
                if confidence >= self.confidence_threshold:
                    detections.append(Detection(
                        hazard_type="Waterlogging",
                        confidence=round(confidence, 2),
                        severity=severity,
                        bbox=(x, y, w, h)
                    ))
        
        return detections
    
    def _detect_road_wear(self, image: np.ndarray) -> List[Detection]:
        """Detect road wear using Canny edge detection."""
        detections = []
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Canny edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Dilate edges to connect them
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > MIN_CONTOUR_AREA * 2:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate edge density
                roi = edges[y:y+h, x:x+w] if h > 0 and w > 0 else edges
                edge_density = np.sum(roi > 0) / roi.size if roi.size > 0 else 0
                
                if edge_density > 0.15:
                    confidence = min(0.88, 0.65 + edge_density)
                    severity = "Low" if area < 8000 else "Medium"
                    
                    if confidence >= self.confidence_threshold:
                        detections.append(Detection(
                            hazard_type="Road Wear",
                            confidence=round(confidence, 2),
                            severity=severity,
                            bbox=(x, y, w, h)
                        ))
        
        return detections
    
    def _detect_debris(self, image: np.ndarray) -> List[Detection]:
        """Detect debris using brightness variance."""
        detections = []
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate local variance (texture)
        kernel = np.ones((5, 5), np.float32) / 25
        local_mean = cv2.filter2D(gray.astype(float), -1, kernel)
        variance = np.abs(gray.astype(float) - local_mean)
        
        # Threshold to find high variance areas
        _, thresh = cv2.threshold(variance.astype(np.uint8), 30, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > MIN_CONTOUR_AREA:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate average variance in region
                roi = variance[y:y+h, x:x+w] if h > 0 and w > 0 else variance
                avg_variance = np.mean(roi) if roi.size > 0 else 0
                
                if avg_variance > 20:
                    confidence = min(0.85, 0.60 + (avg_variance / 100))
                    severity = "Low" if area < 5000 else "Medium"
                    
                    if confidence >= self.confidence_threshold:
                        detections.append(Detection(
                            hazard_type="Debris",
                            confidence=round(confidence, 2),
                            severity=severity,
                            bbox=(x, y, w, h)
                        ))
        
        return detections
    
    def _draw_detection(self, image: np.ndarray, detection: Detection) -> None:
        """Draw a detection on the image."""
        x, y, w, h = detection.bbox
        
        # Color based on hazard type
        color_map = {
            "Pothole": (0, 0, 255),      # Red
            "Road Crack": (0, 165, 255), # Orange
            "Waterlogging": (255, 0, 0), # Blue
            "Road Wear": (128, 0, 128),  # Purple
            "Debris": (128, 128, 128)    # Gray
        }
        
        color = color_map.get(detection.hazard_type, (0, 255, 0))
        
        # Draw rectangle
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        
        # Draw label background
        label = f"{detection.hazard_type}: {detection.confidence:.0%}"
        (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(image, (x, y - label_h - 10), (x + label_w, y), color, -1)
        
        # Draw label text
        cv2.putText(
            image,
            label,
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )


def create_demo_image(image_type: str = "pothole") -> Image.Image:
    """
    Create a demo image with simulated road hazards.
    
    Args:
        image_type: Type of hazard to simulate
    
    Returns:
        PIL Image with drawn hazard
    """
    # Create blank image (640x480)
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Fill with road-like gray background
    img[:, :] = (120, 125, 130)  # BGR
    
    if image_type == "pothole":
        # Draw dark irregular shapes
        cv2.ellipse(img, (200, 200), (60, 50), 0, 0, 360, (30, 30, 30), -1)
        cv2.ellipse(img, (450, 300), (40, 35), 30, 0, 360, (25, 25, 25), -1)
        
    elif image_type == "waterlogging":
        # Draw blue-ish water areas
        cv2.rectangle(img, (100, 150), (400, 350), (180, 120, 80), -1)
        cv2.rectangle(img, (150, 180), (350, 320), (160, 100, 60), -1)
        
    elif image_type == "crack":
        # Draw line cracks
        cv2.line(img, (50, 100), (200, 150), (40, 40, 40), 3)
        cv2.line(img, (200, 150), (250, 200), (40, 40, 40), 2)
        cv2.line(img, (250, 200), (300, 250), (40, 40, 40), 3)
        cv2.line(img, (400, 300), (550, 280), (35, 35, 35), 2)
        
    elif image_type == "debris":
        # Draw scattered debris
        for i in range(20):
            x = np.random.randint(50, 590)
            y = np.random.randint(50, 430)
            size = np.random.randint(5, 20)
            cv2.circle(img, (x, y), size, (80, 80, 80), -1)
            
    else:  # clear
        pass
    
    # Add road markings
    cv2.line(img, (320, 0), (320, 480), (200, 200, 200), 2)
    cv2.line(img, (0, 400), (640, 400), (180, 180, 180), 3)
    
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
