from kivy.uix.textinput import TextInput
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
import openai
import simpleaudio as sa
import json

class ExerciseTimer:
    def __init__(self, app):
        self.app = app
        self.remaining_time = 0
        self.timer = None
        self.paused = False

    def start(self, time):
        self.cancel()  # Cancel any existing timers
        self.remaining_time = time
        self.paused = False
        self.timer = Clock.schedule_interval(self.update_timer, 1)

    def cancel(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None

    def toggle_pause(self):
        if self.paused:
            self.timer = Clock.schedule_interval(self.update_timer, 1)
        else:
            self.cancel()
        self.paused = not self.paused

    def update_timer(self, dt):
        if self.remaining_time > 0 and not self.paused:
            self.remaining_time -= 1
            self.app.update_timer_display(self.remaining_time)
        elif self.remaining_time <= 0:
            self.cancel()
            wave_obj = sa.WaveObject.from_wave_file("file.wav")
            play_obj = wave_obj.play()
            play_obj.wait_done()

class TrainingSessionApp(App):
    def __init__(self, **kwargs):
        super(TrainingSessionApp, self).__init__(**kwargs)
        self.current_session_index = None  # Initialize to None
        self.current_exercise_index = None  # Initialize to None
        self.load_training_sessions()  # Add this line to load sessions when the app starts

    def build(self):
        self.screen_manager = ScreenManager()
        self.create_initial_input_screen()
        self.exercise_timer = ExerciseTimer(self)
        self.create_session_list_screen()  # Moved this line here so it's always created
        self.create_training_screen()
        return self.screen_manager

    def load_training_sessions(self):  # New method to load sessions
        try:
            with open('training_session.json', 'r') as f:
                self.training_sessions = json.load(f)
        except FileNotFoundError:
            self.training_sessions = []

    def initialize_training_sessions(self):
        self.initialize_training_sessions()

    def create_initial_input_screen(self):
        self.initial_input_screen = Screen(name='initial_input')
        layout = BoxLayout(orientation='vertical')

        self.api_key_input = TextInput(hint_text='Enter ChatGPT API Key', multiline=False)
        self.num_exercises_input = TextInput(hint_text='Enter Number of Exercises', multiline=False)
        self.duration_input = TextInput(hint_text='Enter Duration in Minutes', multiline=False)
        self.muscle_focus_input = TextInput(hint_text='Enter Muscle Focus', multiline=False)
        self.material_input = TextInput(hint_text='Enter Material Available', multiline=False)
        self.rest_input = TextInput(hint_text='Enter Rest Time Between Exercises', multiline=False)

        submit_button = Button(text='Submit', size_hint=(None, None), size=(200, 50))
        submit_button.bind(on_press=self.submit_initial_input)

        skip_button = Button(text='Skip', size_hint=(None, None), size=(200, 50))
        skip_button.bind(on_press=self.skip_initial_input)

        layout.add_widget(self.api_key_input)
        layout.add_widget(self.num_exercises_input)
        layout.add_widget(self.duration_input)
        layout.add_widget(self.muscle_focus_input)
        layout.add_widget(self.material_input)
        layout.add_widget(self.rest_input)
        layout.add_widget(submit_button)
        layout.add_widget(skip_button)  # Add the skip button to the layout

        self.initial_input_screen.add_widget(layout)
        self.screen_manager.add_widget(self.initial_input_screen)
        self.screen_manager.current = 'initial_input'

    def submit_initial_input(self, instance):
        self.api_key = self.api_key_input.text
        self.num_exercises = int(self.num_exercises_input.text)
        self.duration = int(self.duration_input.text)
        self.muscle_focus = self.muscle_focus_input.text
        self.material = self.material_input.text
        self.rest_time = int(self.rest_input.text)

        openai.api_key = self.api_key

        prompt = f"Generate a set by set list for a {self.num_exercises}-exercise {self.muscle_focus} training session. The session title should be {self.num_exercises} exercises, {self.duration} minutes long, focusing on {self.muscle_focus}. Total reps: . For each exercise, include the following details: exercise name, number of reps, duration, explanation of how to perform it, muscles worked (for example 60% chest, 20% biceps, 15% deltoids, 5% forearm), materials needed. Please write the content between [start] and [end] to make it easily parseable."
            # Step 1: Generate Training Session Information
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=2500
        )
        print(response)
        raw_training_info = response.choices[0].text.strip()
        if not response.choices or not response.choices[0].text.strip():
            print("No valid text response from the first API call.")
            return
        
        # Step 2: Generate JSON String
        json_prompt = f"For the workout session: name: The name or description of the workout session. For example, 4 exercises, 50 minutes long, focusing on chest, lat. exercises: A list of exercise dictionaries, each containing details about an individual exercise. For each exercise in the exercises list: name: The name of the exercise, such as Bench press. reps: The number of repetitions for the exercise, like 12. duration: The estimated duration of the exercise considering the number of reps in seconds (50 for example). explanation: A text description explaining how to perform the exercise. material: The equipment needed for the exercise, like Dumbbells. Muscle focus: % of each muscle worked in this exercise (example: 40% biceps, 30% chest, 25% trapezius, 5% forearm). sets: The current set in the exercise (example: 1/5). For each exercise, include the following details:- Exercise name- Number of reps (ex:12)- Duration in seconds (ex:50)- Explanation of how to perform it- Muscles worked (for example, biceps: 70, forearms: 20, shoulders: 10)- Materials needed. Please write the content in a JSON-compatible format. Convert the following training session information into a well-formatted JSON object:\\n{raw_training_info}"
        
        json_response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=json_prompt,
            max_tokens=2500
        )
        print(json_response)
        if not json_response.choices or not json_response.choices[0].text.strip():
            print("No valid JSON response from the second API call.")
            return
        json_string = json_response.choices[0].text.strip()
        
        # Step 3: Save to JSON File
        try:
            with open('training_session.json', 'r') as f:
                existing_sessions = json.load(f)
        except FileNotFoundError:
            existing_sessions = []
        print(f"JSON String: {json_string}")
        new_session = json.loads(json_string)
        existing_sessions.append(new_session)
        
        with open('training_session.json', 'w') as f:
            json.dump(existing_sessions, f)
        
        self.training_sessions = existing_sessions
        self.screen_manager.current = 'session_list'

    def create_session_list_screen(self):
        self.session_list_screen = Screen(name='session_list')
        layout = BoxLayout(orientation='vertical')
        session_list = ScrollView()
        session_list_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        session_list_grid.bind(minimum_height=session_list_grid.setter('height'))
        for i, session in enumerate(self.training_sessions):
            button = Button(text=session['name'], size_hint_y=None, height=50)
            button.bind(on_release=lambda btn, index=i: self.start_session(index))
            session_list_grid.add_widget(button)
        session_list.add_widget(session_list_grid)
        layout.add_widget(Label(text='Select a Training Session:', font_size=20))
        layout.add_widget(session_list)
        self.session_list_screen.add_widget(layout)
        self.screen_manager.add_widget(self.session_list_screen)
        back_button = Button(text='Back', size_hint=(None, None), size=(200, 50))
        back_button.bind(on_press=lambda instance: setattr(self.screen_manager, 'current', 'initial_input'))
        layout.add_widget(back_button)

    def create_training_screen(self):
        self.training_screen = Screen(name='training')
        self.label = Label(text='', font_size=20)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.label)
        button_layout = BoxLayout(orientation='horizontal', spacing=10)
        self.start_button = Button(text='Start Set', size_hint=(None, None), size=(200, 50))
        self.start_button.bind(on_press=self.start_set)
        self.next_button = Button(text='Next Exercise', size_hint=(None, None), size=(200, 50))
        self.next_button.bind(on_press=self.next_exercise)
        self.back_to_list_button = Button(text='Go Back to List', size_hint=(None, None), size=(200, 50))
        self.back_to_list_button.bind(on_press=self.back_to_list)
        self.pause_button = Button(text='Pause', size_hint=(None, None), size=(200, 50))
        self.pause_button.bind(on_press=self.toggle_pause)
        button_layout.add_widget(self.back_to_list_button)
        button_layout.add_widget(self.next_button)
 
        layout.add_widget(button_layout)
        layout.add_widget(self.start_button)
        self.training_screen.add_widget(layout)
        self.screen_manager.add_widget(self.training_screen)

    def skip_initial_input(self, instance):
        self.load_training_sessions()  # Reload the training sessions
        self.screen_manager.current = 'session_list'

    def start_session(self, session_index):
        self.current_session_index = session_index
        self.current_exercise_index = 0
        self.exercise_timer.cancel()  # Cancel any existing timers
        self.show_next_exercise()
        self.screen_manager.current = 'training'

    def show_next_exercise(self):
        if self.current_session_index is not None:
            session = self.training_sessions[self.current_session_index]
            if self.current_exercise_index < len(session['exercises']):
                exercise = session['exercises'][self.current_exercise_index]
                
                # Convert the muscle focus dictionary to a string
                muscle_focus_str = ", ".join(f"{k}: {v}%" for k, v in exercise['muscle focus'].items())
                
                formatted_text = (
                    f"Exercise: {exercise['name']}\n"
                    f"Reps: {exercise['reps']}\n"
                    f"Duration: {exercise['duration']} seconds\n"
                    f"Materials: {exercise['materials']}\n"
                    f"Sets: {exercise['sets']}\n"
                    f"Muscle Focus: {muscle_focus_str}\n"  # Add this line
                    f"Instructions: {exercise['explanation']}"
                )
                self.label.text = formatted_text
                self.start_button.text = 'Start Set'
            else:
                self.label.text = "Training session completed!"
                self.start_button.text = 'Start Session'
        else:
            self.label.text = "Please select a training session first."


    def start_set(self, instance):
        if self.current_session_index is not None:
            session = self.training_sessions[self.current_session_index]
            if self.current_exercise_index < len(session['exercises']):
                exercise = session['exercises'][self.current_exercise_index]
                if self.start_button.text == 'Start Set':
                    self.exercise_timer.start(exercise['duration'])
                    self.start_button.text = 'Pause'
                else:
                    self.exercise_timer.toggle_pause()
                    self.start_button.text = 'Resume' if self.exercise_timer.paused else 'Pause'
            else:
                self.show_next_exercise()

    def next_exercise(self, instance):
        self.exercise_timer.cancel()  # Cancel the current timer
        self.current_exercise_index += 1
        self.show_next_exercise()

    def back_to_list(self, instance):
        self.exercise_timer.cancel()  # Cancel the current timer
        self.current_session_index = None
        self.current_exercise_index = None
        self.screen_manager.current = 'session_list'

    def toggle_pause(self, instance):
        self.exercise_timer.toggle_pause()
        self.start_button.text = 'Resume' if self.exercise_timer.paused else 'Pause'

    def update_timer_display(self, remaining_time):
        if self.current_exercise_index is not None:
            session = self.training_sessions[self.current_session_index]
            if self.current_exercise_index < len(session['exercises']):
                exercise = session['exercises'][self.current_exercise_index]
                self.label.text = f"{exercise['name']} - Reps: {exercise['reps']}Time Remaining: {remaining_time} seconds{exercise['explanation']}"

    def on_set_completed(self):
        self.next_exercise(None)  # Automatically move to the next exercise
        self.show_next_exercise()  # Update the display for the new exercise

    def on_stop(self):
        self.exercise_timer.cancel()  # Ensure the timer is canceled when the app is closed

if __name__ == '__main__':
    TrainingSessionApp().run()
