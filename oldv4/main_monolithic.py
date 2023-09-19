from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.app import App
#from generator import TrainingGenerator
#from generation import TrainingGenerator
import csv
import random


# Set window size
Window.size = (360, 640)
Window.show_multitouch = True  # set to False to disable red circles on right click


class ExerciseListTab(MDBoxLayout, MDTabsBase):
    '''Exercise List Tab Class.'''
    title = "Exercise Library"

class AutoWorkoutGenerator(MDBoxLayout, MDTabsBase):
    '''Auto Workout Generator Tab Class.'''
    title = "Auto Workout Generator"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.total_focus = 0  # Initialize total focus percentage to 0
        self.slider_dict = {}  # To keep track of sliders
        self.num_exercises = 5  # Default value

    def on_enter(self):
        self.initialize_sliders()

    def initialize_sliders(self):
        # Initialize sliders in on_kv_post so that ids are available
        self.slider_dict = {
            "chest_slider": self.ids.chest_slider,
            "deltoids_slider": self.ids.deltoids_slider,
            "biceps_slider": self.ids.biceps_slider,
            "abs_slider": self.ids.abs_slider,
            "forearm_slider": self.ids.forearm_slider,
            "quadriceps_slider": self.ids.quadriceps_slider,
            "calf_slider": self.ids.calf_slider,
            "hamstring_slider": self.ids.hamstring_slider,
            "gluteus_slider": self.ids.gluteus_slider,
            "lombar_slider": self.ids.lombar_slider,
            "triceps_slider": self.ids.triceps_slider,
            "trapezius_slider": self.ids.trapezius_slider,
        }
        for slider in self.slider_dict.values():
            slider.bind(value=self.update_muscle_focus)

    def update_intensity_label(self, label, value):
        label.text = f"Current: {int(value)}"

    def update_muscle_focus(self, instance, value):
        # Calculate the new total focus if the change is accepted
        new_total_focus = self.total_focus - instance.previous_value + value

        # Check if the new total focus is within the allowed range
        if new_total_focus <= 100:
            # Update the total focus and the previous_value of the changed slider
            self.total_focus = new_total_focus
            instance.previous_value = value
        else:
            # Revert the change
            instance.value = instance.previous_value

    def collect_user_input(self):
        try:
            # Make sure all ids are available
            assert all([
                hasattr(self.ids, 'chest_slider'),
                hasattr(self.ids, 'dumbbell_check'),
                hasattr(self.ids, 'bar_check'),
                hasattr(self.ids, 'band_check'),
                hasattr(self.ids, 'bench_check'),
                hasattr(self.ids, 'machine_check'),
                hasattr(self.ids, 'kettlebell_check'),
                hasattr(self.ids, 'disk_check'),
                hasattr(self.ids, 'traction_bar_check'),
                hasattr(self.ids, 'parallell_bars_check'),
                hasattr(self.ids, 'weighted_chain_check'),
                hasattr(self.ids, 'other_check'),
                hasattr(self.ids, 'workout_focus'),
                hasattr(self.ids, 'intensity_slider'),
                hasattr(self.ids, 'training_time_input'),
                hasattr(self.ids, 'num_exercises_input'),
            ])
        except AssertionError:
            print("Some ids are missing.")
            return

        muscle_focus = {}
        for key, slider in self.slider_dict.items():
            muscle_focus[key] = slider.value

        equipment = {
            'Dumbbell': self.ids.dumbbell_check.active,
            'Bar': self.ids.bar_check.active,
            'Band': self.ids.band_check.active,
            'Bench': self.ids.bench_check.active,
            'Machine': self.ids.machine_check.active,
            'Kettlebell': self.ids.kettlebell_check.active,
            'Disk': self.ids.disk_check.active,
            'Traction Bar': self.ids.traction_bar_check.active,
            'Parallel Bars': self.ids.parallel_bars_check.active,
            'Weighted Chain': self.ids.weighted_chain_check.active,
            'Other': self.ids.other_check.active,
        }

        # Collect text input for time and number of exercises
        try:
            self.training_time = int(self.ids.training_time_input.text)
            self.num_exercises = int(self.ids.num_exercises_input.text)
        except ValueError:
            print("Please enter valid numbers for training time and number of exercises.")
            return

        # Collecting toggle button values for workout focus
        workout_focus = None
        if self.ids.strength_button.state == 'down':
            workout_focus = 'Strength'
        elif self.ids.hypertrophy_button.state == 'down':
            workout_focus = 'Hypertrophy'
        elif self.ids.fit_button.state == 'down':
            workout_focus = 'Fit'

        # Collecting intensity level
        intensity_level = self.ids.intensity_slider.value

        # Once you collect all the inputs, you can call the method to generate the workout
        self.generate_workout(muscle_focus, equipment, workout_focus, intensity_level)

    def get_workout_focus(self):
        if self.ids.strength_button.state == 'down':
            return 'Strength'
        elif self.ids.hypertrophy_button.state == 'down':
            return 'Hypertrophy'
        elif self.ids.fit_button.state == 'down':
            return 'Fit'
        else:
            return None  # or some default value

    def generate_workout(self, preferences):
        # Filter and random sample exercises
        filtered_exercises = [
            exercise for exercise in self.exercise_data
            if any(material in preferences['user_materials'] for material in [exercise['Material 1'], exercise['Material 2'], exercise['Material 3']])
        ]
        sampled_exercises = random.sample(
            filtered_exercises, 
            min(len(filtered_exercises), preferences.get('desired_exercise_count', 5))
        )
        
        # Generate session plan with multiple sets for each exercise
        session_plan = {'Exercises': []}
        for exercise in sampled_exercises:
            for set_number in range(1, 4):  # Assuming 3 sets for each exercise
                reps = random.randint(7, 15)  # Number of reps
                est_time_for_10_reps = float(exercise.get('Est Time for 10 Reps', 0))
                z_time = (est_time_for_10_reps / 10) * reps
                session_plan['Exercises'].append({
                    'Exercise Name': exercise['Exercise Name'],
                    'Set': set_number,
                    'Reps': reps,
                    'Time': round(z_time, 2)
                })
        session_plan['Rest Time'] = 90
        return session_plan

