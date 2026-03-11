"""
SafeRoute AI - Chatbot Page
===========================
AI-powered chatbot using Groq API - Clean Q&A Interface
"""

import streamlit as st
import requests
import json
from config import (
    APP_NAME, APP_VERSION, TEAM_NAME, HACKATHON,
    get_groq_key, DEMO_CITIES, HAZARD_TYPES
)


def get_groq_response(messages: list) -> str:
    """Get response from Groq API with improved error handling."""
    api_key = get_groq_key()
    
    if not api_key:
        return "⚠️ Groq API key not configured. Please add GROQ_API_KEY to Streamlit secrets."
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024,
            "top_p": 0.95,
            "stream": False
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        elif response.status_code == 401:
            return "⚠️ Invalid API key. Please check your Groq API key in secrets.toml."
        elif response.status_code == 429:
            return "⚠️ Rate limit exceeded. Please wait a moment and try again."
        else:
            return f"⚠️ API Error ({response.status_code}): {response.text[:200]}"
            
    except requests.exceptions.Timeout:
        return "⚠️ Request timed out. Please check your internet connection and try again."
    except requests.exceptions.ConnectionError:
        return "⚠️ Connection error. Please check your internet connection."
    except json.JSONDecodeError:
        return "⚠️ Invalid response from API. Please try again."
    except Exception as e:
        return f"⚠️ Unexpected error: {str(e)}"


def show():
    """Display the chatbot page."""
    
    # Page header
    st.markdown("""
    <div class="page-header">
        <h1>💬 SafeRoute AI Assistant</h1>
        <p class="subtitle">Ask me anything about SafeRoute AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Initialize chat history in session state (stored in settings)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # System prompt
    system_prompt = {
        "role": "system",
        "content": f"""You are a helpful AI assistant for SafeRoute AI, an AI-powered road hazard detection system for Indian roads.

About: {APP_NAME} v{APP_VERSION}
Team: {TEAM_NAME}
Hackathon: {HACKATHON}

Features:
1. Dashboard - Real-time hazard monitoring with KPIs and charts
2. Hazard Detection - Upload images to detect potholes, cracks, waterlogging using OpenCV
3. Hazard Map - Interactive Folium map with hazard markers and heatmap
4. Route Planner - A-to-B routing with hazard scoring
5. Analytics - Deep charts and trend analysis
6. Govt Report - Generate PDF reports for municipal authorities

Supported Cities: Mumbai, Pune, Delhi, Bangalore, Chennai, Hyderabad, Kolkata, Chiplun
Hazard Types: Pothole, Road Crack, Waterlogging, Road Wear, Debris
Severity: Low, Medium, High

Be helpful, friendly, and concise."""
    }
    
    # Display chat messages (Q&A only)
    st.markdown("### 💬 Conversation")
    
    for i, msg in enumerate(st.session_state.chat_history):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Quick questions section (only show if chat is empty)
    if not st.session_state.chat_history:
        st.info("💡 Try asking me about:")
        col1, col2, col3, col4 = st.columns(4)
        quick_questions = [
            "What is SafeRoute AI?",
            "How does hazard detection work?",
            "Which cities are supported?",
            "How to report a hazard?"
        ]
        for i, q in enumerate(quick_questions):
            with [col1, col2, col3, col4][i]:
                if st.button(f"📝 {q}", key=f"quick_{i}"):
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": q
                    })
                    messages = [system_prompt] + [
                        {"role": msg["role"], "content": msg["content"]} 
                        for msg in st.session_state.chat_history
                    ]
                    response = get_groq_response(messages)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response
                    })
                    st.rerun()
    
    # Chat input
    st.markdown("---")
    
    if prompt := st.chat_input("Ask me anything about SafeRoute AI..."):
        # Add user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.spinner("🤔 Thinking..."):
            # Build messages for API
            messages = [system_prompt] + [
                {"role": msg["role"], "content": msg["content"]} 
                for msg in st.session_state.chat_history
            ]
            response = get_groq_response(messages)
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)
        
        # Add to history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })
        
        st.rerun()
    
    # Clear chat button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    st.markdown("---")
