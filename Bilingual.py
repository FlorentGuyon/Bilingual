import tkinter as tk
import json
import random
import os

from math import ceil
from tkinter import ttk
from PIL import Image, ImageTk
from functools import partial
from copy import deepcopy
from gtts import gTTS
from playsound import playsound
from time import sleep

COLOR_WHITE = "#FFFFFF"
COLOR_LIGHT_GREY = "#eae5e5"

#COLOR_LIGHT_BLUE = "#c9c5be"
#COLOR_DARK_BLUE = "#394a62"

COLOR_LIGHT_PINK = "#edcbc5"
COLOR_MID_PINK = "#e1a99f"
COLOR_DARK_PINK = "#c39792"

EVENT_LEFT_CLICK = "<Button-1>"

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Bilingual(tk.Tk):

    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self.icons = {}
        self.data = None
        self.explainations = None
        self.spoken_language = None
        self.learned_language = None
        self.current_profile = None
        self.current_category = None
        self.current_lesson = None
        self.current_question = None
        self.configure_style()
        self.create_window()
        self.display_profiles()

    def log_calls(method):
        def wrapper(*args, **kwargs):
            print(method.__name__)
            return method(*args, **kwargs)
        return wrapper

    @log_calls
    def close_app(self, event=None):
        self.remove_temp_files()
        self.destroy()

    @log_calls
    def remove_temp_files(self):
        folder_path = CURRENT_DIRECTORY + "/assets/temp"

        # Check if the folder exists
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            # List all files and subdirectories in the folder
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)

                # Check if it's a file (not a subdirectory) and delete it
                if os.path.isfile(file_path):
                    os.remove(file_path)

    @log_calls
    def save_profile(self):
        for folder_name in self.data.keys():
            for file_name in self.data[folder_name].keys():
                file_path = f"{CURRENT_DIRECTORY}/assets/profiles/{self.current_profile}/{folder_name}/{file_name}.json"
                with open(file_path, 'w', encoding='utf-8') as json_file:
                    try:
                        json_data = json.dumps(self.data[folder_name][file_name], indent=4)
                        json_file.write(json_data)
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON in {file_path}")

    @log_calls
    def load_explainations(self):
        self.explainations = {}  # Dictionary to store the result

        for subdir, _, files in os.walk(CURRENT_DIRECTORY + "/assets/explainations/"):
            json_files = [f for f in files if f.endswith('.json')]

            for json_file in json_files:
                file_name = os.path.splitext(json_file)[0]  # Remove the .json extension
                file_path = os.path.join(subdir, json_file)

                with open(file_path, 'r', encoding='utf-8') as json_file:
                    try:
                        file_content = json.load(json_file)
                        self.explainations[file_name] = file_content
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON in {file_path}")
                        exit()                

    @log_calls
    def load_profile(self):
        self.data = {}  # Dictionary to store the result

        for subdir, _, files in os.walk(CURRENT_DIRECTORY + f"/assets/profiles/{self.current_profile}"):
            folder_name = os.path.basename(subdir)
            json_files = [f for f in files if f.endswith('.json')]

            if json_files:
                self.data[folder_name] = {}

                for json_file in json_files:
                    file_name = os.path.splitext(json_file)[0]  # Remove the .json extension
                    file_path = os.path.join(subdir, json_file)

                    with open(file_path, 'r', encoding='utf-8') as json_file:
                        try:
                            file_content = json.load(json_file)
                            self.data[folder_name][file_name] = file_content
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON in {file_path}")
                            exit()                

    @log_calls
    def load_image(self, name, width, height):
        if name in self.icons.keys():
            if width in self.icons[name].keys():
                if height in self.icons[name][width].keys():
                    return self.icons[name][width][height]

        resized_image = self.resize_image(f'./assets/icons/{name}.png', width, height)
        
        if not resized_image:
            return self.load_image("missing", width, height)
        
        self.icons[name] = {}
        self.icons[name][width] = {}
        self.icons[name][width][height] = resized_image
        return resized_image

    @log_calls
    def resize_image(self, path, width, height):
        try:
            raw_image = Image.open(path)
        except Exception as e:
            print(f'Error: Impossible to resize the image at "{path}" to {width}x{height}.')
            return None
        resize_img = raw_image.resize((width, height))
        image = ImageTk.PhotoImage(resize_img)
        return image

    @log_calls
    def configure_style(self):
        self.style = ttk.Style(self) 
        self.style.configure(".", background=COLOR_LIGHT_GREY, font=('Calibri', 12))

        self.style.configure("CustomLightFrame.TFrame", background=COLOR_LIGHT_PINK)
        self.style.configure("CustomMidFrame.TFrame", background=COLOR_MID_PINK)
        self.style.configure("CustomDarkFrame.TFrame", background=COLOR_DARK_PINK)

        self.style.configure("TLabel", background=COLOR_DARK_PINK, foreground=COLOR_WHITE)
        self.style.configure("CustomAverageLabel.TLabel", font=('Calibri', 14))
        self.style.configure("CustomBigLabel.TLabel", font=('Calibri', 16))

    @log_calls
    def create_window(self):
        self.title("Go Bilingo")
        self.iconbitmap('./assets/icons/icon.ico')
        self.configure(bg=COLOR_LIGHT_GREY)

        window_width = 800
        window_height = 600

        # get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # find the center point
        center_x = int((screen_width  /2) - (window_width  /2))
        center_y = int((screen_height /2) - (window_height /2))

        # set the position of the window to the center of the screen
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.resizable(False, False)

        # configure the style
        #self.configure(bg="blue")
        
        # configure the grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=8)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=8)
        self.rowconfigure(2, weight=1)

        self.window_container = ttk.Frame(self)
        self.window_container.grid(column=0, row=0)
        self.window_container.columnconfigure(0, weight=1)
        self.window_container.rowconfigure(0, weight=1)
   
    @log_calls
    def is_remembered(self, question):
        return random.random() < question[self.learned_language]["success_rate"]

    @log_calls
    def get_all_profiles(self):
        return [profile for profile in os.listdir(CURRENT_DIRECTORY + "/assets/profiles") if os.path.isdir(os.path.join(CURRENT_DIRECTORY + "/assets/profiles", profile))]

    @log_calls
    def get_all_languages(self):
        languages = []
        for folder_name in self.data.keys():
            for file_name in self.data[folder_name].keys():
                for question in self.data[folder_name][file_name]:
                    for language in question.keys():
                        if language not in languages:
                            languages.append(language)
        return languages

    @log_calls
    def get_all_categories(self):
        return list(self.data.keys())

    @log_calls
    def get_all_lessons(self, category=None):
        if category is None:
            category = self.current_category
        return list(self.data[category].keys())

    @log_calls
    def get_category_progress(self, category=None):
        if category is None:
            category = self.current_category
        progressions = [self.get_lesson_progress(category=category, lesson=lesson) for lesson in self.get_all_lessons(category=category)]
        return sum(progressions) / len(progressions)

    @log_calls
    def get_lesson_progress(self, category=None, lesson=None):
        if category is None:
            category = self.current_category
        if lesson is None:
            lesson = self.current_lesson
        progressions = [question[self.learned_language]["success_rate"] for question in self.data[category][lesson]]
        return sum(progressions) / len(progressions)

    @log_calls
    def choose_random_question(self):
        deep_copy = deepcopy(self.data)
        random.shuffle(deep_copy[self.current_category][self.current_lesson])
        for question in deep_copy[self.current_category][self.current_lesson]:
            if question == self.current_question:
                continue
            if not self.is_remembered(question):
                self.current_question = question
                return
        self.current_question = random.choice(deep_copy[self.current_category][self.current_lesson])

    @log_calls
    def bind_widget(self, widget, command, event=EVENT_LEFT_CLICK):
        widget.bind(event, command)
        for child in widget.winfo_children():
            self.bind_widget(child, command, event)

    @log_calls
    def validate_languages(self, spoken_language, learned_language, event=None):
        print(spoken_language)
        print(learned_language)
        if (spoken_language == "") or (learned_language == ""):
            self.display_languages()
        elif spoken_language == learned_language:
            self.display_languages()
        else:
            self.spoken_language = spoken_language
            self.learned_language = learned_language
            self.display_categories()

    @log_calls
    def validate_response(self, response, event=None):
        print("response: " + response)
        response_is_right = None
        answer = self.current_question[self.learned_language]["sentence"]
        question = None

        for question in self.data[self.current_category][self.current_lesson]:
            if question == self.current_question:
                question[self.learned_language]["tries"] += 1
                break

        if (response != "") and (response[-1] == "."):
            response = response[:-1]

        # If the response is right
        if response.lower().strip() == answer.lower().strip():
            self.playsound("correct")
            question[self.learned_language]["success_rate"] = ((question[self.learned_language]["success_rate"] * (question[self.learned_language]["tries"] -1)) +1) / question[self.learned_language]["tries"]
            self.save_profile()
            self.display_questions()

        # If the response is wrong
        else:
            self.playsound("incorrect")
            question[self.learned_language]["success_rate"] = (question[self.learned_language]["success_rate"] * (question[self.learned_language]["tries"] -1)) / question[self.learned_language]["tries"]
            self.display_answer(response)

    @log_calls
    def clear_window(self):
        for widget in self.window_container.winfo_children():
            widget.destroy()

    @log_calls
    def playsound(self, sound, wait=False):
        file_path = CURRENT_DIRECTORY + f"/assets/sounds/{sound}.wav"

        if os.path.isfile(file_path):
            playsound(file_path, wait)

    @log_calls
    def click_button(self, action, args=[], sound="write", event=None):
        if isinstance(args, tk.Event):
            event = args
            args = []

        elif isinstance(sound, tk.Event):
            event = sound
            sound = "write"

        if sound:
            self.playsound(sound)

        if type(args) != list:
            args = [args]

        print("args: " + str(args))

        action(*args)

    @log_calls
    def select_profile(self, profile, event=None):
        self.current_profile = profile
        self.load_profile()
        self.load_explainations()
        self.display_languages()
    
    @log_calls
    def select_category(self, category, event=None):
        self.current_category = category
        self.display_lessons()

    @log_calls
    def select_lesson(self, lesson, event=None):
        self.current_lesson = lesson
        self.display_questions()

    @log_calls
    def display_languages(self, page=1, event=None):
        languages = self.get_all_languages()

        # Configure page grid
        self.clear_window()
        self.title("Pick a language to learn !")
        self.window_container.grid(column=1, row=1)

        for spoken_language_index, spoken_language in enumerate(languages):
            for learned_language_index, learned_language in enumerate(languages):
               
                if spoken_language == learned_language:
                    continue

                frame = ttk.Frame(self.window_container, style="CustomDarkFrame.TFrame")
                frame.pack(pady=10, expand=True, fill=tk.X)

                spoken_language_picture = ttk.Label(frame, image=self.load_image(spoken_language, 45, 45), style="CustomBigLabel.TLabel")
                spoken_language_picture.pack(padx=15, pady=10, side=tk.LEFT)

                arrow_picture = ttk.Label(frame, image=self.load_image("arrow_right", 45, 45), style="CustomBigLabel.TLabel")
                arrow_picture.pack(padx=15, pady=10, side=tk.LEFT)

                learned_language_picture = ttk.Label(frame, image=self.load_image(learned_language, 45, 45), style="CustomBigLabel.TLabel")
                learned_language_picture.pack(padx=15, pady=10, side=tk.LEFT)

                self.bind_widget(frame, partial(self.click_button, self.validate_languages, [spoken_language, learned_language]))

        return_frame = ttk.Frame(self.window_container, style="CustomDarkFrame.TFrame")
        return_frame.pack(pady=10)

        return_frame_picture = ttk.Label(return_frame, image=self.load_image("arrow_left", 25, 25))
        return_frame_picture.pack(padx=10, pady=5, side=tk.LEFT)

        return_frame_text = ttk.Label(return_frame, text="Profiles")
        return_frame_text.pack(ipadx=5, ipady=5, side=tk.LEFT, expand=True, fill=tk.X)
        
        self.bind_widget(return_frame, partial(self.click_button, self.display_profiles, 1, "page"))
    
    @log_calls
    def display_profiles(self, page=1, event=None):

        profiles = self.get_all_profiles()
        tiles_by_line = 4
        lines_by_page = 3
        tiles_by_page = tiles_by_line * lines_by_page
        total_pages = ceil(len(profiles) / tiles_by_page)
        current_page = 1 if (page < 1) or (page > total_pages) else page

        # Configure page grid
        self.clear_window()
        self.title("Pick your profile !")
        self.window_container.grid(column=1, row=1)

        # Initialize variables
        start_index = (current_page - 1) * tiles_by_page
        tile_column, tile_row = 0, 0

        # Iterate through profiles
        for profile in profiles[start_index:]:

            frame = ttk.Frame(self.window_container, style="CustomDarkFrame.TFrame")
            frame.pack(pady=10, expand=True, fill=tk.X)

            frame_picture = ttk.Label(frame, image=self.load_image(profile, 40, 40), style="CustomBigLabel.TLabel")
            frame_picture.pack(padx=15, pady=10, side=tk.LEFT)

            frame_text = ttk.Label(frame, text=profile.capitalize(), style="CustomBigLabel.TLabel")
            frame_text.pack(ipadx=15, ipady=10, side=tk.LEFT, expand=True, fill=tk.X)

            self.bind_widget(frame, partial(self.click_button, self.select_profile, profile))
            
            # Define the position of the next tile if any
            tile_column += 1
            if tile_column >= tiles_by_line:
                tile_column = 0
                tile_row += 1
                if tile_row >= lines_by_page:
                    break

        return_frame = ttk.Frame(self.window_container, style="CustomDarkFrame.TFrame")
        return_frame.pack(pady=10)

        return_frame_picture = ttk.Label(return_frame, image=self.load_image("arrow_left", 25, 25))
        return_frame_picture.pack(padx=10, pady=5, side=tk.LEFT)

        return_frame_text = ttk.Label(return_frame, text="Quit")
        return_frame_text.pack(ipadx=5, ipady=5, side=tk.LEFT, expand=True, fill=tk.X)
        
        self.bind_widget(return_frame, partial(self.click_button, self.close_app))

        #if total_pages > 1:
        #    buttons_container = ttk.Frame(self.window_container)
        #    buttons_container.grid(column=0, row=1)
        #    buttons_container.columnconfigure(0, weight=1)
        #    buttons_container.columnconfigure(1, weight=1)

        #    previous_button = ttk.Button(buttons_container, state=buttons_state, image=self.load_image('previous', 20, 20), compound="left", text="Previous", command=partial(self.display_profiles, current_page -1))
        #    previous_button.grid(column=0, row=0, padx=30, pady=20)

        #    next_button = ttk.Button(buttons_container, state=buttons_state, image=self.load_image('next', 20, 20), compound="right", text="Next", command=partial(self.display_profiles, current_page +1))
        #    next_button.grid(column=1, row=0, padx=30, pady=20)

    @log_calls
    def display_categories(self, page=1, event=None):

        categories = self.get_all_categories()
        tiles_by_line = 4
        lines_by_page = 3
        tiles_by_page = tiles_by_line * lines_by_page
        total_pages = ceil(len(categories) / tiles_by_page)
        current_page = 1 if (page < 1) or (page > total_pages) else page

        # Configure page grid
        self.clear_window()
        self.title("Pick a category !")
        self.window_container.grid(column=1, row=1)

        # Initialize variables
        start_index = (current_page - 1) * tiles_by_page
        tile_column, tile_row = 0, 0

        # Iterate through categories
        for category in categories[start_index:]:

            frame = ttk.Frame(self.window_container, style="CustomDarkFrame.TFrame")
            frame.pack(pady=5, expand=True, fill=tk.X)

            title_frame = ttk.Frame(frame, style="CustomDarkFrame.TFrame")
            title_frame.pack(expand=True, fill=tk.BOTH)

            title_frame_picture = ttk.Label(title_frame, image=self.load_image(category, 35, 35), style="CustomAverageLabel.TLabel")
            title_frame_picture.pack(padx=15, pady=5, side=tk.LEFT)

            title_frame_text_text = category.replace("-", " ").title()
            title_frame_text = ttk.Label(title_frame, text=title_frame_text_text, style="CustomAverageLabel.TLabel")
            title_frame_text.pack(ipadx=15, ipady=5, side=tk.LEFT, expand=True, fill=tk.X)

            progressbar_frame = ttk.Frame(frame, style="CustomDarkFrame.TFrame")
            progressbar_frame.pack(expand=True, fill=tk.X)

            self.update()

            progressbar_frame_left_width = frame.winfo_width() * self.get_category_progress(category=category)
            progressbar_frame_left = ttk.Frame(progressbar_frame, height=5, width=progressbar_frame_left_width, style="CustomMidFrame.TFrame")
            progressbar_frame_left.pack(side=tk.LEFT)
            
            progressbar_frame_right = ttk.Frame(progressbar_frame, height=5, style="CustomLightFrame.TFrame")
            progressbar_frame_right.pack(expand=True, fill=tk.X, side=tk.LEFT)

            self.bind_widget(frame, partial(self.click_button, self.select_category, category))

            # Define the position of the next tile if any
            tile_column += 1
            if tile_column >= tiles_by_line:
                tile_column = 0
                tile_row += 1
                if tile_row >= lines_by_page:
                    break

        return_frame = ttk.Frame(self.window_container, style="CustomDarkFrame.TFrame")
        return_frame.pack(pady=10)

        return_frame_picture = ttk.Label(return_frame, image=self.load_image("arrow_left", 25, 25))
        return_frame_picture.pack(padx=10, pady=5, side=tk.LEFT)

        return_frame_text = ttk.Label(return_frame, text="Languages")
        return_frame_text.pack(ipadx=5, ipady=5, side=tk.LEFT, expand=True, fill=tk.X)
        
        self.bind_widget(return_frame, partial(self.click_button, self.display_languages, 1, "page"))

        #buttons_state = "enabled" if current_page > 1 else "disabled"

        #previous_button = ttk.Button(buttons_container, state=buttons_state, image=self.load_image('previous', 20, 20), compound="left", text="Previous", command=partial(self.display_categories, current_page -1))
        #previous_button.grid(column=1, row=0, padx=30, pady=20)

        #buttons_state = "enabled" if current_page < total_pages else "disabled"

        #next_button = ttk.Button(buttons_container, state=buttons_state, image=self.load_image('next', 20, 20), compound="right", text="Next", command=partial(self.display_categories, current_page +1))
        #next_button.grid(column=2, row=0, padx=30, pady=20)

    @log_calls
    def display_lessons(self, page=1, event=None):

        lessons = self.get_all_lessons()
        tiles_by_line = 4
        lines_by_page = 3
        tiles_by_page = tiles_by_line * lines_by_page
        total_pages = ceil(len(lessons) / tiles_by_page)
        current_page = 1 if (page < 1) or (page > total_pages) else page

        # Configure page grid
        self.clear_window()
        self.title("Pick a lesson !")
        self.window_container.grid(column=1, row=1)

        # Initialize variables
        start_index = (current_page - 1) * tiles_by_page
        tile_column, tile_row = 0, 0

        # Iterate through lessons
        for lesson in lessons[start_index:]:

            frame = ttk.Frame(self.window_container, style="CustomDarkFrame.TFrame")
            frame.pack(pady=5, expand=True, fill=tk.X)

            title_frame = ttk.Frame(frame, style="CustomDarkFrame.TFrame")
            title_frame.pack(expand=True, fill=tk.BOTH)

            title_frame_picture = ttk.Label(title_frame, image=self.load_image(lesson, 35, 35), style="CustomAverageLabel.TLabel")
            title_frame_picture.pack(padx=15, pady=5, side=tk.LEFT)

            title_frame_text_text = lesson.replace("-", " ").title()
            title_frame_text = ttk.Label(title_frame, text=title_frame_text_text, style="CustomAverageLabel.TLabel")
            title_frame_text.pack(ipadx=15, ipady=5, side=tk.LEFT, expand=True, fill=tk.X)

            progressbar_frame = ttk.Frame(frame, style="CustomDarkFrame.TFrame")
            progressbar_frame.pack(expand=True, fill=tk.X)

            self.update()

            progressbar_frame_left_width = frame.winfo_width() * self.get_lesson_progress(lesson=lesson)
            progressbar_frame_left = ttk.Frame(progressbar_frame, height=5, width=progressbar_frame_left_width, style="CustomMidFrame.TFrame")
            progressbar_frame_left.pack(side=tk.LEFT)
            
            progressbar_frame_right = ttk.Frame(progressbar_frame, height=5, style="CustomLightFrame.TFrame")
            progressbar_frame_right.pack(expand=True, fill=tk.X, side=tk.LEFT)

            self.bind_widget(frame, partial(self.click_button, self.select_lesson, lesson))

            # Define the position of the next tile if any
            tile_column += 1
            if tile_column >= tiles_by_line:
                tile_column = 0
                tile_row += 1
                if tile_row >= lines_by_page:
                    break

        return_frame = ttk.Frame(self.window_container, style="CustomDarkFrame.TFrame")
        return_frame.pack(pady=10)

        return_frame_picture = ttk.Label(return_frame, image=self.load_image("arrow_left", 25, 25))
        return_frame_picture.pack(padx=10, pady=5, side=tk.LEFT)

        return_frame_text = ttk.Label(return_frame, text="Categories")
        return_frame_text.pack(ipadx=5, ipady=5, side=tk.LEFT, expand=True, fill=tk.X)
        
        self.bind_widget(return_frame, partial(self.click_button, self.display_categories, 1, "page"))

        #leave_button = ttk.Button(buttons_container, image=self.load_image('leave', 20, 20), compound="left", text="Leave", command=self.display_categories)
        #leave_button.grid(column=0, row=0, padx=30, pady=20)

        #buttons_state = "enabled" if current_page > 1 else "disabled"

        #previous_button = ttk.Button(buttons_container, state=buttons_state, image=self.load_image('previous', 20, 20), compound="left", text="Previous", command=partial(self.display_lessons, current_page -1))
        #previous_button.grid(column=1, row=0, padx=30, pady=20)

        #buttons_state = "enabled" if current_page < total_pages else "disabled"

        #next_button = ttk.Button(buttons_container, state=buttons_state, image=self.load_image('next', 20, 20), compound="right", text="Next", command=partial(self.display_lessons, current_page +1))
        #next_button.grid(column=2, row=0, padx=30, pady=20)

    @log_calls
    def scroll_widget(self, widget, event):
        widget.configure(scrollregion=widget.bbox("all"))

    @log_calls
    def get_random_color(self):
        return random.choice(["red", "blue", "yellow", "green", "magenta", "orange"]) if self.debug_color else None

    @log_calls
    def display_answer(self, response):
        # Configure page grid
        self.clear_window()
        self.title("Nice Try !")
        self.window_container.grid(column=1, row=1)
        
        sentence_LabelFrame = ttk.LabelFrame(self.window_container, text="Sentence")
        sentence_LabelFrame.pack(pady=10)
        
        sentence_text = self.current_question[self.spoken_language]["sentence"].capitalize()
        sentence = ttk.Label(sentence_LabelFrame, text=sentence_text, width=50)
        sentence.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        response_LabelFrame = ttk.LabelFrame(self.window_container, text="Your answer")
        response_LabelFrame.pack(pady=10)
        
        response = ttk.Label(response_LabelFrame, text=response.capitalize(), width=50)
        response.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        answer_labelFrame = ttk.LabelFrame(self.window_container, text="Right answer")
        answer_labelFrame.pack(pady=10)
        
        answer_label_text = self.current_question[self.learned_language]["sentence"].capitalize()
        answer_label = ttk.Label(answer_labelFrame, text=answer_label_text, width=50)
        answer_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        explaination_text = []
 
        if self.learned_language in self.explainations.keys():
            for item in self.explainations[self.learned_language]:
                for patern in item["paterns"]:
                    if patern in self.current_question[self.learned_language]["sentence"]:
                        if self.spoken_language in item["explainations"].keys():
                            explaination_text.append(item["explainations"][self.spoken_language])

        if len(explaination_text) > 0 :
            explaination_LabelFrame = ttk.LabelFrame(self.window_container, text="Explainations")
            explaination_LabelFrame.pack(pady=10)
            
            explaination_canvas = tk.Canvas(explaination_LabelFrame, width=400)
            explaination_canvas.pack(side="left", expand=True, fill=tk.BOTH)

            scrollbar_frame = ttk.Frame(explaination_LabelFrame)
            scrollbar_frame.pack(side="right", expand=True, fill=tk.Y)

            explaination_scrollbar = ttk.Scrollbar(scrollbar_frame, orient='vertical', command=explaination_canvas.yview)
            explaination_scrollbar.pack(expand=True, fill=tk.Y)

            explaination_frame = tk.Frame(explaination_canvas, width=400)
            explaination_frame.pack(expand=True, fill=tk.BOTH)

            explaination_canvas.configure(yscrollcommand=explaination_scrollbar.set)
            explaination_canvas.create_window((4, 4), window=explaination_frame, anchor="nw", tags="frame")
            explaination_frame.bind("<Configure>", partial(self.scroll_widget, explaination_canvas))

            explaination_label_text = "\n\n".join(explaination_text)
            explaination_label = ttk.Label(explaination_frame, wraplength=400, text=explaination_label_text, anchor=tk.W, justify=tk.LEFT)
            explaination_label.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # BUTTONS
        return_frame = ttk.Frame(self.window_container, style="CustomDarkFrame.TFrame")
        return_frame.pack(padx=5, pady=10, side=tk.LEFT)

        return_frame_picture = ttk.Label(return_frame, image=self.load_image("arrow_left", 25, 25))
        return_frame_picture.pack(padx=10, pady=5, side=tk.LEFT)

        return_frame_text = ttk.Label(return_frame, text="Lessons")
        return_frame_text.pack(ipadx=10, ipady=5, side=tk.LEFT, expand=True, fill=tk.X)
        
        self.bind_widget(return_frame, partial(self.click_button, self.display_lessons, 1, "page"))

        validate_frame = ttk.Frame(self.window_container, style="CustomDarkFrame.TFrame")
        validate_frame.pack(padx=5, pady=10, side=tk.RIGHT)

        validate_frame_picture = ttk.Label(validate_frame, image=self.load_image("arrow_right", 25, 25))
        validate_frame_picture.pack(padx=10, pady=5, side=tk.RIGHT)

        validate_frame_text = ttk.Label(validate_frame, text="Next Question")
        validate_frame_text.pack(padx=10, pady=5, side=tk.RIGHT, expand=True, fill=tk.X)
        
        self.bind_widget(validate_frame, partial(self.click_button, self.display_questions))
    
    @log_calls
    def tell_text(self, text, language, event=None):
        file_path = CURRENT_DIRECTORY + "/assets/temp/tts.mp3"
        languages = {
            "english": {
                "language_code": "en",
                "accent_code": "co.uk"
            },
            "french": {
                "language_code": "fr",
                "accent_code": "fr"
            }
        }

        tts = gTTS(text=text, lang=languages[language]["language_code"], tld=languages[language]["accent_code"])

        if os.path.isfile(file_path):
            os.remove(file_path)

        tts.save(file_path)

        while not os.path.isfile(file_path):
            sleep(0.1)

        playsound(file_path, False)

    @log_calls
    def display_questions(self):
        self.choose_random_question()

        # Configure page grid
        self.clear_window()
        self.title("Translate this sentence !")
        self.window_container.grid(column=1, row=1)

        # SENTENCE
        sentence_frame = ttk.Frame(self.window_container, style="CustomDarkFrame.TFrame")
        sentence_frame.pack(pady=10, fill=tk.X)

        sentence_label_text = self.current_question[self.spoken_language]["sentence"].capitalize()
        sentence_label = ttk.Label(sentence_frame, text=sentence_label_text)
        sentence_label.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)

        if self.spoken_language in ["english", "french"]:
            sentence_tts = ttk.Label(sentence_frame, image=self.load_image("speak", 25, 25))
            sentence_tts.pack(side=tk.LEFT, padx=5, pady=5)

            self.bind_widget(sentence_tts, partial(self.click_button, self.tell_text, [sentence_label_text, self.spoken_language], None))

        # HINTS
        if "hints" in self.current_question[self.spoken_language].keys() :
            hints_labelFrame = ttk.LabelFrame(self.window_container, text="Hints")
            hints_labelFrame.pack(expand=True, fill=tk.X, pady=10)
            
            hints_label_text = self.current_question[self.spoken_language]["hints"].capitalize()
            hints_label = ttk.Label(hints_labelFrame, text=hints_label_text, justify=tk.LEFT)
            hints_label.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # ANSWER
        resonse_labelFrame = ttk.LabelFrame(self.window_container, text="Answer")
        resonse_labelFrame.pack(expand=True, fill=tk.X, pady=10)
        
        response_Stringvar = tk.StringVar()
        response_entry = ttk.Entry(resonse_labelFrame, textvariable=response_Stringvar)
        response_entry.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        response_entry.focus()

        # BUTTONS
        return_frame = ttk.Frame(self.window_container, style="CustomDarkFrame.TFrame")
        return_frame.pack(padx=5, pady=10, side=tk.LEFT)

        return_frame_picture = ttk.Label(return_frame, image=self.load_image("arrow_left", 25, 25))
        return_frame_picture.pack(padx=10, pady=5, side=tk.LEFT)

        return_frame_text = ttk.Label(return_frame, text="Lessons")
        return_frame_text.pack(ipadx=10, ipady=5, side=tk.LEFT, expand=True, fill=tk.X)
        
        self.bind_widget(return_frame, partial(self.click_button, self.display_lessons, 1, "page"))

        validate_frame = ttk.Frame(self.window_container, style="CustomDarkFrame.TFrame")
        validate_frame.pack(padx=5, pady=10, side=tk.RIGHT)

        validate_frame_picture = ttk.Label(validate_frame, image=self.load_image("arrow_right", 25, 25))
        validate_frame_picture.pack(padx=10, pady=5, side=tk.RIGHT)

        validate_frame_text = ttk.Label(validate_frame, text="Validate")
        validate_frame_text.pack(padx=10, pady=5, side=tk.RIGHT, expand=True, fill=tk.X)
        
        self.bind_widget(validate_frame, partial(self.validate_response, response_Stringvar.get()))

if __name__ == "__main__":
    app = Bilingual()
    app.mainloop()