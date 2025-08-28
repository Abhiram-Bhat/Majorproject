import random
from typing import Dict, List, Any

# Comprehensive exercise database organized by muscle groups
EXERCISE_DATABASE = {
    'Chest': [
        'Bench Press', 'Incline Dumbbell Press', 'Decline Bench Press', 'Pec Fly',
        'Push-ups', 'Cable Chest Press', 'Incline Barbell Press', 'Chest Dips',
        'Dumbbell Pullover', 'Cable Crossover', 'Incline Fly', 'Decline Fly'
    ],
    'Shoulders': [
        'Military Press', 'Lateral Raises', 'Upright Rows', 'Arnold Press',
        'Front Raises', 'Rear Delt Fly', 'Overhead Press', 'Dumbbell Shrugs',
        'Pike Push-ups', 'Cable Lateral Raises', 'Handstand Push-ups', 'Face Pulls'
    ],
    'Arms': [
        'Barbell Curls', 'Tricep Dips', 'Skull Crushers', 'Hammer Curls',
        'Rope Pushdowns', 'Preacher Curls', 'Overhead Tricep Extension',
        'Cable Curls', '21s Bicep Curls', 'Diamond Push-ups', 'Concentration Curls',
        'Close-Grip Bench Press'
    ],
    'Back': [
        'Deadlifts', 'Barbell Rows', 'Lat Pulldowns', 'Pull-ups',
        'Seated Cable Rows', 'T-Bar Rows', 'Single-Arm Dumbbell Rows',
        'Wide-Grip Pull-ups', 'Reverse Fly', 'Hyperextensions', 'Cable Rows',
        'Inverted Rows'
    ],
    'Legs': [
        'Squats', 'Romanian Deadlifts', 'Lunges', 'Leg Press',
        'Calf Raises', 'Leg Curls', 'Leg Extensions', 'Bulgarian Split Squats',
        'Walking Lunges', 'Goblet Squats', 'Sumo Squats', 'Step-ups',
        'Wall Sits', 'Jump Squats'
    ],
    'Core': [
        'Plank', 'Crunches', 'Russian Twists', 'Mountain Climbers',
        'Bicycle Crunches', 'Dead Bug', 'Leg Raises', 'Side Plank',
        'Ab Wheel Rollouts', 'Hanging Knee Raises', 'V-ups', 'Flutter Kicks'
    ],
    'Cardio': [
        'Burpees', 'High Knees', 'Jumping Jacks', 'Jump Rope',
        'Sprint Intervals', 'Box Jumps', 'Battle Ropes', 'Rowing Machine',
        'Stationary Bike', 'Elliptical', 'Stair Climber', 'Treadmill Running'
    ]
}

