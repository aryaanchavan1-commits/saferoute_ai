"""
SafeRoute AI - Hazard Map Page
==============================
Interactive Folium map with hazard markers and heatmap.
"""

import streamlit as st
import streamlit_folium as st_folium
from folium.plugins import MarkerCluster, HeatMap

from config import (
    CITY_NAMES, DEFAULT_CITY, SEVERITY_COLORS, DEFAULT_MAP_ZOOM
)
from utils.data import filter_hazards, get_city_coordinates
from utils.maps import build_hazard_map


def show():
    """Display the hazard map page."""
    
    # Page header
    st.markdown("""
    <div class="page-header">
        <h1>🗺️ Hazard Map</h1>
        <p class="subtitle">Interactive map showing road hazards across Indian cities</p>
    </div>
    <hr>
    """, unsafe_allow_html=True)
    
    # Get hazards from session state
    hazards = st.session_state.get("hazards", [])
    
    if not hazards:
        st.warning("No hazard data available. Please analyze some images first.")
        return
    
    # ========== SIDEBAR FILTERS ==========
    st.sidebar.markdown("### Map Filters")
    
    # City selector
    city_options = ["All India"] + CITY_NAMES
    default_city = st.session_state.get("user_city", DEFAULT_CITY)
    if default_city in city_options:
        default_index = city_options.index(default_city)
    else:
        default_index = 0
    
    selected_city = st.sidebar.selectbox(
        "Select City",
        options=city_options,
        index=default_index
    )
    
    # Severity filter
    severity_options = ["High", "Medium", "Low"]
    selected_severities = st.sidebar.multiselect(
        "Filter by Severity",
        options=severity_options,
        default=severity_options
    )
    
    # Map display options
    st.sidebar.markdown("### Display Options")
    
    map_cluster = st.sidebar.checkbox("Use Marker Clustering", value=True)
    map_heatmap = st.sidebar.checkbox("Show Heatmap", value=False)
    map_dark = st.sidebar.checkbox("Dark Mode", value=False)
    
    # ========== FILTER HAZARDS ==========
    # Apply filters
    filtered_hazards = filter_hazards(
        hazards,
        city=selected_city,
        severity=selected_severities if selected_severities else None
    )
    
    # ========== SIDEBAR STATS ==========
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Statistics")
    
    # Calculate stats for selected filters
    total_filtered = len(filtered_hazards)
    high_count = len([h for h in filtered_hazards if h.severity == "High"])
    medium_count = len([h for h in filtered_hazards if h.severity == "Medium"])
    low_count = len([h for h in filtered_hazards if h.severity == "Low"])
    
    st.sidebar.metric("Total Hazards", total_filtered)
    st.sidebar.markdown(f"""
    <div style="padding: 10px; background: white; border-radius: 5px; margin-top: 10px;">
        <div style="display: flex; align-items: center; gap: 5px;">
            <span style="background: {SEVERITY_COLORS['High']}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px;">High</span>
            <span>{high_count}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 5px; margin-top: 5px;">
            <span style="background: {SEVERITY_COLORS['Medium']}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px;">Medium</span>
            <span>{medium_count}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 5px; margin-top: 5px;">
            <span style="background: {SEVERITY_COLORS['Low']}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px;">Low</span>
            <span>{low_count}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ========== MAIN MAP AREA ==========
    if filtered_hazards:
        # Determine map center
        if selected_city != "All India":
            center = get_city_coordinates(selected_city)
            zoom = DEFAULT_MAP_ZOOM
        else:
            center = None
            zoom = 5
        
        # Build map
        with st.spinner("Loading map..."):
            hazard_map = build_hazard_map(
                hazards=filtered_hazards,
                center=center,
                zoom=zoom,
                cluster=map_cluster,
                heatmap=map_heatmap,
                dark_mode=map_dark
            )
            
            # Render map
            st_folium.st_folium(
                hazard_map,
                width=800,
                height=500,
                returned_objects=["last_object_clicked"]
            )
        
        # ========== HAZARD LIST ==========
        st.markdown("---")
        st.markdown(f"### Hazards in {selected_city} ({total_filtered})")
        
        # Show filtered hazards in a table
        if filtered_hazards:
            # Create table data
            table_data = []
            for h in filtered_hazards[:20]:  # Show first 20
                severity_color = SEVERITY_COLORS.get(h.severity, "gray")
                
                table_data.append({
                    "ID": h.id,
                    "Type": h.hazard_type,
                    "Severity": h.severity,
                    "City": h.city,
                    "Status": h.status,
                    "Confidence": f"{h.confidence:.0%}"
                })
            
            # Display table
            st.dataframe(
                table_data,
                column_config={
                    "ID": st.column_config.TextColumn("ID", width="medium"),
                    "Type": st.column_config.TextColumn("Type", width="medium"),
                    "Severity": st.column_config.TextColumn("Severity", width="small"),
                    "City": st.column_config.TextColumn("City", width="small"),
                    "Status": st.column_config.TextColumn("Status", width="small"),
                    "Confidence": st.column_config.TextColumn("Confidence", width="small")
                },
                width='stretch',
                hide_index=True
            )
            
            if total_filtered > 20:
                st.info(f"Showing first 20 of {total_filtered} hazards. Use filters to narrow down.")
    else:
        st.info("No hazards match the selected filters. Try changing the city or severity filters.")
    
    # ========== LEGEND ==========
    st.markdown("---")
    st.markdown("""
    ### Map Legend
    
    | Marker Color | Severity |
    |--------------|----------|
    | 🔴 Red | High |
    | 🟠 Orange | Medium |
    | 🟢 Green | Low |
    
    Click on markers to see hazard details.
    """)
