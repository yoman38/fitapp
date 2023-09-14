from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
import csv

# Importing the separated classes
from tabs.exercise_list_tab import ExerciseListTab
from tabs.auto_workout_generator_tab import AutoWorkoutGenerator
from tabs.generated_workout_tab import GeneratedWorkoutTab
from utils.training_generator import TrainingGenerator



# Set window size
Window.size = (360, 640)
Window.show_multitouch = True  # set to False to disable red circles on right click


class FitApp(MDApp):
    def build(self):
        self.root = Builder.load_string(KV)
        self.load_exercise_data()
        
        # Initialize TrainingGenerator
        self.training_generator = TrainingGenerator('C:\\Users\\gbray\\Documents\\fitapp\\exercise_data.csv')

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
            with open('C:\\Users\\gbray\\Documents\\fitapp\\exercise_data.csv', 'r', encoding='utf-8') as f:
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