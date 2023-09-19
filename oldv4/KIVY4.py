from kivy.core.window import Window
from kivy.graphics import Line
from kivy.graphics import Rectangle, Color
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from scipy.spatial.distance import euclidean
import numpy as np

Window.size = (360, 640)

class WorkoutPlannerApp(App):
    def __init__(self, **kwargs):
        super(WorkoutPlannerApp, self).__init__(**kwargs)
        self.workout_plan = []  # Initialize the workout plan list
        
    def build(self):
        self.selected_exercises = []
        self.box = BoxLayout(orientation='vertical')
        # Create a TabbedPanel
        self.tab_panel = TabbedPanel()
        
        # Create the first tab for input fields
        self.input_tab = TabbedPanelItem(text='User Inputs')
        self.box = BoxLayout(orientation='vertical')
        
        # Create TextInputs for muscle groups
        self.muscle_inputs = {}
        for muscle in ['Lats', 'Chest', 'Deltoids', 'Biceps', 'Triceps', 'Abs', 'Forearm', 'Quads', 'Hams', 'Calfs', 'Glutes', 'Lumbar', 'Trapezius']:
            self.muscle_inputs[muscle] = TextInput(hint_text=muscle)
            self.box.add_widget(self.muscle_inputs[muscle])
        
        # Create TextInputs for other numerical inputs
        self.user_rest_time_input = TextInput(hint_text='Rest Time (s)')
        self.total_training_length_input = TextInput(hint_text='Total Training Length (min)')
        self.desired_num_exercises_input = TextInput(hint_text='Desired Number of Exercises')
        self.box.add_widget(self.user_rest_time_input)
        self.box.add_widget(self.total_training_length_input)
        self.box.add_widget(self.desired_num_exercises_input)
        
        # Create Spinner for training goals
        self.training_goal_spinner = Spinner(text='Training Goal', values=('Strength', 'Hypertrophy', 'Endurance'))
        self.box.add_widget(self.training_goal_spinner)
        
        # Create Checkboxes for equipment
        self.equipment_checkboxes = {}
        for equip in ['Dumbbell', 'Bar', 'Machine', 'band']:
            cb = CheckBox()
            self.equipment_checkboxes[equip] = cb
            equip_box = BoxLayout()
            equip_box.add_widget(Label(text=equip))
            equip_box.add_widget(cb)
            self.box.add_widget(equip_box)
       
        # Create a button to collect user input
        self.button = Button(text='Generate Workout Plan')
        self.button.bind(on_press=self.generate_workout_plan)
        self.box.add_widget(self.button)  # Add the button to the box layout
        # Add the input fields to the first tab
        self.input_tab.add_widget(self.box)
        
        # Create the second tab for workout generation
        self.output_tab = TabbedPanelItem(text='Workout Generation')
        self.output_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.output_grid.bind(minimum_height=self.output_grid.setter('height'))

        self.output_scroll = ScrollView(size_hint=(1,1))
        self.output_scroll.add_widget(self.output_grid)

        self.output_tab.add_widget(self.output_scroll)

        
        # Add both tabs to the TabbedPanel
        self.tab_panel.add_widget(self.input_tab)
        self.tab_panel.add_widget(self.output_tab)
        
        return self.tab_panel
    
    def generate_workout_plan(self, instance):
        self.output_grid.clear_widgets()  # Clear previous widgets
        try:
            # Collect user inputs
            user_input_dict = {muscle: float(self.muscle_inputs[muscle].text) for muscle in self.muscle_inputs}
            user_vector = np.array([v for k, v in user_input_dict.items()])
            user_rest_time = float(self.user_rest_time_input.text)
            total_training_length_minutes = float(self.total_training_length_input.text)
            desired_num_exercises = int(self.desired_num_exercises_input.text)
            user_training_goal = self.training_goal_spinner.text
            unavailable_equipment = [equip for equip, cb in self.equipment_checkboxes.items() if not cb.active]
            
            
            # For the sake of this example, exercise_data2_list is your actual list of exercises
            # Note: I have used placeholder data here; replace it with your real exercise data
            exercise_data2_list = [
                {
                    'Exercise Name': 'Sample Exercise',
                    'Lats': 0,
                    'Chest': 0.7,
                    'Deltoids': 0.1,
                    'Biceps': 0.1,
                    'Triceps': 0.2,
                    'Abs': 0,
                    'Forearm': 0.1,
                    'Quads': 0,
                    'Hams': 0,
                    'Calfs': 0,
                    'Glutes': 0,
                    'Lumbar': 0,
                    'Trapezius': 0,
                    'Material 1': 'Dumbbell',
                    'Material 2': '',
                    'Material 3': '',
                    'Est. Time for 10 Reps': 60,
                    'Weight for 10 rep': 80,
                    'Type': 'warmup',
                    'coeff rest time': 1.7
                }
            ]
            
            # Filter exercises based on equipment
            filtered_exercises_list = [exercise for exercise in exercise_data2_list if all(item not in [exercise['Material 1'], exercise['Material 2'], exercise['Material 3']] for item in unavailable_equipment)]
            
            # Function to determine recommended reps and weights based on training goal
            def determine_reps_weights_rest(training_goal, base_reps, base_weight, base_rest_time):
                reps_weights_rest = []
                if isinstance(base_weight, str):
                    weight = base_weight  # If it's a string (like "Body Weight"), keep it as is
                else:
                    weight = round(base_weight)
                
                if training_goal == 'Strength':
                    reps = base_reps
                    for i in range(30):  # I used 30 here as per your original code
                        if isinstance(weight, int):
                            new_weight = round(weight * (1 + 0.25 * i))
                        else:
                            new_weight = weight
                        reps_weights_rest.append({'reps': reps, 'weight': new_weight, 'rest_time': base_rest_time})
                        reps = round(reps * 0.8)  # Decreasing the number of reps by 20%

                        
                elif training_goal == 'Hypertrophy':
                    if isinstance(weight, int):
                        weight = round(weight * 0.6)
                    reps = base_reps
                    for i in range(30):
                        reps_weights_rest.append({'reps': reps, 'weight': weight, 'rest_time': base_rest_time})
                        if isinstance(weight, int):
                            weight = round(weight * 0.9)
                        reps = round(reps * (1 + 0.17))
                        
                elif training_goal == 'Endurance':
                    if isinstance(weight, int):
                        weight = round(weight * 0.4)
                    reps = base_reps
                    for i in range(30):
                        reps_weights_rest.append({'reps': reps, 'weight': weight, 'rest_time': base_rest_time})
                        if isinstance(weight, int):
                            weight = round(weight * 1.1)
                        reps = round(reps * (1 - 0.17))
                        
                return reps_weights_rest

            # Function to estimate time for one set of a given exercise
            def estimate_time_one_set(exercise_row, num_reps):
                est_time_for_10_reps_str = exercise_row['Est. Time for 10 Reps']
                est_time_for_10_reps_seconds = int(est_time_for_10_reps_str)
                time_for_reps = (est_time_for_10_reps_seconds / 10) * num_reps
                coeff_rest_time = exercise_row['coeff rest time']
                total_rest_time = user_rest_time * coeff_rest_time
                return time_for_reps + total_rest_time, total_rest_time

            # Create vectors for filtered exercises based on their attributes
            filtered_exercise_vectors = [np.array([exercise[muscle] for muscle in ['Lats', 'Chest', 'Deltoids', 'Biceps', 'Triceps', 'Abs', 'Forearm', 'Quads', 'Hams', 'Calfs', 'Glutes', 'Lumbar', 'Trapezius']]) for exercise in filtered_exercises_list]

            # Initialize variables for the iterative selection of exercises
            selected_exercises = []
            remaining_time_budget_seconds = total_training_length_minutes * 60
            final_vector = np.zeros(13)
            total_ponderation_factor = 0
            exercise_plan_output = []

            # Iteratively select exercises
            while len(selected_exercises) < desired_num_exercises:
                remaining_budget_per_exercise = remaining_time_budget_seconds / (desired_num_exercises - len(selected_exercises))
                
                best_next_distance = float('inf')
                best_next_exercise_idx = None
                best_next_vector = None
                
                for idx, exercise_vector in enumerate(filtered_exercise_vectors):
                    if idx in selected_exercises:
                        continue  # Skip already selected exercises
                    
                    exercise_row = filtered_exercises_list[idx]
                    num_reps = round(determine_reps_weights_rest(user_training_goal, exercise_row['coeff rest time'], exercise_row['Weight for 10 rep'], user_rest_time)[0]['reps'])
                    time_one_set, rest_time_between_sets = estimate_time_one_set(exercise_row, num_reps)
                    
                    num_sets = int(remaining_budget_per_exercise // time_one_set)
                    if num_sets == 0:
                        continue  # Skip this exercise if it doesn't fit the remaining time budget
                    
                    ponderation_factor = num_reps * num_sets
                    new_intermediate_vector = (final_vector * total_ponderation_factor + exercise_vector * ponderation_factor) / (total_ponderation_factor + ponderation_factor)
                    
                    distance = euclidean(new_intermediate_vector, user_vector)
                    
                    if distance < best_next_distance:
                        best_next_distance = distance
                        best_next_exercise_idx = idx
                        best_next_vector = new_intermediate_vector

                if best_next_exercise_idx is not None:
                    exercise_row = filtered_exercises_list[best_next_exercise_idx]
                    num_reps = round(determine_reps_weights_rest(user_training_goal, exercise_row['coeff rest time'], exercise_row['Weight for 10 rep'], user_rest_time)[0]['reps'])
                    time_one_set, rest_time_between_sets = estimate_time_one_set(exercise_row, num_reps)
                    num_sets = int(remaining_budget_per_exercise // time_one_set)
                    
                    total_time_for_next_exercise = num_sets * time_one_set
                    remaining_time_budget_seconds -= total_time_for_next_exercise
                    
                    ponderation_factor = num_reps * num_sets
                    final_vector = best_next_vector
                    total_ponderation_factor += ponderation_factor
                    
                    selected_exercises.append(best_next_exercise_idx)

                # Initialize variables for displaying the plan
                workout_plan_text = "Generated Workout Plan:\n"

            # Calculating total time and displaying each selected exercise
            total_time_seconds = 0

            self.selected_exercises = []

            for idx in selected_exercises:
                exercise_row = filtered_exercises_list[idx]
                num_reps = determine_reps_weights_rest(user_training_goal, exercise_row['coeff rest time'], exercise_row['Weight for 10 rep'], user_rest_time)[0]['reps']
                time_one_set, rest_time_between_sets = estimate_time_one_set(exercise_row, num_reps)
                num_sets = int(remaining_budget_per_exercise // time_one_set)
                
                for set_number in range(1, num_sets + 1):
                    exercise_box = BoxLayout(size_hint_y=None, height=60)
                    exercise_box.bind(minimum_height=exercise_box.setter('height'))
                    
                    exercise_text = f"{exercise_row['Exercise Name']}, Set: {set_number}/{num_sets}"
                    reps_input = TextInput(text=str(num_reps), size_hint_x=0.2)
                    weight_input = TextInput(text=str(exercise_row['Weight for 10 rep']), size_hint_x=0.2)
                    time_input = TextInput(text=str(time_one_set), size_hint_x=0.2)
                    
                    exercise_box.add_widget(Label(text=exercise_text, size_hint_x=0.6))
                    exercise_box.add_widget(reps_input)
                    exercise_box.add_widget(weight_input)
                    exercise_box.add_widget(time_input)
                    
                    self.output_grid.add_widget(exercise_box)

                    exercise_info = {'name': exercise_row['Exercise Name'],
                    'set': set_number,
                    'total_sets': num_sets,
                    'reps': num_reps,
                    'weight': exercise_row['Weight for 10 rep'],
                    'time': time_one_set,
                    'is_rest': False}
                    self.workout_plan.append(exercise_info)

                    # Adding rest time input between sets
                    if set_number < num_sets:  # No rest after the final set
                        rest_time_input = TextInput(text=str(user_rest_time), hint_text='Rest Time (s)', size_hint_y=None, height=40)
                        self.output_grid.add_widget(rest_time_input)
                        rest_info = {'name': 'Rest',
                                    'set': None,
                                    'total_sets': None,
                                    'reps': None,
                                    'weight': None,
                                    'time': user_rest_time,
                                    'is_rest': True}
                        self.workout_plan.append(rest_info)

                # Adding rest time input between exercises
                rest_time_input_ex = TextInput(text=str(rest_time_between_sets), hint_text='Rest Time (s)', size_hint_y=None, height=40)
                self.output_grid.add_widget(rest_time_input_ex)

                # Switch to the 'Workout Generation' tab to display the results
                self.tab_panel.switch_to(self.output_tab)

            # Calculate Total Time for Workout
            total_time_minutes = total_time_seconds // 60
            total_time_remaining_seconds = total_time_seconds % 60

            # Calculate Matching Percentage
            max_possible_distance = euclidean(np.zeros(13), np.ones(13))
            matching_percentage = ((1 - best_next_distance / max_possible_distance) * 100)*3-200

            # Add Summary Information to output_grid
            summary_grid = GridLayout(cols=1, size_hint_y=None, height=180)
            summary_grid.bind(minimum_height=summary_grid.setter('height'))

            summary_grid.add_widget(Label(text=f"Total Time for Workout: {total_time_minutes} minutes and {total_time_remaining_seconds} seconds",
                                        size_hint_y=None, height=60))
            summary_grid.add_widget(Label(text=f"Matching Percentage: {matching_percentage:.2f}%",
                                        size_hint_y=None, height=60))
            summary_grid.add_widget(Label(text=f"Final Vector: {final_vector}",
                                        size_hint_y=None, height=60))

            self.output_grid.add_widget(summary_grid)
            
        except ValueError:
            self.output_grid.clear_widgets()  # Clear previous widgets
            error_label = Label(text="Invalid input. Please enter numbers.")  # Create a new label for the error message
            self.output_grid.add_widget(error_label)  # Add the new label to the grid layout

        # After you've added all your labels, set the height of the grid
        self.output_grid.height = len(self.output_grid.children) * 40  # Assuming each child takes up 40 pixels in height

        # Add the 'Start Training' button at the end
        start_training_button = Button(text="Start Training", size_hint_y=None, height=60)
        start_training_button.bind(on_press=self.start_training)  # Bind to a method that handles the training start
        self.output_grid.add_widget(start_training_button)
        
        # Switch to the 'Workout Generation' tab to display the results
        self.tab_panel.switch_to(self.output_tab)

        self.workout_tab = TabbedPanelItem(text='Workout Progress')
        self.workout_grid = GridLayout(cols=1)
        self.workout_tab.add_widget(self.workout_grid)
        self.tab_panel.add_widget(self.workout_tab)

        return self.tab_panel
    
    def start_training(self, instance):
        self.tab_panel.switch_to(self.workout_tab)
        self.workout_grid.clear_widgets()
        self.current_workout_index = 0

        # Update self.workout_plan based on changed values in output_grid
        new_workout_plan = []
        grid_children = reversed(self.output_grid.children)
        exercise_info = {}
        for widget in grid_children:
            if isinstance(widget, Button):
                continue  # Skip 'Start Training' button
            if isinstance(widget, TextInput):
                if 'Rest Time' in widget.hint_text:
                    exercise_info = {'name': 'Rest',
                                    'set': None,
                                    'total_sets': None,
                                    'reps': None,
                                    'weight': None,
                                    'time': float(widget.text),
                                    'is_rest': True}
                else:
                    # Assuming that text inputs for exercise info are in the order: Time, Weight, Reps
                    exercise_info['time'] = float(widget.text)
                    exercise_info['weight'] = float(widget.text)
                    exercise_info['reps'] = int(widget.text)
            if isinstance(widget, Label):
                if widget.text.startswith("Exercise:"):
                    exercise_name = widget.text[len("Exercise: "):].strip()
                    exercise_info['name'] = exercise_name
                    new_workout_plan.append(exercise_info.copy())  # Add a copy of exercise_info
                    exercise_info = {}
                    
        self.workout_plan = new_workout_plan

        self.display_current_exercise()

    def display_current_exercise(self):
        if self.current_workout_index >= len(self.workout_plan):
            self.workout_grid.clear_widgets()
            self.workout_grid.add_widget(Label(text="Workout Complete!"))
            return
        
        self.workout_grid.clear_widgets()
        current_info = self.workout_plan[self.current_workout_index]
        
        self.workout_grid.add_widget(Label(text=f"Exercise: {current_info['name']}"))
        self.workout_grid.add_widget(Label(text=f"Set: {current_info['set']}"))
        self.workout_grid.add_widget(Label(text=f"Reps: {current_info['reps']}"))
        self.workout_grid.add_widget(Label(text=f"Weight: {current_info['weight']}"))
        
        # Initialize timer and schedule
        self.timer_value = current_info['time']
        self.timer_label = Label(text=f"Time left: {self.timer_value}")
        self.workout_grid.add_widget(self.timer_label)
        
        Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.timer_value -= 1
        self.timer_label.text = f"Time left: {self.timer_value}"

        if self.timer_value <= 0:
            Clock.unschedule(self.update_timer)
            self.current_workout_index += 1

            if self.current_workout_index < len(self.workout_plan):
                self.display_current_exercise()
            else:
                self.workout_grid.clear_widgets()
                self.workout_grid.add_widget(Label(text="Workout Complete!"))

if __name__ == '__main__':
    WorkoutPlannerApp().run()
