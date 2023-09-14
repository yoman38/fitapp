from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout


class AutoWorkoutGenerator(BoxLayout):

    def collect_user_input(self):
        # Collect and print all the values from the various widgets
        print("Muscle Focuses:")
        print("Chest Focus:", self.ids.chest_slider.value)
        print("Lat Focus:", self.ids.lat_slider.value)
        print("Deltoids Focus:", self.ids.deltoids_slider.value)
        # ... Add the rest of the muscle focuses here

        print("\nWorkout Focus:")
        print("Strength:", self.ids.strength_button.state == "down")
        print("Hypertrophy:", self.ids.hypertrophy_button.state == "down")
        print("Fit:", self.ids.fit_button.state == "down")

        print("\nEquipment:")
        print("Dumbbell:", self.ids.dumbbell_check.active)
        print("Bar:", self.ids.bar_check.active)
        # ... Add the rest of the equipment checkboxes here

        print("\nIntensity Level:", self.ids.intensity_slider.value)

        print("\nTraining Length and Number of Exercises:")
        print("Time:", self.ids.training_time_input.text)
        print("Number of exercises:", self.ids.num_exercises_input.text)

        print("\nWarmup:", "Yes" if self.ids.warmup.state == "down" else "No")

        print("\nCooldown Method:")
        print("Stretching:", self.ids.stretching.state == "down")
        print("Abs:", self.ids.abs.state == "down")

class GeneratedWorkoutTab(BoxLayout):
    pass

class MyApp(MDApp):

    def build(self):
        return Builder.load_file('main.kv')

if __name__ == '__main__':
    MyApp().run()
