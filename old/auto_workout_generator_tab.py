from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.tab import MDTabsBase

class AutoWorkoutGenerator(MDBoxLayout, MDTabsBase):
    '''Auto Workout Generator Tab Class.'''
    title = "Auto Workout Generator"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.total_focus = 0  # Initialize total focus percentage to 0
        self.slider_dict = {}  # To keep track of sliders

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
        # Collecting slider values
        muscle_focus = {key: slider.value for key, slider in self.slider_dict.items()}
        
        # Collecting checkbox values
        equipment = {
            "Dumbbell": self.ids.dumbbell_check.active,
            "Bar": self.ids.bar_check.active,
            "Band": self.ids.band_check.active,
            "Bench": self.ids.bench_check.active
        }
        
        # Collect text input for time and number of exercises
        try:
            training_time = int(self.ids.training_time_input.text)  # Replace with the actual ID
            num_exercises = int(self.ids.num_exercises_input.text)  # Replace with the actual ID
        except ValueError:
            print("Please enter valid numbers for training time and number of exercises.")
            return
    
        # Collecting toggle button values for workout focus
        workout_focus = self.ids.workout_focus.state  # Replace this with the actual ID
        
        # Collecting intensity level
        intensity_level = self.ids.intensity_slider.value


        # Once you collect all the inputs, you can call the method to generate the workout
        self.generate_workout(muscle_focus, equipment, workout_focus, intensity_level)

    def generate_workout(self, muscle_focus, equipment, workout_focus, intensity_level):
        # Convert the user preferences to the format required by TrainingGenerator
        preferences = {
            'muscle_focus': muscle_focus,
            'user_materials': {k for k, v in equipment.items() if v},
            'fitness_goal': workout_focus,
            'intensity_level': intensity_level,
            'desired_exercise_count': num_exercises,  # num_exercises is collected from user
        }
        
        # Access the TrainingGenerator instance and generate the workout
        session_plan = self.parent.parent.training_generator.generate_workout(preferences)
        
        # Display this in the 'Generated Workout' Tab
        self.parent.parent.generated_workout_tab.display_workout(session_plan)