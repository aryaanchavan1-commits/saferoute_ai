"""
SafeRoute AI - Settings Page
============================
User preferences and app configuration.
"""

import streamlit as st

from config import (
    APP_NAME, APP_VERSION, TEAM_NAME, HACKATHON,
    CITY_NAMES, DEFAULT_CITY, DEFAULT_SEVERITY_THRESHOLD,
    DEFAULT_HEATMAP_ENABLED, DEFAULT_DARK_MAP
)


def show():
    """Display the settings page."""
    
    # Page header
    st.markdown("""
    <div class="page-header">
        <h1>⚙️ Settings</h1>
        <p class="subtitle">Configure your SafeRoute AI preferences</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== GENERAL SETTINGS ==========
    st.markdown("### 🎛️ General Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_city = st.selectbox(
            "🏙️ Default City",
            options=CITY_NAMES,
            index=CITY_NAMES.index(st.session_state.get("user_city", DEFAULT_CITY))
        )
    
    with col2:
        severity_threshold = st.slider(
            "📊 Severity Threshold",
            min_value=0,
            max_value=100,
            value=st.session_state.get("severity_threshold", DEFAULT_SEVERITY_THRESHOLD),
            help="Minimum confidence threshold for AI detection"
        )
    
    st.markdown("---")
    
    # ========== MAP SETTINGS ==========
    st.markdown("### 🗺️ Map Settings")
    
    map_col1, map_col2 = st.columns(2)
    
    with map_col1:
        heatmap_enabled = st.toggle(
            "🔥 Enable Heatmap by Default",
            value=st.session_state.get("heatmap_enabled", DEFAULT_HEATMAP_ENABLED)
        )
    
    with map_col2:
        dark_map = st.toggle(
            "🌙 Use Dark Map Tiles",
            value=st.session_state.get("dark_map", DEFAULT_DARK_MAP)
        )
    
    st.markdown("---")
    
    # ========== SAVE SETTINGS ==========
    button_col1, button_col2 = st.columns(2)
    
    with button_col1:
        if st.button("💾 Save Settings", type="primary", width='stretch'):
            st.session_state.user_city = default_city
            st.session_state.severity_threshold = severity_threshold
            st.session_state.heatmap_enabled = heatmap_enabled
            st.session_state.dark_map = dark_map
            st.success("✅ Settings saved successfully!")
    
    with button_col2:
        if st.button("🔄 Reset to Defaults", width='stretch'):
            st.session_state.user_city = DEFAULT_CITY
            st.session_state.severity_threshold = DEFAULT_SEVERITY_THRESHOLD
            st.session_state.heatmap_enabled = DEFAULT_HEATMAP_ENABLED
            st.session_state.dark_map = DEFAULT_DARK_MAP
            st.success("✅ Settings reset to defaults!")
            st.rerun()
    
    st.markdown("---")
    
    # ========== ABOUT SECTION ==========
    st.markdown("### ℹ️ About")
    
    st.info(f"**{APP_NAME} v{APP_VERSION}**")
    
    st.markdown("**AI-powered road hazard detection and smart navigation system for Indian roads.**")
    
    st.markdown("""
    SafeRoute AI uses advanced computer vision to detect potholes, road cracks, 
    waterlogging, and other road hazards from images. It provides real-time 
    hazard mapping, route planning with hazard scoring, and generates reports 
    for municipal authorities.
    """)
    
    st.markdown("---")
    
    st.markdown("**Team:**")
    st.markdown(f"{TEAM_NAME}")
    
    st.markdown("**Hackathon:**")
    st.markdown(f"{HACKATHON}")
    
    st.markdown("---")
    
    st.markdown("**Tech Stack:**")
    st.markdown("""
    - **Frontend:** Streamlit
    - **AI/ML:** OpenCV, scikit-learn, numpy
    - **Maps:** Folium + streamlit-folium
    - **Charts:** Plotly
    - **Data:** Pandas
    - **PDF:** fpdf2
    """)
    
    st.markdown("---")
    st.caption("🚗 Made with ❤️ for safer Indian roads")
