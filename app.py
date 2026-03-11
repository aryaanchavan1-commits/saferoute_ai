"""
SafeRoute AI - Main Application
===============================
AI-powered road hazard detection and smart navigation system for Indian roads.
CODE 1 Hackathon 2026, Team: mortal_coders
"""

import streamlit as st
from pathlib import Path

from config import (
    APP_NAME, APP_VERSION, APP_ICON, TEAM_NAME, DEVELOPER,
    DEFAULT_CITY, PAGES
)
from utils.data import generate_mock_hazards


# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)


# ========== LOAD CSS ==========
def load_css():
    """Load custom CSS styles with responsive design."""
    css_path = Path(__file__).parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Additional inline styles
    st.markdown("""
    <style>
    .stApp { 
        background-color: #1a1a2e !important; 
    }
    html, body, div, p, span, label, h1, h2, h3, h4, h5, h6 { 
        color: white !important; 
    }
    .block-container { 
        background-color: #1a1a2e !important; 
        padding-top: 1rem !important;
    }
    [data-testid="stSidebar"] { 
        background-color: #16213e !important; 
    }
    [data-testid="stMetricValue"] { 
        color: #00d9ff !important; 
    }
    [data-testid="stMetricLabel"] { 
        color: #9ca3af !important; 
    }
    </style>
    """, unsafe_allow_html=True)


# ========== SESSION STATE INIT ==========
def init_session_state():
    """Initialize session state variables."""
    if "hazards" not in st.session_state:
        st.session_state.hazards = generate_mock_hazards(n=80, seed=42)
    
    if "user_city" not in st.session_state:
        st.session_state.user_city = DEFAULT_CITY
    
    if "severity_threshold" not in st.session_state:
        st.session_state.severity_threshold = 70
    
    if "heatmap_enabled" not in st.session_state:
        st.session_state.heatmap_enabled = True
    
    if "dark_map" not in st.session_state:
        st.session_state.dark_map = False
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"


