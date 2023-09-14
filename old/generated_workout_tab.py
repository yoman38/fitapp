from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.tab import MDTabsBase

class GeneratedWorkoutTab(MDBoxLayout, MDTabsBase):
    '''Generated Workout Tab Class.'''
    title = "Generated Workout"

    def display_workout(self, session_plan):
        self.ids.generated_workout_list.clear_widgets()  # Clear any previous data
        
        for exercise in session_plan['Exercises']:
            item = TwoLineAvatarIconListItem(text=exercise['Exercise Name'], secondary_text=f"Primary: {exercise['Primary Muscle']}")
            self.ids.generated_workout_list.add_widget(item)
        
        # Add rest time info
        item = TwoLineAvatarIconListItem(text="Rest Time", secondary_text=f"{session_plan['Rest Time']} seconds")
        self.ids.generated_workout_list.add_widget(item)