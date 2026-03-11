"""
SafeRoute AI - Map Utilities
============================
Folium map builder functions for hazard visualization and routing.
"""

from typing import List, Tuple, Optional

import folium
from folium.plugins import MarkerCluster, HeatMap, MiniMap

from config import (
    COLOR_NAVY, COLOR_TEAL, COLOR_CORAL, COLOR_RED, COLOR_GREEN, COLOR_AMBER,
    SEVERITY_COLORS, HAZARD_COLORS, DEFAULT_MAP_ZOOM, MAP_TILE_LIGHT, MAP_TILE_DARK,
    DEMO_CITIES
)
from utils.data import HazardRecord


def get_severity_icon_color(severity: str) -> str:
    """Get icon color based on severity."""
    return SEVERITY_COLORS.get(severity, "gray")


def create_popup_html(hazard: HazardRecord) -> str:
    """Create HTML popup content for a hazard marker."""
    severity_color = SEVERITY_COLORS.get(hazard.severity, "gray")
    
    html = f"""
    <div style="font-family: Arial, sans-serif; width: 200px;">
        <h4 style="margin: 0 0 10px 0; color: {COLOR_NAVY};">
            {hazard.hazard_type}
        </h4>
        <table style="width: 100%; font-size: 12px;">
            <tr>
                <td><strong>ID:</strong></td>
                <td>{hazard.id}</td>
            </tr>
            <tr>
                <td><strong>Severity:</strong></td>
                <td><span style="color: {severity_color}; font-weight: bold;">{hazard.severity}</span></td>
            </tr>
            <tr>
                <td><strong>Status:</strong></td>
                <td>{hazard.status}</td>
            </tr>
            <tr>
                <td><strong>Confidence:</strong></td>
                <td>{hazard.confidence:.0%}</td>
            </tr>
            <tr>
                <td><strong>City:</strong></td>
                <td>{hazard.city}</td>
            </tr>
            <tr>
                <td><strong>Reported:</strong></td>
                <td>{hazard.reported_by}</td>
            </tr>
        </table>
        <p style="font-size: 11px; margin-top: 10px; color: #666;">
            {hazard.description}
        </p>
    </div>
    """
    return html


def build_hazard_map(
    hazards: List[HazardRecord],
    center: Optional[Tuple[float, float]] = None,
    zoom: int = DEFAULT_MAP_ZOOM,
    cluster: bool = True,
    heatmap: bool = False,
    dark_mode: bool = False
) -> folium.Map:
    """
    Build a Folium map with hazard markers and optional heatmap.
    
    Args:
        hazards: List of HazardRecord objects
        center: Center coordinates (lat, lon). If None, uses first hazard or Mumbai
        zoom: Initial zoom level
        cluster: Whether to use marker clustering
        heatmap: Whether to show heatmap layer
        dark_mode: Whether to use dark map tiles
    
    Returns:
        Folium Map object
    """
    # Determine center
    if center is None:
        if hazards:
            # Use centroid of hazards
            avg_lat = sum(h.latitude for h in hazards) / len(hazards)
            avg_lon = sum(h.longitude for h in hazards) / len(hazards)
            center = (avg_lat, avg_lon)
        else:
            # Default to Mumbai
            center = (DEMO_CITIES[0]["lat"], DEMO_CITIES[0]["lon"])
    
    # Select tile
    tile = MAP_TILE_DARK if dark_mode else MAP_TILE_LIGHT
    
    # Create map
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles=tile
    )
    
    # Add minimap
    MiniMap(toggle_display=True).add_to(m)
    
    # Add heatmap if requested
    if heatmap and hazards:
        heat_data = [[h.latitude, h.longitude, h.confidence] for h in hazards]
        HeatMap(
            heat_data,
            radius=20,
            blur=15,
            max_zoom=13,
            gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'yellow', 0.8: 'orange', 1: 'red'}
        ).add_to(m)
    
    # Add marker cluster if requested
    if cluster:
        marker_cluster = MarkerCluster(
            name="Hazard Markers",
            options={
                "showCoverageOnHover": True,
                "zoomToBoundsOnClick": True,
                "spiderfyOnMaxZoom": True
            }
        ).add_to(m)
        
        for hazard in hazards:
            _add_hazard_marker(marker_cluster, hazard)
    else:
        for hazard in hazards:
            _add_hazard_marker(m, hazard)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m


