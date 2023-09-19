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
            def determine_reps_weights_rest(training_goal, weight_for_10_rep, base_rest_time):
                reps_weights_rest = []
                if training_goal == 'Strength':
                    base_reps = 5  # Set to 5 for Strength
                    base_weight = weight_for_10_rep * 1.3
                elif training_goal == 'Hypertrophy':
                    base_reps = 10  # Set to 10 for Hypertrophy
                    base_weight = weight_for_10_rep
                elif training_goal == 'Endurance':
                    base_reps = 20  # Set to 20 for Endurance
                    base_weight = weight_for_10_rep * 0.5


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

            # Step 1: Initial Exercise Selection
            initial_exercise_idx = np.random.choice(len(filtered_exercises_list))
            initial_exercise = filtered_exercises_list[initial_exercise_idx]
            initial_vector = np.array([initial_exercise[muscle] for muscle in user_input_dict.keys()])
            
            # Initialize intermediate vector and total ponderation factor
            intermediate_vector = initial_vector
            total_ponderation_factor = 3  # Assuming three set for the initial exercise
            initial_exercise['sets'] = 3
            selected_exercises = [initial_exercise]
            
            # Step 2: Iterative Exercise Selection
            while len(selected_exercises) < desired_num_exercises:
                best_next_distance = float('inf')
                best_next_exercise = None
                
                for exercise in filtered_exercises_list:
                    if exercise not in selected_exercises:
                        exercise_vector = np.array([exercise[muscle] for muscle in user_input_dict.keys()])
                        
                        # Calculate new intermediate vector if this exercise is included
                        new_intermediate_vector = (intermediate_vector * total_ponderation_factor + exercise_vector) / (total_ponderation_factor + 1)
                        
                        # Calculate Euclidean distance between new_intermediate_vector and user_vector
                        distance = euclidean(new_intermediate_vector, user_vector)
                        
                        for sets in range(1, 7):  # Iterating from 1 to 6 sets
                            # Calculate new intermediate vector if this exercise is included with 'sets' number of sets
                            new_intermediate_vector = (intermediate_vector * total_ponderation_factor + exercise_vector * sets) / (total_ponderation_factor + sets)
        
                            # Calculate Euclidean distance between new_intermediate_vector and user_vector
                            distance = euclidean(new_intermediate_vector, user_vector)

                            if distance < best_next_distance:
                                best_next_distance = distance
                                best_next_exercise = exercise
                                best_next_sets = sets

                
                if best_next_exercise:
                    # Update intermediate_vector and total ponderation factor
                    best_next_exercise['sets'] = best_next_sets
                    exercise_vector = np.array([best_next_exercise[muscle] for muscle in user_input_dict.keys()])
                    intermediate_vector = (intermediate_vector * total_ponderation_factor + exercise_vector) / (total_ponderation_factor + 1)
                    total_ponderation_factor += 1  # Assuming one set for the new exercise
                    selected_exercises.append(best_next_exercise)
                    
                    # Step 3: Time Adjustment
                    # Calculate time_per_set and rest_time for each exercise
                    for exercise in selected_exercises:
                        # Determine reps and weights based on the training goal
                        reps_weights_rest = determine_reps_weights_rest(user_training_goal, exercise['Weight_for_10_rep'], user_rest_time)
                        chosen_reps_weights_rest = reps_weights_rest[0]
                        num_reps = chosen_reps_weights_rest['reps']

                        exercise['time_per_set'] = (exercise['Est_Time_for_10_Reps'] / 10) * num_reps
                        exercise['rest_time'] = user_rest_time * exercise['coeff_rest_time']  # Updated this line

                    # Calculate initial total workout time
                    total_workout_time = sum((exercise['sets'] * exercise['time_per_set']) + ((exercise['sets'] - 1) * exercise['rest_time']) for exercise in selected_exercises)

                    # Define the acceptable range for total workout time
                    lower_bound = total_training_length_minutes*60 * 0.85
                    upper_bound = total_training_length_minutes*60 * 1.15

                    while not (lower_bound <= total_workout_time <= upper_bound):
                        if total_workout_time > upper_bound:
                            # Find the exercise with the most sets and reduce by one
                            max_sets_exercise = max(selected_exercises, key=lambda x: x['sets'])
                            if max_sets_exercise['sets'] > 1:  # Ensure the number of sets doesn't go below 1
                                max_sets_exercise['sets'] -= 1
                                # Reduce total time by time_per_set for this exercise
                                total_workout_time -= max_sets_exercise['time_per_set']
                                
                        elif total_workout_time < lower_bound:
                            # Find the exercise with the fewest sets and increase by one
                            min_sets_exercise = min(selected_exercises, key=lambda x: x['sets'])
                            min_sets_exercise['sets'] += 1
                            # Increase total time by time_per_set for this exercise
                            total_workout_time += min_sets_exercise['time_per_set']


                # Initialize variables for displaying the plan
                workout_plan_text = "Generated Workout Plan:\n"

            # Calculating total time and displaying each selected exercise
            total_time_seconds = 0

            self.selected_exercises = []

            # Initialize the total workout time
            total_workout_time_seconds = 0

            # Initialize a counter for input IDs
            input_id_counter = 0  

            for exercise in selected_exercises:
                num_sets = exercise['sets']  # Number of sets for this exercise

                weight = exercise.get('Weight_for_10_rep', 'N/A')  # Get weight from the exercise dictionary, default to 'N/A' if not found
                time_per_set = exercise.get('time_per_set', 0)  # Get time_per_set from the exercise dictionary, default to 0 if not found
                total_time_for_one_exercise = time_per_set * num_sets  # Calculate total time for one exercise
    

                for set_num in range(1, num_sets + 1):  # Loop through each set
                    set_box = BoxLayout(size_hint_y=None, height=60)
                    
                    set_box.add_widget(Label(text=f"{exercise['Exercise_Name']} Set {set_num}/{num_sets}"))
                    
                    weight_input = TextInput(hint_text='Weight', input_id=input_id_counter)
                    weight_input.bind(text=self.update_weight_value)
                    set_box.add_widget(weight_input)
                    
                    reps_input = TextInput(hint_text='Reps', input_id=input_id_counter)
                    reps_input.bind(text=self.update_reps_value)
                    set_box.add_widget(reps_input)
                    
                    time_input = TextInput(hint_text='Time', input_id=input_id_counter)
                    time_input.bind(text=self.update_time_value)
                    set_box.add_widget(time_input)

                    rest_input = TextInput(hint_text='Rest Time', input_id=input_id_counter)
                    rest_input.bind(text=self.update_time_value)
                    set_box.add_widget(rest_input)
                    
                    self.output_grid.add_widget(set_box)
                    
                    # Add this set to workout_plan list for future reference
                    exercise_info = {
                        'name': exercise['Exercise_Name'],
                        'set': set_num,
                        'total_sets': num_sets,
                        'input_id': input_id_counter,
                        'is_rest': False  # This is not a rest period
                    }
                    self.workout_plan.append(exercise_info)
                    
                    input_id_counter += 1  # Increment the input_id_counter
                
                # Also add this exercise to workout_plan list for future reference
                exercise_info = {
                    'name': exercise['Exercise_Name'],
                    'set': 1,
                    'total_sets': num_sets,
                    'reps': num_reps,
                    'weight': weight,
                    'time': total_time_for_one_exercise  # total time for this exercise (in seconds)
                }
                self.workout_plan.append(exercise_info)

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