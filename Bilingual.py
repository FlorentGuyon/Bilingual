import tkinter as tk
import json
import random
import os

from math import ceil
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
from functools import partial
from datetime import datetime
from copy import deepcopy


class Bilingual(tk.Tk):

    def __init__(self):
        super().__init__()
        
        self.icons = {}
        self.spoken_language = "english"
        self.learned_language = "french"
        self.current_category = None
        self.current_file = None
        self.current_question = None
        self.load_data()
        self.configure_style()
        self.create_window()
        self.display_languages()

    def log_calls(method):
        def wrapper(*args, **kwargs):
            print(method.__name__)
            return method(*args, **kwargs)
        return wrapper

    @log_calls
    def save_data(self):
        for folder_name in self.data.keys():
            for file_name in self.data[folder_name].keys():
                file_path = f"./assets/categories/{folder_name}/{file_name}.json"
                with open(file_path, 'w', encoding='utf-8') as json_file:
                    try:
                        json_data = json.dumps(self.data[folder_name][file_name], indent=4)
                        json_file.write(json_data)
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON in {file_path}")

    @log_calls
    def load_data(self):
        self.data = {}  # Dictionary to store the result

        for subdir, _, files in os.walk("./assets/categories"):
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
        self.title("Bilingual...")
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
        # The longer the user last without failing to answer the question correctly, 
        # the less chances it gets to answer to the question again.
        # But it won't get the same questions within a day, if it answered them correctly.
        memory_steps = []
        memory_steps.append((60 * 60 * 24 *  1, 0.0))    # <  1 day  :   0%
        memory_steps.append((60 * 60 * 24 *  3, 1.0))    # <  3 days : 100%
        memory_steps.append((60 * 60 * 24 *  7, 0.8))    # <  7 days :  80%
        memory_steps.append((60 * 60 * 24 * 15, 0.6))    # < 15 days :  60%
        memory_steps.append((60 * 60 * 24 * 30, 0.4))    # < 30 days :  40%
        memory_steps.append((60 * 60 * 24 * 60, 0.2))    # < 60 days :  20%
        memory_steps.append((60 * 60 * 24 * 90, 0.1))    # < 90 days :  10%

        # Get the dates to compare
        last_success = question[self.learned_language]["last_success"]
        now = int(datetime.timestamp(datetime.now()))
        
        # If the question has never been successfuly answered
        if last_success is None:
            return False

        for delay, chances in memory_steps:
            if now < (last_success + delay):
                if random.random() < chances:
                    return False
                else:
                    return True

        return True

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
    def choose_random_question_by_category(self):
        date_copy = deepcopy(self.data)
        random.shuffle(date_copy[self.current_category])
        for file_name in date_copy[self.current_category]:
            random.shuffle(date_copy[self.current_category][file_name])
            for question in date_copy[self.current_category][file_name]:
                if not self.is_remembered(question):
                    self.current_file = file_name
                    self.current_question = question

    @log_calls
    def validate_languages(self, spoken_language, learned_language):
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

        if response.lower().strip() == answer.lower().strip():
            for question in self.data[self.current_category][self.current_file]:
                if question == self.current_question:
                    question[self.learned_language]["last_success"] = int(datetime.timestamp(datetime.now()))
            self.save_data()
            self.display_questions()
        else:
            self.display_answer(response)

    @log_calls
    def clear_window(self):
        for widget in self.window_container.winfo_children():
            widget.destroy()

    @log_calls
    def display_languages(self):
        languages = self.get_all_languages()

        # Configure page grid
        self.clear_window()
        self.window_container.grid(column=1, row=1)
        self.window_container.columnconfigure(0, weight=1)

        row_count = (len(languages) *2) +3

        for index in range(0, row_count):
            self.window_container.rowconfigure(index, weight=1)

        spoken_language = tk.StringVar()
        learned_language = tk.StringVar()

        spoken_language_label = ttk.Label(self.window_container, text="Language you speak:")
        spoken_language_label.grid(column=0, row=0, pady=10)

        for index, language in enumerate(languages):
            radio_button = ttk.Radiobutton(self.window_container, text=language.capitalize(), value=language, variable=spoken_language)
            radio_button.grid(column=0, row=index +1)

        learned_language_label = ttk.Label(self.window_container, text="Language you learn:")
        learned_language_label.grid(column=0, row=len(languages) +1, pady=10)

        for index, language in enumerate(languages):
            radio_button = ttk.Radiobutton(self.window_container, text=language.capitalize(), value=language, variable=learned_language)
            radio_button.grid(column=0, row=index + len(languages) +2)

        validate_button = ttk.Button(self.window_container, text="Show categories", image=self.load_image('check', 20, 20), compound="left", command=lambda: self.validate_languages(spoken_language.get(), learned_language.get()))
        validate_button.grid(row=row_count-1, column=0, pady=10, ipadx=2, ipady=2)

    @log_calls
    def select_category(self, category):
        self.current_category = category
        self.display_questions()

    @log_calls
    def display_categories(self, page=1):

        tiles_by_line = 4
        lines_by_page = 3
        tiles_by_page = tiles_by_line * lines_by_page
        total_pages = ceil(len(self.get_all_categories()) / tiles_by_page)
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

        # Get category titles and initialize variables
        categories = self.get_all_categories()
        start_index = (current_page - 1) * tiles_by_page
        tile_column, tile_row = 0, 0

        # Iterate through categories
        for category in categories[start_index:]:
            new_tile = ttk.Button(tiles_container, image=self.load_image(category, 50, 50), text=category.capitalize(), compound="top", command=partial(self.select_category, category))
            new_tile.grid(column=tile_column, row=tile_row, padx=15, pady=10, ipadx=2, ipady=2)

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

            previous_button = ttk.Button(buttons_container, state=buttons_state, image=self.load_image('previous', 20, 20), compound="left", text="Previous", command=partial(self.display_categories, current_page -1))
            previous_button.grid(column=0, row=0, padx=30, pady=20)

            next_button = ttk.Button(buttons_container, state=buttons_state, image=self.load_image('next', 20, 20), compound="right", text="Next", command=partial(self.display_categories, current_page +1))
            next_button.grid(column=1, row=0, padx=30, pady=20)

    @log_calls
    def display_answer(self, response):
        # Configure page grid
        self.clear_window()
        self.window_container.grid(column=1, row=1)
        self.window_container.columnconfigure(0, weight=1)
        self.window_container.grid_columnconfigure(0, minsize=200)
        self.window_container.rowconfigure(0, weight=1)
        self.window_container.rowconfigure(1, weight=1)
        self.window_container.rowconfigure(2, weight=1)
        self.window_container.rowconfigure(3, weight=1)
        
        response_text = f"Your response: {response.capitalize()}"
        response_label = ttk.Label(self.window_container, text=response_text, justify=tk.CENTER)
        response_label.grid(column=0, row=0, pady=10, ipadx=5)
        
        answer = self.current_question[self.learned_language]["sentence"]
        answer_text = f"Answer: {answer.capitalize()}"
        answer_label = ttk.Label(self.window_container, text=answer_text, justify=tk.CENTER)
        answer_label.grid(column=0, row=1, pady=10, ipadx=5)
        
        if "explaination" in self.current_question[self.learned_language].keys():
            explaination = self.current_question[self.learned_language]["explaination"]
            explaination_text = f"Explaination: {explaination.capitalize()}"
            explaination_label = ttk.Label(self.window_container, width=50, wraplength=400, text=explaination_text, justify=tk.CENTER)
            explaination_label.grid(column=0, row=2, pady=10, ipadx=5)

        leave_button = ttk.Button(self.window_container, width=8, image=self.load_image('leave', 20, 20), text="Leave", compound="left", command=lambda: self.display_categories())
        leave_button.grid(column=0, row=3, padx=2, pady=10, sticky=tk.W)

        next_button = ttk.Button(self.window_container, width=8, image=self.load_image('next', 20, 20), text="Next", compound="left", command=lambda: self.display_questions())
        next_button.grid(column=0, row=3, padx=2, pady=10, sticky=tk.E)
    
    @log_calls
    def display_questions(self):

        self.choose_random_question_by_category()
        question = self.current_question[self.spoken_language]["sentence"]
        hints = None

        if "hints" in self.current_question[self.spoken_language].keys():
            hints = self.current_question[self.spoken_language]["hints"]

        # Configure page grid
        self.clear_window()
        self.window_container.grid(column=1, row=1)
        self.window_container.columnconfigure(0, weight=1)
        for index in range(0, 4):
            self.window_container.rowconfigure(index, weight=1)

        question_text = f"Translate from {self.spoken_language.capitalize()} to {self.learned_language.capitalize()}:\n\n{question.capitalize()}"
        question_label = ttk.Label(self.window_container, text=question_text, justify=tk.CENTER)
        question_label.grid(column=0, row=0, pady=10, ipadx=5)

        if hints:
            hints_text = f"Hints: {hints.capitalize()}"
            hints_label = ttk.Label(self.window_container, text=hints_text, justify=tk.CENTER)
            hints_label.grid(column=0, row=1, pady=10, ipadx=5)
        
        response_var = tk.StringVar()
        entry = ttk.Entry(self.window_container, width=50, textvariable=response_var)
        entry.focus()
        entry.grid(column=0, row=2, pady=10, ipadx=5)

        leave_button = ttk.Button(self.window_container, width=8, image=self.load_image('leave', 20, 20), text="Leave", compound="left", command=lambda: self.display_categories())
        leave_button.grid(column=0, row=3, pady=10, sticky=tk.W)

        check_button = ttk.Button(self.window_container, width=8, image=self.load_image('check', 20, 20), text="Validate", compound="left", command=lambda: self.validate_response(response_var.get()))
        check_button.grid(column=0, row=3, pady=10, sticky=tk.E)

if __name__ == "__main__":
    app = Bilingual()
    app.mainloop()