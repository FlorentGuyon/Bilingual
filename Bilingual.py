import tkinter as tk
import json
import random
import os

from math import ceil
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
from functools import partial
from copy import deepcopy
from gtts import gTTS
from playsound import playsound
from time import sleep
from diff_match_patch import diff_match_patch
from threading import Thread

##################################################################### CONSTANTS

# ENVIRONMENT
DEBUG_MODE = True
CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
FILES_ENCODING = "utf8"

# COLORS
COLOR_WHITE = "#FFFFFF"
COLOR_LIGHT_GREY = "#eae5e5"
COLOR_LIGHT_PINK = "#edcbc5"
COLOR_MID_PINK = "#e1a99f"
COLOR_DARK_PINK = "#c39792"

# EVENTS
EVENT_LEFT_CLICK = "<Button-1>"
EVENT_MIDDLE_CLICK = "<Button-2>"
EVENT_RIGHT_CLICK = "<Button-3>"
EVENT_LEFT_RELEASE = "<ButtonRelease-1>"
EVENT_MIDDLE_RELEASE = "<ButtonRelease-2>"
EVENT_RIGHT_RELEASE = "<ButtonRelease-3>"
EVENT_IN_WIDGET = "<Motion>"
EVENT_ENTER_WIDGET = "<Enter>"
EVENT_LEAVE_WIDGET = "<Leave>"
EVENT_KEY_PRESS = "<KeyPress>"
EVENT_KEY_RELEASE = "<KeyRelease>"
EVENT_FOCUS_WIDGET = "<FocusIn>"
EVENT_UNFOCUS_WIDGET = "<FocusOut>"
EVENT_MOVE_RESIZE_WIDGET = "<Configure>"
EVENT_SHOW_WIDGET = "<Map>"
EVENT_HIDE_WIDGET = "<Unmap>"
EVENT_FADE_WIDGET = "<Visibility>"
EVENT_CONTROL_KEY = "<Control-KeyPress>"
EVENT_SHIFT_KEY = "<Shift-KeyPress>"

# SOUNDS
SOUND_PAGE_FORWARDS = "page.wav"
SOUND_PAGE_BACKWARDS = "reverse-page.mp3"
SOUND_POP = "pop.wav"
SOUND_WRITING = "write.wav"
SOUND_CORRECT = "correct.wav"
SOUND_INCORRECT = "incorrect.wav"
SOUND_NEW_STAR = "new-star.wav"

# PATHS
PATH_CATEGORIES = os.path.join(CURRENT_DIRECTORY, "assets", "categories")
PATH_ICONS = os.path.join(CURRENT_DIRECTORY, "assets", "icons")
PATH_EXPLAINATIONS = os.path.join(CURRENT_DIRECTORY, "assets", "explainations")
PATH_PROFILES = os.path.join(CURRENT_DIRECTORY, "assets", "profiles")
PATH_SOUNDS = os.path.join(CURRENT_DIRECTORY, "assets", "sounds")
PATH_TEMPORARY_FILES = os.path.join(CURRENT_DIRECTORY, "assets", "temp")

# ICONS
DEFAULT_ICON = "rabbit-female-pink"

# VALUES
VALUE_STARS = [0.6, 0.8, 0.9] # 60% of success to earn the 1st star, then 80% and 90%

###################################################################### WRAPPERS

def log_calls(method):
    def wrapper(*args, **kwargs):
        if DEBUG_MODE:
            print(f'{method.__name__}({str(args[1:])}, {str(kwargs)})')
        return method(*args, **kwargs)
    return wrapper

####################################################################### CLASSES