# ========== SIDEBAR NAVIGATION ==========
def render_sidebar():
    """Render sidebar with navigation."""
    with st.sidebar:
        # Logo
        st.markdown(f"""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="font-size: 1.5rem; margin: 0; background: linear-gradient(135deg, #00d9ff, #F97316); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                🛣️ {APP_NAME}
            </h1>
            <p style="color: #9ca3af; font-size: 0.8rem; margin: 5px 0 0 0;">{APP_VERSION}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 📍 Navigation")
        
        pages_list = list(PAGES.keys())
        current = st.session_state.current_page
        
        for page in pages_list:
            icon = PAGES[page]
            is_active = page == current
            
            # Create button style for navigation
            btn_style = """
            <style>
            .nav-button {
                display: block;
                width: 100%;
                padding: 12px 15px;
                margin: 5px 0;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                font-size: 1rem;
                text-align: left;
                transition: all 0.3s ease;
            }
            .nav-button:hover {
                background: rgba(0, 217, 255, 0.15);
            }
            .nav-button.active {
                background: linear-gradient(135deg, #0D9488, #00d9ff);
                color: white;
            }
            .nav-button.inactive {
                background: rgba(255, 255, 255, 0.05);
                color: #9ca3af;
            }
            </style>
            """
            st.markdown(btn_style, unsafe_allow_html=True)
            
            if st.button(
                f"{icon} {page}", 
                key=f"nav_{page}", 
                type="primary" if is_active else "secondary",
                use_container_width=True
            ):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("---")
        
        # Live stats from session state - ALL CITIES
        hazards = st.session_state.get("hazards", [])
        current_city = st.session_state.get("user_city", DEFAULT_CITY)
        
        # Get all unique cities from hazards
        all_cities = list(set([h.city for h in hazards])) if hazards else [DEFAULT_CITY]
        
        # Refresh button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 🔄 Live Data")
        with col2:
            if st.button("🔄", key="refresh_btn"):
                st.rerun()
        
        # Get hazards for current city
        city_hazards = [h for h in hazards if h.city == current_city]
        
        # Try to get live accident data
        try:
            from utils.api_utils import accident_data
            live_stats = accident_data.get_city_stats(current_city)
            if live_stats:
                st.markdown(f"""
                <div style="background: rgba(249, 115, 22, 0.2); border-radius: 10px; padding: 12px; margin-bottom: 10px;">
                    <p style="margin: 0; font-weight: bold; color: #F97316;">🚨 LIVE: {current_city}</p>
                    <p style="margin: 3px 0 0 0; font-size: 0.8rem;"> Accidents: {live_stats.get('total_accidents', 0)} | Deaths: {live_stats.get('total_deaths', 0)}</p>
                </div>
                """, unsafe_allow_html=True)
        except:
            pass
        
        st.markdown(f"""
        <div style="background: rgba(0, 217, 255, 0.1); border-radius: 10px; padding: 15px;">
            <p style="margin: 0; font-weight: bold;">📍 {current_city}</p>
            <p style="margin: 5px 0 0 0; font-size: 0.9rem;">🚧 {len(city_hazards)} active hazards</p>
            <p style="margin: 5px 0 0 0; font-size: 0.9rem;">🔴 {len([h for h in city_hazards if h.severity == 'High'])} high severity</p>
            <p style="margin: 5px 0 0 0; font-size: 0.9rem;">🟡 {len([h for h in city_hazards if h.severity == 'Medium'])} medium severity</p>
            <p style="margin: 5px 0 0 0; font-size: 0.9rem;">🟢 {len([h for h in city_hazards if h.severity == 'Low'])} low severity</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ALL CITIES LIVE STATS
        st.markdown("### 🌍 All Cities Live Stats")
        
        for city in sorted(all_cities):
            city_h = [h for h in hazards if h.city == city]
            high = len([h for h in city_h if h.severity == 'High'])
            medium = len([h for h in city_h if h.severity == 'Medium'])
            low = len([h for h in city_h if h.severity == 'Low'])
            total = len(city_h)
            
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 10px; margin: 5px 0;">
                <p style="margin: 0; font-weight: bold;">📍 {city}</p>
                <p style="margin: 3px 0 0 0; font-size: 0.8rem;">🚧 {total} | 🔴 {high} | 🟡 {medium} | 🟢 {low}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Team info
        st.markdown(f"""
        <div style="text-align: center; color: #9ca3af; font-size: 0.8rem;">
            <p style="margin: 0;">🏆 {TEAM_NAME}</p>
            <p style="margin: 5px 0 0 0;">👨‍💻 {DEVELOPER}</p>
        </div>
        """, unsafe_allow_html=True)


# ========== TOP NAVIGATION ==========
def render_top_navigation():
    """Render top navigation for mobile and tablet."""
    
    pages_list = list(PAGES.keys())
    current = st.session_state.current_page
    
    # Get icons for each page
    icons = {
        "Dashboard": "📊",
        "Hazard Detection": "📷",
        "Hazard Map": "🗺️",
        "Route Planner": "🧭",
        "Chatbot": "💬",
        "Analytics": "📈",
        "Govt Report": "📄",
        "Settings": "⚙️"
    }
    
    # Generate tabs HTML
    tabs_html = ""
    for page in pages_list:
        icon = icons.get(page, "📄")
        is_active = "active" if page == current else ""
        tabs_html += f'''
        <button class="top-nav-tab {is_active}" onclick="navigateTo('{page}')">
            <span class="icon">{icon}</span>
            <span class="label">{page}</span>
        </button>
        '''
    
    # Mobile header with logo and tabs
    st.markdown(f"""
    <div class="top-nav">
        <div class="logo">
            <div class="logo-icon">🛣️</div>
            <span class="logo-text">{APP_NAME}</span>
        </div>
        
        <div class="top-nav-tabs">
            {tabs_html}
        </div>
        
        <button class="hamburger" onclick="toggleMobileMenu()">☰</button>
    </div>
    
    <!-- Mobile Menu Overlay -->
    <div class="mobile-menu-overlay" id="mobileOverlay" onclick="toggleMobileMenu()"></div>
    
    <!-- Mobile Menu Panel -->
    <div class="mobile-menu" id="mobileMenu">
        <div class="mobile-menu-header">
            <span style="font-weight: bold; color: #00d9ff;">📍 Menu</span>
            <button class="mobile-menu-close" onclick="toggleMobileMenu()">✕</button>
        </div>
    """, unsafe_allow_html=True)
    
    # Add mobile menu buttons
    for page in pages_list:
        icon = icons.get(page, "📄")
        if st.button(f"{icon} {page}", key=f"mobile_{page}", use_container_width=True):
            st.session_state.current_page = page
            st.rerun()
    
    st.markdown("""
    </div>
    
    <!-- JavaScript -->
    <script>
    function navigateTo(page) {
        // Find and click the corresponding button
        var buttons = document.querySelectorAll('button');
        for (var i = 0; i < buttons.length; i++) {
            if (buttons[i].textContent.includes(page)) {
                buttons[i].click();
                break;
            }
        }
    }
    
    function toggleMobileMenu() {
        var menu = document.getElementById('mobileMenu');
        var overlay = document.getElementById('mobileOverlay');
        
        if (menu.classList.contains('active')) {
            menu.classList.remove('active');
            overlay.classList.remove('active');
        } else {
            menu.classList.add('active');
            overlay.classList.add('active');
        }
    }
    </script>
    """, unsafe_allow_html=True)


# ========== MAIN CONTENT ==========
def main():
    """Main application entry point."""
    load_css()
    init_session_state()
    render_sidebar()
    render_top_navigation()
    
    current_page = st.session_state.current_page
    
    try:
        if current_page == "Dashboard":
            from app_pages import dashboard
            dashboard.show()
        elif current_page == "Hazard Detection":
            from app_pages import detection
            detection.show()
        elif current_page == "Hazard Map":
            from app_pages import hazard_map
            hazard_map.show()
        elif current_page == "Route Planner":
            from app_pages import route_planner
            route_planner.show()
        elif current_page == "Chatbot":
            from app_pages import chatbot
            chatbot.show()
        elif current_page == "Analytics":
            from app_pages import analytics
            analytics.show()
        elif current_page == "Govt Report":
            from app_pages import govt_report
            govt_report.show()
        elif current_page == "Settings":
            from app_pages import settings
            settings.show()
    except Exception as e:
        st.error(f"Error loading page: {str(e)}")
        import traceback
        st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
