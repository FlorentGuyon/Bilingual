import tkinter as tk
import json
import random
import os

from math import ceil
from tkinter import ttk
from PIL import Image, ImageTk
from functools import partial
from copy import deepcopy


class Bilingual(tk.Tk):

    def __init__(self):
        super().__init__()
        
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
    def save_profile(self):
        for folder_name in self.data.keys():
            for file_name in self.data[folder_name].keys():
                file_path = f"./assets/profiles/{self.current_profile}/{folder_name}/{file_name}.json"
                with open(file_path, 'w', encoding='utf-8') as json_file:
                    try:
                        json_data = json.dumps(self.data[folder_name][file_name], indent=4)
                        json_file.write(json_data)
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON in {file_path}")

    @log_calls
    def load_explainations(self):
        self.explainations = {}  # Dictionary to store the result

        for subdir, _, files in os.walk(f"./assets/explainations/"):
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

        for subdir, _, files in os.walk(f"./assets/profiles/{self.current_profile}"):
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
        self.style.configure("TButton", font=('Calibri', 12))
        self.style.configure("TFrame", font=('Calibri', 12))
        self.style.configure("TLabel", font=('Calibri', 12))
        self.style.configure("TEntry", font=('Calibri', 12))

    @log_calls
    def create_window(self):
        self.title("Go Bilingo")
        self.iconbitmap('./assets/icons/icon.ico')

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
        return [profile for profile in os.listdir("./assets/profiles") if os.path.isdir(os.path.join("./assets/profiles", profile))]

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
    def validate_languages(self, spoken_language, learned_language):
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
    def validate_response(self, response):
        answer = self.current_question[self.learned_language]["sentence"]
        question = None

        for question in self.data[self.current_category][self.current_lesson]:
            if question == self.current_question:
                question[self.learned_language]["tries"] += 1
                break

        # If the response is right
        if response.lower().strip() == answer.lower().strip():
            question[self.learned_language]["success_rate"] = ((question[self.learned_language]["success_rate"] * (question[self.learned_language]["tries"] -1)) +1) / question[self.learned_language]["tries"]
            self.save_profile()
            self.display_questions()
        # If the response is wrong
        else:
            question[self.learned_language]["success_rate"] = (question[self.learned_language]["success_rate"] * (question[self.learned_language]["tries"] -1)) / question[self.learned_language]["tries"]
            self.display_answer(response)

    @log_calls
    def clear_window(self):
        for widget in self.window_container.winfo_children():
            widget.destroy()

    @log_calls
    def select_profile(self, profile):
        self.current_profile = profile
        self.load_profile()
        self.load_explainations()
        self.display_languages()
    
    @log_calls
    def select_category(self, category):
        self.current_category = category
        self.display_lessons()

    @log_calls
    def select_lesson(self, lesson):
        self.current_lesson = lesson
        self.display_questions()

    @log_calls
    def display_languages(self):
        languages = self.get_all_languages()

        # Configure page grid
        self.clear_window()
        self.window_container.grid(column=1, row=1)
        self.window_container.columnconfigure(0, weight=1)
        self.window_container.columnconfigure(1, weight=1)
        self.window_container.columnconfigure(3, weight=1)

        row_count = (len(languages) *2) +2

        for index in range(0, row_count):
            self.window_container.rowconfigure(index, weight=1)

        languages_variable = tk.StringVar() 

        for spoken_language_index, spoken_language in enumerate(languages):
            for learned_language_index, learned_language in enumerate(languages):
                if spoken_language == learned_language:
                    continue
                new_radio_button = ttk.Radiobutton(self.window_container, text="", value=[spoken_language, learned_language], variable=languages_variable) 
                new_radio_button.grid(column=0, row=spoken_language_index)

                new_label = tk.Label(self.window_container, text="        ->", image=self.load_image(spoken_language, 50, 50), compound="left")
                new_label.grid(column=1, row=spoken_language_index)
                
                new_label = tk.Label(self.window_container, image=self.load_image(learned_language, 50, 50))
                new_label.grid(column=2, row=spoken_language_index)

        validate_button = ttk.Button(self.window_container, text="Show categories", image=self.load_image('check', 20, 20), compound="left", command=lambda: self.validate_languages(languages_variable.get().split()[0], languages_variable.get().split()[1]))
        validate_button.grid(row=row_count-1, column=1, pady=10, ipadx=2, ipady=2)
    
    @log_calls
    def display_profiles(self, page=1):

        profiles = self.get_all_profiles()
        tiles_by_line = 4
        lines_by_page = 3
        tiles_by_page = tiles_by_line * lines_by_page
        total_pages = ceil(len(profiles) / tiles_by_page)
        current_page = 1 if (page < 1) or (page > total_pages) else page

        # Configure page grid
        self.clear_window()
        self.window_container.grid(column=1, row=1)
        self.window_container.columnconfigure(0, weight=1)
        self.window_container.rowconfigure(0, weight=1)

        # Create a sub-container for tiles
        tiles_container = ttk.Frame(self.window_container)
        tiles_container.grid(column=0, row=0)

        # Initialize variables
        start_index = (current_page - 1) * tiles_by_page
        tile_column, tile_row = 0, 0

        # Iterate through profiles
        for profile in profiles[start_index:]:

            tile_frame = ttk.Frame(tiles_container, width=100)
            tile_frame.grid(column=tile_column, row=tile_row, padx=15, pady=10, ipadx=2, ipady=2)
            tile_frame.columnconfigure(0, weight=1)
            tile_frame.rowconfigure(0, weight=1)
            tile_frame.rowconfigure(1, weight=1)

            new_tile = ttk.Button(tile_frame, image=self.load_image(profile, 50, 50), text=profile.capitalize(), compound="top", command=partial(self.select_profile, profile))
            new_tile.grid(column=0, row=0, ipadx=2, ipady=2)

            # Define the position of the next tile if any
            tile_column += 1
            if tile_column >= tiles_by_line:
                tile_column = 0
                tile_row += 1
                if tile_row >= lines_by_page:
                    break

        if total_pages > 1:
            buttons_container = ttk.Frame(self.window_container)
            buttons_container.grid(column=0, row=1)
            buttons_container.columnconfigure(0, weight=1)
            buttons_container.columnconfigure(1, weight=1)

            previous_button = ttk.Button(buttons_container, state=buttons_state, image=self.load_image('previous', 20, 20), compound="left", text="Previous", command=partial(self.display_profiles, current_page -1))
            previous_button.grid(column=0, row=0, padx=30, pady=20)

            next_button = ttk.Button(buttons_container, state=buttons_state, image=self.load_image('next', 20, 20), compound="right", text="Next", command=partial(self.display_profiles, current_page +1))
            next_button.grid(column=1, row=0, padx=30, pady=20)

    @log_calls
    def display_categories(self, page=1):

        categories = self.get_all_categories()
        tiles_by_line = 4
        lines_by_page = 3
        tiles_by_page = tiles_by_line * lines_by_page
        total_pages = ceil(len(categories) / tiles_by_page)
        current_page = 1 if (page < 1) or (page > total_pages) else page

        # Configure page grid
        self.clear_window()
        self.window_container.grid(column=1, row=1)
        self.window_container.columnconfigure(0, weight=1)
        self.window_container.rowconfigure(0, weight=4)
        self.window_container.rowconfigure(1, weight=1)

        # Create a sub-container for tiles
        tiles_container = ttk.Frame(self.window_container)
        tiles_container.grid(column=0, row=0)

        # Initialize variables
        start_index = (current_page - 1) * tiles_by_page
        tile_column, tile_row = 0, 0

        # Iterate through categories
        for category in categories[start_index:]:

            tile_frame = ttk.Frame(tiles_container, width=100)
            tile_frame.grid(column=tile_column, row=tile_row, padx=15, pady=10, ipadx=2, ipady=2)
            tile_frame.columnconfigure(0, weight=1)
            tile_frame.rowconfigure(0, weight=1)
            tile_frame.rowconfigure(1, weight=1)
            tile_frame.rowconfigure(2, weight=1)

            new_tile = ttk.Button(tile_frame, image=self.load_image(category, 50, 50), text=category.capitalize(), compound="top", command=partial(self.select_category, category))
            new_tile.grid(column=0, row=0, ipadx=2, ipady=2)

            progress_value = ceil(self.get_category_progress(category=category) * 100)

            progress = ttk.Label(tile_frame, text=f'{progress_value}%')
            progress.grid(column=0, row=1)

            progressbar = ttk.Progressbar(tile_frame, orient="horizontal", length=100, mode="determinate", value=progress_value)
            progressbar.grid(column=0, row=2)

            # Define the position of the next tile if any
            tile_column += 1
            if tile_column >= tiles_by_line:
                tile_column = 0
                tile_row += 1
                if tile_row >= lines_by_page:
                    break

        buttons_container = ttk.Frame(self.window_container)
        buttons_container.grid(column=0, row=1)
        buttons_container.columnconfigure(0, weight=1)
        buttons_container.columnconfigure(1, weight=1)
        buttons_container.columnconfigure(2, weight=1)

        leave_button = ttk.Button(buttons_container, image=self.load_image('leave', 20, 20), compound="left", text="Leave", command=self.display_profiles)
        leave_button.grid(column=0, row=0, padx=30, pady=20)

        buttons_state = "enabled" if current_page > 1 else "disabled"

        previous_button = ttk.Button(buttons_container, state=buttons_state, image=self.load_image('previous', 20, 20), compound="left", text="Previous", command=partial(self.display_categories, current_page -1))
        previous_button.grid(column=1, row=0, padx=30, pady=20)

        buttons_state = "enabled" if current_page < total_pages else "disabled"

        next_button = ttk.Button(buttons_container, state=buttons_state, image=self.load_image('next', 20, 20), compound="right", text="Next", command=partial(self.display_categories, current_page +1))
        next_button.grid(column=2, row=0, padx=30, pady=20)

    @log_calls
    def display_lessons(self, page=1):

        lessons = self.get_all_lessons()
        tiles_by_line = 4
        lines_by_page = 3
        tiles_by_page = tiles_by_line * lines_by_page
        total_pages = ceil(len(lessons) / tiles_by_page)
        current_page = 1 if (page < 1) or (page > total_pages) else page

        # Configure page grid
        self.clear_window()
        self.window_container.grid(column=1, row=1)
        self.window_container.columnconfigure(0, weight=1)
        self.window_container.rowconfigure(0, weight=4)
        self.window_container.rowconfigure(1, weight=1)

        # Create a sub-container for tiles
        tiles_container = ttk.Frame(self.window_container)
        tiles_container.grid(column=0, row=0)

        # initialize variables
        start_index = (current_page - 1) * tiles_by_page
        tile_column, tile_row = 0, 0

        # Iterate through lessons
        for lesson in lessons[start_index:]:

            tile_frame = ttk.Frame(tiles_container, width=100)
            tile_frame.grid(column=tile_column, row=tile_row, padx=15, pady=10, ipadx=2, ipady=2)
            tile_frame.columnconfigure(0, weight=1)
            tile_frame.rowconfigure(0, weight=1)
            tile_frame.rowconfigure(1, weight=1)
            tile_frame.rowconfigure(2, weight=1)

            new_tile = ttk.Button(tile_frame, image=self.load_image(lesson, 50, 50), text=lesson.replace('-', ' ').capitalize(), compound="top", command=partial(self.select_lesson, lesson))
            new_tile.grid(column=0, row=0, ipadx=2, ipady=2)

            progress_value = ceil(self.get_lesson_progress(lesson=lesson) * 100)

            progress = ttk.Label(tile_frame, text=f'{progress_value}%')
            progress.grid(column=0, row=1)
            
            progressbar = ttk.Progressbar(tile_frame, orient="horizontal", length=100, mode="determinate", value=progress_value)
            progressbar.grid(column=0, row=2)

            # Define the position of the next tile if any
            tile_column += 1
            if tile_column >= tiles_by_line:
                tile_column = 0
                tile_row += 1
                if tile_row >= lines_by_page:
                    break

        buttons_container = ttk.Frame(self.window_container)
        buttons_container.grid(column=0, row=1)
        buttons_container.columnconfigure(0, weight=1)
        buttons_container.columnconfigure(1, weight=1)
        buttons_container.columnconfigure(2, weight=1)

        leave_button = ttk.Button(buttons_container, image=self.load_image('leave', 20, 20), compound="left", text="Leave", command=self.display_categories)
        leave_button.grid(column=0, row=0, padx=30, pady=20)

        buttons_state = "enabled" if current_page > 1 else "disabled"

        previous_button = ttk.Button(buttons_container, state=buttons_state, image=self.load_image('previous', 20, 20), compound="left", text="Previous", command=partial(self.display_lessons, current_page -1))
        previous_button.grid(column=1, row=0, padx=30, pady=20)

        buttons_state = "enabled" if current_page < total_pages else "disabled"

        next_button = ttk.Button(buttons_container, state=buttons_state, image=self.load_image('next', 20, 20), compound="right", text="Next", command=partial(self.display_lessons, current_page +1))
        next_button.grid(column=2, row=0, padx=30, pady=20)

    @log_calls
    def display_answer(self, response):
        # Configure page grid
        self.clear_window()
        self.window_container.grid(column=1, row=1)
        self.window_container.columnconfigure(0, weight=1)
        self.window_container.columnconfigure(1, weight=1)
        self.window_container.grid_columnconfigure(1, minsize=200)
        self.window_container.rowconfigure(0, weight=1)
        self.window_container.rowconfigure(1, weight=1)
        self.window_container.rowconfigure(2, weight=1)
        self.window_container.rowconfigure(3, weight=1)
        
        response_title_text = "Your response"
        response_title_label = ttk.Label(self.window_container, text=response_title_text, anchor="w", justify=tk.LEFT)
        response_title_label.grid(column=0, row=0, padx=10, pady=10, ipadx=5, ipady=5)
        
        response_text = response.capitalize()
        response_label = ttk.Label(self.window_container, text=response_text, anchor="w", justify=tk.LEFT)
        response_label.grid(column=1, row=0, padx=10, pady=10, ipadx=5, ipady=5)
        
        answer_title_text = "Answer"
        answer_title_label = ttk.Label(self.window_container, text=answer_title_text, anchor="w", justify=tk.LEFT)
        answer_title_label.grid(column=0, row=1, padx=10, pady=10, ipadx=5, ipady=5)
        
        answer_text = self.current_question[self.learned_language]["sentence"].capitalize()
        answer_label = ttk.Label(self.window_container, text=answer_text, anchor="w", justify=tk.LEFT)
        answer_label.grid(column=1, row=1, padx=10, pady=10, ipadx=5, ipady=5)
        
        explaination_title_text = "Explainations"
        explaination_title_label = ttk.Label(self.window_container, text=explaination_title_text, anchor="w", justify=tk.LEFT)
        explaination_title_label.grid(column=0, row=2, padx=10, pady=10, ipadx=5, ipady=5)
        
        explaination_text = []
 
        if self.learned_language in self.explainations.keys():
            for item in self.explainations[self.learned_language]:
                for patern in item["paterns"]:
                    if patern in self.current_question[self.learned_language]["sentence"]:
                        if self.spoken_language in item["explainations"].keys():
                            explaination_text.append(item["explainations"][self.spoken_language])

        explaination_label = ttk.Label(self.window_container, width=50, wraplength=400, text="\n\n".join(explaination_text), anchor="w", justify=tk.LEFT)
        explaination_label.grid(column=1, row=2, padx=10, pady=10, ipadx=5, ipady=5)

        leave_button = ttk.Button(self.window_container, width=8, image=self.load_image('leave', 20, 20), text="Leave", compound="left", command=lambda: self.display_categories())
        leave_button.grid(column=1, row=3, padx=10, pady=10, ipady=5, sticky=tk.W)

        next_button = ttk.Button(self.window_container, width=8, image=self.load_image('next', 20, 20), text="Next", compound="left", command=lambda: self.display_questions())
        next_button.grid(column=1, row=3, padx=10, pady=10, ipady=5, sticky=tk.E)
    
    @log_calls
    def display_questions(self):

        self.choose_random_question()
        question = self.current_question[self.spoken_language]["sentence"]
        hints = None

        if "hints" in self.current_question[self.spoken_language].keys():
            hints = self.current_question[self.spoken_language]["hints"]
        else:
            hints = "x"

        # Configure page grid
        self.clear_window()
        self.window_container.grid(column=1, row=1)
        self.window_container.columnconfigure(0, weight=1)
        self.window_container.columnconfigure(1, weight=3)
        self.window_container.rowconfigure(0, weight=3)
        self.window_container.rowconfigure(1, weight=1)
        self.window_container.rowconfigure(2, weight=1)
        self.window_container.rowconfigure(3, weight=1)
        self.window_container.rowconfigure(4, weight=1)
        self.window_container.rowconfigure(5, weight=3)

        new_label_text = f"Category : {self.current_category.capitalize()}"
        new_label = ttk.Label(self.window_container, text=new_label_text, justify=tk.CENTER)
        new_label.grid(column=0, row=0, padx=10, pady=10, ipadx=5, ipady=5)

        new_label_text = f"Lesson : {self.current_lesson.replace('-', ' ').capitalize()}"
        new_label = ttk.Label(self.window_container, text=new_label_text, justify=tk.CENTER)
        new_label.grid(column=1, row=0, padx=10, pady=10, ipadx=5, ipady=5)

        new_label = ttk.Label(self.window_container, text="Task", justify=tk.LEFT)
        new_label.grid(column=0, row=1, padx=10, pady=10, ipadx=5, ipady=5)

        new_label_text = f"Translate the following sentence from {self.spoken_language.capitalize()} to {self.learned_language.capitalize()}:"
        new_label = ttk.Label(self.window_container, text=new_label_text, justify=tk.LEFT)
        new_label.grid(column=1, row=1, padx=10, pady=10, ipadx=5, ipady=5)

        new_label = ttk.Label(self.window_container, text="Sentence", justify=tk.LEFT)
        new_label.grid(column=0, row=2, padx=10, pady=10, ipadx=5, ipady=5)

        new_label_text = question.capitalize()
        new_label = ttk.Label(self.window_container, text=new_label_text, justify=tk.LEFT)
        new_label.grid(column=1, row=2, padx=10, pady=10, ipadx=5, ipady=5)

        new_label = ttk.Label(self.window_container, text="Context", justify=tk.LEFT)
        new_label.grid(column=0, row=3, padx=10, pady=10, ipadx=5, ipady=5)

        new_label_text = hints.capitalize()
        new_label = ttk.Label(self.window_container, text=new_label_text, justify=tk.LEFT)
        new_label.grid(column=1, row=3, padx=10, pady=10, ipadx=5, ipady=5)

        new_label = ttk.Label(self.window_container, text="Answer", justify=tk.LEFT)
        new_label.grid(column=0, row=4, padx=10, pady=10, ipadx=5, ipady=5)
        
        response_var = tk.StringVar()
        entry = ttk.Entry(self.window_container, width=50, textvariable=response_var)
        entry.focus()
        entry.grid(column=1, row=4, padx=10, pady=10, ipadx=5, ipady=5)

        leave_button = ttk.Button(self.window_container, width=8, image=self.load_image('leave', 20, 20), text="Leave", compound="left", command=lambda: self.display_lessons())
        leave_button.grid(column=1, row=5, padx=10, pady=10, ipadx=5, ipady=5, sticky=tk.W)

        check_button = ttk.Button(self.window_container, width=8, image=self.load_image('check', 20, 20), text="Validate", compound="left", command=lambda: self.validate_response(response_var.get()))
        check_button.grid(column=1, row=5, padx=10, pady=10, ipadx=5, ipady=5, sticky=tk.E)

if __name__ == "__main__":
    app = Bilingual()
    app.mainloop()