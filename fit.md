# AI Fitness Trainer App

## Overview

This is a Streamlit-based AI Fitness Trainer application that provides personalized workout recommendations and exercise guidance. The app features user profiling with BMI calculations, ML-based workout plan generation, and interactive pose detection feedback. Users can input their personal fitness data to receive customized 7-day workout splits tailored to their fitness level and goals.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application with custom CSS styling
- **Layout**: Wide layout with expandable sidebar for navigation
- **Visualization**: Plotly integration for interactive charts and graphs
- **UI Components**: Custom styled cards for BMI display, dark theme implementation
- **Data Export**: PDF generation capability for workout plans

### Application Structure
- **Main Application** (`app.py`): Central Streamlit app handling user interface and workflow orchestration
- **Workout Engine** (`workout_data.py`): Rule-based ML recommender using decision tree logic for workout generation
- **Pose Detection** (`pose_detection.py`): Mock pose detection interface providing exercise feedback and form correction
- **Utilities** (`utils.py`): Helper functions for BMI calculations, categorization, and data processing

### Data Management
- **Exercise Database**: Comprehensive in-memory database organized by muscle groups (Chest, Shoulders, Arms, Back, Legs, Core, Cardio)
- **User Profiling**: Collects name, age, gender, height, weight, fitness level, and goals
- **BMI Calculation**: Automatic BMI computation with health category classification
- **Workout Splits**: Dynamic 7-day workout plan generation based on user profile

### ML/Recommendation System
- **Algorithm**: Rule-based decision tree logic for workout recommendations
- **Input Features**: BMI category, fitness level (Beginner/Intermediate/Advanced), and goals (Muscle Building/Fat Loss/Strength Training)
- **Output**: Personalized weekly workout splits with 4-6 exercises per day
- **Exercise Matching**: Intelligent exercise selection based on target muscle groups and user capabilities

### Interactive Features
- **Pose Detection**: Real-time exercise form feedback with key points and common mistake identification
- **Progress Visualization**: Plotly charts for tracking fitness metrics
- **Export Functionality**: PDF generation for workout plans and progress reports

## External Dependencies

### Python Libraries
- **streamlit**: Web application framework for the main interface
- **pandas**: Data manipulation and analysis for workout data management
- **numpy**: Numerical computations for fitness calculations
- **plotly**: Interactive data visualization for charts and graphs
- **datetime**: Date and time handling for workout scheduling

### File Processing
- **json**: Data serialization for user profiles and workout plans
- **base64**: Data encoding for file exports
- **io.StringIO/BytesIO**: In-memory file handling for data processing

### Potential Future Integrations
- **Computer Vision Library**: For actual pose detection implementation (currently mocked)
- **PDF Generation Library**: For workout plan exports
- **Database System**: For persistent user data storage (currently in-memory)
- **Authentication Service**: For user account management