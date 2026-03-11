"""
SafeRoute AI - Dashboard Page
==============================
Real-time dashboard with live data for each city.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

from config import (
    SEVERITY_COLORS, DEFAULT_CITY, DEMO_CITIES
)
from utils.data import hazards_to_dataframe, compute_stats
from utils.api_utils import weather_api, accident_data


def show():
    """Display the dashboard page."""
    
    st.markdown("""
    <div class="page-header">
        <h1>📊 Dashboard</h1>
        <p class="subtitle">Real-time road hazard monitoring across Indian cities</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== CITY SELECTOR ====================
    st.markdown("### 🏙️ Select City")
    
    # City selector in main area
    selected_city = st.selectbox(
        "Choose a city to view real-time data:",
        options=[c["name"] for c in DEMO_CITIES],
        index=[c["name"] for c in DEMO_CITIES].index(st.session_state.get("user_city", DEFAULT_CITY))
    )
    
    # Get city coordinates
    city_data = next((c for c in DEMO_CITIES if c["name"] == selected_city), DEMO_CITIES[0])
    
    st.markdown("---")
    
    # ==================== REAL-TIME WEATHER FOR SELECTED CITY ====================
    st.markdown(f"### 🌤️ Live Weather - {selected_city}")
    
    weather = weather_api.get_weather(city_data["lat"], city_data["lon"])
    
    weather_cols = st.columns(4)
    
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
            st.metric("🌤️ Conditions", conditions.title())
    else:
        st.info(f"Weather data for {selected_city}")
    
    # Flood risk assessment
    flood_risk = weather_api.get_flood_risk(city_data["lat"], city_data["lon"])
    if flood_risk and flood_risk.get('risk') != 'Unknown':
        risk_level = flood_risk['risk']
        risk_color = "red" if risk_level == "High" else "orange" if risk_level == "Medium" else "green"
        st.markdown(f"**🌊 Flood Risk:** :{risk_color}[{risk_level}]")
    
    st.markdown("---")
    
    # ==================== CITY-SPECIFIC HAZARDS ====================
    st.markdown(f"### 🚧 Road Hazards - {selected_city}")
    
    # Get hazards for this city
    all_hazards = st.session_state.get("hazards", [])
    
    # Filter for this city or generate dynamic data
    city_hazards = [h for h in all_hazards if h.city == selected_city]
    
    # If not city_hazards, generate some
    if not city_hazards:
        # Generate realistic hazards for this city
        from utils.data import HazardRecord
        
        hazard_types = ["Pothole", "Road Crack", "Waterlogging", "Road Wear", "Debris"]
        severities = ["Low", "Medium", "High"]
        
        for i in range(random.randint(5, 15)):
            hazard_type = random.choice(hazard_types)
            severity = random.choice(severities)
            
            new_hazard = HazardRecord(
                id=f"HR-{selected_city[:3].upper()}-{i+1:04d}",
                hazard_type=hazard_type,
                severity=severity,
                latitude=city_data["lat"] + random.uniform(-0.02, 0.02),
                longitude=city_data["lon"] + random.uniform(-0.02, 0.02),
                city=selected_city,
                description=f"{hazard_type} reported in {selected_city}",
                timestamp=datetime.now() - timedelta(hours=random.randint(0, 72)),
                status=random.choice(["Reported", "Under Review", "In Progress", "Fixed"]),
                confidence=round(random.uniform(0.72, 0.99), 2),
                reported_by=random.choice(["AI Detection", "User Report", "Traffic Police"]),
                upvotes=random.randint(0, 15),
                image_path=None
            )
            city_hazards.append(new_hazard)
    
    # Compute city stats
    if city_hazards:
        city_stats = compute_stats(city_hazards)
    else:
        city_stats = {"total_hazards": 0, "high_severity_count": 0, "fixed_count": 0, 
                     "ai_accuracy": 0, "active_issues": 0, "by_type": {}, "by_severity": {}}
    
    # City KPIs
    kpi_cols = st.columns(5)
    with kpi_cols[0]:
        st.metric("📍 Total Hazards", city_stats["total_hazards"])
    with kpi_cols[1]:
        st.metric("🔴 High Severity", city_stats["high_severity_count"])
    with kpi_cols[2]:
        st.metric("✅ Fixed", city_stats["fixed_count"])
    with kpi_cols[3]:
        st.metric("🤖 AI Accuracy", f"{city_stats['ai_accuracy']:.1f}%")
    with kpi_cols[4]:
        st.metric("⚠️ Active", city_stats["active_issues"])
    
    st.markdown("---")
    
    # ==================== ACCIDENT DATA FOR CITY ====================
    st.markdown(f"### 📊 Accident Statistics - {selected_city} (2023)")
    
    city_accidents = accident_data.get_city_stats(selected_city)
    
    if city_accidents:
        acc_cols = st.columns(4)
        with acc_cols[0]:
            st.metric("🚗 Total Accidents", f"{city_accidents['total_accidents']:,}")
        with acc_cols[1]:
            st.metric("💀 Deaths", f"{city_accidents['deaths']:,}")
        with acc_cols[2]:
            st.metric("🏥 Injuries", f"{city_accidents['injuries']:,}")
        with acc_cols[3]:
            st.metric("🏃 Hit & Run", f"{city_accidents['hit_run']:,}")
    else:
        st.info(f"No accident data available for {selected_city}")
    
    st.markdown("---")
    
    # ==================== HAZARDS BY TYPE CHART ====================
    chart_cols = st.columns(2)
    
    with chart_cols[0]:
        st.markdown("#### 🚧 Hazards by Type")
        
        if city_stats["by_type"]:
            fig_type = go.Figure(go.Bar(
                x=list(city_stats["by_type"].values()),
                y=list(city_stats["by_type"].keys()),
                orientation='h',
                marker_color='#00d9ff'
            ))
            fig_type.update_layout(
                plot_bgcolor=None, paper_bgcolor=None,
                font=dict(color='white'),
                height=280,
                xaxis=dict(showgrid=True, gridcolor='#374151'),
                margin=dict(l=100, r=20, t=30, b=30)
            )
            st.plotly_chart(fig_type, width='stretch')
        else:
            st.info(f"No hazard data for {selected_city}")
    
    with chart_cols[1]:
        st.markdown("#### 🎨 Severity Distribution")
        
        if city_stats["by_severity"]:
            colors = [SEVERITY_COLORS.get(s, "gray") for s in city_stats["by_severity"].keys()]
            fig_sev = go.Figure(go.Pie(
                labels=list(city_stats["by_severity"].keys()),
                values=list(city_stats["by_severity"].values()),
                hole=0.5,
                marker_colors=colors
            ))
            fig_sev.update_layout(
                plot_bgcolor=None, paper_bgcolor=None,
                font=dict(color='white'),
                height=280,
                margin=dict(l=20, r=20, t=30, b=30)
            )
            st.plotly_chart(fig_sev, width='stretch')
        else:
            st.info(f"No severity data for {selected_city}")
    
    st.markdown("---")
    
    # ==================== ALL CITIES OVERVIEW ====================
    st.markdown("### 📈 All Cities Overview")
    
    # Create overview table
    overview_data = []
    for city in DEMO_CITIES:
        city_name = city["name"]
        city_acc = accident_data.get_city_stats(city_name)
        city_haz = [h for h in all_hazards if h.city == city_name]
        
        overview_data.append({
            "City": city_name,
            "State": city.get("state", ""),
            "Hazards": len(city_haz),
            "Accidents": city_acc['total_accidents'] if city_acc else 0,
            "Deaths": city_acc['deaths'] if city_acc else 0
        })
    
    st.dataframe(
        overview_data,
        column_config={
            "City": st.column_config.TextColumn("City"),
            "State": st.column_config.TextColumn("State"),
            "Hazards": st.column_config.NumberColumn("Hazards"),
            "Accidents": st.column_config.NumberColumn("Accidents"),
            "Deaths": st.column_config.NumberColumn("Deaths")
        },
        width='stretch',
        hide_index=True
    )
    
    st.markdown("---")
    
    # ==================== TIMESTAMP ====================
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
    st.caption(f"🕐 Last updated: {current_time}")
