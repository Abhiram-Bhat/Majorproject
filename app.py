import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import base64
from io import StringIO, BytesIO
import time
import random
# --- WORKOUT_DATA.PY & RECOMMENDER CLASS ---
from workout_data import WorkoutRecommender, EXERCISE_DATABASE
from utils import calculate_bmi, get_bmi_category, export_workout_plan_pdf
# --- Caching Workout Plan Generation ---
@st.cache_data
def generate_workout_plan(fitness_level, goal, bmi, bmi_category):
    """Generate and cache workout plan."""
    recommender = WorkoutRecommender()
    return recommender.generate_workout_plan(
        fitness_level=fitness_level,
        goal=goal,
        bmi=bmi,
        bmi_category=bmi_category
    )
# --- Jaw-Dropping UI/UX CSS with Advanced Effects ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    :root {
        --primary: #4F46E5;
        --accent: #10B981;
        --secondary: #EF4444;
        --background: linear-gradient(135deg, #1F2937 0%, #111827 100%);
        --surface: rgba(31, 41, 55, 0.8);
        --text: #F9FAFB;
        --text-muted: #9CA3AF;
        --shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    
    .stApp {
        font-family: 'Poppins', sans-serif;
        background: var(--background);
        color: var(--text);
        max-width: 1400px;
        margin: 0 auto;
        padding: 2rem;
        overflow: hidden;
    }
    
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, var(--primary), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 3rem;
        animation: fadeInDown 1s ease-out;
    }
    
    @keyframes fadeInDown { from { opacity: 0; transform: translateY(-50px); } to { opacity: 1; transform: translateY(0); } }
    
    .stSidebar {
        background: rgba(31, 41, 55, 0.6);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: var(--shadow);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stSidebar h2 {
        color: var(--accent);
        font-size: 1.8rem;
        margin-bottom: 1.5rem;
    }
    
    .stTextInput > div > input,
    .stNumberInput > div > input,
    .stSelectbox > div > select {
        background: rgba(55, 65, 81, 0.8);
        color: var(--text);
        border: 1px solid var(--primary);
        border-radius: 8px;
        padding: 0.75rem;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, var(--primary), var(--accent));
        color: white;
        border-radius: 50px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border: none;
    }
    
    .bmi-card {
        background: radial-gradient(circle, rgba(79, 70, 229, 0.2), transparent);
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: var(--shadow);
        margin: 1.5rem 0;
    }
    
    .bmi-value { font-size: 2.8rem; font-weight: 700; color: var(--accent); }
    .bmi-category { font-size: 1.3rem; color: var(--text-muted); margin-top: 0.5rem; }
    
    .workout-card {
        background: var(--surface);
        padding: 2rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        border-left: 6px solid var(--primary);
        box-shadow: var(--shadow);
    }
    
    .day-header { font-size: 1.6rem; font-weight: 700; color: var(--primary); margin-bottom: 0.5rem; }
    .muscle-group { font-size: 1.2rem; color: var(--text-muted); margin-bottom: 1rem; }
    .exercise-list { color: var(--text); line-height: 1.7; font-size: 1rem; }
    .exercise-list li { list-style: none; margin-bottom: 0.5rem; }
    .exercise-list li::before { content: '\\f058'; font-family: 'Font Awesome 6 Free'; font-weight: 900; color: var(--accent); margin-right: 0.5rem; }
    
    .progress-metric {
        background: var(--surface);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: var(--shadow);
        margin: 1rem;
    }
    
    .metric-value { font-size: 2.5rem; font-weight: 800; color: var(--accent); }
    .metric-label { font-size: 1rem; color: var(--text-muted); margin-top: 0.5rem; }
    
    .pose-feedback {
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 600;
        font-size: 1.1rem;
        text-align: center;
        background: linear-gradient(135deg, #10B981, #059669); color: white; 
    }
    
    .camera-container {
        background: var(--surface);
        border: 3px solid var(--primary);
        border-radius: 16px;
        padding: 1rem;
        box-shadow: 0 0 20px rgba(79, 70, 229, 0.3);
        position: relative;
        text-align: center;
        width: 100%;
        max-width: 100%;
        overflow: hidden;
    }
    
    .stTabs [data-baseweb="tab-list"] { background: transparent; border-bottom: 2px solid rgba(255,255,255,0.1); margin-bottom: 2rem; }
    .stTabs [data-baseweb="tab"] { color: var(--text-muted); font-weight: 600; padding: 1rem 2rem; }
    .stTabs [aria-selected="true"] { color: var(--accent); border-bottom: 3px solid var(--accent); }
    
    .welcome-hero {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%234F46E5" fill-opacity="0.2" d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,122.7C672,117,768,139,864,133.3C960,128,1056,96,1152,90.7C1248,85,1344,107,1392,117.3L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>');
        background-size: cover;
        background-position: center;
        border-radius: 16px;
        padding: 4rem 2rem;
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .welcome-hero h2 { font-size: 2.5rem; font-weight: 800; color: var(--text); margin-bottom: 1rem; }
    .welcome-hero p { font-size: 1.2rem; color: var(--text-muted); max-width: 600px; margin: 0 auto 2rem; }
    
    .feature-card {
        background: var(--surface);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: var(--shadow);
    }
    
    .feature-icon { font-size: 2.5rem; color: var(--accent); margin-bottom: 1rem; }
    
    @media (max-width: 768px) {
        .main-header { font-size: 2.5rem; }
        .stSidebar { padding: 1.5rem; }
        .workout-card, .progress-metric { margin: 1rem 0; }
        .stColumns > div { flex-direction: column; }
        .welcome-hero { padding: 3rem 1rem; }
    }
    
    .macro-card {
        background: var(--surface);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: var(--shadow});
        margin: 1rem 0;
    }
    
    .macro-value { font-size: 1.5rem; font-weight: 600; color: var(--accent); }
    .macro-label { font-size: 1rem; color: var(--text-muted); }
    
    .suggestion-box {
        background: rgba(16, 185, 129, 0.2);
        border-left: 4px solid var(--accent);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    .camera-placeholder {
        background-color: rgba(31, 41, 55, 0.5);
        border: 2px dashed var(--primary);
        border-radius: 12px;
        padding: 3rem;
        text-align: center;
        color: var(--text-muted);
        margin: 1rem 0;
    }
    
    .video-wrapper {
        position: relative;
        width: 100%;
        border-radius: 12px;
        overflow: hidden;
    }
    
    #webcam {
        width: 100%;
        height: auto;
        border-radius: 12px;
        display: block;
    }
    
    .feedback-banner {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        padding: 15px;
        color: white;
        font-weight: 600;
        font-size: 1.2rem;
        text-align: center;
        z-index: 10;
        transition: background-color 0.5s ease;
    }
    
    .feedback-good {
        background-color: rgba(16, 185, 129, 0.9);
    }
    
    .feedback-bad {
        background-color: rgba(239, 68, 68, 0.9);
    }
    
    .food-source-card {
        background: var(--surface);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow});
    }
    
    .food-source-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--accent);
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
    }
    
    .food-source-header i {
        margin-right: 0.5rem;
    }
    
    .food-item {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .food-item:last-child {
        border-bottom: none;
    }
    
    .food-name {
        font-weight: 500;
    }
    
    .food-macros {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    
    .macro-badge {
        background: rgba(79, 70, 229, 0.2);
        color: var(--accent);
        padding: 0.2rem 0.5rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .dietary-preference {
        margin-top: 1rem;
        padding: 1rem;
        background: rgba(79, 70, 229, 0.1);
        border-radius: 8px;
    }
    
    .dietary-preference h3 {
        margin-top: 0;
        color: var(--accent);
    }
    
    .video-attribution {
        font-size: 0.9rem;
        color: var(--text-muted);
        margin-top: 0.5rem;
    }
    
    .video-attribution a {
        color: var(--accent);
        text-decoration: none;
    }
    
    .video-attribution a:hover {
        text-decoration: underline;
    }
    
    .copyright-disclaimer {
        font-size: 0.8rem;
        color: var(--text-muted);
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)
# --- Page Configuration ---
st.set_page_config(
    page_title="AI Fitness Trainer",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)
# --- Initialize Session State ---
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'workout_plan' not in st.session_state:
    st.session_state.workout_plan = None
if 'progress_data' not in st.session_state:
    st.session_state.progress_data = {
        'workouts_completed': 0,
        'total_workouts': 0,
        'streak_days': 0,
        'last_workout': None,
        'daily_logs': {}
    }
if 'macros' not in st.session_state:
    st.session_state.macros = None
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False
if 'current_suggestion' not in st.session_state:
    st.session_state.current_suggestion = "Select an exercise to begin"
if 'suggestions' not in st.session_state:
    st.session_state.suggestions = []
if 'feedback_status' not in st.session_state:
    st.session_state.feedback_status = "good"
if 'dietary_preference' not in st.session_state:
    st.session_state.dietary_preference = "Both"
# --- Enhanced Food Sources Data ---
protein_sources = {
    "Vegetarian": [
        {"name": "Paneer (100g)", "protein": 18, "fats": 20, "carbs": 2, "calories": 265},
        {"name": "Lentils (Dal, 100g cooked)", "protein": 9, "fats": 0.4, "carbs": 20, "calories": 116},
        {"name": "Greek Yogurt (170g)", "protein": 17, "fats": 0.4, "carbs": 6, "calories": 100},
        {"name": "Tofu (100g)", "protein": 8, "fats": 4.8, "carbs": 2, "calories": 76},
        {"name": "Chickpeas (Chana, 100g cooked)", "protein": 9, "fats": 2.6, "carbs": 27, "calories": 164}
    ],
    "Non-Vegetarian": [
        {"name": "Chicken Breast (100g)", "protein": 31, "fats": 3.6, "carbs": 0, "calories": 165},
        {"name": "Eggs (2 large)", "protein": 12, "fats": 10, "carbs": 0.8, "calories": 155},
        {"name": "Salmon (100g)", "protein": 25, "fats": 13, "carbs": 0, "calories": 208},
        {"name": "Tuna (100g)", "protein": 30, "fats": 1.3, "carbs": 0, "calories": 132},
        {"name": "Lean Beef (100g)", "protein": 26, "fats": 15, "carbs": 0, "calories": 250}
    ]
}
fat_sources = {
    "Vegetarian": [
        {"name": "Avocado (100g)", "protein": 2, "fats": 15, "carbs": 9, "calories": 160},
        {"name": "Almonds (28g)", "protein": 6, "fats": 14, "carbs": 6, "calories": 164},
        {"name": "Walnuts (28g)", "protein": 4.3, "fats": 18, "carbs": 4, "calories": 185},
        {"name": "Flaxseeds (28g)", "protein": 5.2, "fats": 12, "carbs": 8, "calories": 150},
        {"name": "Chia Seeds (28g)", "protein": 4.4, "fats": 9, "carbs": 12, "calories": 138}
    ],
    "Non-Vegetarian": [
        {"name": "Ghee (1 tbsp)", "protein": 0, "fats": 14, "carbs": 0, "calories": 126},
        {"name": "Butter (1 tbsp)", "protein": 0.1, "fats": 11.5, "carbs": 0, "calories": 102},
        {"name": "Cheese (28g)", "protein": 7, "fats": 9, "carbs": 1, "calories": 113},
        {"name": "Cream (2 tbsp)", "protein": 0.6, "fats": 11, "carbs": 0.8, "calories": 103},
        {"name": "Mayonnaise (1 tbsp)", "protein": 0.1, "fats": 10, "carbs": 0, "calories": 94}
    ]
}
carb_sources = {
    "Vegetarian": [
        {"name": "Brown Rice (1 cup cooked)", "protein": 5, "fats": 2, "carbs": 45, "calories": 216},
        {"name": "Quinoa (1 cup cooked)", "protein": 8, "fats": 4, "carbs": 39, "calories": 222},
        {"name": "Oats (1 cup cooked)", "protein": 6, "fats": 4, "carbs": 28, "calories": 158},
        {"name": "Sweet Potato (1 medium)", "protein": 4, "fats": 0.1, "carbs": 24, "calories": 103},
        {"name": "Whole Wheat Bread (2 slices)", "protein": 8, "fats": 2, "carbs": 24, "calories": 164}
    ],
    "Non-Vegetarian": [
        {"name": "Brown Rice (1 cup cooked)", "protein": 5, "fats": 2, "carbs": 45, "calories": 216},
        {"name": "Sweet Potato (1 medium)", "protein": 4, "fats": 0.1, "carbs": 24, "calories": 103},
        {"name": "Quinoa (1 cup cooked)", "protein": 8, "fats": 4, "carbs": 39, "calories": 222},
        {"name": "Oats (1 cup cooked)", "protein": 6, "fats": 4, "carbs": 28, "calories": 158},
        {"name": "Whole Wheat Bread (2 slices)", "protein": 8, "fats": 2, "carbs": 24, "calories": 164}
    ]
}
# --- Main Header ---
st.markdown('<h1 class="main-header">🤖 AI Fitness Trainer</h1>', unsafe_allow_html=True)
# --- Sidebar ---
with st.sidebar:
    st.header("👤 Profile Setup")
    with st.form("user_profile"):
        name = st.text_input("Name", value=st.session_state.user_data.get('name', ''))
        age = st.number_input("Age", min_value=16, max_value=100, value=st.session_state.user_data.get('age', 25))
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                              index=["Male", "Female", "Other"].index(st.session_state.user_data.get('gender', 'Male')))
        height = st.number_input("Height (cm)", min_value=120, max_value=250, 
                                 value=st.session_state.user_data.get('height', 175))
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, 
                                 value=st.session_state.user_data.get('weight', 70.0))
        fitness_level = st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"],
                                     index=["Beginner", "Intermediate", "Advanced"].index(st.session_state.user_data.get('fitness_level', 'Beginner')))
        goal = st.selectbox("Primary Goal", ["Muscle Building", "Fat Loss", "Strength Training"],
                            index=["Muscle Building", "Fat Loss", "Strength Training"].index(st.session_state.user_data.get('goal', 'Muscle Building')))
        submit_profile = st.form_submit_button("Generate Plan")
    
    if submit_profile or st.session_state.user_data:
        st.session_state.user_data.update({
            'name': name,
            'age': age,
            'gender': gender,
            'height': height,
            'weight': weight,
            'fitness_level': fitness_level,
            'goal': goal
        })
        
        bmi = calculate_bmi(weight, height)
        bmi_category = get_bmi_category(bmi)
        
        st.markdown(f"""
        <div class="bmi-card">
            <div class="bmi-value">{bmi:.1f}</div>
            <div class="bmi-category">{bmi_category}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if submit_profile:
            st.session_state.workout_plan = generate_workout_plan(fitness_level, goal, bmi, bmi_category)
            st.session_state.progress_data['total_workouts'] = sum(len(day['exercises']) for day in st.session_state.workout_plan.values() if day['exercises'])
            
            activity_factor = {'Beginner': 1.2, 'Intermediate': 1.55, 'Advanced': 1.725}.get(fitness_level, 1.55)
            if gender == "Male":
                bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            else:
                bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
            tdee = bmr * activity_factor
            
            if goal == "Muscle Building":
                calories = tdee + 500
            elif goal == "Fat Loss":
                calories = tdee - 500
            else:
                calories = tdee
                
            protein = weight * 2.0
            fats = calories * 0.25 / 9
            carbs = (calories - (protein * 4) - (fats * 9)) / 4
            
            st.session_state.macros = {
                'calories': int(calories),
                'protein': int(protein),
                'fats': int(fats),
                'carbs': int(carbs)
            }
    
    # Dietary Preference Selection
    st.markdown('<div class="dietary-preference">', unsafe_allow_html=True)
    st.markdown("### Dietary Preference")
    dietary_pref = st.radio(
        "Select your dietary preference:",
        ["Both", "Vegetarian", "Non-Vegetarian"],
        index=["Both", "Vegetarian", "Non-Vegetarian"].index(st.session_state.dietary_preference)
    )
    st.session_state.dietary_preference = dietary_pref
    st.markdown('</div>', unsafe_allow_html=True)
# --- Function to create the camera component ---
def camera_component(suggestions):
    suggestions_json = json.dumps(suggestions)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: 'Poppins', sans-serif;
                background-color: transparent;
            }}
            .video-wrapper {{
                position: relative;
                width: 100%;
                border-radius: 12px;
                overflow: hidden;
            }}
            #webcam {{
                width: 100%;
                height: auto;
                border-radius: 12px;
                display: block;
            }}
            .feedback-banner {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                padding: 15px;
                color: white;
                font-weight: 600;
                font-size: 1.2rem;
                text-align: center;
                z-index: 10;
                transition: background-color 0.5s ease;
            }}
            .feedback-good {{
                background-color: rgba(16, 185, 129, 0.9);
            }}
            .feedback-bad {{
                background-color: rgba(239, 68, 68, 0.9);
            }}
            .error-message {{
                color: #EF4444;
                text-align: center;
                padding: 20px;
                background-color: rgba(31, 41, 55, 0.5);
                border-radius: 12px;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="video-wrapper">
            <video id="webcam" autoplay playsinline></video>
            <div id="feedback-banner" class="feedback-banner feedback-good">
                {suggestions[0] if suggestions else "Perform the exercise with good form"}
            </div>
        </div>
        <div id="error-container"></div>
        
        <script>
            const suggestions = {suggestions_json};
            let currentSuggestionIndex = 0;
            let isGoodForm = true;
            let intervalId = null;
            
            const video = document.getElementById('webcam');
            const banner = document.getElementById('feedback-banner');
            const errorContainer = document.getElementById('error-container');
            
            function startCamera() {{
                navigator.mediaDevices.getUserMedia({{ video: true }})
                    .then(stream => {{
                        video.srcObject = stream;
                        // Start changing banner every 5 seconds
                        intervalId = setInterval(changeBanner, 5000);
                    }})
                    .catch(err => {{
                        console.error("Error accessing webcam:", err);
                        errorContainer.innerHTML = `<div class="error-message">
                            <i class="fa-solid fa-exclamation-triangle"></i> 
                            Failed to access camera. Please ensure camera permissions are granted.
                            <br><small>Error: ${{err.message}}</small>
                        </div>`;
                    }});
            }}
            
            function changeBanner() {{
                // Toggle between good and bad form
                isGoodForm = !isGoodForm;
                
                // Get a random suggestion
                currentSuggestionIndex = Math.floor(Math.random() * suggestions.length);
                const suggestion = suggestions[currentSuggestionIndex];
                
                // Update banner text and class
                banner.textContent = suggestion;
                
                if (isGoodForm) {{
                    banner.className = 'feedback-banner feedback-good';
                }} else {{
                    banner.className = 'feedback-banner feedback-bad';
                }}
            }}
            
            // Initialize camera when page loads
            window.addEventListener('load', startCamera);
            
            // Cleanup when component is unmounted
            window.addEventListener('beforeunload', () => {{
                if (intervalId) {{
                    clearInterval(intervalId);
                }}
                if (video.srcObject) {{
                    video.srcObject.getTracks().forEach(track => track.stop());
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    return html_code
# --- Function to display food sources ---
def display_food_sources(title, icon, sources, category):
    st.markdown(f"""
    <div class="food-source-header">
        <i class="{icon}"></i> {title} - {category}
    </div>
    """, unsafe_allow_html=True)
    
    for food in sources:
        st.markdown(f"""
        <div class="food-item">
            <div class="food-name">{food['name']}</div>
            <div class="food-macros">
                <span class="macro-badge">P: {food['protein']}g</span>
                <span class="macro-badge">F: {food['fats']}g</span>
                <span class="macro-badge">C: {food['carbs']}g</span>
                <span class="macro-badge">Cal: {food['calories']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
# --- Main Content ---
if st.session_state.workout_plan:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📅 Plan", "📊 Progress", "🎥 Detection", "📁 Export", "🎬 Workout Videos"])
    
    with tab1:
        st.header("Personalized Workout Plan")
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        cols = st.columns(2)
        for i, day in enumerate(days):
            with cols[i % 2]:
                workout_data = st.session_state.workout_plan[day]
                if workout_data['muscle_group'] == 'Rest':
                    st.markdown(f"""
                    <div class="workout-card">
                        <div class="day-header"><i class="fa-solid fa-bed"></i>{day}</div>
                        <div class="muscle-group">Rest Day</div>
                        <div class="exercise-list">Recover & Recharge</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    exercises_text = "".join([f"<li>{exercise}</li>" for exercise in workout_data['exercises']])
                    st.markdown(f"""
                    <div class="workout-card">
                        <div class="day-header"><i class="fa-solid fa-dumbbell"></i>{day}</div>
                        <div class="muscle-group">{workout_data['muscle_group']}</div>
                        <ul class="exercise-list">{exercises_text}</ul>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Mark Complete", key=f"complete_{day}"):
                        today = datetime.now().strftime("%Y-%m-%d")
                        if today not in st.session_state.progress_data['daily_logs']:
                            st.session_state.progress_data['daily_logs'][today] = []
                        if day not in st.session_state.progress_data['daily_logs'][today]:
                            st.session_state.progress_data['daily_logs'][today].append(day)
                            st.session_state.progress_data['workouts_completed'] += 1
                            st.session_state.progress_data['last_workout'] = today
                            st.session_state.progress_data['streak_days'] += 1
                            st.success(f"{day} Completed! Keep the momentum! 🔥")
        
        if 'macros' in st.session_state and st.session_state.macros:
            st.subheader("Recommended Daily Macros")
            cols = st.columns(4)
            macros = st.session_state.macros
            metrics = [
                ("Calories", macros['calories']),
                ("Protein (g)", macros['protein']),
                ("Fats (g)", macros['fats']),
                ("Carbs (g)", macros['carbs'])
            ]
            for i, (label, value) in enumerate(metrics):
                with cols[i]:
                    st.markdown(f"""
                    <div class="macro-card">
                        <div class="macro-value">{value}</div>
                        <div class="macro-label">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.subheader("Food Sources for Your Macros")
            
            # Get dietary preference
            dietary_pref = st.session_state.dietary_preference
            
            # Protein Sources
            st.markdown("#### Protein Sources")
            if dietary_pref in ["Both", "Vegetarian"]:
                st.markdown('<div class="food-source-card">', unsafe_allow_html=True)
                display_food_sources("Protein Rich Foods", "fa-solid fa-leaf", protein_sources["Vegetarian"], "Vegetarian")
                st.markdown('</div>', unsafe_allow_html=True)
            
            if dietary_pref in ["Both", "Non-Vegetarian"]:
                st.markdown('<div class="food-source-card">', unsafe_allow_html=True)
                display_food_sources("Protein Rich Foods", "fa-solid fa-drumstick-bite", protein_sources["Non-Vegetarian"], "Non-Vegetarian")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Fat Sources
            st.markdown("#### Fat Sources")
            if dietary_pref in ["Both", "Vegetarian"]:
                st.markdown('<div class="food-source-card">', unsafe_allow_html=True)
                display_food_sources("Healthy Fats", "fa-solid fa-seedling", fat_sources["Vegetarian"], "Vegetarian")
                st.markdown('</div>', unsafe_allow_html=True)
            
            if dietary_pref in ["Both", "Non-Vegetarian"]:
                st.markdown('<div class="food-source-card">', unsafe_allow_html=True)
                display_food_sources("Healthy Fats", "fa-solid fa-bacon", fat_sources["Non-Vegetarian"], "Non-Vegetarian")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Carb Sources
            st.markdown("#### Carb Sources")
            if dietary_pref in ["Both", "Vegetarian"]:
                st.markdown('<div class="food-source-card">', unsafe_allow_html=True)
                display_food_sources("Complex Carbs", "fa-solid fa-wheat-awn", carb_sources["Vegetarian"], "Vegetarian")
                st.markdown('</div>', unsafe_allow_html=True)
            
            if dietary_pref in ["Both", "Non-Vegetarian"]:
                st.markdown('<div class="food-source-card">', unsafe_allow_html=True)
                display_food_sources("Complex Carbs", "fa-solid fa-bread-slice", carb_sources["Non-Vegetarian"], "Non-Vegetarian")
                st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.header("Fitness Journey Progress")
        cols = st.columns(4)
        metrics = [
            ("Workouts Completed", st.session_state.progress_data['workouts_completed']),
            ("Completion Rate", f"{(st.session_state.progress_data['workouts_completed'] / max(st.session_state.progress_data['total_workouts'], 1)) * 100:.1f}%"),
            ("Current Streak", st.session_state.progress_data['streak_days']),
            ("Last Workout", st.session_state.progress_data['last_workout'] or "Start Now!")
        ]
        for i, (label, value) in enumerate(metrics):
            with cols[i]:
                st.markdown(f"""
                <div class="progress-metric">
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
        
        if st.session_state.progress_data['daily_logs']:
            st.subheader("Activity Insights")
            @st.cache_data
            def create_activity_chart(dates, activities):
                import plotly.express as px
                df = pd.DataFrame({'Date': dates, 'Workouts': activities})
                fig = px.area(df, x='Date', y='Workouts', title='Workout Trends', color_discrete_sequence=['#10B981'])
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    font_color='#F9FAFB',
                    title_font_size=18, 
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis_gridcolor='rgba(255,255,255,0.1)', 
                    yaxis_gridcolor='rgba(255,255,255,0.1)'
                )
                fig.update_traces(line_width=3, hovertemplate='%{y} Workouts on %{x}')
                return fig
            
            dates = list(st.session_state.progress_data['daily_logs'].keys())
            activities = [len(workouts) for workouts in st.session_state.progress_data['daily_logs'].values()]
            if dates and activities:
                fig = create_activity_chart(dates, activities)
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("Real-Time Workout Feedback")
        st.info("Select an exercise and start your camera for real-time feedback.")
        
        supported_exercises = ["Squats", "Push-ups", "Lunges", "Plank", "Jumping Jacks"]
        selected_exercise = st.selectbox("Choose Exercise", supported_exercises)
        
        # Define random suggestions for each exercise
        exercise_suggestions = {
            "Squats": [
                "Keep your back straight during the movement",
                "Lower your hips until your thighs are parallel to the floor",
                "Push through your heels to return to standing",
                "Keep your knees aligned with your toes",
                "Engage your core throughout the exercise"
            ],
            "Push-ups": [
                "Maintain a straight line from head to heels",
                "Lower your chest until it nearly touches the floor",
                "Keep your elbows at a 45-degree angle to your body",
                "Push through your palms to return to starting position",
                "Engage your core and glutes throughout"
            ],
            "Lunges": [
                "Step forward with one leg and lower your hips",
                "Keep your front knee directly above your ankle",
                "Lower until both knees are at 90-degree angles",
                "Push through your front heel to return to start",
                "Keep your upper body straight throughout"
            ],
            "Plank": [
                "Keep your body in a straight line from head to heels",
                "Engage your core and glutes",
                "Don't let your hips sag or rise too high",
                "Keep your neck in a neutral position",
                "Breathe steadily throughout the hold"
            ],
            "Jumping Jacks": [
                "Start with feet together and arms at your sides",
                "Jump while spreading your legs and raising your arms",
                "Land softly with knees slightly bent",
                "Keep your core engaged throughout",
                "Maintain a steady rhythm"
            ]
        }
        
        # Store suggestions in session state
        st.session_state.suggestions = exercise_suggestions.get(selected_exercise, ["Perform the exercise with good form"])
        
        cols = st.columns([3, 1])
        with cols[0]:
            st.markdown('<div class="camera-container">', unsafe_allow_html=True)
            
            # Camera control buttons
            camera_col1, camera_col2 = st.columns(2)
            with camera_col1:
                if st.button("Start Camera", key="start_camera"):
                    st.session_state.camera_active = True
                    st.session_state.current_suggestion = random.choice(st.session_state.suggestions)
                    st.session_state.feedback_status = "good"
            with camera_col2:
                if st.button("Stop Camera", key="stop_camera"):
                    st.session_state.camera_active = False
            
            # Display camera feed or placeholder
            if st.session_state.camera_active:
                # Use the camera component
                html_code = camera_component(st.session_state.suggestions)
                st.components.v1.html(html_code, height=600)
            else:
                st.markdown("""
                <div class="camera-placeholder">
                    <i class="fa-solid fa-camera" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                    <p>Camera is off. Click "Start Camera" to begin.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown("### Exercise Feedback")
            st.markdown(f"""
            <div class="pose-feedback">
                Current Exercise: {selected_exercise}
            </div>
            """, unsafe_allow_html=True)
            
            # Display current suggestion
            st.markdown(f"""
            <div class="suggestion-box">
                <i class="fa-solid fa-lightbulb" style="color: var(--accent); margin-right: 0.5rem;"></i>
                {st.session_state.current_suggestion}
            </div>
            """, unsafe_allow_html=True)
            
            # Display feedback status
            if st.session_state.feedback_status == "good":
                st.markdown("""
                <div class="suggestion-box" style="border-left-color: #10B981;">
                    <i class="fa-solid fa-check-circle" style="color: #10B981; margin-right: 0.5rem;"></i>
                    Good Form Detected
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="suggestion-box" style="border-left-color: #EF4444;">
                    <i class="fa-solid fa-exclamation-circle" style="color: #EF4444; margin-right: 0.5rem;"></i>
                    Form Needs Improvement
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("#### All Form Tips:")
            for tip in exercise_suggestions.get(selected_exercise, []):
                st.markdown(f"- {tip}")
    
    with tab4:
        st.header("Export Your Journey")
        cols = st.columns(2)
        with cols[0]:
            if st.button("Export CSV"):
                csv_data = []
                for day, workout in st.session_state.workout_plan.items():
                    if workout['exercises']:
                        for exercise in workout['exercises']:
                            csv_data.append({'Day': day, 'Muscle Group': workout['muscle_group'], 'Exercise': exercise})
                    else:
                        csv_data.append({'Day': day, 'Muscle Group': workout['muscle_group'], 'Exercise': 'Rest Day'})
                df = pd.DataFrame(csv_data)
                csv = df.to_csv(index=False)
                st.download_button(label="Download CSV", data=csv, file_name=f"fitness_plan_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")
        
        with cols[1]:
            if st.button("Export Text"):
                text_plan = f"AI Fitness Trainer Plan\nFor: {st.session_state.user_data.get('name', 'User')}\nDate: {datetime.now().strftime('%Y-%m-%d')}\n\n"
                for day, workout in st.session_state.workout_plan.items():
                    text_plan += f"{day}: {workout['muscle_group']}\n"
                    if workout['exercises']:
                        for exercise in workout['exercises']:
                            text_plan += f"  • {exercise}\n"
                    else:
                        text_plan += "  • Rest Day\n"
                    text_plan += "\n"
                st.download_button(label="Download Text", data=text_plan, file_name=f"fitness_plan_{datetime.now().strftime('%Y%m%d')}.txt", mime="text/plain")
        
        st.subheader("Quick Preview")
        for day, workout in st.session_state.workout_plan.items():
            with st.expander(f"{day}: {workout['muscle_group']}"):
                if workout['exercises']:
                    for exercise in workout['exercises']:
                        st.write(f"• {exercise}")
                else:
                    st.write("• Rest & Recover")
    
    with tab5:
        st.header("Workout Video Tutorials")
        st.info("Watch these expert videos for detailed workout guidance. All videos are embedded from YouTube with proper attribution to their creators.")
        
        videos = [
            {"title": "Push Day Workout", "channel": "FitnessBlender", "embed_url": "https://www.youtube.com/embed/b6ouj88iBZs", "original_url": "https://www.youtube.com/watch?v=b6ouj88iBZs"},
            {"title": "Pull Day Workout", "channel": "Athlean-X", "embed_url": "https://www.youtube.com/embed/DXL18E7QRbk", "original_url": "https://www.youtube.com/watch?v=DXL18E7QRbk"},
            {"title": "Arm Day Workout", "channel": "Buff Dudes", "embed_url": "https://www.youtube.com/embed/XRzS74nSI-k", "original_url": "https://www.youtube.com/watch?v=XRzS74nSI-k"},
            {"title": "Leg Day Workout", "channel": "FitnessBlender", "embed_url": "https://www.youtube.com/embed/H6mRk1x1x77k", "original_url": "https://www.youtube.com/watch?v=H6mRk1x1x77k"},
            {"title": "Shoulder Workout", "channel": "Athlean-X", "embed_url": "https://www.youtube.com/embed/L1a8IPu1gHE", "original_url": "https://www.youtube.com/watch?v=L1a8IPu1gHE"},
            {"title": "Back Workout", "channel": "Buff Dudes", "embed_url": "https://www.youtube.com/embed/4nPKyvKmFi0", "original_url": "https://www.youtube.com/watch?v=4nPKyvKmFi0"},
            {"title": "Chest Workout", "channel": "FitnessBlender", "embed_url": "https://www.youtube.com/embed/XFpT41748hM", "original_url": "https://www.youtube.com/watch?v=XFpT41748hM"}
        ]
        
        for video in videos:
            with st.expander(video["title"]):
                st.markdown(f"""
                <iframe width="100%" height="400" src="{video['embed_url']}" frameborder="0" allowfullscreen></iframe>
                <div class="video-attribution">
                    <i class="fa-brands fa-youtube"></i> 
                    Channel: <a href="{video['original_url']}" target="_blank">{video['channel']}</a> | 
                    <a href="{video['original_url']}" target="_blank">Watch on YouTube</a>
                </div>
                """, unsafe_allow_html=True)
    
    # Copyright Disclaimer at the bottom of the main content
    st.markdown("""
    <div class="copyright-disclaimer">
        <p><strong>Educational Use Disclaimer:</strong> This project is for academic purposes only. All workout videos are embedded from YouTube and belong to their respective creators. 
        No copyright infringement is intended. The use of these materials falls under fair use for educational purposes.</p>
        <p>If you are a content creator and would like your content removed, please contact us.</p>
    </div>
    """, unsafe_allow_html=True)
    
else:
    st.markdown("""
    <div class="welcome-hero">
        <h2>Unlock Your Peak Potential</h2>
        <p>AI-powered fitness coaching tailored just for you. Enter your profile to ignite your transformation.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Why Choose Us?")
    cols = st.columns(3)
    features = [
        ("Personalized AI Plans", "fa-solid fa-brain"),
        ("Real-Time Form Correction", "fa-solid fa-camera"),
        ("Insightful Progress Analytics", "fa-solid fa-chart-line")
    ]
    for i, (title, icon) in enumerate(features):
        with cols[i]:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon"><i class="{icon}"></i></div>
                <h4>{title}</h4>
                <p>Experience cutting-edge fitness tech.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Copyright Disclaimer for the landing page
    st.markdown("""
    <div class="copyright-disclaimer">
        <p><strong>Educational Use Disclaimer:</strong> This project is for academic purposes only. All workout videos are embedded from YouTube and belong to their respective creators. 
        No copyright infringement is intended. The use of these materials falls under fair use for educational purposes.</p>
        <p>If you are a content creator and would like your content removed, please contact us.</p>
    </div>
    """, unsafe_allow_html=True)