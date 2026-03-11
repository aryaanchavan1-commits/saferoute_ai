"""
SafeRoute AI - Configuration Constants
=====================================
AI-powered road hazard detection and smart navigation system for Indian roads.
CODE 1 Hackathon 2026, Team: mortal_coders
"""

from pathlib import Path
from typing import Final

# App Configuration
APP_NAME: Final[str] = "SafeRoute AI"
APP_VERSION: Final[str] = "1.0.0"
APP_ICON: Final[str] = "🛣️"
TEAM_NAME: Final[str] = "mortal_coders"
HACKATHON: Final[str] = ""


# Color Palette
COLOR_NAVY: Final[str] = "#0B1F3A"
COLOR_TEAL: Final[str] = "#0D9488"
COLOR_CORAL: Final[str] = "#F97316"
COLOR_WHITE: Final[str] = "#FFFFFF"
COLOR_LIGHT: Final[str] = "#F0FDFA"
COLOR_AMBER: Final[str] = "#F59E0B"
COLOR_RED: Final[str] = "#EF4444"
COLOR_GREEN: Final[str] = "#22C55E"
COLOR_CYAN: Final[str] = "#00D9FF"

# Severity Colors
SEVERITY_COLORS: Final[dict] = {
    "High": COLOR_RED,
    "Medium": COLOR_AMBER,
    "Low": COLOR_GREEN
}

# Hazard Type Colors (for maps and charts)
HAZARD_COLORS: Final[dict] = {
    "Pothole": "#EF4444",
    "Road Crack": "#F97316",
    "Waterlogging": "#3B82F6",
    "Road Wear": "#8B5CF6",
    "Debris": "#6B7280",
    "Clear Road": "#22C55E"
}

# Indian Cities with Coordinates (Real data)
DEMO_CITIES: Final[list] = [
    {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777, "state": "Maharashtra"},
    {"name": "Pune", "lat": 18.5204, "lon": 73.8567, "state": "Maharashtra"},
    {"name": "Delhi", "lat": 28.7041, "lon": 77.1025, "state": "Delhi"},
    {"name": "Bangalore", "lat": 12.9716, "lon": 77.5946, "state": "Karnataka"},
    {"name": "Chennai", "lat": 13.0827, "lon": 80.2707, "state": "Tamil Nadu"},
    {"name": "Hyderabad", "lat": 17.3850, "lon": 78.4867, "state": "Telangana"},
    {"name": "Chiplun", "lat": 17.5333, "lon": 73.5333, "state": "Maharashtra"},
    {"name": "Kolkata", "lat": 22.5726, "lon": 88.3639, "state": "West Bengal"},
    {"name": "Ahmedabad", "lat": 23.0225, "lon": 72.5714, "state": "Gujarat"},
    {"name": "Jaipur", "lat": 26.9124, "lon": 75.7873, "state": "Rajasthan"},
    {"name": "Surat", "lat": 21.1702, "lon": 72.8311, "state": "Gujarat"},
    {"name": "Lucknow", "lat": 26.8467, "lon": 80.9462, "state": "Uttar Pradesh"},
    {"name": "Kanpur", "lat": 26.4499, "lon": 80.3319, "state": "Uttar Pradesh"},
    {"name": "Nagpur", "lat": 21.1458, "lon": 79.0882, "state": "Maharashtra"},
    {"name": "Indore", "lat": 22.7196, "lon": 75.8577, "state": "Madhya Pradesh"},
    {"name": "Thane", "lat": 19.1860, "lon": 72.9750, "state": "Maharashtra"},
    {"name": "Bhopal", "lat": 23.2599, "lon": 77.4126, "state": "Madhya Pradesh"},
    {"name": "Visakhapatnam", "lat": 17.6868, "lon": 83.2185, "state": "Andhra Pradesh"},
    {"name": "Vadodara", "lat": 22.3072, "lon": 73.1812, "state": "Gujarat"},
    {"name": "Guwahati", "lat": 26.1445, "lon": 91.7362, "state": "Assam"}
]

CITY_NAMES: Final[list] = [city["name"] for city in DEMO_CITIES]

# Hazard Types
HAZARD_TYPES: Final[list] = [
    "Pothole",
    "Road Crack",
    "Waterlogging",
    "Road Wear",
    "Debris"
]

