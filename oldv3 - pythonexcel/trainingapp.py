from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.properties import ObjectProperty
from scipy.spatial.distance import euclidean
import numpy as np
from itertools import combinations

# Load the .kv file
Builder.load_file('main.kv')

# Define classes for different tabs and widgets as per main.kv file
class ExerciseListTab(BoxLayout):
    pass

class AutoWorkoutGenerator(BoxLayout):
    
    def update_training_goal(self, instance, value):
        if value == "down":  # Check if the button is pressed
            if instance.id == "strength_button":
                user_training_goal = "Strength"
            elif instance.id == "hypertrophy_button":
                user_training_goal = "Hypertrophy"
            elif instance.id == "fit_button":
                user_training_goal = "Fit"
            
            print(f"User training goal updated to {user_training_goal}")


user_input_dict = {
    'Lats': 30,
    'Chest': 30,
    'Deltoids': 0,
    'Biceps': 20,
    'Triceps': 20,
    'Abs': 0,
    'Forearm': 0,
    'Quads': 0,
    'Hams': 0,
    'Calfs': 0,
    'Glutes': 0,
    'Lumbar': 0,
    'Trapezius': 0
}

user_vector = np.array([v for k, v in user_input_dict.items()])

# Add your own user-defined values for these variables
user_rest_time = 60  # Example value
user_training_goal = 'Strength'  # Example value
total_training_length_minutes = 60  # Example value
desired_num_exercises = 1  # Example value
available_equipment = ['Dumbbell', 'Bar', 'Machine']  # Example value
unavailable_equipment = ['band']  # Example value

# Placeholder for exercise data (originally read from CSV)
exercise_data2_list = [
    {
        'Exercise Name': 'Developpe assis a la machine convergente',
        'Lats': 0,
        'Chest': 0.7,
        'Deltoids': 0.1,
        'Biceps': 0.1,
        'Triceps': 0.2,
        'Abs': 0,
        'Forearm': 0.1,
        'Quads': 0,
        'Hams': 0,
        'Calfs': 0,
        'Glutes': 0,
        'Lumbar': 0,
        'Trapezius': 0,
        'Material 1': 'Machine',
        'Material 2': '',
        'Material 3': '',
        'Est. Time for 10 Reps': 60,
        'Weight for 10 rep': 80,
        'Type': 'warmup',
        'coeff rest time': 1.7
    }
]

# Filter exercises based on equipment
filtered_exercises_list = [exercise for exercise in exercise_data2_list if all(item not in [exercise['Material 1'], exercise['Material 2'], exercise['Material 3']] for item in unavailable_equipment)]

# Create numpy array for filtered exercises
filtered_exercise_vectors = np.array([[exercise[feature] for feature in user_input_dict.keys()] for exercise in filtered_exercises_list])

    def update_training_goal(self, instance, value):
        if value == "down":  # Check if the button is pressed
            if instance.id == "strength_button":
                user_training_goal = "Strength"
            elif instance.id == "hypertrophy_button":
                user_training_goal = "Hypertrophy"
            elif instance.id == "fit_button":
                user_training_goal = "Fit"
            
            print(f"User training goal updated to {user_training_goal}")
                
    # Function to determine recommended reps and weights based on training goal
    def determine_reps_weights_rest(training_goal, base_reps, base_weight, base_rest_time):
        reps_weights_rest = []
        if isinstance(base_weight, str):
            weight = base_weight  # If it's a string (like "Body Weight"), keep it as is
        else:
            weight = round(base_weight)
        
        if training_goal == 'Strength':
            reps = base_reps
            for i in range(30):  # I used 30 here as per your original code
                if isinstance(weight, int):
                    new_weight = round(weight * (1 + 0.25 * i))
                else:
                    new_weight = weight
                reps_weights_rest.append({'reps': reps, 'weight': new_weight, 'rest_time': base_rest_time})
                reps = round(reps * 0.8)  # Decreasing the number of reps by 20%

                
        elif training_goal == 'Hypertrophy':
            if isinstance(weight, int):
                weight = round(weight * 0.6)
            reps = base_reps
            for i in range(30):
                reps_weights_rest.append({'reps': reps, 'weight': weight, 'rest_time': base_rest_time})
                if isinstance(weight, int):
                    weight = round(weight * 0.9)
                reps = round(reps * (1 + 0.17))
                
        elif training_goal == 'Endurance':
            if isinstance(weight, int):
                weight = round(weight * 0.4)
            reps = base_reps
            for i in range(30):
                reps_weights_rest.append({'reps': reps, 'weight': weight, 'rest_time': base_rest_time})
                if isinstance(weight, int):
                    weight = round(weight * 1.1)
                reps = round(reps * (1 - 0.17))
                
        return reps_weights_rest

    # Function to estimate time for one set of a given exercise
    def estimate_time_one_set(exercise_row, num_reps):
        est_time_for_10_reps_str = exercise_row['Est. Time for 10 Reps']
        est_time_for_10_reps_seconds = int(est_time_for_10_reps_str)
        time_for_reps = (est_time_for_10_reps_seconds / 10) * num_reps
        coeff_rest_time = exercise_row['coeff rest time']
        total_rest_time = user_rest_time * coeff_rest_time
        return time_for_reps + total_rest_time, total_rest_time

