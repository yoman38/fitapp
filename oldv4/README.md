# Exercise Planner README

This Python script is designed to help you plan your workout by selecting exercises that match your training goal and equipment availability. It uses a set of user input data, such as muscle focus, available equipment, and training goal, to recommend a personalized workout plan.

## Prerequisites

Before using the script, ensure you have the following installed:

- Python 3
- NumPy
- SciPy

You can install NumPy and SciPy using pip:

```bash
pip install numpy scipy
```

## Usage

1. Open the script in a Python environment or an integrated development environment (IDE).

2. Customize the following variables with your own values:

   - `user_input_dict`: This dictionary contains your muscle focus data. Modify the values to reflect your preferences for each muscle group.

   - `user_rest_time`: Set the rest time in seconds between sets.

   - `user_training_goal`: Specify your training goal, which can be 'Strength', 'Hypertrophy', or 'Endurance'.

   - `total_training_length_minutes`: Set the total time you want to spend on your workout in minutes.

   - `desired_num_exercises`: Define how many exercises you want to include in your workout plan.

   - `available_equipment`: List the equipment you have access to.

   - `unavailable_equipment`: List any equipment that you don't have access to.

3. Run the script.

4. The script will generate an exercise plan based on your input and display it in the console. The plan will include exercise names, recommended sets and reps, weights, and rest times.

5. You will also see the total time needed for your workout in minutes and seconds, the matching percentage of your muscle focus preferences, and the final vector representing your workout plan.

## Customization

Feel free to modify the script further to suit your specific needs. You can add more exercise data to the `exercise_data2_list` and adjust the logic in the script to meet your requirements.

## Note

This script provides exercise recommendations based on the input data and may require additional adjustments to align with your personal fitness goals and preferences. Always consult with a fitness professional before starting a new workout routine.

---

Enjoy your personalized workout planning with this Python script! If you have any questions or encounter any issues, please don't hesitate to reach out for assistance.# fitapp
 