class WorkoutRecommender:
    """Rule-based ML workout recommender using decision tree logic"""
    
    def __init__(self):
        self.fitness_levels = {
            'Beginner': {'exercises_per_day': 4, 'rest_days': 2},
            'Intermediate': {'exercises_per_day': 5, 'rest_days': 2},
            'Advanced': {'exercises_per_day': 6, 'rest_days': 1}
        }
        
        self.goal_priorities = {
            'Muscle Building': {
                'primary_focus': ['Chest', 'Back', 'Legs', 'Shoulders', 'Arms'],
                'workout_style': 'hypertrophy'
            },
            'Fat Loss': {
                'primary_focus': ['Cardio', 'Legs', 'Core', 'Chest', 'Back'],
                'workout_style': 'circuit'
            },
            'Strength Training': {
                'primary_focus': ['Back', 'Chest', 'Legs', 'Shoulders', 'Arms'],
                'workout_style': 'strength'
            }
        }
    
    def generate_workout_plan(self, fitness_level: str, goal: str, bmi: float, bmi_category: str) -> Dict[str, Any]:
        """Generate a 7-day workout plan based on user parameters"""
        
        level_config = self.fitness_levels[fitness_level]
        goal_config = self.goal_priorities[goal]
        exercises_per_day = level_config['exercises_per_day']
        rest_days_count = level_config['rest_days']
        
        # Base workout split based on fitness level and goal
        if fitness_level == 'Beginner':
            base_split = self._get_beginner_split(goal_config['primary_focus'])
        elif fitness_level == 'Intermediate':
            base_split = self._get_intermediate_split(goal_config['primary_focus'])
        else:  # Advanced
            base_split = self._get_advanced_split(goal_config['primary_focus'])
        
        # Adjust for BMI if needed
        if bmi_category in ['Overweight', 'Obese'] and goal != 'Fat Loss':
            # Add more cardio for higher BMI individuals
            base_split = self._add_cardio_emphasis(base_split)
        
        # Generate specific exercises for each day
        workout_plan = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for i, day in enumerate(days):
            muscle_group = base_split[i]
            
            if muscle_group == 'Rest':
                workout_plan[day] = {
                    'muscle_group': 'Rest',
                    'exercises': [],
                    'notes': 'Recovery day - light stretching or walking recommended'
                }
            else:
                exercises = self._select_exercises(muscle_group, exercises_per_day, goal_config['workout_style'])
                workout_plan[day] = {
                    'muscle_group': muscle_group,
                    'exercises': exercises,
                    'notes': f'Focus on {muscle_group.lower()} development'
                }
        
        return workout_plan
    
    def _get_beginner_split(self, focus_areas: List[str]) -> List[str]:
        """Generate beginner-friendly workout split"""
        return [
            'Chest',      # Monday
            'Back',       # Tuesday  
            'Rest',       # Wednesday
            'Legs',       # Thursday
            'Arms',       # Friday
            'Rest',       # Saturday
            'Core'        # Sunday
        ]
    
    def _get_intermediate_split(self, focus_areas: List[str]) -> List[str]:
        """Generate intermediate workout split"""
        return [
            'Chest',      # Monday
            'Back',       # Tuesday
            'Legs',       # Wednesday
            'Shoulders',  # Thursday
            'Arms',       # Friday
            'Core',       # Saturday
            'Rest'        # Sunday
        ]
    
    def _get_advanced_split(self, focus_areas: List[str]) -> List[str]:
        """Generate advanced workout split"""
        return [
            'Chest',      # Monday
            'Shoulders',  # Tuesday
            'Arms',       # Wednesday
            'Back',       # Thursday
            'Arms',       # Friday (Arms + Shoulders focus)
            'Legs',       # Saturday
            'Rest'        # Sunday
        ]
    
    def _add_cardio_emphasis(self, split: List[str]) -> List[str]:
        """Add cardio emphasis for weight loss"""
        # Replace one rest day with cardio for higher BMI individuals
        modified_split = split.copy()
        for i, day in enumerate(modified_split):
            if day == 'Rest' and i > 0:  # Keep at least one rest day
                modified_split[i] = 'Cardio'
                break
        return modified_split
    
    def _select_exercises(self, muscle_group: str, count: int, workout_style: str) -> List[str]:
        """Select specific exercises for a muscle group"""
        available_exercises = EXERCISE_DATABASE.get(muscle_group, [])
        
        if not available_exercises:
            return []
        
        # Ensure we don't exceed available exercises
        count = min(count, len(available_exercises))
        
        # Select exercises based on workout style
        if workout_style == 'hypertrophy':
            # Focus on compound and isolation exercises
            selected = self._prioritize_compound_exercises(available_exercises, count)
        elif workout_style == 'circuit':
            # Mix of compound exercises and higher intensity
            selected = self._prioritize_circuit_exercises(available_exercises, count)
        else:  # strength
            # Focus on compound movements
            selected = self._prioritize_strength_exercises(available_exercises, count)
        
        return selected
    
    def _prioritize_compound_exercises(self, exercises: List[str], count: int) -> List[str]:
        """Prioritize compound exercises for hypertrophy"""
        compound_keywords = ['Press', 'Pull', 'Row', 'Squat', 'Deadlift', 'Dip']
        
        # Sort exercises by compound movement priority
        compound_exercises = [ex for ex in exercises if any(keyword in ex for keyword in compound_keywords)]
        isolation_exercises = [ex for ex in exercises if ex not in compound_exercises]
        
        # Select mix of compound and isolation
        selected = []
        
        # Start with compound exercises
        for ex in compound_exercises[:max(1, count // 2)]:
            selected.append(ex)
        
        # Fill remaining with isolation
        remaining = count - len(selected)
        for ex in isolation_exercises[:remaining]:
            selected.append(ex)
        
        # If still need more, add remaining compound
        remaining = count - len(selected)
        for ex in compound_exercises[len(selected):]:
            if len(selected) < count:
                selected.append(ex)
        
        return selected[:count]
    
    def _prioritize_circuit_exercises(self, exercises: List[str], count: int) -> List[str]:
        """Select exercises suitable for circuit training"""
        # Prefer bodyweight and dynamic exercises for circuits
        circuit_friendly = ['Push-ups', 'Pull-ups', 'Squats', 'Burpees', 'Mountain Climbers', 
                           'Jump Squats', 'High Knees', 'Plank', 'Jumping Jacks']
        
        # Filter available exercises that are circuit-friendly
        preferred = [ex for ex in exercises if any(friendly in ex for friendly in circuit_friendly)]
        others = [ex for ex in exercises if ex not in preferred]
        
        # Select from preferred first, then others
        selected = preferred[:count]
        if len(selected) < count:
            remaining = count - len(selected)
            selected.extend(others[:remaining])
        
        return selected[:count]
    
    def _prioritize_strength_exercises(self, exercises: List[str], count: int) -> List[str]:
        """Prioritize heavy compound movements for strength"""
        strength_exercises = ['Deadlifts', 'Squats', 'Bench Press', 'Military Press', 
                            'Barbell Rows', 'Pull-ups', 'Overhead Press']
        
        # Prioritize strength movements
        preferred = [ex for ex in exercises if any(strength in ex for strength in strength_exercises)]
        others = [ex for ex in exercises if ex not in preferred]
        
        selected = preferred[:count]
        if len(selected) < count:
            remaining = count - len(selected)
            selected.extend(others[:remaining])
        
        return selected[:count]
