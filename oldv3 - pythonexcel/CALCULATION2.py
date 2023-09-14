import pandas as pd
import numpy as np
from itertools import combinations
from scipy.spatial.distance import euclidean

# Load Data
exercise_data2_df = pd.read_excel('exercise_data2.xlsm', sheet_name='Exercise_data2')
user_input_df = pd.read_excel('exercise_data2.xlsm', sheet_name='User_input', header=None)

# Fetch rest time and training goal from user input
user_rest_time = user_input_df.iloc[25, 1]
user_training_goal = user_input_df.iloc[13, 1]

# Correct typo if any
user_training_goal = 'Strength' if user_training_goal == 'Strenght' else user_training_goal

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

# Create User Vector
user_vector = [float(x) for x in user_input_df.iloc[0:13, 1].tolist() if isinstance(x, (int, float, str)) and str(x).replace('.', '', 1).isdigit()]

# Validate User Vector
total_percentage = sum(user_vector)
if total_percentage != 100:
    print("The total percentage must sum to 100")
    exit()

# Create Exercise Vectors
muscle_group_cols = exercise_data2_df.columns[1:14]
exercise_vectors = exercise_data2_df[muscle_group_cols].values * 100

# Find the Best Combination of Exercises
exercise_combinations = list(combinations(range(len(exercise_vectors)), 5))
best_combination = None
best_distance = float('inf')

for combination in exercise_combinations:
    avg_vector = np.mean([exercise_vectors[i] for i in combination], axis=0)
    distance = euclidean(avg_vector, user_vector)
    if distance < best_distance:
        best_distance = distance
        best_combination = combination

# Output the Best Exercises
best_exercises_info = []

for i in best_combination:
    exercise_name = exercise_data2_df.iloc[i]['Exercise Name']
    coeff_rest_time = exercise_data2_df.iloc[i]['coeff rest time']
    total_rest_time = user_rest_time * coeff_rest_time
    recommended_reps = determine_reps(user_training_goal, coeff_rest_time)
    
    best_exercises_info.append({
        'Exercise Name': exercise_name,
        'Total Rest Time (s)': total_rest_time,
        'Recommended Reps': recommended_reps
    })

print("Best combination of exercises:", best_exercises_info)
