import csv
import random

class TrainingGenerator:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.exercise_data = []
        self.load_exercise_data()

    def load_exercise_data(self):
        with open(self.csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.exercise_data.append(row)

    def filter_by_material_and_goal(self, user_materials, fitness_goal):
        return [exercise for exercise in self.exercise_data if exercise['Material 1'] in user_materials and fitness_goal in exercise['Fitness Goal']]

    def adjust_intensity(self, intensity_level):
        intensity_to_rest = {'very low': 240, 'low': 180, 'medium': 120, 'high': 90, 'very high': 60}
        return intensity_to_rest.get(intensity_level, 120)

    def calculate_weights(self, available_exercises, muscle_focus):
        weights = []
        for exercise in available_exercises:
            weight = 0
            primary_focus = int(exercise['Primary Muscle'].split()[-1].strip('%'))
            secondary_focus = int(exercise['Secondary Muscle'].split()[-1].strip('%')) if exercise['Secondary Muscle'] else 0
            if exercise['Primary Muscle'].split()[0] in muscle_focus:
                weight += muscle_focus[exercise['Primary Muscle'].split()[0]] * primary_focus
            if exercise['Secondary Muscle'].split()[0] in muscle_focus:
                weight += muscle_focus[exercise['Secondary Muscle'].split()[0]] * secondary_focus
            weights.append(weight)
        return weights

    def weighted_random_choice(self, available_exercises, weights):
        total = sum(weights)
        rnd = total * random.random()
        for i, w in enumerate(weights):
            rnd -= w
            if rnd < 0:
                return available_exercises[i]

    def select_exercises(self, available_exercises, muscle_focus, desired_exercise_count):
        weights = self.calculate_weights(available_exercises, muscle_focus)
        selected_exercises = []
        while len(selected_exercises) < desired_exercise_count:
            chosen_exercise = self.weighted_random_choice(available_exercises, weights)
            selected_exercises.append(chosen_exercise)
        return selected_exercises

    def generate_workout(self, preferences):
        user_materials = preferences.get('user_materials', set())
        fitness_goal = preferences.get('fitness_goal', 'fitness')
        intensity_level = preferences.get('intensity_level', 'medium')
        muscle_focus = preferences.get('muscle_focus', {})
        desired_exercise_count = preferences.get('desired_exercise_count', 5)

        rest_time = self.adjust_intensity(intensity_level)
        available_exercises = self.filter_by_material_and_goal(user_materials, fitness_goal)
        selected_exercises = self.select_exercises(available_exercises, muscle_focus, desired_exercise_count)

        session_plan = {
            'Exercises': selected_exercises,
            'Rest Time': rest_time
        }
        return session_plan
