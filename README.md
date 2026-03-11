# SafeRoute AI

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.13%2B-green" alt="Python">
  <img src="https://img.shields.io/badge/Hackathon-CODE%201%202026-orange" alt="Hackathon">
</p>

**SafeRoute AI** is an AI-powered road hazard detection and smart navigation system for Indian roads. Built for CODE 1 Hackathon 2026 by Team: **mortal_coders**.

## 🚀 Quick Start

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

## 📁 Project Structure

```
saferoute_ai/
├── app.py                  # Main entry point
├── requirements.txt        # All pip dependencies
├── README.md               # This file
├── config.py               # App-wide constants & settings
├── pages/
│   ├── __init__.py
│   ├── dashboard.py        # KPI cards + charts + recent table
│   ├── detection.py        # Image upload → AI detection → annotated output
│   ├── hazard_map.py       # Folium map with hazard markers + heatmap
│   ├── route_planner.py    # A-to-B routing with hazard score
│   ├── analytics.py        # Deep charts: trend, city, type breakdowns
│   ├── govt_report.py      # Generate PDF report + submit form
│   └── settings.py         # City filter, severity threshold, preferences
├── utils/
│   ├── __init__.py
│   ├── data.py             # HazardRecord dataclass + mock data generator
│   ├── detector.py         # OpenCV-based road hazard detection engine
│   └── maps.py             # Folium map builder functions
└── assets/
    └── style.css           # Extra CSS injected via st.markdown
```

## 📋 Features

### 1. Dashboard
- **5 KPI Metrics**: Total Hazards, High Severity count, Fixed count, AI Accuracy %, Active Issues
- **Bar Chart**: Hazards by type (horizontal)
- **Pie/Donut Chart**: Severity distribution
- **Area Chart**: Daily hazard reports (last 30 days, stacked by severity)
- **Bar Chart**: Top cities by hazard count
- **Funnel Chart**: Repair status pipeline
- **Recent Detections Table**: Last 12 records with severity colors

### 2. Hazard Detection
- **3 Tabs**: Upload Image, Use Camera, Run Demo
- **Upload**: Accepts jpg/png/jpeg files
- **Camera**: st.camera_input for live capture
- **Demo**: 4 preset demo images simulating road hazards
- **Detection**: OpenCV-based analysis with thresholding and contour detection
- **Logging**: Save detected hazards to the system

### 3. Hazard Map
- **City Selector**: 8 Indian cities + "All India"
- **Severity Filter**: Multiselect checkboxes
- **Display Options**: Toggle Heatmap / Markers / Both
- **Interactive Map**: Click markers for hazard details
- **Sidebar Stats**: Count by severity

### 4. Route Planner
- **Start/End City**: Select from 8 cities
- **Avoid Severity**: Option to avoid High/Medium severity hazards
- **Route Map**: Folium map with route polyline and hazard markers
- **Hazard Score**: Color-coded gauge (green <3, orange 3-6, red >6)
- **Route Info**: Distance, duration, hazard count

### 5. Analytics
- **Date Range Filter**: Last 7/14/30 days
- **City Multi-select**: Filter by city
- **6 Charts**:
  1. Line chart: Detection confidence trend
  2. Grouped bar: Hazard types per city
  3. Scatter map: Lat/lon colored by severity
  4. Pie: Reporter breakdown (AI vs User)
  5. Bar: Average time-to-fix by type
  6. Heatmap: City vs Hazard Type matrix

### 6. Govt Report
- **Form**: Reporter name, city, date range, severity filter
- **PDF Generation**: fpdf2 with header, summary table, top 10 hazards
- **Download**: st.download_button for PDF
- **Submit Form**: Mock submission to municipality with success message

### 7. Settings
- **Default City**: Select preferred city
- **Severity Threshold**: Slider (0-100 for confidence cutoff)
- **Heatmap Toggle**: Enable/disable by default
- **Dark Map Toggle**: Light/dark map tiles
- **Reset to Defaults**: Restore all settings
- **About Section**: Project description, team, tech stack

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| Charts | Plotly |
| Maps | Folium + streamlit-folium |
| Image Processing | OpenCV, Pillow |
| AI/ML | scikit-learn, numpy |
| Data | Pandas |
| PDF | fpdf2 |

## ⚙️ Requirements

- Python 3.13+
- Streamlit >= 1.35.0
- Plotly >= 5.22.0
- Folium >= 0.17.0
- streamlit-folium >= 0.22.0
- opencv-python-headless >= 4.10.0
- Pillow >= 10.4.0
- numpy >= 2.0.0
- pandas >= 2.2.0
- fpdf2 >= 2.8.0
- scikit-learn >= 1.5.0

## 🎯 Supported Cities

1. Mumbai, Maharashtra
2. Pune, Maharashtra
3. Delhi, NCR
4. Bangalore, Karnataka
5. Chennai, Tamil Nadu
6. Hyderabad, Telangana
7. Chiplun, Maharashtra
8. Kolkata, West Bengal

## 🔍 Hazard Types

- **Pothole**: Road surface damage
- **Road Crack**: Surface cracks
- **Waterlogging**: Standing water
- **Road Wear**: Surface deterioration
- **Debris**: Obstructions on road

## 👥 Team

- **Team Name**: mortal_coders
- **Hackathon**: CODE 1 Hackathon 2026

## 📝 MongoDB Integration (Optional)

To use MongoDB for data persistence, add the following to your `.streamlit/secrets.toml`:

```toml
[mongo_db_url]
mongodb_connection_string = "your_connection_string"
```

Then access it in your code:

```python
import streamlit as st
mongo_url = st.secrets.get("mongo_db_url", "")
```

## 📄 License

This project is built for the CODE 1 Hackathon 2026.

---

<p align="center">
  🚗 Made with ❤️ for safer Indian roads
</p>
