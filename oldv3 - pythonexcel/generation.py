import csv
import random

class TrainingGenerator:
    def __init__(self, csv_path):
        self.exercises = []
        self.load_data_from_csv(csv_path)

    def load_data_from_csv(self, csv_path):
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.exercises = [row for row in reader]
        except Exception as e:
            print(f"An error occurred: {e}")

    def filter_exercises(self, materials):
        return [e for e in self.exercises if any(mat in e['Material 1'] for mat in materials)]

    def generate_workout(self, focus, materials, time, num_exercises):
        filtered_exercises = self.filter_exercises(materials)
        
        total_reps = 0
        muscle_reps = {muscle: 0 for muscle in focus.keys()}
        workout = []

        while len(workout) < num_exercises and time > 0:
            chosen_exercise = random.choice(filtered_exercises)
            
            sets = 3
            reps_per_set = 10
            total_sets_reps = sets * reps_per_set
            
            for i in range(1, 6):  # Loop through all muscle groups involved in the exercise
                muscle = chosen_exercise.get(f'Muscle {i}', None)
                muscle_percentage = chosen_exercise.get(f'Muscle {i} %', None)
                
                if muscle and muscle_percentage:
                    muscle_percentage = float(muscle_percentage.strip('%')) / 100
                    muscle_reps[muscle] = muscle_reps.get(muscle, 0) + (total_sets_reps * muscle_percentage)
                    
            total_reps += total_sets_reps
            time -= int(chosen_exercise['Time for 10 Reps'].strip('s')) * sets
            
            workout.append({
                'exercise': chosen_exercise['Exercise Name'],
                'sets': sets,
                'reps': reps_per_set
            })

        # Calculate final percentages
        final_percentages = {muscle: (muscle_reps.get(muscle, 0) / total_reps) * 100 for muscle in focus.keys()}
        
        return workout, final_percentages

# Example usage
csv_path = "C:\\Users\\gbray\\Documents\\fitapp\\exercise_data.csv"
generator = TrainingGenerator(csv_path)
focus = {'Chest': 50, 'Back': 50}
materials = ['Dumbbell', 'Bar']
time = 60
num_exercises = 5

workout, final_percentages = generator.generate_workout(focus, materials, time, num_exercises)

print("Generated Workout:", workout)
print("Final Muscle Focus Percentages:", final_percentages)
