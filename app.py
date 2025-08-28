import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import base64
from io import StringIO, BytesIO
import plotly.express as px
import plotly.graph_objects as go
import cv2
import mediapipe as mp
import av
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import time

# --- WORKOUT_DATA.PY & RECOMMENDER CLASS (Merged) ---
# Assuming these files are working and structured correctly,
# we'll keep their imports as is.
# If these files are not in the same directory, you'll need to
# place them there or adjust the import paths.
from workout_data import WorkoutRecommender, EXERCISE_DATABASE
from utils import calculate_bmi, get_bmi_category, export_workout_plan_pdf

# --- POSE DETECTION INTERFACE (Merged) ---
# This is the corrected and integrated PoseDetectionInterface.
# It uses the VideoTransformerBase from streamlit-webrtc.

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

class PoseDetectionInterface(VideoTransformerBase):
    """
    Analyzes live video frames for exercise form using MediaPipe.
    """
    def __init__(self, exercise: str):
        self.exercise = exercise
        self.pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.rep_count = 0
        self.correct_reps = 0
        self.stage = "start"
        self.feedback = "Ready to start."
        self.last_feedback_time = 0
        self.last_rep_time = time.time()
        self.feedback_history = []
        
    def calculate_angle(self, a, b, c):
        """Calculates the angle between three points in degrees."""
        a = np.array([a.x, a.y])
        b = np.array([b.x, b.y])
        c = np.array([c.x, c.y])
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(np.degrees(radians))
        
        return 360 - angle if angle > 180.0 else angle
    
    def log_feedback(self, message, is_correct=False):
        """Logs feedback message with a timestamp and handles rate-limiting."""
        current_time = time.time()
        if current_time - self.last_feedback_time > 1.5:
            self.feedback = message
            self.feedback_history.append({'time': time.strftime("%H:%M:%S"), 'message': message, 'is_correct': is_correct})
            self.last_feedback_time = current_time

    def analyze_squat(self, landmarks):
        """Analyzes squat form and counts repetitions."""
        try:
            l_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
            l_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
            l_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
            
            knee_angle = self.calculate_angle(l_hip, l_knee, l_ankle)
            
            if knee_angle > 160 and self.stage == "down":
                self.rep_count += 1
                self.correct_reps += 1
                self.log_feedback("Rep complete! Perfect Squat!", is_correct=True)
                self.stage = "up"
            
            if knee_angle < 90 and self.stage == "up":
                self.stage = "down"
                self.log_feedback("Go deeper!")
            
            l_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            l_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
            l_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
            torso_angle = self.calculate_angle(l_shoulder, l_hip, l_knee)
            if torso_angle < 60 and self.stage == 'down':
                self.log_feedback("Don't lean forward! Keep your chest up.")
                self.correct_reps = max(0, self.correct_reps - 1)
        except:
            self.log_feedback("Position yourself in camera view.")

    def analyze_pushup(self, landmarks):
        """Analyzes push-up form and counts repetitions."""
        try:
            l_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            l_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
            l_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
            
            elbow_angle = self.calculate_angle(l_shoulder, l_elbow, l_wrist)
            
            if elbow_angle > 160 and self.stage == "down":
                self.rep_count += 1
                self.correct_reps += 1
                self.log_feedback("Rep complete!", is_correct=True)
                self.stage = "up"
                
            if elbow_angle < 90 and self.stage == "up":
                self.stage = "down"
                self.log_feedback("Go lower!")
            
            l_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
            l_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
            body_angle = self.calculate_angle(l_shoulder, l_hip, l_ankle)
            if abs(body_angle - 180) > 15:
                self.log_feedback("Keep your body straight!")
                self.correct_reps = max(0, self.correct_reps - 1)
        except:
            self.log_feedback("Position yourself in camera view.")

    def transform(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.pose.process(img_rgb)
        
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            if self.exercise == "Squats":
                self.analyze_squat(results.pose_landmarks.landmark)
            elif self.exercise == "Push-ups":
                self.analyze_pushup(results.pose_landmarks.landmark)
            else:
                self.log_feedback("This exercise is not yet supported for live analysis.")

        cv2.putText(img, f"Reps: {self.rep_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(img, f"Correct: {self.correct_reps}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(img, f"Feedback: {self.feedback}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- MAIN APP.PY SCRIPT (Original content with modifications) ---

# Page configuration
st.set_page_config(
    page_title="AI Fitness Trainer",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for professional UI with animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Animated gradient background */
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 4s ease-in-out infinite;
        margin-bottom: 2rem;
        text-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Enhanced BMI card with animations */
    .bmi-card {
        background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
        padding: 2rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        text-align: center;
        box-shadow: 0 10px 30px rgba(255, 107, 107, 0.3);
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .bmi-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(45deg);
        animation: shimmer 3s linear infinite;
    }
    
    .bmi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(255, 107, 107, 0.4);
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .bmi-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        z-index: 1;
        position: relative;
    }
    
    .bmi-category {
        font-size: 1.3rem;
        color: white;
        margin-top: 0.5rem;
        font-weight: 500;
        z-index: 1;
        position: relative;
    }
    
    /* Enhanced workout cards */
    .workout-card {
        background: linear-gradient(145deg, #2d3748, #1a202c);
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        border-left: 5px solid #ff6b6b;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        animation: slideInLeft 0.6s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .workout-card::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 100px;
        height: 100px;
        background: radial-gradient(circle, rgba(255,107,107,0.1), transparent);
        border-radius: 50%;
    }
    
    .workout-card:hover {
        transform: translateX(10px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.4);
        border-left-color: #4ecdc4;
    }
    
    .day-header {
        font-size: 1.6rem;
        font-weight: 600;
        color: #ff6b6b;
        margin-bottom: 0.8rem;
        animation: pulse 2s ease-in-out infinite;
    }
    
    .muscle-group {
        font-size: 1.2rem;
        color: #4ecdc4;
        margin-bottom: 0.8rem;
        font-weight: 500;
    }
    
    .exercise-list {
        color: #e2e8f0;
        line-height: 1.8;
        font-weight: 400;
    }
    
    /* Enhanced pose feedback */
    .pose-feedback {
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        animation: bounceIn 0.5s ease-out;
    }
    
    .correct-pose {
        background: linear-gradient(135deg, #48bb78, #38a169);
        color: white;
        box-shadow: 0 4px 15px rgba(72, 187, 120, 0.4);
    }
    
    .incorrect-pose {
        background: linear-gradient(135deg, #f56565, #e53e3e);
        color: white;
        box-shadow: 0 4px 15px rgba(245, 101, 101, 0.4);
    }
    
    /* Enhanced metrics */
    .progress-metric {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(145deg, #2d3748, #1a202c);
        border-radius: 15px;
        margin: 0.5rem;
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .progress-metric:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(45deg, #4ecdc4, #45b7d1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-label {
        font-size: 0.95rem;
        color: #a0aec0;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* Button enhancements */
    .stButton > button {
        background: linear-gradient(145deg, #ff6b6b, #e55353);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(145deg, #e55353, #d44848);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
    }
    
    /* Camera interface */
    .camera-container {
        background: linear-gradient(145deg, #1f2937, #111827);
        border: 3px solid #4ecdc4;
        border-radius: 20px;
        padding: 1rem;
        box-shadow: 0 10px 30px rgba(78, 205, 196, 0.2);
        animation: cameraGlow 2s ease-in-out infinite alternate;
    }
    
    @keyframes cameraGlow {
        0% { box-shadow: 0 10px 30px rgba(78, 205, 196, 0.2); }
        100% { box-shadow: 0 10px 30px rgba(78, 205, 196, 0.4); }
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes bounceIn {
        0% {
            opacity: 0;
            transform: scale(0.3);
        }
        50% {
            opacity: 1;
            transform: scale(1.05);
        }
        70% {
            transform: scale(0.9);
        }
        100% {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes pulse {
        0% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
        100% {
            opacity: 1;
        }
    }
    
    /* Loading spinner for pose detection */
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #4ecdc4;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #2d3748;
        border-radius: 10px 10px 0 0;
        color: #a0aec0;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(145deg, #ff6b6b, #e55353);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
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

# Main header
st.markdown('<h1 class="main-header">🤖 AI Fitness Trainer</h1>', unsafe_allow_html=True)

# Sidebar for user input
with st.sidebar:
    st.header("👤 User Profile")
    
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
        
        submit_profile = st.form_submit_button("Generate Workout Plan", type="primary")
    
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
            recommender = WorkoutRecommender()
            workout_plan = recommender.generate_workout_plan(
                fitness_level=fitness_level,
                goal=goal,
                bmi=bmi,
                bmi_category=bmi_category
            )
            st.session_state.workout_plan = workout_plan
            st.session_state.progress_data['total_workouts'] = sum(len(day['exercises']) for day in workout_plan.values() if day['exercises'])

# Main content area
if st.session_state.workout_plan:
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Weekly Plan", "📊 Progress", "🎥 Pose Detection", "📁 Export"])
    
    with tab1:
        st.header("Your Personalized 7-Day Workout Plan")
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        col1, col2 = st.columns(2)
        
        for i, day in enumerate(days):
            with col1 if i % 2 == 0 else col2:
                workout_data = st.session_state.workout_plan[day]
                
                if workout_data['muscle_group'] == 'Rest':
                    st.markdown(f"""
                    <div class="workout-card">
                        <div class="day-header">{day}</div>
                        <div class="muscle-group">🛌 Rest Day</div>
                        <div class="exercise-list">Recovery and relaxation</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    exercises_text = "<br>".join([f"• {exercise}" for exercise in workout_data['exercises']])
                    st.markdown(f"""
                    <div class="workout-card">
                        <div class="day-header">{day}</div>
                        <div class="muscle-group">🎯 {workout_data['muscle_group']}</div>
                        <div class="exercise-list">{exercises_text}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Mark {day} as Complete", key=f"complete_{day}"):
                        today = datetime.now().strftime("%Y-%m-%d")
                        if today not in st.session_state.progress_data['daily_logs']:
                            st.session_state.progress_data['daily_logs'][today] = []
                        
                        if day not in st.session_state.progress_data['daily_logs'][today]:
                            st.session_state.progress_data['daily_logs'][today].append(day)
                            st.session_state.progress_data['workouts_completed'] += 1
                            st.session_state.progress_data['last_workout'] = today
                            
                            if st.session_state.progress_data['last_workout']:
                                st.session_state.progress_data['streak_days'] += 1
                            
                            st.success(f"Great job completing {day}'s workout! 💪")
                            st.rerun()
    
    with tab2:
        st.header("📊 Your Fitness Progress")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="progress-metric">
                <div class="metric-value">{st.session_state.progress_data['workouts_completed']}</div>
                <div class="metric-label">Workouts Completed</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            completion_rate = (st.session_state.progress_data['workouts_completed'] / 
                               max(st.session_state.progress_data['total_workouts'], 1)) * 100
            st.markdown(f"""
            <div class="progress-metric">
                <div class="metric-value">{completion_rate:.1f}%</div>
                <div class="metric-label">Completion Rate</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="progress-metric">
                <div class="metric-value">{st.session_state.progress_data['streak_days']}</div>
                <div class="metric-label">Current Streak</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            last_workout = st.session_state.progress_data['last_workout'] or "Never"
            st.markdown(f"""
            <div class="progress-metric">
                <div class="metric-value" style="font-size: 1rem;">{last_workout}</div>
                <div class="metric-label">Last Workout</div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.session_state.progress_data['daily_logs']:
            st.subheader("Weekly Activity")
            
            dates = list(st.session_state.progress_data['daily_logs'].keys())
            activities = [len(workouts) for workouts in st.session_state.progress_data['daily_logs'].values()]
            
            if dates and activities:
                df = pd.DataFrame({
                    'Date': dates,
                    'Workouts': activities
                })
                
                fig = px.bar(df, x='Date', y='Workouts', 
                             title='Daily Workout Activity',
                             color='Workouts',
                             color_continuous_scale='Viridis')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("🎥 Pose Detection")
        st.info("Select an exercise and allow camera access to begin real-time form analysis.")
        
        webrtc_ctx_key = "pose_detection_session"
        
        supported_exercises = ["Squats", "Push-ups"]
        selected_pose_exercise = st.selectbox("Select Exercise for Pose Analysis", supported_exercises)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="camera-container" style="width:100%; height:400px; text-align:center;">', unsafe_allow_html=True)
            webrtc_ctx = webrtc_streamer(
                key=webrtc_ctx_key,
                video_transformer_factory=lambda: PoseDetectionInterface(selected_pose_exercise),
                media_stream_constraints={"video": True, "audio": False},
                async_processing=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 📊 Live Metrics")
            if webrtc_ctx.state.playing and webrtc_ctx.video_transformer:
                try:
                    reps_display = webrtc_ctx.video_transformer.rep_count
                    correct_reps_display = webrtc_ctx.video_transformer.correct_reps
                    feedback_display = webrtc_ctx.video_transformer.feedback
                    
                    st.metric(label="Total Reps", value=reps_display)
                    st.metric(label="Correct Reps", value=correct_reps_display)
                    
                    if "Perfect" in feedback_display:
                        st.success(feedback_display)
                    elif "Position" in feedback_display:
                        st.info(feedback_display)
                    else:
                        st.warning(feedback_display)
                    
                    st.markdown("---")
                    st.markdown("### 📝 Feedback Log")
                    
                    for log in reversed(webrtc_ctx.video_transformer.feedback_history):
                        if log['is_correct']:
                            st.success(f"✅ {log['time']}: {log['message']}")
                        else:
                            st.warning(f"⚠️ {log['time']}: {log['message']}")
                except Exception:
                    st.info("Loading pose detection module...")
            else:
                st.info("Click 'Start' on the camera feed to begin analysis.")
    
    with tab4:
        st.header("📁 Export Your Workout Plan")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Export as CSV", type="primary"):
                csv_data = []
                for day, workout in st.session_state.workout_plan.items():
                    if workout['exercises']:
                        for exercise in workout['exercises']:
                            csv_data.append({'Day': day, 'Muscle Group': workout['muscle_group'], 'Exercise': exercise})
                    else:
                        csv_data.append({'Day': day, 'Muscle Group': workout['muscle_group'], 'Exercise': 'Rest Day'})
                
                df = pd.DataFrame(csv_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"workout_plan_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📋 Export as Text", type="secondary"):
                text_plan = f"🤖 AI Fitness Trainer - Workout Plan\n"
                text_plan += f"Generated for: {st.session_state.user_data.get('name', 'User')}\n"
                text_plan += f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
                
                for day, workout in st.session_state.workout_plan.items():
                    text_plan += f"{day}: {workout['muscle_group']}\n"
                    if workout['exercises']:
                        for exercise in workout['exercises']:
                            text_plan += f"  • {exercise}\n"
                    else:
                        text_plan += "  • Rest Day\n"
                    text_plan += "\n"
                
                st.download_button(
                    label="Download Text",
                    data=text_plan,
                    file_name=f"workout_plan_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
        
        st.subheader("Preview")
        for day, workout in st.session_state.workout_plan.items():
            with st.expander(f"{day}: {workout['muscle_group']}"):
                if workout['exercises']:
                    for exercise in workout['exercises']:
                        st.write(f"• {exercise}")
                else:
                    st.write("• Rest Day")

else:
    st.markdown("""
    ## Welcome to Your Personal AI Fitness Trainer! 💪
    
    Get started by filling out your profile in the sidebar to receive a personalized workout plan.
    
    ### Features:
    - 🎯 **Personalized Workout Plans** - Based on your fitness level, goals, and BMI
    - 📊 **Progress Tracking** - Monitor your workout completion and streaks
    - 🎥 **Pose Detection** - Get feedback on your exercise form
    - 📁 **Export Options** - Save your workout plans in various formats
    
    ### How it works:
    1. **Enter your details** in the sidebar (height, weight, fitness level, etc.)
    2. **Get your BMI** calculated automatically
    3. **Receive a personalized 7-day workout plan** based on ML recommendations
    4. **Track your progress** and maintain workout streaks
    5. **Use pose detection** to improve your exercise form
    
    Fill out the form on the left to get started! 👈
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.image("https://pixabay.com/get/g47f9e4a9fad24506f296c0879b67b5d4c3c521bd629c21071ca9e180cdf7cc8b0550bffd815706b9336ac90e1ea907384525e862ec0a49e461683ab2f2297081_1280.jpg", 
                 caption="Strength Training")
    
    with col2:
        st.image("https://pixabay.com/get/g71778dac7e9b84e23b12354592fcd7afec6f88c9aea450c69ece545cd04436f1b5e6a1b35ee30a5387217b24a40f6801f5e7780e90013dbe108048109907fdcf_1280.jpg", 
                 caption="Cardio Workouts")
    
    with col3:
        st.image("https://pixabay.com/get/gb168417f59bf862ef2e12e34eed6fbc16ddf775664adb4628e0a9ab3e947ea1122764dd50472faf603ea67d8ddd1b6d706ab565fa4f0362d0278dc0c86b6f7ea_1280.jpg",  
                 caption="Flexibility Training")