import math
from typing import Dict, Any
import streamlit as st
from datetime import datetime

def calculate_bmi(weight: float, height: float) -> float:
    """
    Calculate BMI from weight (kg) and height (cm)
    
    Args:
        weight: Weight in kilograms
        height: Height in centimeters
    
    Returns:
        BMI value rounded to 1 decimal place
    """
    height_m = height / 100  # Convert cm to meters
    bmi = weight / (height_m ** 2)
    return round(bmi, 1)

def get_bmi_category(bmi: float) -> str:
    """
    Categorize BMI value into health categories
    
    Args:
        bmi: BMI value
    
    Returns:
        BMI category string
    """
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def get_bmi_color(bmi_category: str) -> str:
    """
    Get color code for BMI category
    
    Args:
        bmi_category: BMI category string
    
    Returns:
        Hex color code
    """
    colors = {
        "Underweight": "#74c0fc",
        "Normal": "#51cf66",
        "Overweight": "#ffd43b",
        "Obese": "#ff6b6b"
    }
    return colors.get(bmi_category, "#ffffff")

def calculate_calories_burned(exercise: str, duration_minutes: int, weight_kg: float) -> int:
    """
    Estimate calories burned during exercise
    
    Args:
        exercise: Type of exercise
        duration_minutes: Duration in minutes
        weight_kg: Body weight in kilograms
    
    Returns:
        Estimated calories burned
    """
    # METs (Metabolic Equivalent of Task) values for different exercises
    met_values = {
        'Chest': 6.0,      # Weight training, moderate
        'Back': 6.0,
        'Shoulders': 5.5,
        'Arms': 5.5,
        'Legs': 7.0,       # Slightly higher due to larger muscle groups
        'Core': 4.5,
        'Cardio': 8.0,     # High intensity cardio
        'Rest': 0.0
    }
    
    # Default MET value if exercise not found
    met = met_values.get(exercise, 5.5)
    
    # Calories = METs × weight (kg) × time (hours)
    calories = met * weight_kg * (duration_minutes / 60)
    
    return round(calories)

def format_workout_duration(minutes: int) -> str:
    """
    Format workout duration into hours and minutes
    
    Args:
        minutes: Duration in minutes
    
    Returns:
        Formatted duration string
    """
    if minutes < 60:
        return f"{minutes}m"
    else:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes > 0:
            return f"{hours}h {remaining_minutes}m"
        else:
            return f"{hours}h"

def get_motivational_message(completion_rate: float) -> str:
    """
    Get motivational message based on completion rate
    
    Args:
        completion_rate: Completion rate as percentage (0-100)
    
    Returns:
        Motivational message
    """
    if completion_rate >= 90:
        messages = [
            "🔥 You're absolutely crushing it!",
            "💪 Unstoppable! Keep up the amazing work!",
            "🏆 Champion level consistency!",
            "⭐ You're an inspiration to others!"
        ]
    elif completion_rate >= 70:
        messages = [
            "🎯 Great consistency! You're on fire!",
            "💪 Strong dedication showing results!",
            "🚀 You're building an amazing habit!",
            "⚡ Keep up this fantastic momentum!"
        ]
    elif completion_rate >= 50:
        messages = [
            "📈 Good progress! Stay consistent!",
            "💪 You're building strength every day!",
            "🎯 Keep pushing towards your goals!",
            "🌟 Every workout counts - great job!"
        ]
    elif completion_rate >= 25:
        messages = [
            "🌱 Every step forward counts!",
            "💪 Progress takes time - keep going!",
            "🎯 Focus on consistency over perfection!",
            "🚀 You've got this! One day at a time!"
        ]
    else:
        messages = [
            "🌟 Starting is the hardest part - you did it!",
            "💪 Small steps lead to big changes!",
            "🎯 Your journey begins with a single workout!",
            "🌱 Every expert was once a beginner!"
        ]
    
    import random
    return random.choice(messages)

