"""
SafeRoute AI - Data Utilities
=============================
HazardRecord dataclass, mock data generator, and utility functions.
"""

import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

import numpy as np
import pandas as pd

from config import (
    DEMO_CITIES, HAZARD_TYPES, STATUS_OPTIONS, REPORTER_TYPES,
    DEFAULT_CITY
)


@dataclass
class HazardRecord:
    """Data class representing a road hazard record."""
    id: str
    hazard_type: str
    severity: str  # Low, Medium, High
    latitude: float
    longitude: float
    city: str
    description: str
    timestamp: datetime
    status: str
    confidence: float
    reported_by: str
    upvotes: int = 0
    image_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "hazard_type": self.hazard_type,
            "severity": self.severity,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "city": self.city,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "confidence": self.confidence,
            "reported_by": self.reported_by,
            "upvotes": self.upvotes,
            "image_path": self.image_path
        }


# Severity distribution: 30% Low, 45% Medium, 25% High
SEVERITY_WEIGHTS = [0.30, 0.45, 0.25]
SEVERITY_LEVELS = ["Low", "Medium", "High"]

# Status distribution
STATUS_WEIGHTS = [0.15, 0.20, 0.25, 0.40]
STATUS_DISTRIBUTION = dict(zip(STATUS_OPTIONS, STATUS_WEIGHTS))

# Reporter distribution
REPORTER_WEIGHTS = [0.50, 0.30, 0.10, 0.10]
REPORTER_DISTRIBUTION = dict(zip(REPORTER_TYPES, REPORTER_WEIGHTS))

# Hazard type descriptions
HAZARD_DESCRIPTIONS = {
    "Pothole": [
        "Deep pothole causing vehicle damage",
        "Large pothole on main road",
        "Multiple potholes in sequence",
        "Water-filled pothole"
    ],
    "Road Crack": [
        "Longitudinal crack on road surface",
        "Wide crack requiring immediate attention",
        "Multiple cracks forming pattern",
        "Crack with vegetation growth"
    ],
    "Waterlogging": [
        "Severe water accumulation after rain",
        "Road flooded due to drainage issue",
        "Standing water covering half the road",
        "Water level hazardous for two-wheelers"
    ],
    "Road Wear": [
        "Significant surface wear and tear",
        "Road texture deteriorated",
        "Uneven road surface",
        "Exposed aggregate causing skidding"
    ],
    "Debris": [
        "Construction debris on road",
        "Fallen tree branches blocking lane",
        "Scattered stones and rubble",
        "Abandoned objects on road"
    ]
}


def generate_mock_hazards(n: int = 80, seed: int = 42) -> List[HazardRecord]:
    """
    Generate mock hazard records for demo purposes.
    
    Args:
        n: Number of hazards to generate
        seed: Random seed for reproducibility
    
    Returns:
        List of HazardRecord objects
    """
    random.seed(seed)
    np.random.seed(seed)
    
    hazards: List[HazardRecord] = []
    
    # Get today's date for timestamp generation
    today = datetime.now()
    
    for i in range(n):
        # Random city
        city_data = random.choice(DEMO_CITIES)
        city_name = city_data["name"]
        
        # Add random offset to city coordinates (within ~5km)
        lat_offset = np.random.uniform(-0.03, 0.03)
        lon_offset = np.random.uniform(-0.03, 0.03)
        
        latitude = city_data["lat"] + lat_offset
        longitude = city_data["lon"] + lon_offset
        
        # Random hazard type
        hazard_type = random.choice(HAZARD_TYPES)
        
        # Severity based on weighted distribution
        severity = random.choices(SEVERITY_LEVELS, weights=SEVERITY_WEIGHTS, k=1)[0]
        
        # Status (more likely to be fixed over time)
        status = random.choices(
            list(STATUS_DISTRIBUTION.keys()),
            weights=list(STATUS_DISTRIBUTION.values()),
            k=1
        )[0]
        
        # Reporter type
        reported_by = random.choices(
            list(REPORTER_DISTRIBUTION.keys()),
            weights=list(REPORTER_DISTRIBUTION.values()),
            k=1
        )[0]
        
        # Timestamp within last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        timestamp = today - timedelta(days=days_ago, hours=hours_ago)
        
        # Confidence between 0.72 and 0.99
        confidence = round(random.uniform(0.72, 0.99), 2)
        
        # Description
        description = random.choice(HAZARD_DESCRIPTIONS[hazard_type])
        
        # Upvotes (0-15)
        upvotes = random.randint(0, 15)
        
        # Generate unique ID
        hazard_id = f"HR-{city_name[:3].upper()}-{i+1:04d}"
        
        hazard = HazardRecord(
            id=hazard_id,
            hazard_type=hazard_type,
            severity=severity,
            latitude=round(latitude, 6),
            longitude=round(longitude, 6),
            city=city_name,
            description=description,
            timestamp=timestamp,
            status=status,
            confidence=confidence,
            reported_by=reported_by,
            upvotes=upvotes,
            image_path=None
        )
        
        hazards.append(hazard)
    
    # Sort by timestamp (most recent first)
    hazards.sort(key=lambda x: x.timestamp, reverse=True)
    
    return hazards


def hazards_to_dataframe(hazards: List[HazardRecord]) -> pd.DataFrame:
    """
    Convert list of HazardRecord to pandas DataFrame.
    
    Args:
        hazards: List of HazardRecord objects
    
    Returns:
        DataFrame with hazard data
    """
    if not hazards:
        return pd.DataFrame()
    
    data = [h.to_dict() for h in hazards]
    df = pd.DataFrame(data)
    
    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    return df


