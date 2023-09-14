from scipy.spatial.distance import euclidean
import numpy as np
import pandas as pd
from itertools import combinations

# Fetch user inputs from CSV
user_input_df = pd.read_csv("User_input.csv")
user_input_dict = user_input_df.set_index(user_input_df.columns[0]).to_dict()[user_input_df.columns[1]]
user_vector = np.array([v for k, v in user_input_dict.items()])

# Add your own user-defined values for these variables
user_rest_time = 60  # Example value
user_training_goal = 'Strength'  # Example value
total_training_length_minutes = 60  # Example value
desired_num_exercises = 5  # Example value
available_equipment = ['Dumbbell', 'Bar']  # Example value
unavailable_equipment = ['Machine']  # Example value

# Load exercise data from CSV
exercise_data2_df = pd.read_csv("exercise_data2.csv")

# Filter exercises based on available and unavailable equipment
filtered_exercises_df = exercise_data2_df[exercise_data2_df.apply(lambda row: all(item not in row[['Material 1', 'Material 2', 'Material 3']].values for item in unavailable_equipment), axis=1)]

# Create a numpy array for filtered exercises
filtered_exercise_vectors = filtered_exercises_df.loc[:, 'Lats':'Trapezius'].values * 100

# Function to determine recommended reps and weights based on training goal
def determine_reps_weights_rest(training_goal, base_reps, base_weight, base_rest_time):
    reps_weights_rest = []
    if isinstance(base_weight, str):
        weight = base_weight  # If it's a string (like "Body Weight"), keep it as is
    else:
        weight = round(base_weight)
    
    if training_goal == 'Strength':
        reps = base_reps
        for i in range(3):
            if isinstance(weight, int):
                new_weight = round(weight * (1 + 0.25 * i))
            else:
                new_weight = weight
            reps_weights_rest.append({'reps': reps, 'weight': new_weight, 'rest_time': base_rest_time})
            
    elif training_goal == 'Hypertrophy':
        if isinstance(weight, int):
            weight = round(weight * 0.6)
        reps = base_reps
        for i in range(3):
            reps_weights_rest.append({'reps': reps, 'weight': weight, 'rest_time': base_rest_time})
            if isinstance(weight, int):
                weight = round(weight * 0.9)
            reps = round(reps * (1 + 0.17))
            
    elif training_goal == 'Endurance':
        if isinstance(weight, int):
            weight = round(weight * 0.4)
        reps = base_reps
        for i in range(3):
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
        
        exercise_row = filtered_exercises_df.iloc[idx]
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
        exercise_row = filtered_exercises_df.iloc[best_next_exercise_idx]
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
