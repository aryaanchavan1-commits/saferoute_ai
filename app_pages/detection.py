"""
SafeRoute AI - Hazard Detection Page
====================================
Image upload, camera input, and AI-powered hazard detection.
"""

import streamlit as st
from datetime import datetime
import random

from PIL import Image

from config import (
    COLOR_NAVY, COLOR_TEAL, COLOR_CORAL, SEVERITY_COLORS, 
    HAZARD_TYPES, CITY_NAMES, DEFAULT_CITY
)
from utils.detector import HazardDetector, create_demo_image
from utils.data import HazardRecord


def show():
    """Display the hazard detection page."""
    
    # Page header
    st.markdown("""
    <div class="page-header">
        <h1>🔍 Hazard Detection</h1>
        <p class="subtitle">Upload images or use camera to detect road hazards using AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Create tabs for different input methods
    tab1, tab2, tab3 = st.tabs(["📤 Upload Image", "📷 Use Camera", "🖼️ Run Demo"])
    
    # Initialize detector
    detector = HazardDetector()
    
    # Store detection results in session state
    if "detection_results" not in st.session_state:
        st.session_state.detection_results = None
    
    # ========== TAB 1: UPLOAD IMAGE ==========
    with tab1:
        st.markdown("#### 📁 Upload an Image")
        
        uploaded_file = st.file_uploader(
            "Choose an image file (jpg, jpeg, png)",
            type=["jpg", "jpeg", "png"],
            help="Upload a road image to analyze for hazards"
        )
        
        if uploaded_file is not None:
            with st.spinner("🔄 Processing image..."):
                # Open and process image
                image = Image.open(uploaded_file)
                
                # Run detection
                annotated_image, detections = detector.detect(image)
                
                # Store results
                st.session_state.detection_results = {
                    "original": image,
                    "annotated": annotated_image,
                    "detections": detections,
                    "source": "upload"
                }
    
    # ========== TAB 2: USE CAMERA ==========
    with tab2:
        st.markdown("#### 📸 Capture from Camera")
        
        camera_input = st.camera_input(
            "Take a photo of the road",
            help="Use your camera to capture a road image"
        )
        
        if camera_input is not None:
            with st.spinner("🔄 Processing image..."):
                # Open and process image
                image = Image.open(camera_input)
                
                # Run detection
                annotated_image, detections = detector.detect(image)
                
                # Store results
                st.session_state.detection_results = {
                    "original": image,
                    "annotated": annotated_image,
                    "detections": detections,
                    "source": "camera"
                }
    
    # ========== TAB 3: RUN DEMO ==========
    with tab3:
        st.markdown("#### 🖼️ Demo Images")
        st.markdown("Choose a demo image type to see the detection in action:")
        
        demo_options = {
            "pothole": "🚧 Pothole Detection",
            "waterlogging": "💧 Waterlogging Detection",
            "crack": "⚡ Road Crack Detection",
            "debris": "🪨 Debris Detection"
        }
        
        selected_demo = st.selectbox(
            "Select demo type",
            options=list(demo_options.keys()),
            format_func=lambda x: demo_options[x],
            index=0
        )
        
        if st.button("▶️ Run Demo Detection", type="primary"):
            with st.spinner("🔄 Generating demo image and detecting hazards..."):
                # Create demo image
                demo_image = create_demo_image(selected_demo)
                
                # Run detection
                annotated_image, detections = detector.detect(demo_image)
                
                # Store results
                st.session_state.detection_results = {
                    "original": demo_image,
                    "annotated": annotated_image,
                    "detections": detections,
                    "source": "demo"
                }
    
    # ========== DISPLAY RESULTS ==========
    results = st.session_state.detection_results
    
    if results:
        st.markdown("---")
        st.markdown("### 📊 Detection Results")
        
        # Show original and annotated images side by side
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📷 Original Image**")
            st.image(results["original"], width='stretch')
        
        with col2:
            st.markdown("**🎯 Annotated Result**")
            st.image(results["annotated"], width='stretch')
        
        # Display detections
        detections = results["detections"]
        
        if detections:
            st.markdown(f"### ✅ Found {len(detections)} Hazard(s)")
            
            # Create detection cards
            for i, detection in enumerate(detections):
                hazard_type = detection.hazard_type.lower().replace(" ", "-")
                
                severity_color = SEVERITY_COLORS.get(detection.severity, "#6b7280")
                
                st.markdown(f"""
                <div class="detection-card {hazard_type}">
                    <h3 style="margin: 0 0 10px 0; color: white !important;">
                        {detection.hazard_type}
                    </h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Show detection details
                det_col1, det_col2, det_col3 = st.columns(3)
                
                with det_col1:
                    st.markdown("**⚠️ Severity:**")
                    severity_html = f"""
                    <span style="background: {severity_color}; 
                                 color: white; 
                                 padding: 5px 15px; 
                                 border-radius: 20px; 
                                 font-weight: bold;">
                        {detection.severity}
                    </span>
                    """
                    st.markdown(severity_html, unsafe_allow_html=True)
                
                with det_col2:
                    st.markdown("**📈 Confidence:**")
                    st.progress(detection.confidence)
                    st.caption(f"{detection.confidence:.0%}")
                
                with det_col3:
                    st.markdown("**📐 Bounding Box:**")
                    x, y, w, h = detection.bbox
                    st.caption(f"Position: ({x}, {y})")
                    st.caption(f"Size: {w}×{h}px")
                
                st.markdown("---")
            
            # ========== LOG HAZARD BUTTON ==========
            st.markdown("### 💾 Log This Hazard")
            
            # Create form for logging
            with st.form("log_hazard_form"):
                log_col1, log_col2 = st.columns(2)
                
                with log_col1:
                    selected_city = st.selectbox(
                        "🏙️ City",
                        options=CITY_NAMES,
                        index=CITY_NAMES.index(DEFAULT_CITY)
                    )
                
                with log_col2:
                    selected_type = st.selectbox(
                        "🚧 Hazard Type",
                        options=[d.hazard_type for d in detections]
                    )
                
                submitted = st.form_submit_button("💾 Log This Hazard", type="primary")
                
                if submitted:
                    # Create new hazard record
                    from utils.data import get_city_coordinates
                    
                    coords = get_city_coordinates(selected_city)
                    
                    # Get the selected detection
                    selected_detection = next((d for d in detections if d.hazard_type == selected_type), detections[0])
                    
                    # Generate unique ID
                    hazard_id = f"HR-{selected_city[:3].upper()}-{random.randint(1000, 9999)}"
                    
                    new_hazard = HazardRecord(
                        id=hazard_id,
                        hazard_type=selected_detection.hazard_type,
                        severity=selected_detection.severity,
                        latitude=coords[0] + random.uniform(-0.01, 0.01),
                        longitude=coords[1] + random.uniform(-0.01, 0.01),
                        city=selected_city,
                        description=f"Detected via {results['source']}: {selected_detection.hazard_type}",
                        timestamp=datetime.now(),
                        status="Reported",
                        confidence=selected_detection.confidence,
                        reported_by="AI Detection",
                        upvotes=0,
                        image_path=None
                    )
                    
                    # Add to hazards list
                    if "hazards" not in st.session_state:
                        st.session_state.hazards = []
                    
                    st.session_state.hazards.insert(0, new_hazard)
                    
                    st.success(f"✅ Hazard logged successfully! ID: {hazard_id}")
        else:
            st.success("✅ Clear Road - No hazards detected!")
            
            # Option to log as confirmed clear
            if st.button("✅ Confirm Clear Road"):
                st.success("Road marked as clear. Thank you for your report!")
    
    else:
        # Show placeholder when no image processed
        st.info("👆 Upload an image, use camera, or run a demo to detect hazards")
        
        # Show helpful tips
        st.markdown("""
        ### 💡 Tips for Best Results
        - 📸 Take photos in good lighting
        - 🛣️ Ensure the road is clearly visible
        - 📐 Keep the camera steady
        - 🏙️ Include the hazard in the frame
        """)
