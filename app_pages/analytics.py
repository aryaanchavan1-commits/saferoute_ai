"""
SafeRoute AI - Analytics Page
==============================
Deep charts: trends, city breakdown, type breakdown, scatter maps.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from config import (
    COLOR_NAVY, COLOR_TEAL, COLOR_CORAL, COLOR_RED, COLOR_GREEN,
    SEVERITY_COLORS, HAZARD_COLORS, CITY_NAMES
)
from utils.data import hazards_to_dataframe, filter_hazards


def show():
    """Display the analytics page."""
    
    # Page header
    st.markdown("""
    <div class="page-header">
        <h1>📈 Analytics</h1>
        <p class="subtitle">Deep insights and trends in road hazard data</p>
    </div>
    <hr>
    """, unsafe_allow_html=True)
    
    # Get hazards from session state
    hazards = st.session_state.get("hazards", [])
    
    if not hazards:
        st.warning("⚠️ No hazard data available. Please analyze some images first.")
        return
    
    # Convert to dataframe
    df = hazards_to_dataframe(hazards)
    
    # ========== FILTERS ==========
    st.sidebar.markdown("### 🎛️ Analytics Filters")
    
    # Date range filter
    date_options = {
        "Last 7 days": 7,
        "Last 14 days": 14,
        "Last 30 days": 30
    }
    selected_date_range = st.sidebar.selectbox(
        "📅 Date Range",
        options=list(date_options.keys()),
        index=2
    )
    days = date_options[selected_date_range]
    
    # City filter
    city_filter = st.sidebar.multiselect(
        "🏙️ Filter by City",
        options=["All"] + CITY_NAMES,
        default=["All"]
    )
    
    # Apply filters
    start_date = datetime.now() - timedelta(days=days)
    
    if "All" in city_filter:
        filtered_hazards = filter_hazards(hazards, start_date=start_date)
    else:
        filtered_hazards = filter_hazards(hazards, start_date=start_date, city=city_filter[0] if len(city_filter) == 1 else None)
    
    if filtered_hazards:
        filtered_df = hazards_to_dataframe(filtered_hazards)
    else:
        filtered_df = df[df["timestamp"] >= start_date]
    
    # ========== CHART 1: Detection Confidence Trend ==========
    st.markdown("### 📈 Detection Confidence Trend")
    
    if not filtered_df.empty:
        # Group by date
        filtered_df = filtered_df.copy()
        filtered_df["date"] = filtered_df["timestamp"].dt.date
        daily_conf = filtered_df.groupby("date")["confidence"].mean().reset_index()
        
        fig_conf = px.line(
            daily_conf,
            x="date",
            y="confidence",
            markers=True,
            line_shape="spline"
        )
        
        fig_conf.update_traces(line_color='#00d9ff', line_width=2)
        fig_conf.update_layout(
            plot_bgcolor=None,
            paper_bgcolor=None,
            xaxis_title="Date",
            yaxis_title="Average Confidence",
            yaxis_range=[0.5, 1.0],
            font=dict(family="Arial", size=12, color='white'),
            height=300,
            xaxis=dict(showgrid=True, gridcolor='#374151'),
            yaxis=dict(showgrid=True, gridcolor='#374151')
        )
        
        st.plotly_chart(fig_conf, width='stretch')
    else:
        st.info("No data available for the selected filters")
    
    st.markdown("---")
    
    # ========== CHART 2: Hazard Types per City ==========
    st.markdown("### 🏙️ Hazard Types per City")
    
    if not filtered_df.empty:
        # Group by city and type
        city_type = filtered_df.groupby(["city", "hazard_type"]).size().reset_index(name="count")
        
        fig_city_type = px.bar(
            city_type,
            x="city",
            y="count",
            color="hazard_type",
            barmode="group",
            color_discrete_map=HAZARD_COLORS
        )
        
        fig_city_type.update_layout(
            plot_bgcolor=None,
            paper_bgcolor=None,
            xaxis_title="City",
            yaxis_title="Count",
            font=dict(family="Arial", size=12, color='white'),
            height=350,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='white')),
            xaxis=dict(showgrid=True, gridcolor='#374151'),
            yaxis=dict(showgrid=True, gridcolor='#374151')
        )
        
        st.plotly_chart(fig_city_type, width='stretch')
    else:
        st.info("No data available")
    
    st.markdown("---")
    
    # ========== CHART 3: Scatter Map (Lat/Lon) ==========
    st.markdown("### 🗺️ Geographic Distribution (Color = Severity)")
    
    if not filtered_df.empty:
        # Create scatter map
        fig_scatter = px.scatter_mapbox(
            filtered_df,
            lat="latitude",
            lon="longitude",
            color="severity",
            size="confidence",
            hover_name="id",
            hover_data={
                "hazard_type": True,
                "city": True,
                "severity": True,
                "confidence": True
            },
            color_discrete_map=SEVERITY_COLORS,
            zoom=4,
            center={"lat": 20, "lon": 78},
            height=400
        )
        
        fig_scatter.update_layout(
            mapbox_style="open-street-map",
            paper_bgcolor=None,
            font=dict(family="Arial", size=12),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        st.plotly_chart(fig_scatter, width='stretch')
    else:
        st.info("No geographic data available")
    
    st.markdown("---")
    
    # ========== CHART 4: Reported By Breakdown ==========
    st.markdown("### 👤 Reporter Breakdown (AI vs User)")
    
    if not filtered_df.empty:
        reporter_counts = filtered_df["reported_by"].value_counts()
        
        fig_reporter = go.Figure(data=[
            go.Pie(
                labels=reporter_counts.index,
                values=reporter_counts.values,
                hole=0.5,
                marker_colors=['#00d9ff', '#f97316', '#16213e', '#22c55e'],
                textinfo='label+percent',
                textfont=dict(color='white')
            )
        ])
        
        fig_reporter.update_layout(
            plot_bgcolor=None,
            paper_bgcolor=None,
            font=dict(family="Arial", size=12, color='white'),
            height=300,
            showlegend=True,
            legend=dict(font=dict(color='white'))
        )
        
        st.plotly_chart(fig_reporter, width='stretch')
    else:
        st.info("No reporter data available")
    
    st.markdown("---")
    
    # ========== CHART 5: Average Time-to-Fix by Type ==========
    st.markdown("### ⏱️ Average Time-to-Fix by Hazard Type")
    
    # Mock data for time-to-fix (in days)
    time_to_fix_data = {
        "Pothole": 7,
        "Road Crack": 14,
        "Waterlogging": 3,
        "Road Wear": 21,
        "Debris": 2
    }
    
    types = list(time_to_fix_data.keys())
    times = list(time_to_fix_data.values())
    
    fig_fix = go.Figure(go.Bar(
        x=types,
        y=times,
        marker_color='#00d9ff'
    ))
    
    fig_fix.update_layout(
        plot_bgcolor=None,
        paper_bgcolor=None,
        xaxis_title="Hazard Type",
        yaxis_title="Average Days to Fix",
        font=dict(family="Arial", size=12, color='white'),
        height=300,
        xaxis=dict(showgrid=True, gridcolor='#374151'),
        yaxis=dict(showgrid=True, gridcolor='#374151')
    )
    
    st.plotly_chart(fig_fix, width='stretch')
    
    st.caption("*Time-to-fix data is simulated based on typical municipal response times.*")
    
    st.markdown("---")
    
    # ========== CHART 6: Heatmap Table (City vs Type) ==========
    st.markdown("### 🔥 City vs Hazard Type Matrix")
    
    if not filtered_df.empty:
        # Create pivot table
        pivot = filtered_df.pivot_table(
            index="city",
            columns="hazard_type",
            aggfunc="size",
            fill_value=0
        )
        
        # Create heatmap
        fig_heatmap = px.imshow(
            pivot,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="Blues"
        )
        
        fig_heatmap.update_layout(
            plot_bgcolor=None,
            paper_bgcolor=None,
            xaxis_title="Hazard Type",
            yaxis_title="City",
            font=dict(family="Arial", size=11, color='white'),
            height=350
        )
        
        st.plotly_chart(fig_heatmap, width='stretch')
    else:
        st.info("No matrix data available")
