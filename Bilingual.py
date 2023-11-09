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

# ENVIRONMENT
DEBUG_MODE = True
CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

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
        style = ttk.Style(self) 
        style.configure(".", background=COLOR_LIGHT_GREY, font=('Calibri', 12))

        style.configure("CustomLightFrame.TFrame", background=COLOR_LIGHT_PINK)
        style.configure("CustomMidFrame.TFrame", background=COLOR_MID_PINK)

        style.configure("CustomDarkFrame.TFrame", background=COLOR_DARK_PINK)
        style.configure("Active.CustomDarkFrame.TFrame", background=COLOR_MID_PINK)

        style.configure("TLabel", background=COLOR_DARK_PINK, foreground=COLOR_WHITE)
        style.configure("Active.TLabel", background=COLOR_MID_PINK)

    @log_calls
    def create_window(self):
        self.title("Go Bilingo")
        self.iconbitmap(CURRENT_DIRECTORY + '/assets/icons/megan.ico')
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
    def clear_window(self):
        for widget in self.window_container.winfo_children():
            widget.destroy()
   
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
    def get_category_results(self, category=None):
        if category is None:
            category = self.current_category
        results = [self.get_lesson_results(category=category, lesson=lesson) for lesson in self.get_all_lessons(category=category)]
        return sum(results) / len(results)

    @log_calls
    def get_category_progress(self, category=None):
        if category is None:
            category = self.current_category
        progressions = [self.get_lesson_progress(category=category, lesson=lesson) for lesson in self.get_all_lessons(category=category)]
        return sum(progressions) / len(progressions)

    @log_calls
    def get_lesson_results(self, category=None, lesson=None):
        if category is None:
            category = self.current_category
        if lesson is None:
            lesson = self.current_lesson
        results = [question[self.learned_language]["success_rate"] for question in self.data[category][lesson]]
        return sum(results) / len(results) * self.get_lesson_progress(category, lesson)

    @log_calls
    def get_lesson_progress(self, category=None, lesson=None):
        if category is None:
            category = self.current_category
        if lesson is None:
            lesson = self.current_lesson
        progressions = 0
        for question in self.data[category][lesson]:
            if (question[self.learned_language]["tries"] > 0):
                progressions += 1
        return progressions / len(self.data[category][lesson])

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
    def get_random_color(self):
        return random.choice(["red", "blue", "yellow", "green", "magenta", "orange"]) if self.debug_color else None
    
    @log_calls
    def scroll_widget(self, widget, event):
        widget.configure(scrollregion=widget.bbox("all"))

    @log_calls
    def playsound(self, sound, wait=False):
        file_path = CURRENT_DIRECTORY + f"/assets/sounds/{sound}"

        if os.path.isfile(file_path):
            Thread(target=playsound, args=(file_path, wait), daemon=True).start()
    
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

        if isinstance(text, tk.StringVar):
            text = text.get()

        tts = gTTS(text=text, lang=languages[language]["language_code"], tld=languages[language]["accent_code"])

        if os.path.isfile(file_path):
            os.remove(file_path)

        tts.save(file_path)

        while not os.path.isfile(file_path):
            sleep(0.1)

        playsound(file_path, False)

    @log_calls
    def bind_widget(self, widget, command, event=EVENT_LEFT_CLICK, recursive=True):
        widget.bind(event, command)
        if recursive:
            for child in widget.winfo_children():
                self.bind_widget(child, command, event)

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
    def find_differences(self, reference, text, missing_letters=True):
        color_mapping = {-1: "red", 0: COLOR_WHITE, 1: "blue"}
        dmp = diff_match_patch()
        differences = dmp.diff_main(reference, text)
        dmp.diff_cleanupSemantic(differences)
        return differences

    @log_calls
    def enter_widget(self, widget, sound=True, event=None):
        if sound:
            self.playsound(SOUND_POP)
        widget.configure(style=f'Active.{widget["style"]}')
        for child in widget.winfo_children():
            self.enter_widget(child, False)

    @log_calls
    def leave_widget(self, widget, event=None):
        widget.configure(style=widget["style"].replace("Active.", ""))
        for child in widget.winfo_children():
            self.leave_widget(child)

    @log_calls
    def create_frame(self, parent, text):
        new_frame = ttk.Frame(parent, style="CustomDarkFrame.TFrame")
        new_frame.pack(expand=True, fill=tk.X, pady=10)

        new_label = ttk.Label(new_frame, text=text)
        new_label.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)

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

        new_label = ttk.Label(new_frame, text=text)
        new_label.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)

        if language in ["english", "french"]:
            tts_frame = ttk.Frame(new_frame, style="CustomDarkFrame.TFrame")
            tts_frame.pack(side=tk.LEFT)

            tts = ttk.Label(tts_frame, image=self.load_image("speak", 25, 25), style="TLabel")
            tts.pack(padx=10, pady=5)

            self.bind_widget(tts, partial(self.click_button, self.tell_text, [text, language], None))

            if animate:
                self.bind_widget(tts_frame, partial(self.enter_widget, tts_frame), EVENT_ENTER_WIDGET, recursive=False)
                self.bind_widget(tts_frame, partial(self.leave_widget, tts_frame), EVENT_LEAVE_WIDGET, recursive=False)

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

            tts = ttk.Label(tts_frame, image=self.load_image("speak", 25, 25), style="TLabel")
            tts.pack(padx=10, pady=5)

            self.bind_widget(tts, partial(self.click_button, self.tell_text, [new_Stringvar, language], None))

            if animate:
                self.bind_widget(tts_frame, partial(self.enter_widget, tts_frame), EVENT_ENTER_WIDGET, recursive=False)
                self.bind_widget(tts_frame, partial(self.leave_widget, tts_frame), EVENT_LEAVE_WIDGET, recursive=False)

        return new_frame, new_Stringvar

    @log_calls
    def create_button(self, parent, image, text, action, arguments=[], sound=None, image_first=True, alone_in_row=True, animate=True):
        side = tk.TOP if alone_in_row else tk.LEFT
        new_frame = ttk.Frame(parent, style="CustomDarkFrame.TFrame")
        new_frame.pack(padx=10, pady=10, expand=True, fill=tk.X, side=side)

        side = tk.LEFT if image_first else tk.RIGHT
        
        anchor = tk.E if image_first else tk.W
        new_image = ttk.Label(new_frame, image=self.load_image(image, 25, 25), anchor=anchor, style="TLabel")
        new_image.pack(side=side, padx=5, expand=True, fill=tk.BOTH)

        anchor = tk.W if image_first else tk.E
        new_label = ttk.Label(new_frame, text=text, anchor=anchor, style="TLabel")
        new_label.pack(side=side, padx=5, expand=True, fill=tk.BOTH)
        
        self.bind_widget(new_frame, partial(self.click_button, action, arguments, sound))

        if animate:
            self.bind_widget(new_frame, partial(self.enter_widget, new_frame), EVENT_ENTER_WIDGET, recursive=False)
            self.bind_widget(new_frame, partial(self.leave_widget, new_frame), EVENT_LEAVE_WIDGET, recursive=False)

    @log_calls
    def create_image_frame(self, parent, image, text, action, arguments, sound=None, animate=True):
        new_frame = ttk.Frame(parent, style="CustomDarkFrame.TFrame")
        new_frame.pack(pady=5, expand=True, fill=tk.X)

        title_frame = ttk.Frame(new_frame, style="CustomDarkFrame.TFrame")
        title_frame.pack(expand=True, fill=tk.BOTH)

        title_frame_picture = ttk.Label(title_frame, image=self.load_image(image, 35, 35), style="TLabel")
        title_frame_picture.pack(padx=15, pady=5, side=tk.LEFT)

        title_frame_text_text = text.replace("-", " ").title()
        title_frame_text = ttk.Label(title_frame, text=title_frame_text_text, style="TLabel")
        title_frame_text.pack(ipadx=15, ipady=5, side=tk.LEFT, expand=True, fill=tk.X)

        self.bind_widget(new_frame, partial(self.click_button, action, arguments))

        if animate:
            self.bind_widget(new_frame, partial(self.enter_widget, new_frame), EVENT_ENTER_WIDGET, recursive=False)
            self.bind_widget(new_frame, partial(self.leave_widget, new_frame), EVENT_LEAVE_WIDGET, recursive=False)

    @log_calls
    def create_progress_frame(self, parent, image, text, progress, results, action, arguments, sound=None, animate=True):
        new_frame = ttk.Frame(parent, style="CustomDarkFrame.TFrame")
        new_frame.pack(pady=5, expand=True, fill=tk.X)

        title_frame = ttk.Frame(new_frame, style="CustomDarkFrame.TFrame")
        title_frame.pack(expand=True, fill=tk.BOTH)

        title_frame_picture = ttk.Label(title_frame, image=self.load_image(image, 35, 35), style="TLabel")
        title_frame_picture.pack(padx=15, pady=5, side=tk.LEFT)

        title_frame_text_text = text.replace("-", " ").title()
        title_frame_text = ttk.Label(title_frame, text=title_frame_text_text, style="TLabel")
        title_frame_text.pack(ipadx=15, ipady=5, side=tk.LEFT, expand=True, fill=tk.X)

        # % of success to achieve to earn each start
        stars = [0.4, 0.6, 0.8]
        earned = len([i for i, value in enumerate(stars) if value <= results])

        stars_image = ttk.Label(title_frame, image=self.load_image(f'{earned}-star', 53, 25), style="TLabel")
        stars_image.pack(padx=15, pady=5, side=tk.LEFT)

        progressbar_frame = ttk.Frame(new_frame, style="CustomDarkFrame.TFrame")
        progressbar_frame.pack(expand=True, fill=tk.X)

        self.update()

        progressbar_frame_left_width = new_frame.winfo_width() * results
        progressbar_frame_left = ttk.Frame(progressbar_frame, height=5, width=progressbar_frame_left_width, style="CustomMidFrame.TFrame")
        progressbar_frame_left.pack(side=tk.LEFT)
        
        progressbar_frame_right = ttk.Frame(progressbar_frame, height=5, style="CustomLightFrame.TFrame")
        progressbar_frame_right.pack(expand=True, fill=tk.X, side=tk.LEFT)

        self.bind_widget(new_frame, partial(self.click_button, action, arguments))

        if animate:
            self.bind_widget(new_frame, partial(self.enter_widget, new_frame), EVENT_ENTER_WIDGET, recursive=False)
            self.bind_widget(new_frame, partial(self.leave_widget, new_frame), EVENT_LEAVE_WIDGET, recursive=False)

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

    @log_calls
    def validate_response(self, response, event=None):
        response_is_right = None
        response = response
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
            self.playsound(SOUND_CORRECT)
            question[self.learned_language]["success_rate"] = ((question[self.learned_language]["success_rate"] * (question[self.learned_language]["tries"] -1)) +1) / question[self.learned_language]["tries"]
            self.save_profile()
            self.display_questions()

        # If the response is wrong
        else:
            self.playsound(SOUND_INCORRECT)
            question[self.learned_language]["success_rate"] = (question[self.learned_language]["success_rate"] * (question[self.learned_language]["tries"] -1)) / question[self.learned_language]["tries"]
            self.display_answer(response)

    @log_calls
    def select_profile(self, profile, event=None):
        self.current_profile = profile
        self.iconbitmap(CURRENT_DIRECTORY + f'/assets/icons/{profile}.ico')
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
    def display_profiles(self, page=1, event=None):

        profiles = self.get_all_profiles()
        item_by_page = 5
        total_pages = ceil(len(profiles) / item_by_page)
        current_page = 1 if (page < 1) or (page > total_pages) else page

        # Configure page grid
        self.clear_window()
        self.title("Pick your profile !")
        self.window_container.grid(column=1, row=1)

        # Initialize variables
        start_index = (current_page - 1) * item_by_page

        # Iterate through profiles
        for profile in profiles[start_index:]:
            self.create_image_frame(self.window_container, profile, profile, self.select_profile, profile)

        # QUIT BUTTON
        self.create_button(self.window_container, "arrow_left", "Quit", self.close_app)

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
                frame.pack(pady=5, expand=True, fill=tk.X)

                spoken_language_picture = ttk.Label(frame, image=self.load_image(spoken_language, 35, 35), style="TLabel", anchor=tk.CENTER)
                spoken_language_picture.pack(padx=10, pady=5, side=tk.LEFT, expand=True, fill=tk.X)

                arrow_picture = ttk.Label(frame, image=self.load_image("next", 35, 35), style="TLabel", anchor=tk.CENTER)
                arrow_picture.pack(padx=10, pady=5, side=tk.LEFT)

                learned_language_picture = ttk.Label(frame, image=self.load_image(learned_language, 35, 35), style="TLabel", anchor=tk.CENTER)
                learned_language_picture.pack(padx=10, pady=5, side=tk.LEFT, expand=True, fill=tk.X)

                self.bind_widget(frame, partial(self.click_button, self.validate_languages, [spoken_language, learned_language]))
                self.bind_widget(frame, partial(self.enter_widget, frame), EVENT_ENTER_WIDGET, recursive=False)
                self.bind_widget(frame, partial(self.leave_widget, frame), EVENT_LEAVE_WIDGET, recursive=False)

        # RETURN BUTTON
        self.create_button(self.window_container, "arrow_left", "Profiles", self.display_profiles, arguments=1, sound=SOUND_PAGE_BACKWARDS)

    @log_calls
    def display_categories(self, page=1, event=None):

        categories = self.get_all_categories()
        item_by_page = 4
        total_pages = ceil(len(categories) / item_by_page)
        current_page = 1 if (page < 1) or (page > total_pages) else page

        # Configure page grid
        self.clear_window()
        self.title("Pick a category !")
        self.window_container.grid(column=1, row=1)

        # Initialize variables
        start_index = (current_page - 1) * item_by_page
        end_index = (start_index + item_by_page) if (len(categories) >= (start_index + item_by_page)) else len(categories)

        # Iterate through categories
        for category in categories[start_index:end_index]:
            self.create_progress_frame(self.window_container, category, category, self.get_category_progress(category=category), self.get_category_results(category=category), self.select_category, category)

        # RETURN BUTTON
        self.create_button(self.window_container, "arrow_left", "Languages", self.display_languages, arguments=1, sound=SOUND_PAGE_BACKWARDS, alone_in_row=(total_pages == 1))
        
        # PREVIOUS BUTTON
        if current_page > 1:
            self.create_button(self.window_container, "previous", "Previous", self.display_categories, arguments=current_page -1, sound=SOUND_PAGE_BACKWARDS, alone_in_row=False)
        
        # NEXT BUTTON
        if current_page < total_pages:
            self.create_button(self.window_container, "next", "Next", self.display_categories, arguments=current_page +1, sound=SOUND_PAGE_FORWARDS, alone_in_row=False)

    @log_calls
    def display_lessons(self, page=1, event=None):

        lessons = self.get_all_lessons()
        item_by_page = 4
        total_pages = ceil(len(lessons) / item_by_page)
        current_page = 1 if (page < 1) or (page > total_pages) else page

        # Configure page grid
        self.clear_window()
        self.title("Pick a lesson !")
        self.window_container.grid(column=1, row=1)

        # Initialize variables
        start_index = (current_page - 1) * item_by_page
        end_index = (start_index + item_by_page) if (len(lessons) >= (start_index + item_by_page)) else len(lessons)

        # Iterate through lessons
        for lesson in lessons[start_index:end_index]:
            self.create_progress_frame(self.window_container, lesson, lesson, self.get_lesson_progress(lesson=lesson), self.get_lesson_results(lesson=lesson), self.select_lesson, lesson)

        # RETURN BUTTON
        self.create_button(self.window_container, "arrow_left", "Categories", self.display_categories, arguments=1, sound=SOUND_PAGE_BACKWARDS, alone_in_row=(total_pages == 1))
        
        # PREVIOUS BUTTON
        if current_page > 1:
            self.create_button(self.window_container, "previous", "Previous", self.display_lessons, arguments=current_page -1, sound=SOUND_PAGE_BACKWARDS, alone_in_row=False)
        
        # NEXT BUTTON
        if current_page < total_pages:
            self.create_button(self.window_container, "next", "Next", self.display_lessons, arguments=current_page +1, sound=SOUND_PAGE_FORWARDS, alone_in_row=False)

    @log_calls
    def display_questions(self):
        self.choose_random_question()

        # Configure page grid
        self.clear_window()
        self.title("Translate this sentence !")
        self.window_container.grid(column=1, row=1)

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
        self.title("Nice Try !")
        self.window_container.grid(column=1, row=1)
        differences = self.find_differences(self.current_question[self.learned_language]["sentence"].capitalize(), response.capitalize())

        # SENTENCE
        self.create_speakable_frame(self.window_container, self.current_question[self.spoken_language]["sentence"].capitalize(), self.spoken_language)

        # RESONSE
        new_frame = ttk.Frame(self.window_container, style="CustomDarkFrame.TFrame")
        new_frame.pack(expand=True, fill=tk.X, pady=10)

        new_text = tk.Text(new_frame, width=40, height=1, relief="flat", background=COLOR_DARK_PINK, foreground=COLOR_WHITE, font=('Calibri', 12))
        new_text.insert("1.0", response.capitalize())
        new_text.tag_configure("red", background="#b30000")
        new_text.tag_configure("green", background="#009900")

        char_index = 0

        for difference in differences:
            if difference[0] == 1:
                new_text.tag_add("red", f"1.{char_index}", f"1.{char_index + len(difference[1])}")
            if difference[0] == -1:
                new_text.insert(f"1.{char_index}", difference[1])
                new_text.tag_add("green", f"1.{char_index}", f"1.{char_index + len(difference[1])}")
            char_index += len(difference[1])

        new_text.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)
        new_text.configure(state="disabled")

        # ANSWER
        self.create_speakable_frame(self.window_container, self.current_question[self.learned_language]["sentence"].capitalize(), self.learned_language)        

        explaination_text = []
 
        if self.learned_language in self.explainations.keys():
            for item in self.explainations[self.learned_language]:
                for patern in item["paterns"]:
                    if patern in self.current_question[self.learned_language]["sentence"]:
                        if self.spoken_language in item["explainations"].keys():
                            explaination_text.append(item["explainations"][self.spoken_language])

        if len(explaination_text) > 0 :
            self.create_scrollable_frame(self.window_container, f"\n\n{'-' * 72}\n\n".join(explaination_text))

        # RETURN BUTTON
        self.create_button(self.window_container, "arrow_left", "Lessons", self.display_lessons, arguments=1, sound=SOUND_PAGE_BACKWARDS, alone_in_row=False)
        
        # VALIDATE BUTTON
        self.create_button(self.window_container, "arrow_right", "Next Question", self.display_questions, image_first=False, alone_in_row=False)

##################################################################### MAIN CODE

if __name__ == "__main__":
    app = Bilingual()
    app.mainloop()