# Initialize variables for the iterative selection of exercises
selected_exercises = []
remaining_time_budget_seconds = total_training_length_minutes * 60
final_vector = np.zeros(13)
total_ponderation_factor = 0
exercise_plan_output = []

# Iteratively select exercises
while len(selected_exercises) < desired_num_exercises:
    remaining_budget_per_exercise = remaining_time_budget_seconds / (desired_num_exercises - len(selected_exercises))
    
    best_next_distance = float('inf')
    best_next_exercise_idx = None
    best_next_vector = None
    
    for idx, exercise_vector in enumerate(filtered_exercise_vectors):
        if idx in selected_exercises:
            continue  # Skip already selected exercises
        
        exercise_row = filtered_exercises_list[idx]
        num_reps = determine_reps_weights_rest(user_training_goal, exercise_row['coeff rest time'], exercise_row['Weight for 10 rep'], user_rest_time)[0]['reps']
        time_one_set, rest_time_between_sets = estimate_time_one_set(exercise_row, num_reps)
        
        num_sets = int(remaining_budget_per_exercise // time_one_set)
        if num_sets == 0:
            continue  # Skip this exercise if it doesn't fit the remaining time budget
        
        ponderation_factor = num_reps * num_sets
        new_intermediate_vector = (final_vector * total_ponderation_factor + exercise_vector * ponderation_factor) / (total_ponderation_factor + ponderation_factor)
        
        distance = euclidean(new_intermediate_vector, user_vector)
        
        if distance < best_next_distance:
            best_next_distance = distance
            best_next_exercise_idx = idx
            best_next_vector = new_intermediate_vector

    if best_next_exercise_idx is not None:
        exercise_row = filtered_exercises_list[best_next_exercise_idx]
        num_reps = determine_reps_weights_rest(user_training_goal, exercise_row['coeff rest time'], exercise_row['Weight for 10 rep'], user_rest_time)[0]['reps']
        time_one_set, rest_time_between_sets = estimate_time_one_set(exercise_row, num_reps)
        num_sets = int(remaining_budget_per_exercise // time_one_set)
        
        total_time_for_next_exercise = num_sets * time_one_set
        remaining_time_budget_seconds -= total_time_for_next_exercise
        
        ponderation_factor = num_reps * num_sets
        final_vector = best_next_vector
        total_ponderation_factor += ponderation_factor
        
        selected_exercises.append(best_next_exercise_idx)
        
        exercise_plan_output.append({
            'Exercise Name': exercise_row['Exercise Name'],
            'Total Rest Time (s)': total_time_for_next_exercise - time_one_set,
            'RestTimeInSeconds': rest_time_between_sets,
            'Recommended Reps': num_reps,
            'Time for Recommended Reps': time_one_set - (user_rest_time * exercise_row['coeff rest time']),
            'Recommended Sets': num_sets,
            'Time for Exercise (s)': total_time_for_next_exercise,
            'Weight for 10 rep': exercise_row['Weight for 10 rep']
        })

# Generate the final exercise plan based on selected exercises
total_time_seconds = 0
for exercise in exercise_plan_output:
total_time_seconds += exercise['Time for Exercise (s)']

# Calculate the total time in minutes and remaining seconds
total_time_minutes = total_time_seconds // 60
total_time_remainder_seconds = total_time_seconds % 60

# Calculate the percentage of matching user input for muscle focus
matching_percentage = 100 * (1 - euclidean(final_vector / np.sum(final_vector), user_vector / np.sum(user_vector)) / np.sqrt(2))

# Display the updated exercise plan in the requested format
print(f"Training Goal: {user_training_goal}")
print("Best combination of exercises:")
for exercise in exercise_plan_output:
print(f"'Exercise Name': {exercise['Exercise Name']}")
print(f"'Recommended Sets': {exercise['Recommended Sets']}")
reps_weights_rest = determine_reps_weights_rest(user_training_goal, exercise['Recommended Reps'], exercise['Weight for 10 rep'], exercise['RestTimeInSeconds'])
for set_num, rwr in enumerate(reps_weights_rest, 1):
    print(f"set {set_num} (Weight: {rwr['weight']}): {rwr['reps']} reps, Time for Recommended Reps: {exercise['Time for Recommended Reps']}")
    print(f"RestTimeInSeconds: {rwr['rest_time']}")
print(f"Time for Exercise (s)': {exercise['Time for Exercise (s)']}")
print()

print(f"Total time needed: {total_time_minutes} minutes and {total_time_remainder_seconds} seconds")
print(f"Matching percentage: {matching_percentage}%")
print(f"Final vector: {final_vector}")