def validate_user_input(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate user input data
    
    Args:
        data: Dictionary containing user input data
    
    Returns:
        Dictionary of validation errors (empty if no errors)
    """
    errors = {}
    
    # Name validation
    if not data.get('name') or len(data['name'].strip()) < 1:
        errors['name'] = "Name is required"
    elif len(data['name']) > 50:
        errors['name'] = "Name must be less than 50 characters"
    
    # Age validation
    age = data.get('age', 0)
    if age < 16 or age > 100:
        errors['age'] = "Age must be between 16 and 100"
    
    # Height validation
    height = data.get('height', 0)
    if height < 120 or height > 250:
        errors['height'] = "Height must be between 120 and 250 cm"
    
    # Weight validation
    weight = data.get('weight', 0)
    if weight < 30 or weight > 300:
        errors['weight'] = "Weight must be between 30 and 300 kg"
    
    return errors

def export_workout_plan_pdf(workout_plan: Dict[str, Any], user_data: Dict[str, Any]) -> str:
    """
    Generate a formatted text version of the workout plan for export
    
    Args:
        workout_plan: Dictionary containing the workout plan
        user_data: Dictionary containing user data
    
    Returns:
        Formatted string ready for export
    """
    export_text = f"""
AI FITNESS TRAINER - WORKOUT PLAN
=================================

Generated for: {user_data.get('name', 'User')}
Date: {datetime.now().strftime('%B %d, %Y')}
BMI: {calculate_bmi(user_data.get('weight', 70), user_data.get('height', 175))}
Fitness Level: {user_data.get('fitness_level', 'Beginner')}
Primary Goal: {user_data.get('goal', 'General Fitness')}

WEEKLY SCHEDULE
===============

"""
    
    for day, workout in workout_plan.items():
        export_text += f"{day.upper()}: {workout['muscle_group']}\n"
        export_text += "-" * (len(day) + len(workout['muscle_group']) + 2) + "\n"
        
        if workout['exercises']:
            for i, exercise in enumerate(workout['exercises'], 1):
                export_text += f"{i}. {exercise}\n"
        else:
            export_text += "Rest Day - Focus on recovery\n"
        
        if workout.get('notes'):
            export_text += f"\nNotes: {workout['notes']}\n"
        
        export_text += "\n"
    
    export_text += """
GENERAL GUIDELINES
==================

- Warm up for 5-10 minutes before each workout
- Cool down and stretch after each session  
- Stay hydrated throughout your workout
- Listen to your body and rest when needed
- Progress gradually by increasing weight or reps
- Maintain proper form over heavy weight
- Get adequate sleep for recovery

For questions or modifications, consult with a fitness professional.

Generated by AI Fitness Trainer
"""
    
    return export_text

def get_exercise_tips(exercise: str) -> Dict[str, Any]:
    """
    Get tips and instructions for specific exercises
    
    Args:
        exercise: Name of the exercise
    
    Returns:
        Dictionary with exercise tips and information
    """
    tips_database = {
        'Push-ups': {
            'setup': 'Start in plank position with hands slightly wider than shoulders',
            'execution': 'Lower body until chest nearly touches floor, then push back up',
            'breathing': 'Inhale on the way down, exhale on the way up',
            'common_mistakes': ['Sagging hips', 'Partial range of motion', 'Flared elbows'],
            'progressions': ['Knee push-ups', 'Incline push-ups', 'Standard', 'Decline', 'One-arm']
        },
        'Squats': {
            'setup': 'Stand with feet shoulder-width apart, toes slightly pointed out',
            'execution': 'Lower hips back and down, keeping chest up and knees aligned',
            'breathing': 'Inhale on the way down, exhale on the way up',
            'common_mistakes': ['Knees caving in', 'Forward lean', 'Shallow depth'],
            'progressions': ['Bodyweight', 'Goblet', 'Barbell back', 'Front squat', 'Overhead']
        },
        'Plank': {
            'setup': 'Start in forearm plank with elbows under shoulders',
            'execution': 'Hold straight line from head to heels, engage core',
            'breathing': 'Breathe normally, don\'t hold your breath',
            'common_mistakes': ['Hips too high', 'Hips sagging', 'Holding breath'],
            'progressions': ['Knee plank', 'Standard', 'Single arm', 'Plank up-downs']
        }
    }
    
    return tips_database.get(exercise, {
        'setup': 'Follow proper exercise form guidelines',
        'execution': 'Perform movement with control and full range of motion',
        'breathing': 'Coordinate breathing with movement',
        'common_mistakes': ['Poor form', 'Too much weight', 'Rushing movement'],
        'progressions': ['Start light and progress gradually']
    })
