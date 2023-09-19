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
from kivy.uix.slider import Slider
from kivy.clock import Clock
from scipy.spatial.distance import euclidean
import numpy as np
import csv
import sqlite3

Window.size = (360, 640)

class WorkoutPlannerApp(App):
    def __init__(self, **kwargs):
        super(WorkoutPlannerApp, self).__init__(**kwargs)
        self.workout_plan = []  # Initialize the workout plan list
        self.current_exercise_index = 0
        self.total_slider_value = 0.0
        # Initialize SQLite database connection
        self.conn = sqlite3.connect("C:\\Users\\gbray\\Documents\\fitapp\\exercises.db")
        self.c = self.conn.cursor()

    def build(self):
        self.selected_exercises = []

        # Create a TabbedPanel
        self.tab_panel = TabbedPanel()
        
        # Create the first tab for input fields
        self.input_tab = TabbedPanelItem(text='User Inputs')
        
        # Create main BoxLayout for the first tab
        self.input_box = BoxLayout(orientation='vertical', size_hint_y=None)
        self.input_box.bind(minimum_height=self.input_box.setter('height'))
            
        # Create Sliders for muscle groups
        self.muscle_sliders = {}
        self.muscle_slider_labels = {}  # Step 1: Create a dictionary to hold the labels
        for muscle in ['Lats', 'Chest', 'Deltoids', 'Biceps', 'Triceps', 'Abs', 'Forearm', 'Quads', 'Hams', 'Calfs', 'Glutes', 'Lumbar', 'Trapezius']:
            slider = Slider(min=0, max=1, value=0, step=0.01)
            self.muscle_sliders[muscle] = slider
            slider.bind(value=self.on_slider_value_change)  # Bind to method
            
            muscle_box = BoxLayout()
            value_label = Label(text="0.0")  # Step 2: Create the label
            self.muscle_slider_labels[muscle] = value_label  # Step 2: Store the label in the dictionary
            
            muscle_box.add_widget(Label(text=muscle))
            muscle_box.add_widget(slider)
            muscle_box.add_widget(value_label)  # Step 2: Add the label to the muscle_box
            
            self.input_box.add_widget(muscle_box)
            
        # Create additional input fields for the first tab
        self.user_rest_time_input = TextInput(hint_text='Rest Time (s)')
        self.total_training_length_input = TextInput(hint_text='Total Training Length (min)')
        self.desired_num_exercises_input = TextInput(hint_text='Desired Number of Exercises')
        
        self.input_box.add_widget(self.user_rest_time_input)
        self.input_box.add_widget(self.total_training_length_input)
        self.input_box.add_widget(self.desired_num_exercises_input)
        
        # Add Spinner for training goals
        self.training_goal_spinner = Spinner(text='Training Goal', values=('Strength', 'Hypertrophy', 'Endurance'))
        self.input_box.add_widget(self.training_goal_spinner)
        
        # Add Checkboxes for equipment
        self.equipment_checkboxes = {}
        for equip in ['Dumbbell', 'Bar', 'Machine', 'Bench', 'ResistanceBand', 'Plate', 'KettleBell', 'DrawBar', 'ParallelsBar', 'Other']:
            cb = CheckBox()
            self.equipment_checkboxes[equip] = cb
            equip_box = BoxLayout()
            equip_box.add_widget(Label(text=equip))
            equip_box.add_widget(cb)
            self.input_box.add_widget(equip_box)
        
        # Create a button to collect user input
        self.button = Button(text='Generate Workout Plan')
        self.button.bind(on_press=self.generate_workout_plan)
        self.input_box.add_widget(self.button)


        for muscle_box in self.input_box.children:  # Assuming each muscle slider is wrapped in a BoxLayout
            muscle_box.size_hint_y = None
            muscle_box.height = 40  # Or any other height you find appropriate
      
        # Create ScrollView for the first tab
        self.scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.scroll_view.add_widget(self.input_box)
        
        # Add ScrollView to the first tab
        self.input_tab.add_widget(self.scroll_view)
        # Create the TabbedPanel and add the first tab to it
        self.tab_panel.add_widget(self.input_tab)

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
        total_workout_time_seconds = 0  # Initialize total workout time to zero
        self.output_grid.clear_widgets()  # Clear previous widgets
        try:
            # Collect user inputs
            user_input_dict = {muscle: slider.value for muscle, slider in self.muscle_sliders.items()}
            user_vector = np.array([v for k, v in user_input_dict.items()])
            user_rest_time = float(self.user_rest_time_input.text)
            total_training_length_minutes = float(self.total_training_length_input.text)
            desired_num_exercises = int(self.desired_num_exercises_input.text)
            user_training_goal = self.training_goal_spinner.text
            unavailable_equipment = [equip for equip, cb in self.equipment_checkboxes.items() if not cb.active]
            
            # Query the database to replace the placeholder exercises
            self.c.execute("SELECT * FROM Exercises")
            exercise_data2_list = self.c.fetchall()

            # Convert the SQLite rows into a list of dictionaries
            columns = [desc[0] for desc in self.c.description]
            exercise_data2_list = [dict(zip(columns, row)) for row in exercise_data2_list]

            # Filter exercises based on equipment
            filtered_exercises_list = [exercise for exercise in exercise_data2_list if all(item not in [exercise['Material_1'], exercise['Material_2'], exercise['Material_3']] for item in unavailable_equipment)]
            
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
                est_time_for_10_reps_str = exercise_row['Est_Time_for_10_Reps']
                est_time_for_10_reps_seconds = int(est_time_for_10_reps_str)
                time_for_reps = (est_time_for_10_reps_seconds / 10) * num_reps
                coeff_rest_time = exercise_row['coeff_rest_time']
                total_rest_time = user_rest_time * coeff_rest_time
                return time_for_reps, total_rest_time

            # Create vectors for filtered exercises based on their attributes
            filtered_exercise_vectors = [np.array([exercise[muscle] for muscle in ['Lats', 'Chest', 'Deltoids', 'Biceps', 'Triceps', 'Abs', 'Forearm', 'Quads', 'Hams', 'Calfs', 'Glutes', 'Lumbar', 'Trapezius']]) for exercise in filtered_exercises_list]

            # Initialize variables for the iterative selection of exercises
            selected_exercises = []
            remaining_time_budget_seconds = total_training_length_minutes * 60
            final_vector = np.zeros(13)
            total_ponderation_factor = 0
            exercise_plan_output = []
            total_rest_time_for_all_exercises = 0

            # Iteratively select exercises
            while len(selected_exercises) < desired_num_exercises:
                remaining_time_budget_seconds = (total_training_length_minutes * 60) - total_rest_time_for_all_exercises
                remaining_budget_per_exercise = remaining_time_budget_seconds / (desired_num_exercises - len(selected_exercises))
                
                best_next_distance = float('inf')
                best_next_exercise_idx = None
                best_next_vector = None
                
                for idx, exercise_vector in enumerate(filtered_exercise_vectors):
                    if idx in selected_exercises:
                        continue  # Skip already selected exercises
                    
                    exercise_row = filtered_exercises_list[idx]
                    num_reps = round(determine_reps_weights_rest(user_training_goal, exercise_row['coeff_rest_time'], exercise_row['Weight_for_10_rep'], user_rest_time)[0]['reps'])
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
                    num_reps = round(determine_reps_weights_rest(user_training_goal, exercise_row['coeff_rest_time'], exercise_row['Weight_for_10_rep'], user_rest_time)[0]['reps'])
                    time_one_set, rest_time_between_sets = estimate_time_one_set(exercise_row, num_reps)
                    num_sets = int(remaining_budget_per_exercise // time_one_set)
                    
                    total_time_for_next_exercise = num_sets * time_one_set
                    remaining_time_budget_seconds -= total_time_for_next_exercise
                    total_workout_time_seconds += total_time_for_next_exercise  # Update the total workout time
                    
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
                num_reps = round(determine_reps_weights_rest(user_training_goal, exercise_row['coeff_rest_time'], exercise_row['Weight_for_10_rep'], user_rest_time)[0]['reps'])
                time_one_set, rest_time_between_sets = estimate_time_one_set(exercise_row, num_reps)
                num_sets = int(remaining_budget_per_exercise // time_one_set)

                for set_number in range(1, num_sets + 1):
                    exercise_box = BoxLayout(size_hint_y=None, height=60)
                    exercise_box.bind(minimum_height=exercise_box.setter('height'))
                    
                    exercise_text = f"{exercise_row['Exercise_Name']}, Set: {set_number}/{num_sets}"
                    reps_input = TextInput(text=str(num_reps), size_hint_x=0.2)
                    weight_input = TextInput(text=str(exercise_row['Weight_for_10_rep']), size_hint_x=0.2)
                    time_input = TextInput(text=str(time_one_set), size_hint_x=0.2)

                    exercise_box.add_widget(Label(text=exercise_text, size_hint_x=0.6))
                    exercise_box.add_widget(reps_input)
                    exercise_box.add_widget(weight_input)
                    exercise_box.add_widget(time_input)

                    self.output_grid.add_widget(exercise_box)

                    # Add the new exercise to the workout_plan list
                    exercise_info = {'name': exercise_row['Exercise_Name'],
                                    'set': set_number,
                                    'total_sets': num_sets,
                                    'reps': num_reps,
                                    'weight': exercise_row['Weight_for_10_rep'],
                                    'time': time_one_set,
                                    'is_rest': False,
                                    'input_id': f"exercise_{len(self.workout_plan)}"}  # New line to add
                    self.workout_plan.append(exercise_info)

                    reps_input.bind(text=self.update_reps_value)
                    reps_input.input_id = exercise_info['input_id']  # Assign the unique input_id
                    weight_input.bind(text=self.update_weight_value)
                    weight_input.input_id = exercise_info['input_id']  # Assign the unique input_id

                    # Bind the time_input to update_time_value method
                    time_input.bind(text=self.update_time_value)
                    time_input.input_id = exercise_info['input_id']  # Assign the unique input_id

                    rest_time_input = TextInput(text=str(rest_time_between_sets), hint_text='Rest Time (s)', size_hint_x=0.2)
                    rest_time_input.input_id = f"rest_{len(self.workout_plan)}"  # Assign a unique input_id
                    rest_time_input.bind(text=self.update_time_value)  # Bind to the same update function

                    rest_time_box = BoxLayout(size_hint_y=None, height=60)
                    rest_time_box.add_widget(Label(text="Rest Time", size_hint_x=0.8))
                    rest_time_box.add_widget(rest_time_input)
                    self.output_grid.add_widget(rest_time_box)


                    # Add a corresponding rest period after each exercise in the workout plan
                    rest_info = {'name': 'Rest',
                                'set': set_number,
                                'total_sets': num_sets,
                                'reps': 'Rest',
                                'weight': 'Rest',
                                'time': rest_time_between_sets,
                                'is_rest': True,
                                'input_id': f"rest_{len(self.workout_plan)}"}  # New line to add
                    self.workout_plan.append(rest_info)
                    total_workout_time_seconds += rest_time_between_sets  # Update the total workout time for rest period

                # Adding rest time input between exercises
                rest_time_input_ex = TextInput(text=str(rest_time_between_sets), hint_text='Rest Time (s)', size_hint_y=None, height=40)
                self.output_grid.add_widget(rest_time_input_ex)

                # Switch to the 'Workout Generation' tab to display the results
                self.tab_panel.switch_to(self.output_tab)

            # Calculate Total Time for Workout
            total_time_minutes = total_workout_time_seconds // 60
            total_time_remaining_seconds = total_workout_time_seconds % 60
            self.total_time_label = Label(text=f"Total Time for Workout: {total_time_minutes} minutes and {total_time_remaining_seconds} seconds",
                                    size_hint_y=None, height=60)

            # Calculate Matching Percentage
            max_possible_distance = euclidean(np.zeros(13), np.ones(13))
            matching_percentage = ((1 - best_next_distance / max_possible_distance) * 100)*3-200

            # Add Summary Information to output_grid
            summary_grid = GridLayout(cols=1, size_hint_y=None, height=180)
            summary_grid.bind(minimum_height=summary_grid.setter('height'))
            summary_grid.add_widget(Label(text=f"Matching Percentage: {matching_percentage:.2f}%",
                                        size_hint_y=None, height=60))
            summary_grid.add_widget(Label(text=f"Final Vector: {final_vector}",
                                        size_hint_y=None, height=60))
            summary_grid.add_widget(self.total_time_label)

            self.output_grid.add_widget(summary_grid)

            self.recalculate_total_time()  # Add this line to update the total workout time
            
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
        start_training_button.bind(on_press=self.start_training)

        # Switch to the 'Workout Generation' tab to display the results
        self.tab_panel.switch_to(self.output_tab)

        self.workout_tab = TabbedPanelItem(text='Workout Progress')
        self.workout_grid = GridLayout(cols=1)
        self.workout_tab.add_widget(self.workout_grid)
        self.tab_panel.add_widget(self.workout_tab)

        return self.tab_panel

    def start_training(self, instance):
        self.tab_panel.switch_to(self.workout_tab)
        self.current_exercise_index = 0  # Initialize the index for the first exercise
        self.current_set = 1  # Initialize the set counter
        self.workout_grid.clear_widgets()  # Clear the workout grid
        self.display_current_exercise()  # Display the first exercise
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)  # Schedule the timer to update every second

    def display_current_exercise(self):
        current_exercise = self.workout_plan[self.current_exercise_index]
        self.current_time_left = current_exercise['time']  # Initialize the countdown timer
        
        self.workout_grid.clear_widgets()  # Clear the workout grid
        self.workout_grid.add_widget(Label(text=f"Exercise: {current_exercise['name']}"))
        self.workout_grid.add_widget(Label(text=f"Set: {self.current_set}"))
        self.workout_grid.add_widget(Label(text=f"Reps: {current_exercise['reps']}"))
        self.workout_grid.add_widget(Label(text=f"Weight: {current_exercise['weight']}"))
        self.timer_label = Label(text=f"Time Left: {self.current_time_left}")
        self.workout_grid.add_widget(self.timer_label)

    def update_timer(self, dt):
        self.current_time_left -= 1  # Decrease the timer by one second
        self.timer_label.text = f"Time Left: {self.current_time_left}"  # Update the timer display

        if self.current_time_left <= 0:  # Time's up for the current set or rest period
            if self.workout_plan[self.current_exercise_index]['is_rest']:  # If it was a rest period
                self.current_set += 1  # Increment the set counter
            self.current_exercise_index += 1  # Move on to the next exercise or rest period

            # Check if the workout is over
            if self.current_exercise_index >= len(self.workout_plan):
                self.timer_event.cancel()  # Stop the timer
                self.workout_grid.clear_widgets()
                self.workout_grid.add_widget(Label(text="Workout Complete!"))
                return

            # Set the timer to the updated time value from the workout plan for the next exercise/rest period
            current_exercise = self.workout_plan[self.current_exercise_index]
            self.current_time_left = current_exercise['time']

            self.display_current_exercise()  # Display the next exercise or rest period

    def update_time_value(self, instance, value):
        self.recalculate_total_time()  # Recalculate the total workout time
        try:
            new_time = int(value)  # Convert the new value to an integer
        except ValueError:
            return  # Exit if the new value isn't a valid integer

        # Find the corresponding exercise in self.workout_plan using input_id
        for exercise in self.workout_plan:
            if exercise['input_id'] == instance.input_id:
                exercise['time'] = new_time  # Update the time value for that exercise
                break

    def update_reps_value(self, instance, value):
        try:
            new_reps = int(value)  # Convert the new value to an integer
        except ValueError:
            return  # Exit if the new value isn't a valid integer

        # Find the corresponding exercise in self.workout_plan using input_id
        for exercise in self.workout_plan:
            if exercise['input_id'] == instance.input_id:
                exercise['reps'] = new_reps  # Update the reps value for that exercise
                break
                
    def update_weight_value(self, instance, value):
        try:
            new_weight = float(value)  # Convert the new value to a float
        except ValueError:
            return  # Exit if the new value isn't a valid float

        # Find the corresponding exercise in self.workout_plan using input_id
        for exercise in self.workout_plan:
            if exercise['input_id'] == instance.input_id:
                exercise['weight'] = new_weight  # Update the weight value for that exercise
                break

    def recalculate_total_time(self):
        total_time_seconds = 0
        for exercise in self.workout_plan:
            total_time_seconds += exercise['time']
        total_time_minutes = total_time_seconds // 60
        total_time_remaining_seconds = total_time_seconds % 60
        self.total_time_label.text = f"Total Time for Workout: {total_time_minutes} minutes and {total_time_remaining_seconds} seconds"

    def on_slider_value_change(self, instance, value):
        new_total = sum(slider.value for slider in self.muscle_sliders.values())
        
        if new_total > 1:
            excess_value = new_total - 1
            instance.value -= excess_value  # Reduce the value of the currently moved slider
            return  # Exit to avoid further calculations
        
        self.total_slider_value = new_total  # Update the total value
        
        # Find the muscle associated with the changed slider and update its label
        for muscle, slider in self.muscle_sliders.items():
            if slider == instance:
                self.muscle_slider_labels[muscle].text = f"{value:.2f}"  # Step 3: Update the label's text
                break

    def on_stop(self):
        # Close SQLite database connection when the app stops
        self.conn.close()
        
if __name__ == '__main__':
    WorkoutPlannerApp().run()