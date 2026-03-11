"""
SafeRoute AI - Route Planner Page
=================================
A-to-B routing with real-time data.
"""

import streamlit as st
import streamlit_folium as st_folium
from datetime import datetime

from config import (
    CITY_NAMES, DEFAULT_CITY, SEVERITY_COLORS, COLOR_GREEN, COLOR_AMBER, COLOR_RED,
    DEMO_CITIES
)
from utils.api_utils import routing_api, weather_api, accident_data
from utils.maps import build_route_map


def show():
    """Display the route planner page."""
    
    # Page header
    st.markdown("""
    <div class="page-header">
        <h1>🧭 Route Planner</h1>
        <p class="subtitle">Real-time route planning with hazard scoring and live data</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Get hazards from session state
    hazards = st.session_state.get("hazards", [])
    
    # ========== REAL-TIME WEATHER ==========
    st.markdown("### 🌤️ Live Weather Conditions")
    
    weather_cols = st.columns(4)
    
    # Get weather for first city (start city default)
    weather = None
    if DEMO_CITIES:
        city_weather = weather_api.get_weather(DEMO_CITIES[0]["lat"], DEMO_CITIES[0]["lon"])
        if city_weather:
            weather = city_weather
    
    if weather:
        with weather_cols[0]:
            temp = weather.get('main', {}).get('temp', 0)
            st.metric("🌡️ Temperature", f"{temp:.1f}°C")
        
        with weather_cols[1]:
            humidity = weather.get('main', {}).get('humidity', 0)
            st.metric("💧 Humidity", f"{humidity}%")
        
        with weather_cols[2]:
            wind = weather.get('wind', {}).get('speed', 0)
            st.metric("💨 Wind", f"{wind} m/s")
        
        with weather_cols[3]:
            conditions = weather.get('weather', [{}])[0].get('description', 'Unknown')
            st.metric("🌤️ Conditions", conditions)
    else:
        st.info("Weather data unavailable - Add OpenWeatherMap API key for live data")
    
    st.markdown("---")
    
    # ========== ROUTE INPUTS ==========
    st.markdown("### 🗺️ Plan Your Route")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_city = st.selectbox(
            "🏁 Start City",
            options=CITY_NAMES,
            index=CITY_NAMES.index(DEFAULT_CITY)
        )
    
    with col2:
        end_city = st.selectbox(
            "🏁 End City",
            options=CITY_NAMES,
            index=CITY_NAMES.index("Pune") if "Pune" in CITY_NAMES else 1
        )
    
    with col3:
        avoid_severity = st.selectbox(
            "⚠️ Avoid Severity",
            options=["None", "High", "Medium"],
            index=0
        )
    
    # Find route button
    if st.button("🔍 Find Safe Route", type="primary", width='stretch'):
        if start_city == end_city:
            st.error("Start and end cities must be different!")
        else:
            with st.spinner("🧮 Calculating route with real-time data..."):
                # Get city coordinates
                start_data = next((c for c in DEMO_CITIES if c["name"] == start_city), DEMO_CITIES[0])
                end_data = next((c for c in DEMO_CITIES if c["name"] == end_city), DEMO_CITIES[1])
                
                start_coords = (start_data["lat"], start_data["lon"])
                end_coords = (end_data["lat"], end_data["lon"])
                
                # Get real route waypoints
                waypoints = routing_api.get_route_waypoints(start_coords, end_coords)
                
                # Calculate distance and duration
                distance_km = routing_api.calculate_distance(start_coords, end_coords)
                duration_min = routing_api.estimate_duration(distance_km)
                
                # Calculate hazard score based on real accident data
                hazard_score = 0
                
                # Get accident stats for cities
                start_accidents = accident_data.get_city_stats(start_city)
                end_accidents = accident_data.get_city_stats(end_city)
                
                if start_accidents:
                    # Add score based on accident severity
                    accident_rate = start_accidents['total_accidents'] / 1000
                    hazard_score += min(accident_rate, 5)
                
                # Add weather risk
                weather_risk = weather_api.get_flood_risk(start_coords[0], start_coords[1])
                if weather_risk['risk'] == 'High':
                    hazard_score += 3
                elif weather_risk['risk'] == 'Medium':
                    hazard_score += 1
                
                # Cap hazard score at 10
                hazard_score = min(int(hazard_score), 10)
                
                # Get hazards on route
                from utils.data import mock_route
                avoid_severity_val = None if avoid_severity == "None" else avoid_severity
                route_hazards = mock_route(start_city, end_city, hazards, avoid_severity_val)
                
                # Store in session state
                st.session_state.current_route = {
                    "start": start_city,
                    "end": end_city,
                    "start_coords": start_coords,
                    "end_coords": end_coords,
                    "waypoints": waypoints,
                    "distance_km": distance_km,
                    "duration_min": duration_min,
                    "hazard_score": hazard_score,
                    "hazards_on_route": route_hazards.get("hazards_on_route", []),
                    "num_hazards": route_hazards.get("num_hazards", 0),
                    "weather_risk": weather_risk,
                    "accident_stats": start_accidents
                }
    
    # ========== ROUTE RESULTS ==========
    if "current_route" in st.session_state:
        route = st.session_state.current_route
        
        st.markdown("---")
        
        # Route info panel
        st.markdown("### 📍 Route Information")
        
        info_cols = st.columns(4)
        
        with info_cols[0]:
            st.metric("🏁 From", route["start"])
        
        with info_cols[1]:
            st.metric("🏁 To", route["end"])
        
        with info_cols[2]:
            st.metric("📏 Distance", f"{route['distance_km']:.1f} km")
        
        with info_cols[3]:
            st.metric("⏱️ Duration", f"~{route['duration_min']} min")
        
        # Hazard score gauge
        hazard_score = route["hazard_score"]
        
        st.markdown("### ⚠️ Risk Assessment")
        
        score_col1, score_col2 = st.columns([1, 2])
        
        with score_col1:
            if hazard_score < 3:
                score_class = "green"
                score_label = "✅ LOW RISK"
                score_emoji = "🟢"
            elif hazard_score < 6:
                score_class = "orange"
                score_label = "⚠️ MODERATE RISK"
                score_emoji = "🟠"
            else:
                score_class = "red"
                score_label = "❌ HIGH RISK"
                score_emoji = "🔴"
            
            st.markdown(f"""
            <div class="hazard-score {score_class}">
                {score_emoji} {hazard_score}/10
            </div>
            <p style="text-align: center; font-size: 1.2rem; font-weight: bold;">{score_label}</p>
            """, unsafe_allow_html=True)
        
        with score_col2:
            # Progress bar for hazard score
            st.progress(hazard_score / 10)
            
            # Show risk factors
            risk_factors = []
            
            if "accident_stats" in route and route["accident_stats"]:
                stats = route["accident_stats"]
                risk_factors.append(f"📊 {route['start']}: {stats['total_accidents']:,} accidents in 2023")
                risk_factors.append(f"💀 {stats['deaths']:,} deaths recorded")
            
            if "weather_risk" in route and route["weather_risk"]:
                wr = route["weather_risk"]
                if wr.get('risk') != 'Low':
                    risk_factors.append(f"🌧️ Weather risk: {wr['risk']}")
                    for factor in wr.get('factors', []):
                        risk_factors.append(f"  • {factor}")
            
            if route.get("hazards_on_route"):
                risk_factors.append(f"🛣️ {len(route['hazards_on_route'])} road hazards on route")
            
            if risk_factors:
                for factor in risk_factors:
                    st.caption(factor)
        
        # ========== MAP ==========
        st.markdown("---")
        st.markdown("### 🗺️ Route Map")
        
        with st.spinner("Loading map..."):
            route_map = build_route_map(
                start=route["start"],
                end=route["end"],
                waypoints=route["waypoints"],
                hazards_on_route=route.get("hazards_on_route", []),
                dark_mode=False
            )
            
            st_folium.st_folium(
                route_map,
                width=800,
                height=450
            )
        
        # ========== ACCIDENT STATS ==========
        if "accident_stats" in route and route["accident_stats"]:
            st.markdown("---")
            st.markdown(f"### 📊 Accident Statistics for {route['start']}")
            
            stats = route["accident_stats"]
            
            acc_cols = st.columns(4)
            
            with acc_cols[0]:
                st.metric("Total Accidents", f"{stats['total_accidents']:,}")
            
            with acc_cols[1]:
                st.metric("Deaths", f"{stats['deaths']:,}", delta_color="inverse")
            
            with acc_cols[2]:
                st.metric("Injuries", f"{stats['injuries']:,}")
            
            with acc_cols[3]:
                st.metric("Hit & Run", f"{stats['hit_run']:,}")
        
        # ========== HAZARDS ON ROUTE ==========
        if route.get("hazards_on_route"):
            st.markdown("---")
            st.markdown(f"### 🚧 Hazards on Route ({route['num_hazards']})")
            
            for hazard in route["hazards_on_route"]:
                severity_color = SEVERITY_COLORS.get(hazard.severity, "gray")
                
                with st.expander(f"⚠️ {hazard.hazard_type} - {hazard.severity} Severity"):
                    st.markdown(f"""
                    - **ID:** {hazard.id}
                    - **Location:** {hazard.city}
                    - **Severity:** :{severity_color.replace('#', '')}[**{hazard.severity}**]
                    - **Status:** {hazard.status}
                    - **Confidence:** {hazard.confidence:.0%}
                    - **Description:** {hazard.description}
                    """)
        else:
            st.success("✅ No road hazards detected on this route!")
    
    else:
        # Show placeholder
        st.info("👆 Select start and end cities, then click 'Find Safe Route' to get started")
        
        # Show API status
        st.markdown("### 🔌 API Status")
        
        api_cols = st.columns(2)
        
        with api_cols[0]:
            if weather_api.api_key:
                st.success("✅ Weather API: Connected")
            else:
                st.warning("⚠️ Weather API: Add OpenWeatherMap key for live weather")
        
        with api_cols[1]:
            if routing_api.api_key:
                st.success("✅ Routing API: Connected")
            else:
                st.warning("⚠️ Routing API: Using fallback calculations")
        
        # Show example data
        st.markdown("### 📊 Sample Accident Data")
        
        total_accidents = accident_data.get_total_accidents()
        total_deaths = accident_data.get_total_deaths()
        
        sample_cols = st.columns(2)
        with sample_cols[0]:
            st.metric("Total Accidents (8 cities)", f"{total_accidents:,}")
        with sample_cols[1]:
            st.metric("Total Deaths", f"{total_deaths:,}")