class Bilingual(tk.Tk):

    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self.debug_mode = True
        self.icons = {}
        self.categories = None
        self.explainations = None
        self.spoken_language = None
        self.learned_language = None
        self.current_profile = None
        self.current_category = None
        self.current_lesson = None
        self.current_question_id = None
        self.current_question = None
        self.load_categories()
        self.set_styles()
        self.create_window()
        self.display_profiles()

    ################################################################### READERS

    # IMAGES
    @log_calls
    def load_image(self, name, width, height):
        if name in self.icons.keys():
            if width in self.icons[name].keys():
                if height in self.icons[name][width].keys():
                    return self.icons[name][width][height]

        image_name = name + ".png"
        image_path = os.path.join(PATH_ICONS, image_name)
        resized_image = self.resize_image(image_path, width, height)
        
        if not resized_image:
            return None
        
        self.icons[name] = {}
        self.icons[name][width] = {}
        self.icons[name][width][height] = resized_image
        return resized_image

    @log_calls
    def read_from_file(self, file_path, critical=True):
        with open(file_path, 'r', encoding=FILES_ENCODING) as file:
            try:
                return file.read()
            except json.JSONDecodeError:
                print(f"Error while reading at {file_path}.")
                if critical:
                    exit()   

    # PROFILES
    @log_calls
    def load_profile(self):
        profile_path = os.path.join(PATH_PROFILES, self.current_profile + ".json")
        profile_content = self.read_from_file(profile_path)
        profile = json.loads(profile_content)

        self.set_window_icon(profile["icon"])

        for category in profile["categories"].keys():
            for lesson in profile["categories"][category].keys():
                for question in profile["categories"][category][lesson].keys():
                    for language in profile["categories"][category][lesson][question].keys():

                        success_rate = profile["categories"][category][lesson][question][language]["success_rate"]
                        self.set_question_success(success_rate, category, lesson, question, language)
                        
                        tries = profile["categories"][category][lesson][question][language]["tries"]
                        self.set_question_tries(tries, category, lesson, question, language)

    # CATEGORIES
    @log_calls
    def load_categories(self):
        self.categories = {}  # Dictionary to store the result
        json_files = self.get_files(PATH_CATEGORIES, "json")

        for file_path in json_files:
            folder_name = os.path.basename(os.path.dirname(file_path))
            file_name = os.path.basename(file_path).replace(".json", "")
            json_content = json.loads(self.read_from_file(file_path))

            if folder_name not in self.categories.keys():
                self.categories[folder_name] = {}

            self.categories[folder_name][file_name] = json_content

    # QUESTIONS
    @log_calls
    def load_explainations(self):
        self.explainations = {}  # Dictionary to store the result

        for subdir, _, files in os.walk(PATH_EXPLAINATIONS):
            json_files = [f for f in files if f.endswith('.json')]

            for json_file in json_files:
                file_name = os.path.splitext(json_file)[0]  # Remove the .json extension
                file_path = os.path.join(subdir, json_file)

                with open(file_path, 'r', encoding=FILES_ENCODING) as json_file:
                    try:
                        file_content = json.load(json_file)
                        self.explainations[file_name] = file_content
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON in {file_path}")
                        exit()                

    ################################################################### WRITERS
    
    @log_calls
    def write_in_file(self, file_path, content):
        with open(file_path, 'w', encoding=FILES_ENCODING) as file:
            try:
                file.write(content)
            except json.JSONDecodeError:
                print(f"Error while writing {content[:15]}... in {file_path}.")   
    
    # TEMP
    @log_calls
    def remove_temp_files(self):
        # Check if the folder exists
        if os.path.exists(PATH_TEMPORARY_FILES) and os.path.isdir(PATH_TEMPORARY_FILES):
            # List all files and subdirectories in the folder
            for filename in os.listdir(PATH_TEMPORARY_FILES):
                file_path = os.path.join(PATH_TEMPORARY_FILES, filename)

                # Check if it's a file (not a subdirectory) and delete it
                if os.path.isfile(file_path):
                    os.remove(file_path)

    # PROFILES
    @log_calls
    def save_profile(self):
        profile_path = os.path.join(PATH_PROFILES, self.current_profile + ".json")
        profile_content = self.read_from_file(profile_path)
        profile = json.loads(profile_content)

        for category in self.categories.keys():
            for lesson in self.categories[category].keys():
                for question_id in self.categories[category][lesson]["questions"].keys():
                    for data in ["success_rate", "tries"]:
                        value = self.categories[category][lesson]["questions"][question_id][self.learned_language][data]
                        profile["categories"][category][lesson][question_id][self.learned_language][data] = value

                        print(category, lesson, question_id, data, value)

        file_content = json.dumps(profile, indent=4)
        self.write_in_file(profile_path, file_content)   

    ################################################################### GETTERS
    
    # FILES
    @log_calls
    def get_files(self, parent, extension=None):
        files_list = []
        for subdir, _, files in os.walk(parent):
            if extension:
                files_list += [os.path.join(subdir, f) for f in files if f.endswith(extension)]
            else:
                files_list += [os.path.join(subdir, f) for f in files]
        return files_list

    # PROFILES
    @log_calls
    def get_all_profiles(self):
        profiles = self.get_files(PATH_PROFILES, "json")
        return [os.path.basename(profile).replace(".json", "") for profile in profiles]

    # LANGUAGES
    @log_calls
    def get_all_languages(self):
        languages = []
        for category in self.categories.keys():
            for lesson in self.categories[category].keys():
                for question in self.categories[category][lesson]["questions"].values():
                    for language in question.keys():
                        if language not in languages:
                            languages.append(language)
        return languages

    # STARS
    @log_calls
    def get_stars(self, category=None, lesson=None):
        if (category) and (not lesson):
            success = self.get_category_success(category)
        else:
            success = self.get_lesson_success(category, lesson)
        return len([i for i, value in enumerate(VALUE_STARS) if value <= success])

    # CATEGORIES
    @log_calls
    def get_all_categories(self):
        return list(self.categories.keys())

    @log_calls
    def get_category_success(self, category=None):
        category = category if category else self.current_category
        success_rates = [self.get_lesson_success(category, lesson) for lesson in self.get_all_lessons(category)]
        success_rate = sum(success_rates) / len(success_rates)
        return success_rate

    @log_calls
    def get_category_overview(self, category=None):
        category = category if category else self.current_category
        overviews = [self.get_lesson_overview(category, lesson) for lesson in self.get_all_lessons(category)]
        overview = sum(overviews) / len(overviews)
        return overview

    # LESSONS
    @log_calls
    def get_all_lessons(self, category=None):
        if category is None:
            category = self.current_category
        return list(self.categories[category].keys())

    @log_calls
    def get_lesson_success(self, category=None, lesson=None):
        category = category if category else self.current_category
        lesson = lesson if lesson else self.current_lesson
        lesson_overview = self.get_lesson_overview(category, lesson)
        success_rates = [question[self.learned_language]["success_rate"] for question in self.categories[category][lesson]["questions"].values()]
        success_rate = sum(success_rates) / len(success_rates) * lesson_overview
        return success_rate

    @log_calls
    def get_lesson_overview(self, category=None, lesson=None):
        category = category if category else self.current_category
        lesson = lesson if lesson else self.current_lesson
        views = 0
        for question in self.categories[category][lesson]["questions"].values():
            if question[self.learned_language]["tries"] > 0:
                views += 1
        questions = len(self.categories[category][lesson]["questions"].values()) 
        overview = views / questions
        return overview

    # QUESTIONS
    @log_calls
    def get_question_data(self, data, category=None, lesson=None, question_id=None, language=None):
        category = category if category else self.current_category
        lesson = lesson if lesson else self.current_lesson
        question_id = question_id if question_id else self.current_question_id
        language = language if language else self.learned_language
        return self.categories[category][lesson]["questions"][question_id][language][data]

    @log_calls
    def get_question_answer(self, question=None):
        question = question if question else self.current_question
        return question[self.learned_language]["sentence"]
    
    @log_calls
    def get_question_explainations(self, question=None):
        question = question if question else self.current_question
        explaination_text = []
 
        if self.learned_language in self.explainations.keys():
            for item in self.explainations[self.learned_language]:
                for patern in item["paterns"]:
                    if patern in self.current_question[self.learned_language]["sentence"]:
                        if self.spoken_language in item["explainations"].keys():
                            explaination_text.append(item["explainations"][self.spoken_language])

        return explaination_text

    ################################################################### SETTERS

    # WINDOW
    @log_calls
    def set_window_icon(self, icon=DEFAULT_ICON):
        file_name = icon + ".ico"
        file_path = os.path.join(PATH_ICONS, file_name)
        self.iconbitmap(file_path)

    @log_calls
    def set_window_title(self, title):
        self.title(title)

    # QUESTIONS
    @log_calls
    def set_question_success(self, success, category=None, lesson=None, question_id=None, language=None):
        category = category if category else self.current_category
        lesson = lesson if lesson else self.current_lesson
        question_id = question_id if question_id else self.current_question_id
        language = language if language else self.learned_language
        self.categories[category][lesson]["questions"][question_id][language]["success_rate"] = success
    
    @log_calls
    def set_question_tries(self, tries, category=None, lesson=None, question_id=None, language=None):
        category = category if category else self.current_category
        lesson = lesson if lesson else self.current_lesson
        question_id = question_id if question_id else self.current_question_id
        language = language if language else self.learned_language
        self.categories[category][lesson]["questions"][question_id][language]["tries"] = tries

    ################################################################ VALIDATORS

    # LANGUAGES
    @log_calls
    def validate_languages(self, spoken_language, learned_language, event=None):
        if (spoken_language == "") or (learned_language == ""):
            self.display_languages()
        elif spoken_language == learned_language:
            self.display_languages()
        else:
            self.spoken_language = spoken_language
            self.learned_language = learned_language
            self.display_categories()

    # QUESTIONS
    @log_calls
    def validate_response(self, response, event=None):
        response = response.replace('.', '')
        answer = self.get_question_answer()
        self.increase_question_tries()

        # If the response is right
        if response.lower().strip() == answer.lower().strip():
            self.playsound(SOUND_CORRECT)
            self.increase_question_success()
            self.save_profile()
            self.display_questions()

        # If the response is wrong
        else:
            self.playsound(SOUND_INCORRECT)
            self.decrease_question_success()
            self.save_profile()
            self.display_answer(response)

    ################################################################# LISTENERS

    # WINDOW
    @log_calls
    def close_app(self, event=None):
        self.remove_temp_files()
        self.destroy()

    # WIDGET
    @log_calls
    def tell_text(self, text, language, event=None):
        file_path = os.path.join(PATH_TEMPORARY_FILES, "tts.mp3")
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

        if isinstance(text, tk.StringVar):
            text = text.get()

        tts = gTTS(text=text, lang=languages[language]["language_code"], tld=languages[language]["accent_code"])

        if os.path.isfile(file_path):
            os.remove(file_path)

        tts.save(file_path)

        while not os.path.isfile(file_path):
            sleep(0.1)

        self.playsound(file_path, False)

    @log_calls
    def click_button(self, action, args=[], sound=SOUND_PAGE_FORWARDS, event=None):
        if isinstance(args, tk.Event):
            event = args
            args = []

        elif isinstance(sound, tk.Event):
            event = sound
            sound = SOUND_PAGE_FORWARDS

        if sound:
            self.playsound(sound)

        if type(args) != list:
            args = [args]

        action(*args)        
    
    @log_calls
    def enter_widget(self, widget, sound=None, event=None):
        if sound:
            self.playsound(SOUND_POP)
        widget.configure(style=f'Active.{widget["style"]}')
        for child in widget.winfo_children():
            self.enter_widget(child)

    @log_calls
    def leave_widget(self, widget, event=None):
        widget.configure(style=widget["style"].replace("Active.", ""))
        for child in widget.winfo_children():
            self.leave_widget(child)
    
    ################################################################## BUILDERS

    # WINDOW
    @log_calls
    def create_window(self):
        self.set_window_icon()
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

    # FRAMES
    @log_calls
    def create_frame(self, parent, text):
        new_frame = ttk.Frame(parent, style="CustomDarkFrame.TFrame")
        new_frame.pack(expand=True, fill=tk.X, pady=10)

        new_label = ttk.Label(new_frame, text=text, style="Default.TLabel")
        new_label.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)
    
    @log_calls
    def create_stat_frame(self, parent, text, stat, alone_in_row=True):
        side = tk.TOP if alone_in_row else tk.LEFT
        frame = ttk.Frame(parent, style="CustomDarkFrame.TFrame")
        frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=10, side=side)

        stat_label = ttk.Label(frame, text=stat, style="Big.Default.TLabel", anchor="center")
        stat_label.pack(expand=True, fill=tk.Y, padx=5, pady=5)

        text_label = ttk.Label(frame, text=text, wraplength=650, style="Small.Default.TLabel", anchor="center")
        text_label.pack(expand=True, fill=tk.X, padx=5, pady=5)

    @log_calls
    def create_scrollable_frame(self, parent, text):
        frame = ttk.Frame(parent, style="CustomDarkFrame.TFrame")
        frame.pack(pady=10)

        scrolledtext = ScrolledText(frame, width=45, height=10, background=COLOR_DARK_PINK, foreground=COLOR_WHITE, font=('Calibri', 12), relief=tk.FLAT)
        scrolledtext.pack(fill=tk.BOTH, expand=True)
        scrolledtext.insert(tk.INSERT, text)
        scrolledtext.configure(state="disabled")
        scrolledtext.vbar.configure(width=0)

    @log_calls
    def create_speakable_frame(self, parent, text, language, animate=True):
        new_frame = ttk.Frame(parent, style="CustomDarkFrame.TFrame")
        new_frame.pack(expand=True, fill=tk.X, pady=10)

        new_label = ttk.Label(new_frame, text=text, style="Default.TLabel")
        new_label.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)

        if language in ["english", "french"]:
            tts_frame = ttk.Frame(new_frame, style="CustomDarkFrame.TFrame")
            tts_frame.pack(side=tk.LEFT)

            tts = ttk.Label(tts_frame, image=self.load_image("speak", 25, 25), style="Default.TLabel")
            tts.pack(padx=10, pady=5)

            self.bind_widget(tts, partial(self.click_button, self.tell_text, [text, language], None))

            if animate:
                self.bind_widget(tts_frame, partial(self.enter_widget, tts_frame), EVENT_ENTER_WIDGET, recursive=False)
                self.bind_widget(tts_frame, partial(self.leave_widget, tts_frame), EVENT_LEAVE_WIDGET, recursive=False)

    @log_calls
    def create_image_frame(self, parent, image, text, action, arguments, sound=None, animate=True):
        new_frame = ttk.Frame(parent, style="CustomDarkFrame.TFrame")
        new_frame.pack(pady=5, expand=True, fill=tk.X)

        title_frame = ttk.Frame(new_frame, style="CustomDarkFrame.TFrame")
        title_frame.pack(expand=True, fill=tk.BOTH)

        title_frame_picture = ttk.Label(title_frame, image=self.load_image(image, 35, 35), style="Default.TLabel")
        title_frame_picture.pack(padx=15, pady=5, side=tk.LEFT)

        title_frame_text_text = text.replace("-", " ").title()
        title_frame_text = ttk.Label(title_frame, text=title_frame_text_text, style="Default.TLabel")
        title_frame_text.pack(ipadx=15, ipady=5, side=tk.LEFT, expand=True, fill=tk.X)

        self.bind_widget(new_frame, partial(self.click_button, action, arguments))

        if animate:
            self.bind_widget(new_frame, partial(self.enter_widget, new_frame), EVENT_ENTER_WIDGET, recursive=False)
            self.bind_widget(new_frame, partial(self.leave_widget, new_frame), EVENT_LEAVE_WIDGET, recursive=False)

    @log_calls
    def create_progress_frame(self, parent, image, text, progress, stars, action, arguments, sound=None, animate=True):
        new_frame = ttk.Frame(parent, style="CustomDarkFrame.TFrame")
        new_frame.pack(pady=5, expand=True, fill=tk.X)

        title_frame = ttk.Frame(new_frame, style="CustomDarkFrame.TFrame")
        title_frame.pack(expand=True, fill=tk.BOTH)

        title_frame_picture = ttk.Label(title_frame, image=self.load_image(image, 35, 35), style="Default.TLabel")
        title_frame_picture.pack(padx=15, pady=5, side=tk.LEFT)

        title_frame_text_text = text.replace("-", " ").title()
        title_frame_text = ttk.Label(title_frame, text=title_frame_text_text, style="Default.TLabel")
        title_frame_text.pack(ipadx=15, ipady=5, side=tk.LEFT, expand=True, fill=tk.X)

        stars_image = ttk.Label(title_frame, image=self.load_image(f'{stars}-star', 53, 25), style="Default.TLabel")
        stars_image.pack(padx=15, pady=5, side=tk.LEFT)

        progressbar_frame = ttk.Frame(new_frame, style="CustomDarkFrame.TFrame")
        progressbar_frame.pack(expand=True, fill=tk.X)

        self.update()

        progressbar_frame_left_width = new_frame.winfo_width() * progress
        progressbar_frame_left = ttk.Frame(progressbar_frame, height=5, width=progressbar_frame_left_width, style="CustomMidFrame.TFrame")
        progressbar_frame_left.pack(side=tk.LEFT)
        
        progressbar_frame_right = ttk.Frame(progressbar_frame, height=5, style="CustomLightFrame.TFrame")
        progressbar_frame_right.pack(expand=True, fill=tk.X, side=tk.LEFT)

        self.bind_widget(new_frame, partial(self.click_button, action, arguments))

        if animate:
            self.bind_widget(new_frame, partial(self.enter_widget, new_frame), EVENT_ENTER_WIDGET, recursive=False)
            self.bind_widget(new_frame, partial(self.leave_widget, new_frame), EVENT_LEAVE_WIDGET, recursive=False)

    # BUTTONS
    @log_calls
    def create_button(self, parent, image, text, action, arguments=[], sound=None, image_first=True, alone_in_row=True, animate=True):
        side = tk.TOP if alone_in_row else tk.LEFT
        new_frame = ttk.Frame(parent, style="CustomDarkFrame.TFrame")
        new_frame.pack(padx=10, pady=10, expand=True, fill=tk.X, side=side)

        side = tk.LEFT if image_first else tk.RIGHT
        
        anchor = tk.E if image_first else tk.W
        new_image = ttk.Label(new_frame, image=self.load_image(image, 25, 25), anchor=anchor, style="Default.TLabel")
        new_image.pack(side=side, padx=5, expand=True, fill=tk.BOTH)

        anchor = tk.W if image_first else tk.E
        new_label = ttk.Label(new_frame, text=text, anchor=anchor, style="Default.TLabel")
        new_label.pack(side=side, padx=5, expand=True, fill=tk.BOTH)
        
        self.bind_widget(new_frame, partial(self.click_button, action, arguments, sound))

        if animate:
            self.bind_widget(new_frame, partial(self.enter_widget, new_frame), EVENT_ENTER_WIDGET, recursive=False)
            self.bind_widget(new_frame, partial(self.leave_widget, new_frame), EVENT_LEAVE_WIDGET, recursive=False)

    # ENTRIES
    @log_calls
    def create_speakable_entry(self, parent, language, animate=True):
        new_frame = ttk.Frame(parent, style="CustomDarkFrame.TFrame")
        new_frame.pack(expand=True, fill=tk.X, pady=10)
        
        new_Stringvar = tk.StringVar()
        # The Entry widget from ttk does not support the "background" argument
        new_entry = tk.Entry(new_frame, width=45, textvariable=new_Stringvar, background=COLOR_DARK_PINK, foreground=COLOR_WHITE, relief="flat", insertbackground=COLOR_WHITE, font=('Calibri', 12))
        new_entry.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)
        new_entry.focus()

        if language in ["english", "french"]:
            tts_frame = ttk.Frame(new_frame, style="CustomDarkFrame.TFrame")
            tts_frame.pack(side=tk.LEFT)

            tts = ttk.Label(tts_frame, image=self.load_image("speak", 25, 25), style="Default.TLabel")
            tts.pack(padx=10, pady=5)

            self.bind_widget(tts, partial(self.click_button, self.tell_text, [new_Stringvar, language], None))

            if animate:
                self.bind_widget(tts_frame, partial(self.enter_widget, tts_frame), EVENT_ENTER_WIDGET, recursive=False)
                self.bind_widget(tts_frame, partial(self.leave_widget, tts_frame), EVENT_LEAVE_WIDGET, recursive=False)

        return new_frame, new_Stringvar

    ################################################################ DISPLAYERS
   
    # PROFILES
    @log_calls
    def display_profiles(self, page=1, event=None):
        profiles = self.get_all_profiles()
        item_by_page = 5
        total_pages = ceil(len(profiles) / item_by_page)
        current_page = 1 if (page < 1) or (page > total_pages) else page

        # Configure page grid
        self.clear_window()
        self.set_window_title("Pick your profile !")
        self.window_container.grid(column=1, row=1)

        # Initialize variables
        start_index = (current_page - 1) * item_by_page

        # Iterate through profiles
        for profile in profiles[start_index:]:
            self.create_image_frame(self.window_container, profile, profile, self.select_profile, profile)

        # QUIT BUTTON
        self.create_button(self.window_container, "arrow_left", "Quit", self.close_app)

    # LANGUAGES
    @log_calls
    def display_languages(self, page=1, event=None):
        languages = self.get_all_languages()

        # Configure page grid
        self.clear_window()
        self.set_window_title("Pick a language to learn !")
        self.window_container.grid(column=1, row=1)

        for spoken_language_index, spoken_language in enumerate(languages):
            for learned_language_index, learned_language in enumerate(languages):
                if spoken_language == learned_language:
                    continue

                frame = ttk.Frame(self.window_container, style="CustomDarkFrame.TFrame")
                frame.pack(pady=5, expand=True, fill=tk.X)

                spoken_language_picture = ttk.Label(frame, image=self.load_image(spoken_language, 35, 35), style="Default.TLabel", anchor=tk.CENTER)
                spoken_language_picture.pack(padx=10, pady=5, side=tk.LEFT, expand=True, fill=tk.X)

                arrow_picture = ttk.Label(frame, image=self.load_image("next", 35, 35), style="Default.TLabel", anchor=tk.CENTER)
                arrow_picture.pack(padx=10, pady=5, side=tk.LEFT)

                learned_language_picture = ttk.Label(frame, image=self.load_image(learned_language, 35, 35), style="Default.TLabel", anchor=tk.CENTER)
                learned_language_picture.pack(padx=10, pady=5, side=tk.LEFT, expand=True, fill=tk.X)

                self.bind_widget(frame, partial(self.click_button, self.validate_languages, [spoken_language, learned_language]))
                self.bind_widget(frame, partial(self.enter_widget, frame), EVENT_ENTER_WIDGET, recursive=False)
                self.bind_widget(frame, partial(self.leave_widget, frame), EVENT_LEAVE_WIDGET, recursive=False)

        # RETURN BUTTON
        self.create_button(self.window_container, "arrow_left", "Profiles", self.display_profiles, arguments=1, sound=SOUND_PAGE_BACKWARDS)

    # STARS
    @log_calls
    def display_new_star(self, parent, max_height, height=1):
        for child in parent.winfo_children()[1:]:
            child.destroy()
        ttk.Label(parent, image=self.load_image(f'{self.get_stars()}-star', int(height * 2.09), height), anchor="center").pack(side="left", expand=True, fill=tk.X)
        ttk.Label(parent, image=self.load_image(f'0-star', 105, 50), anchor="center").pack(side="left", expand=True, fill=tk.X)
        if height < max_height:
            self.after(15, partial(self.display_new_star, parent, max_height, height+7))
    
    # CATEGORIES
    @log_calls
    def display_categories(self, page=1, event=None):

        categories = self.get_all_categories()
        item_by_page = 4
        total_pages = ceil(len(categories) / item_by_page)
        current_page = 1 if (page < 1) or (page > total_pages) else page

        # Configure page grid
        self.clear_window()
        self.set_window_title("Pick a category !")
        self.window_container.grid(column=1, row=1)

        # Initialize variables
        start_index = (current_page - 1) * item_by_page
        end_index = (start_index + item_by_page) if (len(categories) >= (start_index + item_by_page)) else len(categories)

        # Iterate through categories
        for category in categories[start_index:end_index]:
            self.create_progress_frame(self.window_container, category, category, self.get_category_overview(category), self.get_stars(category), self.select_category, category)

        # RETURN BUTTON
        self.create_button(self.window_container, "arrow_left", "Languages", self.display_languages, arguments=1, sound=SOUND_PAGE_BACKWARDS, alone_in_row=(total_pages == 1))
        
        # PREVIOUS BUTTON
        if current_page > 1:
            self.create_button(self.window_container, "previous", "Previous", self.display_categories, arguments=current_page -1, sound=SOUND_PAGE_BACKWARDS, alone_in_row=False)
        
        # NEXT BUTTON
        if current_page < total_pages:
            self.create_button(self.window_container, "next", "Next", self.display_categories, arguments=current_page +1, sound=SOUND_PAGE_FORWARDS, alone_in_row=False)

    # LESSONS
    @log_calls
    def display_lessons(self, page=1, event=None):

        lessons = self.get_all_lessons()
        item_by_page = 4
        total_pages = ceil(len(lessons) / item_by_page)
        current_page = 1 if (page < 1) or (page > total_pages) else page

        # Configure page grid
        self.clear_window()
        self.set_window_title("Pick a lesson !")
        self.window_container.grid(column=1, row=1)

        # Initialize variables
        start_index = (current_page - 1) * item_by_page
        end_index = (start_index + item_by_page) if (len(lessons) >= (start_index + item_by_page)) else len(lessons)

        # Iterate through lessons
        for lesson in lessons[start_index:end_index]:
            self.create_progress_frame(self.window_container, lesson, lesson, self.get_lesson_overview(lesson=lesson), self.get_stars(self.current_category, lesson), self.select_lesson, lesson)

        # RETURN BUTTON
        self.create_button(self.window_container, "arrow_left", "Categories", self.display_categories, arguments=1, sound=SOUND_PAGE_BACKWARDS, alone_in_row=(total_pages == 1))
        
        # PREVIOUS BUTTON
        if current_page > 1:
            self.create_button(self.window_container, "previous", "Previous", self.display_lessons, arguments=current_page -1, sound=SOUND_PAGE_BACKWARDS, alone_in_row=False)
        
        # NEXT BUTTON
        if current_page < total_pages:
            self.create_button(self.window_container, "next", "Next", self.display_lessons, arguments=current_page +1, sound=SOUND_PAGE_FORWARDS, alone_in_row=False)

    # QUESTIONS
    @log_calls
    def display_questions(self):
        self.choose_random_question()

        # Configure page grid
        self.clear_window()
        self.set_window_title("Translate this sentence !")
        self.window_container.grid(column=1, row=1)

        # STARS
        stars_frame = ttk.Frame(self.window_container)
        stars_frame.pack(expand=True, fill=tk.BOTH, pady=10) 

        ttk.Label(stars_frame, image=self.load_image(f'0-star', 105, 50), anchor="center").pack(side="left", expand=True, fill=tk.X)
        
        if self.get_stars() > self.current_lesson_stars:
            self.current_lesson_stars = self.get_stars()
            self.after(350, partial(self.playsound, SOUND_NEW_STAR))
            self.after(250, partial(self.display_new_star, stars_frame, 50))
        else:
            ttk.Label(stars_frame, image=self.load_image(f'{self.current_lesson_stars}-star', 105, 50), anchor="center").pack(side="left", expand=True, fill=tk.X)
            ttk.Label(stars_frame, image=self.load_image(f'0-star', 105, 50), anchor="center").pack(side="left", expand=True, fill=tk.X)

        # STATS
        stat_frame = ttk.Frame(self.window_container)
        stat_frame.pack(expand=True, fill=tk.X, pady=10) 

        lesson_overview = f'{ceil(self.get_lesson_overview() * 100)}%'
        self.create_stat_frame(stat_frame, text="Lesson Overview", stat=lesson_overview, alone_in_row=False)

        lesson_success_text = f'{ceil(self.get_lesson_success() * 100)}%'
        self.create_stat_frame(stat_frame, text="Lesson Success", stat=lesson_success_text, alone_in_row=False)

        question_tries = self.current_question[self.learned_language]["tries"]
        self.create_stat_frame(stat_frame, text="Question Attempts", stat=question_tries, alone_in_row=False)

        question_success = f'{ceil(self.current_question[self.learned_language]["success_rate"] * 100)}%'
        self.create_stat_frame(stat_frame, text="Question Success", stat=question_success, alone_in_row=False)

        # SENTENCE
        self.create_speakable_frame(self.window_container, self.current_question[self.spoken_language]["sentence"].capitalize(), self.spoken_language)

        # HINTS
        if "hints" in self.current_question[self.spoken_language].keys() :
            self.create_frame(self.window_container, f'PS : {self.current_question[self.spoken_language]["hints"].capitalize()}')

        # ANSWER
        speakable_entry, response_Stringvar = self.create_speakable_entry(self.window_container, self.learned_language)

        # ENTER KEY
        self.bind_widget(speakable_entry, lambda EVENT_KEY_PRESS: self.validate_response(response_Stringvar.get()) if (EVENT_KEY_PRESS.char == "\r") else None, EVENT_KEY_PRESS)

        # RETURN BUTTON
        self.create_button(self.window_container, "arrow_left", "Lessons", self.display_lessons, arguments=1, sound=SOUND_PAGE_BACKWARDS, alone_in_row=False)
        
        # VALIDATE BUTTON
        self.create_button(self.window_container, "arrow_right", "Validate", lambda: self.validate_response(response_Stringvar.get()), image_first=False, alone_in_row=False)

    @log_calls
    def display_answer(self, response):
        # Configure page grid
        self.clear_window()
        self.set_window_title("Nice Try !")
        self.window_container.grid(column=1, row=1)
        explainations = self.get_question_explainations()
        
        # SENTENCE
        self.create_speakable_frame(self.window_container, self.current_question[self.spoken_language]["sentence"].capitalize(), self.spoken_language)

        # RESONSE
        new_frame = ttk.Frame(self.window_container, style="CustomDarkFrame.TFrame")
        new_frame.pack(expand=True, fill=tk.X, pady=10)

        new_text = tk.Text(new_frame, width=40, height=1, relief="flat", background=COLOR_DARK_PINK, foreground=COLOR_WHITE, font=('Calibri', 12))
        new_text.insert("1.0", response.capitalize())
        self.color_differences(new_text, self.current_question[self.learned_language]["sentence"].capitalize(), response.capitalize())

        # ANSWER
        self.create_speakable_frame(self.window_container, self.current_question[self.learned_language]["sentence"].capitalize(), self.learned_language)                

        # EXPLAINATIONS
        if len(explainations) > 0 :
            self.create_scrollable_frame(self.window_container, f"\n\n{'-' * 72}\n\n".join(explainations))

        # RETURN BUTTON
        self.create_button(self.window_container, "arrow_left", "Lessons", self.display_lessons, arguments=1, sound=SOUND_PAGE_BACKWARDS, alone_in_row=False)
        
        # VALIDATE BUTTON
        self.create_button(self.window_container, "arrow_right", "Next Question", self.display_questions, image_first=False, alone_in_row=False)
    
    ##################################################################### OTHER

    # WINDOW
    @log_calls
    def clear_window(self):
        for widget in self.window_container.winfo_children():
            widget.destroy()
    
    @log_calls
    def set_styles(self):
        style = ttk.Style(self) 
        style.configure(".", background=COLOR_LIGHT_GREY, font=('Calibri', 12))

        style.configure("CustomLightFrame.TFrame", background=COLOR_LIGHT_PINK)
        style.configure("CustomMidFrame.TFrame", background=COLOR_MID_PINK)

        style.configure("CustomDarkFrame.TFrame", background=COLOR_DARK_PINK)
        style.configure("Active.CustomDarkFrame.TFrame", background=COLOR_MID_PINK)

        style.configure("Default.TLabel", background=COLOR_DARK_PINK, foreground=COLOR_WHITE)
        style.configure("Active.Default.TLabel", background=COLOR_MID_PINK)
        style.configure("Small.Default.TLabel", font=('Calibri', 8))
        style.configure("Big.Default.TLabel", font=('Calibri', 16))

    @log_calls
    def playsound(self, sound, wait=False):
        if not os.path.isfile(sound):
            sound = os.path.join(PATH_SOUNDS, sound)
        if os.path.isfile(sound):
            Thread(target=playsound, args=(sound, wait), daemon=True).start()
    
    # WIDGETS
    @log_calls
    def bind_widget(self, widget, command, event=EVENT_LEFT_CLICK, recursive=True):
        widget.bind(event, command)
        if recursive:
            for child in widget.winfo_children():
                self.bind_widget(child, command, event)

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

    # PROFILES
    @log_calls
    def select_profile(self, profile, event=None):
        self.current_profile = profile
        self.load_profile()
        self.load_explainations()
        self.display_languages()
    
    # CATEGORIES
    @log_calls
    def select_category(self, category, event=None):
        self.current_category = category
        self.display_lessons()

    # LESSONS
    @log_calls
    def select_lesson(self, lesson, event=None):
        self.current_lesson = lesson
        self.current_lesson_stars = self.get_stars()
        self.display_questions()

    # QUESTIONS
    @log_calls
    def is_remembered(self, question):
        return random.random() < question[self.learned_language]["success_rate"] * 0.95
    
    @log_calls
    def choose_random_question(self):
        deep_copy = deepcopy(self.categories)
        questions_id = list(deep_copy[self.current_category][self.current_lesson]["questions"].keys())
        random.shuffle(questions_id)
        
        for question_id in questions_id:
            question = deep_copy[self.current_category][self.current_lesson]["questions"][question_id]
            if (self.current_question) and (self.current_question[self.learned_language]["sentence"] == question[self.learned_language]["sentence"]):
                continue
            if self.is_remembered(question):
                continue
            self.current_question_id = question_id
            self.current_question = question
            return

        self.current_question_id = random.choice(deep_copy[self.current_category][self.current_lesson]["questions"].keys())
        self.current_question = deep_copy[self.current_category][self.current_lesson]["questions"][self.current_question_id]
    
    @log_calls
    def increase_question_success(self, question=None):
        question = question if question else self.current_question
        success_rate = self.get_question_data("success_rate")
        tries = self.get_question_data("tries")
        new_success_rate = ((success_rate * (tries -1)) +1) / tries
        self.set_question_success(new_success_rate)

    @log_calls
    def decrease_question_success(self, question=None):
        question = question if question else self.current_question
        success_rate = self.get_question_data("success_rate")
        tries = self.get_question_data("tries")
        new_success_rate = (success_rate * (tries -1)) / tries
        self.set_question_success(new_success_rate)

    @log_calls
    def increase_question_tries(self, question=None):
        question = question if question else self.current_question
        new_tries = question[self.learned_language]["tries"] = 1
        self.set_question_tries(new_tries)

    # DIFFERENCES
    @log_calls
    def find_differences(self, reference, text, missing_letters=True):
        dmp = diff_match_patch()
        differences = dmp.diff_main(reference, text)
        dmp.diff_cleanupSemantic(differences)
        return differences
   
    @log_calls
    def color_differences(self, text_widget, reference, text):
        differences = self.find_differences(reference, text)
        text_widget.tag_configure("red", background="#b30000")
        text_widget.tag_configure("green", background="#009900")

        char_index = 0
        for difference in differences:
            if difference[0] == 1:
                text_widget.tag_add("red", f"1.{char_index}", f"1.{char_index + len(difference[1])}")
            if difference[0] == -1:
                text_widget.insert(f"1.{char_index}", difference[1])
                text_widget.tag_add("green", f"1.{char_index}", f"1.{char_index + len(difference[1])}")
            char_index += len(difference[1])

        text_widget.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)
        text_widget.configure(state="disabled")

##################################################################### MAIN CODE

if __name__ == "__main__":
    app = Bilingual()
    app.mainloop()