def compute_stats(hazards: List[HazardRecord]) -> Dict[str, Any]:
    """
    Compute statistics from hazard records.
    
    Args:
        hazards: List of HazardRecord objects
    
    Returns:
        Dictionary with computed statistics
    """
    if not hazards:
        return {
            "total_hazards": 0,
            "high_severity_count": 0,
            "fixed_count": 0,
            "ai_accuracy": 0.0,
            "active_issues": 0,
            "by_type": {},
            "by_severity": {},
            "by_city": {},
            "by_status": {}
        }
    
    df = hazards_to_dataframe(hazards)
    
    # Total hazards
    total = len(hazards)
    
    # High severity count
    high_severity = len([h for h in hazards if h.severity == "High"])
    
    # Fixed count
    fixed_count = len([h for h in hazards if h.status == "Fixed"])
    
    # Active issues (not fixed)
    active_issues = total - fixed_count
    
    # AI accuracy (average confidence for AI-reported hazards)
    ai_hazards = [h for h in hazards if h.reported_by == "AI Detection"]
    ai_accuracy = sum(h.confidence for h in ai_hazards) / len(ai_hazards) * 100 if ai_hazards else 0.0
    
    # By type
    by_type = df["hazard_type"].value_counts().to_dict()
    
    # By severity
    by_severity = df["severity"].value_counts().to_dict()
    
    # By city
    by_city = df["city"].value_counts().to_dict()
    
    # By status
    by_status = df["status"].value_counts().to_dict()
    
    return {
        "total_hazards": total,
        "high_severity_count": high_severity,
        "fixed_count": fixed_count,
        "ai_accuracy": round(ai_accuracy, 1),
        "active_issues": active_issues,
        "by_type": by_type,
        "by_severity": by_severity,
        "by_city": by_city,
        "by_status": by_status
    }


def get_city_coordinates(city_name: str) -> tuple:
    """Get coordinates for a city."""
    for city in DEMO_CITIES:
        if city["name"] == city_name:
            return (city["lat"], city["lon"])
    # Default to Mumbai
    return (DEMO_CITIES[0]["lat"], DEMO_CITIES[0]["lon"])


def mock_route(
    start: str, 
    end: str, 
    hazards: List[HazardRecord],
    avoid_severity: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a mock route between two cities.
    
    Args:
        start: Start city name
        end: End city name
        hazards: List of hazard records
        avoid_severity: Severity level to avoid (optional)
    
    Returns:
        Dictionary with route information
    """
    start_coords = get_city_coordinates(start)
    end_coords = get_city_coordinates(end)
    
    # Calculate approximate distance using coordinate difference
    lat_diff = abs(start_coords[0] - end_coords[0])
    lon_diff = abs(start_coords[1] - end_coords[1])
    distance_km = round(np.sqrt(lat_diff**2 + lon_diff**2) * 111, 1)  # Rough conversion
    
    # Estimated duration (assuming 40 km/h average speed)
    duration_min = round(distance_km / 40 * 60)
    
    # Generate waypoints (simple straight line for demo)
    num_waypoints = 5
    waypoints = []
    for i in range(num_waypoints + 1):
        lat = start_coords[0] + (end_coords[0] - start_coords[0]) * i / num_waypoints
        lon = start_coords[1] + (end_coords[1] - start_coords[1]) * i / num_waypoints
        waypoints.append((lat, lon))
    
    # Filter hazards on route (simple distance check)
    hazards_on_route = []
    hazard_score = 0
    
    for hazard in hazards:
        # Check if hazard is near the route
        for waypoint in waypoints:
            distance = np.sqrt(
                (hazard.latitude - waypoint[0])**2 + 
                (hazard.longitude - waypoint[1])**2
            )
            # Within ~0.1 degrees (~10km)
            if distance < 0.1:
                if avoid_severity and hazard.severity == avoid_severity:
                    continue
                hazards_on_route.append(hazard)
                # Add to hazard score based on severity
                if hazard.severity == "High":
                    hazard_score += 3
                elif hazard.severity == "Medium":
                    hazard_score += 2
                else:
                    hazard_score += 1
                break
    
    # Cap hazard score at 10
    hazard_score = min(hazard_score, 10)
    
    return {
        "start": start,
        "end": end,
        "start_coords": start_coords,
        "end_coords": end_coords,
        "waypoints": waypoints,
        "distance_km": distance_km,
        "duration_min": duration_min,
        "hazard_score": hazard_score,
        "hazards_on_route": hazards_on_route,
        "num_hazards": len(hazards_on_route)
    }


def filter_hazards(
    hazards: List[HazardRecord],
    city: Optional[str] = None,
    severity: Optional[List[str]] = None,
    hazard_type: Optional[List[str]] = None,
    status: Optional[List[str]] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[HazardRecord]:
    """
    Filter hazard records by various criteria.
    
    Args:
        hazards: List of HazardRecord objects
        city: City name to filter by
        severity: List of severity levels
        hazard_type: List of hazard types
        status: List of statuses
        start_date: Start date for timestamp filter
        end_date: End date for timestamp filter
    
    Returns:
        Filtered list of HazardRecord objects
    """
    filtered = hazards
    
    if city and city != "All India":
        filtered = [h for h in filtered if h.city == city]
    
    if severity:
        filtered = [h for h in filtered if h.severity in severity]
    
    if hazard_type:
        filtered = [h for h in filtered if h.hazard_type in hazard_type]
    
    if status:
        filtered = [h for h in filtered if h.status in status]
    
    if start_date:
        filtered = [h for h in filtered if h.timestamp >= start_date]
    
    if end_date:
        filtered = [h for h in filtered if h.timestamp <= end_date]
    
    return filtered
