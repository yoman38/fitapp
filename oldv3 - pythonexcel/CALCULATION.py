import pandas as pd
import numpy as np
from itertools import combinations
from scipy.spatial.distance import euclidean

# Load Data
exercise_data2_df = pd.read_excel('exercise_data2.xlsm', sheet_name='Exercise_data2')
user_input_df = pd.read_excel('exercise_data2.xlsm', sheet_name='User_input', header=None)

# Create User Vector
user_vector = [float(x) for x in user_input_df.iloc[0:13, 1].tolist() if isinstance(x, (int, float, str)) and str(x).replace('.', '', 1).isdigit()]

# Validate User Vector
total_percentage = sum(user_vector)
if total_percentage != 100:
    print("The total percentage must sum to 100")
    exit()

# Create Exercise Vectors
muscle_group_cols = exercise_data2_df.columns[1:14]  # Muscle groups are between columns 1 and 13
exercise_vectors = exercise_data2_df[muscle_group_cols].values * 100  # Multiply by 100 to match the user vector scale

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
best_exercises = [exercise_data2_df.iloc[i]['Exercise Name'] for i in best_combination]
print("Best combination of exercises:", best_exercises)
