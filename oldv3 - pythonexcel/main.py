# Importing the necessary modules from Kivy and KivyMD
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivymd.app import MDApp
from kivymd.uix.tab import MDTabsBase
from random import choice
import csv


# Reading the exercise data from the CSV file into a list of dictionaries
exercise_data = []
with open('exercise_data2.csv', 'r') as f:  # Replace with your actual CSV path
    csv_reader = csv.DictReader(f)
    for row in csv_reader:
        exercise_data.append(row)

# Function to generate random exercises for the workout
def generate_random_workout(n=5):
    """Generates a random workout consisting of 'n' exercises."""
    workout = []
    for _ in range(n):
        workout.append(choice(exercise_data))
    return workout

# Custom class to define the ExerciseListTab
class ExerciseListTab(BoxLayout, MDTabsBase):
    pass

# Custom class to define the AutoWorkoutGenerator
class AutoWorkoutGenerator(BoxLayout, MDTabsBase):
    def generate_workout(self):
        random_workout = generate_random_workout()
        generated_workout_tab = self.parent.parent.parent.parent.ids.generated_workout_tab
        generated_workout_tab.clear_widgets()
        for exercise in random_workout:
            generated_workout_tab.add_widget(Label(text=exercise['Exercise Name']))

# Custom class to define the GeneratedWorkoutTab
class GeneratedWorkoutTab(BoxLayout, MDTabsBase):
    pass

# Main App class
class WorkoutApp(MDApp):
    def build(self):
        # Reading the main.kv file to set up the UI
        Builder.load_file('main.kv')  # Make sure to place updated_main.kv in the same folder

# Running the app
if __name__ == '__main__':
    WorkoutApp().run()

