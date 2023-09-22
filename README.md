# fitapp

GPT:
### High-Level Overview

1. Vector Initialization: For each exercise, a 13-dimensional vector is created, where each dimension corresponds to a muscle group. The user also selects their preferences, which forms another 13-dimensional vector.

2. Initial Exercise: A random exercise is selected to start with.

3. Iterative Exercise Selection: The app goes through the filtered exercises to pick the next best exercise that will make the workout plan vector closer to the user's input vector.

4. Time Adjustment: Once the exercise is added, the time taken for that exercise is calculated, and the total workout time is updated. The app adjusts the number of sets for each exercise to make sure the total workout time falls within an acceptable range.

### Code Breakdown

#### Vector Initialization

```python
user_input_dict = {muscle: slider.value for muscle, slider in self.muscle_sliders.items()}
user_vector = np.array([v for k, v in user_input_dict.items()])
```

Here, user_vector is initialized based on the slider values chosen by the user for each muscle group.

#### Initial Exercise Selection

```python
initial_exercise_idx = np.random.choice(len(filtered_exercises_list))
initial_exercise = filtered_exercises_list[initial_exercise_idx]
```

An initial exercise is randomly selected from the filtered list of exercises.

#### Iterative Exercise Selection

```python
while len(selected_exercises) < desired_num_exercises:
best_next_distance = float('inf')
best_next_exercise = None

for exercise in filtered_exercises_list:
# ... (distance calculation and comparison)

if distance < best_next_distance:
best_next_distance = distance
best_next_exercise = exercise
```

The algorithm iterates through the list of exercises not yet selected (`filtered_exercises_list`) and calculates the Euclidean distance between a temporary new workout vector and the user's preferred vector. It selects the exercise that minimizes this distance.

#### Time Adjustment

```python
while not (lower_bound <= total_workout_time <= upper_bound):
if total_workout_time > upper_bound:
# Reduce sets for the exercise with the most sets
elif total_workout_time < lower_bound:
# Increase sets for the exercise with the fewest sets
```

Here, the code adjusts the number of sets for each exercise to ensure that the total workout time is within a specific range (`lower_bound` and upper_bound).

### Summary

The core logic aims to create a workout plan where the exercises selected make the workout vector as close as possible to the user's preference vector, while also making sure that the total workout time remains within an acceptable range. 