class GeneratedWorkoutTab(MDBoxLayout, MDTabsBase):
    '''Generated Workout Tab Class.'''
    title = "Generated Workout"

    def display_workout(self, session_plan):
        self.ids.generated_workout_list.clear_widgets()
        for exercise in session_plan['Exercises']:
            display_text = f"Exercise {exercise['Exercise Name']}, Set {exercise['Set']}: {exercise['Reps']} reps, Time {exercise['Time']} seconds"
            item = TwoLineAvatarIconListItem(text=display_text)
            self.ids.generated_workout_list.add_widget(item)

            rest_item = TwoLineAvatarIconListItem(text=f"Rest 1, Duration: {session_plan['Rest Time']} seconds")
            self.ids.generated_workout_list.add_widget(rest_item)

class TrainingGenerator:
    def __init__(self, filename):
        self.exercise_data = []

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.exercise_data = [row for row in reader]
        except Exception as e:
            print(f"An error occurred while reading the CSV file: {e}")

        def generate_workout(self, preferences):
            # Randomly sample exercises
            sampled_exercises = random.sample(
                self.exercise_data, 
                min(len(self.exercise_data), preferences.get('desired_exercise_count', 5))
            )
            
            # Generate session plan with multiple sets for each exercise
            session_plan = {'Exercises': []}
            for exercise in sampled_exercises:
                for set_number in range(1, 4):  # Assuming 3 sets for each exercise
                    reps = random.randint(7, 15)  # Number of reps
                    est_time_for_10_reps = float(exercise.get('Est Time for 10 Reps', 0))
                    z_time = (est_time_for_10_reps / 10) * reps
                    session_plan['Exercises'].append({
                        'Exercise Name': exercise['Exercise Name'],
                        'Set': set_number,
                        'Reps': reps,
                        'Time': round(z_time, 2)
                    })
            session_plan['Rest Time'] = 90
            return session_plan
    
class FitApp(MDApp):
    def build(self):
        self.root = Builder.load_file('main.kv')        
        self.load_exercise_data()
        
        # Initialize TrainingGenerator
        self.training_generator = TrainingGenerator('exercise_data.csv')

        # Add the AutoWorkoutGenerator as a new tab
        self.auto_workout_tab = AutoWorkoutGenerator()
        self.root.ids.tabs.add_widget(self.auto_workout_tab)

        # Add the GeneratedWorkoutTab as a new tab
        self.generated_workout_tab = GeneratedWorkoutTab()
        self.root.ids.tabs.add_widget(self.generated_workout_tab)

    def load_exercise_data(self):
        # Create a new tab for exercises if it does not exist
        if not hasattr(self, 'exercise_tab'):
            self.exercise_tab = ExerciseListTab()
            self.root.ids.tabs.add_widget(self.exercise_tab)

        # Clear previous data
        self.exercise_tab.ids.exercise_list.clear_widgets()

        try:
            # Read exercise data from CSV file
            with open('C:\\Users\\gbray\\Documents\\fitapp\\exercise_data2.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    print(f"Reading Row: {row}")  # Debug statement
                    primary_muscle = row['Primary Muscle']
                    secondary_muscle = row['Secondary Muscle']
                    muscle_info = f"Primary: {primary_muscle}, Secondary: {secondary_muscle}"
                    item = TwoLineAvatarIconListItem(text=row['Exercise Name'], secondary_text=muscle_info)
                    self.exercise_tab.ids.exercise_list.add_widget(item)
                    print(f"Added Item: {row['Exercise Name']}")  # Debug statement
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    FitApp().run()