def _add_hazard_marker(parent: folium.Map, hazard: HazardRecord) -> None:
    """Add a single hazard marker to the map."""
    # Get icon color based on severity
    icon_color = get_severity_icon_color(hazard.severity)
    
    # Create custom icon
    icon = folium.Icon(
        color=_get_folium_color(icon_color),
        icon="exclamation-triangle",
        prefix="fa"
    )
    
    # Create popup
    popup = folium.Popup(create_popup_html(hazard), max_width=300)
    
    # Add marker
    folium.Marker(
        location=(hazard.latitude, hazard.longitude),
        popup=popup,
        icon=icon,
        tooltip=f"{hazard.hazard_type} - {hazard.severity}"
    ).add_to(parent)


def _get_folium_color(hex_color: str) -> str:
    """Convert hex color to Folium color name."""
    color_map = {
        COLOR_RED: "red",
        COLOR_GREEN: "green", 
        COLOR_AMBER: "orange",
        "#3B82F6": "blue",
        "#8B5CF6": "purple",
        "#6B7280": "gray"
    }
    return color_map.get(hex_color, "gray")


def build_route_map(
    start: str,
    end: str,
    waypoints: List[Tuple[float, float]],
    hazards_on_route: List[HazardRecord],
    dark_mode: bool = False
) -> folium.Map:
    """
    Build a Folium map showing a route with hazards.
    
    Args:
        start: Start city name
        end: End city name
        waypoints: List of (lat, lon) tuples for route
        hazards_on_route: List of hazards on the route
        dark_mode: Whether to use dark map tiles
    
    Returns:
        Folium Map object
    """
    # Calculate center
    if waypoints:
        center_lat = sum(wp[0] for wp in waypoints) / len(waypoints)
        center_lon = sum(wp[1] for wp in waypoints) / len(waypoints)
        center = (center_lat, center_lon)
    else:
        center = (DEMO_CITIES[0]["lat"], DEMO_CITIES[0]["lon"])
    
    # Select tile
    tile = MAP_TILE_DARK if dark_mode else MAP_TILE_LIGHT
    
    # Create map
    m = folium.Map(
        location=center,
        zoom_start=6,
        tiles=tile
    )
    
    # Add minimap
    MiniMap(toggle_display=True).add_to(m)
    
    # Draw route line
    if len(waypoints) > 1:
        folium.PolyLine(
            locations=waypoints,
            weight=5,
            color=COLOR_TEAL,
            opacity=0.8,
            popup=f"Route: {start} to {end}"
        ).add_to(m)
    
    # Add start marker
    if waypoints:
        folium.Marker(
            location=waypoints[0],
            popup=f"<b>Start:</b> {start}",
            icon=folium.Icon(color="green", icon="play", prefix="fa"),
            tooltip=f"Start: {start}"
        ).add_to(m)
        
        # Add end marker
        folium.Marker(
            location=waypoints[-1],
            popup=f"<b>End:</b> {end}",
            icon=folium.Icon(color="red", icon="flag-checkered", prefix="fa"),
            tooltip=f"End: {end}"
        ).add_to(m)
    
    # Add hazard markers
    for hazard in hazards_on_route:
        icon_color = get_severity_icon_color(hazard.severity)
        
        folium.CircleMarker(
            location=(hazard.latitude, hazard.longitude),
            radius=8,
            color=COLOR_RED,
            fill=True,
            fill_color=icon_color,
            fill_opacity=0.7,
            popup=create_popup_html(hazard),
            tooltip=f"{hazard.hazard_type} ({hazard.severity})"
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m
