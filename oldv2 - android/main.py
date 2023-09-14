from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

class FitnessApp(MDApp):

    def build(self):
        # Load the main kv file
        Builder.load_file('kv/main.kv')
        
        # Load other kv files
        Builder.load_file('kv/tabs/auto_workout_generator.kv')
        Builder.load_file('kv/tabs/generated_workout.kv')
        Builder.load_file('kv/tabs/exercise_library.kv')

        # Return root widget
        return BoxLayout()