# Status Options
STATUS_OPTIONS: Final[list] = [
    "Reported",
    "Under Review",
    "In Progress",
    "Fixed"
]

# Reporters
REPORTER_TYPES: Final[list] = [
    "AI Detection",
    "User Report",
    "Municipality",
    "Traffic Police"
]

# Project Paths
BASE_DIR: Final[Path] = Path(__file__).parent
ASSETS_DIR: Final[Path] = BASE_DIR / "assets"
PAGES_DIR: Final[Path] = BASE_DIR / "pages"
UTILS_DIR: Final[Path] = BASE_DIR / "utils"

# Default Settings
DEFAULT_CITY: Final[str] = "Mumbai"
DEFAULT_SEVERITY_THRESHOLD: Final[int] = 70
DEFAULT_HEATMAP_ENABLED: Final[bool] = True
DEFAULT_DARK_MAP: Final[bool] = False

# Map Settings
DEFAULT_MAP_ZOOM: Final[int] = 12
MAP_TILE_LIGHT: Final[str] = "OpenStreetMap"
MAP_TILE_DARK: Final[str] = "CartoDB dark_matter"

# Detection Settings
CONFIDENCE_THRESHOLD: Final[float] = 0.5
MIN_CONTOUR_AREA: Final[int] = 500

# Page Navigation
PAGES: Final[dict] = {
    "Dashboard": "📊",
    "Hazard Detection": "🔍",
    "Hazard Map": "🗺️",
    "Route Planner": "🧭",
    "Chatbot": "💬",
    "Analytics": "📈",
    "Govt Report": "📄",
    "Settings": "⚙️"
}

# ==================== REAL API CONFIGURATION ====================

# Nominatim (OpenStreetMap) - Free, Unlimited geocoding
NOMINATIM_BASE_URL: Final[str] = "https://nominatim.openstreetmap.org"

# OpenRouteService - 2000 requests/day free
OPENROUTESERVICE_API_KEY: Final[str] = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjkzZmI0MDNjNTJkNTRmYWJiOTMzNWM5NGU2YmI5OGM1IiwiaCI6Im11cm11cjY0In0="

# TomTom Traffic API - 2500 requests/day free
TOMTOM_API_KEY: Final[str] = "wOXjnozPcjhF1mBp8JhWTjUtmZBi4lDs"

# OpenWeatherMap - 1000 requests/day free
OPENWEATHERMAP_API_KEY: Final[str] = "635ba792-1c98-11f1-9211-0242ac120003-635ba800-1c98-11f1-9211-0242ac120003"

# Indian Government Open Data - Accident Statistics
# Data source: https://data.gov.in (Ministry of Road Transport & Highways)
INDIA_ACCIDENT_DATA_URL: Final[str] = "https://data.gov.in/api/datastore"

# MongoDB Configuration (Optional)
# Use Streamlit secrets for MongoDB connection
# Add to .streamlit/secrets.toml:
# mongo_db_url = "your_mongodb_connection_string"

def get_mongo_db_url() -> str:
    """Get MongoDB URL from Streamlit secrets."""
    import streamlit as st
    try:
        return st.secrets.get("mongo_db_url", "")
    except Exception:
        return ""

def get_openrouteservice_key() -> str:
    """Get OpenRouteService API key from Streamlit secrets."""
    import streamlit as st
    try:
        return st.secrets.get("OPENROUTESERVICE_API_KEY", OPENROUTESERVICE_API_KEY)
    except Exception:
        return OPENROUTESERVICE_API_KEY

def get_tomtom_key() -> str:
    """Get TomTom API key from Streamlit secrets."""
    import streamlit as st
    try:
        return st.secrets.get("TOMTOM_API_KEY", TOMTOM_API_KEY)
    except Exception:
        return TOMTOM_API_KEY

def get_openweathermap_key() -> str:
    """Get OpenWeatherMap API key from Streamlit secrets."""
    import streamlit as st
    try:
        return st.secrets.get("OPENWEATHERMAP_API_KEY", OPENWEATHERMAP_API_KEY)
    except Exception:
        return OPENWEATHERMAP_API_KEY


def get_groq_key() -> str:
    """Get Groq API key from Streamlit secrets."""
    import streamlit as st
    try:
        return st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        return ""
