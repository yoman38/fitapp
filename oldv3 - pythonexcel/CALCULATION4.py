import pandas as pd
import numpy as np
from itertools import combinations
from scipy.spatial.distance import euclidean

# Load Data
exercise_data2_df = pd.read_excel('exercise_data2.xlsm', sheet_name='Exercise_data2')
user_input_df = pd.read_excel('exercise_data2.xlsm', sheet_name='User_input', header=None)

# Fetch user inputs
user_rest_time = user_input_df.iloc[25, 1]
user_training_goal = user_input_df.iloc[13, 1]
total_training_length_minutes = user_input_df.iloc[27, 1]
desired_num_exercises = user_input_df.iloc[28, 1]
equipment_df = user_input_df.iloc[14:24, 0:2]
available_equipment = equipment_df[equipment_df[1] == 'x'][0].tolist()
unavailable_equipment = equipment_df[equipment_df[1] != 'x'][0].tolist()

# Filter exercises based on available and unavailable equipment
filtered_exercises_df = exercise_data2_df[~exercise_data2_df[['Material 1', 'Material 2', 'Material 3']].apply(lambda row: row.isin(unavailable_equipment).any(), axis=1)]
filtered_exercise_vectors = filtered_exercises_df.iloc[:, 1:14].values * 100

# Function to determine recommended reps
def determine_reps(training_goal, coeff_rest_time):
    if training_goal == 'Strength':
        base_reps = 7
        scaling_factor = 1 / coeff_rest_time
    elif training_goal == 'Hypertrophy':
        base_reps = 14
        scaling_factor = 1
    elif training_goal == 'Endurance':
        base_reps = 30
        scaling_factor = coeff_rest_time

    num_reps = round(base_reps * scaling_factor)
    num_reps = max(1, min(num_reps, 30))
    return num_reps

# Function to estimate time for one set of a given exercise
def estimate_time_one_set(exercise_row, num_reps, user_rest_time):
    est_time_for_10_reps_str = exercise_row['Est. Time for 10 Reps']
    est_time_for_10_reps_seconds = int(est_time_for_10_reps_str)
    time_for_reps = (est_time_for_10_reps_seconds / 10) * num_reps
    coeff_rest_time = exercise_row['coeff rest time']
    total_rest_time = user_rest_time * coeff_rest_time
    return time_for_reps + total_rest_time

# Initialize variables for the iterative selection of exercises
selected_exercises = []
remaining_time_budget_seconds = total_training_length_minutes * 60
final_vector = np.zeros(13)
total_ponderation_factor = 0

# Iteratively select exercises
while len(selected_exercises) < desired_num_exercises:
    remaining_budget_per_exercise = remaining_time_budget_seconds / (desired_num_exercises - len(selected_exercises))
    
    # Find the best next exercise considering the remaining time budget
    best_next_distance = float('inf')
    best_next_exercise_idx = None
    best_next_vector = None
    
    for idx, exercise_vector in enumerate(filtered_exercise_vectors):
        if idx in selected_exercises:
            continue  # Skip already selected exercises
        
        # Estimate time for one set of this exercise
        exercise_row = filtered_exercises_df.iloc[idx]
        num_reps = determine_reps(user_training_goal, exercise_row['coeff rest time'])
        time_one_set = estimate_time_one_set(exercise_row, num_reps)
        
        # Calculate the number of sets for this exercise
        num_sets = int(remaining_budget_per_exercise // time_one_set)
        if num_sets == 0:
            continue  # Skip this exercise if it doesn't fit the remaining time budget
        
        # Calculate the new intermediate vector
        ponderation_factor = num_reps * num_sets
        new_intermediate_vector = (final_vector * total_ponderation_factor + exercise_vector * ponderation_factor) / (total_ponderation_factor + ponderation_factor)
        
        # Calculate the distance to the user vector
        distance = euclidean(new_intermediate_vector, user_vector)
        
        if distance < best_next_distance:
            best_next_distance = distance
            best_next_exercise_idx = idx
            best_next_vector = new_intermediate_vector

    # Update the selected exercises, remaining time budget, and final vector
    if best_next_exercise_idx is not None:
        exercise_row = filtered_exercises_df.iloc[best_next_exercise_idx]
        num_reps = determine_reps(user_training_goal, exercise_row['coeff rest time'])
        time_one_set = estimate_time_one_set(exercise_row, num_reps)
        num_sets = int(remaining_budget_per_exercise // time_one_set)
        
        # Update remaining time budget
        total_time_for_next_exercise = num_sets * time_one_set
        remaining_time_budget_seconds -= total_time_for_next_exercise
        
        # Update final vector and total ponderation factor
        ponderation_factor = num_reps * num_sets
        final_vector = best_next_vector
        total_ponderation_factor += ponderation_factor
        
        # Add this exercise to the list of selected exercises
        selected_exercises.append(best_next_exercise_idx)

# Generate the final exercise plan based on selected exercises
best_exercises_info = []
total_time_seconds = 0

for idx in selected_exercises:
    exercise_row = filtered_exercises_df.iloc[idx]
    exercise_name = exercise_row['Exercise Name']
    num_reps = determine_reps(user_training_goal, exercise_row['coeff rest time'])
    time_one_set, rest_time_between_sets = estimate_time_one_set(exercise_row, num_reps, user_rest_time)
    num_sets = int(remaining_budget_per_exercise // time_one_set)
    total_time_for_exercise = num_sets * time_one_set
    total_time_seconds += total_time_for_exercise
    
    best_exercises_info.append({
        'Exercise Name': exercise_name,
        'Total Rest Time (s)': total_time_for_exercise - time_one_set,
        'Rest Time Between Sets (s)': rest_time_between_sets,
        'Recommended Reps': num_reps,
        'Time for Recommended Reps': time_one_set - (user_rest_time * exercise_row['coeff rest time']),
        'Recommended Sets': num_sets,
        'Time for Exercise (s)': total_time_for_exercise
    })


# Calculate the total time in minutes and remaining seconds
total_time_minutes = total_time_seconds // 60
total_time_remainder_seconds = total_time_seconds % 60

# Calculate the percentage of matching user input for muscle focus
matching_percentage = 100 * (1 - euclidean(final_vector / np.sum(final_vector), user_vector / np.sum(user_vector)) / np.sqrt(2))

print("Best combination of exercises:", best_exercises_info)
print(f"Total time needed: {total_time_minutes} minutes and {total_time_remainder_seconds} seconds")
print(f"Final vector: {final_vector}, Matching percentage: {matching_percentage}%")
