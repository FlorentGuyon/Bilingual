from copy import deepcopy
from functools import partial
from json import load, loads, dumps, JSONDecodeError
from math import ceil
from os import path, walk, listdir, remove
from os.path import join, isfile, dirname, isdir, exists, basename, abspath
from random import random, shuffle, choice
from subprocess import Popen
from sys import version_info, executable
from threading import Thread
from time import sleep
from tkinter import Tk, X, Y, E, W, CENTER, LEFT, BOTH, RIGHT, Text, StringVar, Event, TOP, FLAT, INSERT, Text, Entry
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Label, Frame, Style
# MORE REQUIREMENTS BELOW

##################################################################### CONSTANTS

# ENVIRONMENT
DEBUG_MODE = False
CURRENT_DIRECTORY = dirname(abspath(__file__))
FILES_ENCODING = "utf8"

# LANGUAGES
LEARNED_LANGUAGE = "french"
SPOKEN_LANGUAGE = "english"

# COLORS
COLOR_WHITE = "#FFFFFF"
COLOR_LIGHT_GREY = "#eae5e5"
COLOR_MID_GREY = "#d3c9c9"
COLOR_DARK_GREY = "#c8bbbb"
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
SOUND_BLOCKED = "blocked.wav"
SOUND_UNLOCK = "unlock.wav"

# PATHS
PATH_CATEGORIES = join(CURRENT_DIRECTORY, "assets", "categories")
PATH_ICONS = join(CURRENT_DIRECTORY, "assets", "icons")
PATH_EXPLAINATIONS = join(CURRENT_DIRECTORY, "assets", "explainations")
PATH_PROFILES = join(CURRENT_DIRECTORY, "assets", "profiles")
PATH_SOUNDS = join(CURRENT_DIRECTORY, "assets", "sounds")
PATH_TEMPORARY_FILES = join(CURRENT_DIRECTORY, "assets", "temp")

# ICONS
DEFAULT_ICON = "rabbit-pink"

# STARS
VALUE_STARS = [0.6, 0.8, 0.9] # 60% of success in a lesson to earn the first star, then 80% and 90%

########################################################################### INIT

# CHECK PYTHON VERSION
current_python_version = version_info[:2]
minimal_python_version = (3, 11)
if current_python_version < minimal_python_version:
    print(f"Warning : This program has been developed for the version {minimal_python_version} of Python.")
    print(f"This program has been executed with the Python version {current_python_version}.")
    print("It can be impossible to meet the requirements for this program or the program can disfunction.")
    execute = input("Do you still want to execute this program ? (y/N) : ")
    if execute not in ["y", "Y"] :
        exit()

# IMPORT REQUIREMENTS
import_successful = False
import_attemps = 0
while not import_successful:
    try:
        import_attemps += 1
        from PIL import Image, ImageTk
        from gtts import gTTS
        from diff_match_patch import diff_match_patch
        from playsound import playsound
    except:
        if import_attemps == 1:
            print("Error : The requirements for the exection of this program are not met.")
            install_requirements = input("Do you want to start the installer program that downloads and installs the requirements now ? (y/N) : ")
            if install_requirements in ["y", "Y"] :
                try:
                    command = [executable, join(CURRENT_DIRECTORY, "installer.py")]
                    Popen(command).wait()
                except Exception as e:
                    print(f"Error : Impossible to start the installer. ({e})")
                    exit()
            else:
                exit()
        else:
            print(f"Error : Still impossible to import the requirements.")
            exit()
    import_successful = True

###################################################################### WRAPPERS

def log_calls(method):
    def wrapper(*args, **kwargs):
        if DEBUG_MODE:
            print(f'{method.__name__}({str(args[1:])}, {str(kwargs)})')
        return method(*args, **kwargs)
    return wrapper

####################################################################### CLASSES

class Language:
    def __init__(self, name=None, sentence=None, hints=None, success=0, tries=0):
        self._name = name
        self._sentence = sentence
        self._hints = hints
        self._success = success
        self._tries = tries

    ################################################################### GETTERS
    @property
    def name(self):
        return self._name

    # Getter for sentence
    @property
    def sentence(self):
        return self._sentence

    # Getter for hints
    @property
    def hints(self):
        return self._hints

    # Getter for success
    @property
    def success(self):
        return self._success

    # Getter for tries
    @property
    def tries(self):
        return self._tries

    ################################################################### SETTERS

    # Setter for name
    @name.setter
    def name(self, name):
        self._name = name

    # Setter for sentence
    @sentence.setter
    def sentence(self, sentence):
        self._sentence = sentence

    # Setter for hints
    @hints.setter
    def hints(self, hints):
        self._hints = hints

    # Setter for success
    @success.setter
    def success(self, success):
        self._success = success

    # Setter for tries
    @tries.setter
    def tries(self, tries):
        self._tries = tries


class Question:
    def __init__(self, uid=None, languages=None):
        self._uid = uid
        self._languages = languages if languages else {}
        self._sentence = None
        self._answer = None
        self._hints = None
        self._success = None
        self._tries = None

    ################################################################### GETTERS

    @property
    def uid(self):
        return self._uid

    @property
    def languages(self):
        return self._languages

    @property
    def sentence(self):
        return self.languages[SPOKEN_LANGUAGE].sentence

    @property
    def answer(self):
        return self.languages[LEARNED_LANGUAGE].sentence

    @property
    def hints(self):
        return self.languages[SPOKEN_LANGUAGE].hints

    @property
    def success(self):
        return self.languages[LEARNED_LANGUAGE].success

    @property
    def tries(self):
        return self.languages[LEARNED_LANGUAGE].tries


    ################################################################### SETTERS

    @uid.setter
    def uid(self, uid):
        self._uid = uid

    @languages.setter
    def languages(self, languages):
        self._languages = languages

    @tries.setter
    def tries(self, tries):
        self.languages[LEARNED_LANGUAGE].tries = tries

    @success.setter
    def success(self, success):
        self.languages[LEARNED_LANGUAGE].success = success

    ################################################################### METHODS

    def add_language(self, language):
        self._languages[language.name] = language

    def propose(self, response):
        self.tries += 1
        correct = (response.lower().strip() == self.answer.lower().strip())
        if correct:
            self.success = ((self.success * (self.tries -1)) +1) / self.tries
        else:
            self.success = (self.success * (self.tries -1)) / self.tries
        return correct


class Lesson:
    def __init__(self, uid=None, name=None, icon=None, prerequisites=None, questions=None, is_locked=None):
        self._uid = uid
        self._name = name
        self._icon = icon
        self._prerequisites = prerequisites
        self._questions = questions if questions else {}
        self._is_locked = is_locked
        self._question = None
        self._progress = None
        self._success = None
        self._stars = None
        self._languages = None

    ################################################################### GETTERS

    @property
    def uid(self):
        return self._uid

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def prerequisites(self):
        return self._prerequisites

    @property
    def questions(self):
        return self._questions

    @property
    def question(self):
        return self._question

    @property
    def is_locked(self):
        return self._is_locked

    @property
    def progress(self):
        return sum([1 for question in self.questions.values() if question.tries > 0]) / len(self.questions.keys())

    @property
    def success(self):
        return sum([question.success for question in self.questions.values()]) / len(self.questions.keys())

    @property
    def languages(self):
        languages = set()
        for question in self.questions.values():
            for language in question.languages.keys():
                languages.add(language)
        return list(languages)

    @property
    def stars(self):
        return len([i for i, value in enumerate(VALUE_STARS) if value <= self.success])

    ################################################################### SETTERS

    @uid.setter
    def uid(self, uid):
        self._uid = uid

    @name.setter
    def name(self, name):
        self._name = name

    @icon.setter
    def icon(self, icon):
        self._icon = icon

    @prerequisites.setter
    def prerequisites(self, prerequisites):
        self._prerequisites = prerequisites

    @questions.setter
    def questions(self, questions):
        self._questions = questions

    @question.setter
    def question(self, question):
        self._question = question

    @is_locked.setter
    def is_locked(self, is_locked):
        self._is_locked = is_locked

    @stars.setter
    def stars(self, stars):
        self._stars = stars

    ################################################################### METHODS

    def add_question(self, question):
        self._questions[question.uid] = question

    def next_question(self):
        deep_copy = deepcopy(self.questions)
        questions_id = list(deep_copy.keys())
        shuffle(questions_id)
        for question_id in questions_id:
            if (self.question) and (self.question.uid == question_id):
                continue
            if random() < self.questions[question_id].success * 0.95:
                continue
            self.question = self.questions[question_id]
            return self.question
        self.question = choice(list(self.questions.values()))
        return self.question


class Category:

    def __init__(self, uid=None, name=None, icon=None, lessons=None, lesson=None):
        self._uid = uid
        self._name = name
        self._icon = icon
        self._lessons = lessons if lessons else {}
        self._lesson = None
        self._is_locked = None
        self._progress = None
        self._success = None
        self._stars = None
        self._languages = None

    ################################################################### GETTERS

    @property
    def uid(self):
        return self._uid

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def lessons(self):
        return self._lessons

    @property
    def lesson(self):
        return self._lesson

    @property
    def is_locked(self):
        for lesson in self.lessons.values():
            if not lesson.is_locked:
                return False
        return True

    @property
    def progress(self):
        return sum([lesson.progress for lesson in self.lessons.values()]) / len(self.lessons.keys())

    @property
    def success(self):
        return sum([lesson.success for lesson in self.lessons.values()]) / len(self.lessons.keys())

    @property
    def stars(self):
        return len([i for i, value in enumerate(VALUE_STARS) if value <= self.success])

    @property
    def languages(self):
        languages = set()
        for lesson in self.lessons.values():
            for language in lesson.languages:
                languages.add(language)
        return list(languages)


    ################################################################### SETTERS

    @uid.setter
    def uid(self, uid):
        self._uid = uid

    @name.setter
    def name(self, name):
        self._name = name

    @icon.setter
    def icon(self, icon):
        self._icon = icon

    @lessons.setter
    def lessons(self, lessons):
        self._lessons = lessons

    @lesson.setter
    def lesson(self, lesson):
        self._lesson = lesson

    @is_locked.setter
    def is_locked(self, is_locked):
        self._is_locked = is_locked

    ################################################################### METHODS

    def add_lesson(self, lesson):
        self.lessons[lesson.uid] = lesson

    def next_question(self):
        return self.lesson.next_question()


class Profile:

    def __init__(self, uid=None, name=None, icon=None):
        self._uid = uid
        self._name = name
        self._icon = icon

    ################################################################### GETTERS

    @property
    def uid(self):
        return self._uid

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    ################################################################### SETTERS

    @uid.setter
    def uid(self, uid):
        self._uid = uid

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @icon.setter
    def icon(self, new_icon):
        self._icon = new_icon


class Bilingual(Tk):

    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self._icons = {}
        self._icon = None
        self._profiles = {}
        self._profile = None
        self._categories = {}
        self._category = None
        self._lessons = None
        self._lesson = None
        self._languages = None
        self._questions = None
        self._question = None
        self._last_lesson_stars = None
        self._explainations = None
        self.load_profiles()
        self.load_categories()
        self.set_styles()
        self.create_window()
        self.display_profiles()

    ################################################################### GETTERS
    
    # FILES
    @log_calls
    def get_files(self, parent, extension=None):
        files_list = []
        for subdir, _, files in walk(parent):
            if extension:
                files_list += [join(subdir, f) for f in files if f.endswith(extension)]
            else:
                files_list += [join(subdir, f) for f in files]
        return files_list

    # ICONS
    @property
    def icons(self):
        return self._icons

    @property
    def icon(self):
        return self._icon

    # PROFILES
    @property
    def profile(self):
        return self._profile

    @property
    def profiles(self):
        return self._profiles

    @log_calls
    def get_profiles_count(self):
        return len(self.profiles.keys())

    # LANGUAGES
    @property
    def languages(self):
        languages = set()
        for category in self.categories.values():
            for language in category.languages:
                languages.add(language)
        return list(languages)

    # STARS
    @property
    def last_lesson_stars(self):
        return self._last_lesson_stars

    # CATEGORIES
    @property
    def category(self):
        return self._category

    @property
    def categories(self):
        return self._categories

    # LESSONS
    @property
    def lesson(self):
        return self._lesson

    @property
    def lessons(self):
        lessons = {}
        for category in self.categories.values():
            for lesson in category.lessons.values():
                lessons[lesson.uid] = lesson
        return lessons

    # QUESTION
    @property
    def question(self):
        return self._question

    @property
    def explainations(self):
        return self._explainations

    @log_calls 
    def get_question_explainations(self): 
        explaination_text = [] 
        if LEARNED_LANGUAGE in self.explainations.keys(): 
            for item in self.explainations[LEARNED_LANGUAGE]: 
                for patern in item["paterns"]: 
                    if patern in self.question.answer: 
                        if SPOKEN_LANGUAGE in item["explainations"].keys(): 
                            explaination_text.append(item["explainations"][SPOKEN_LANGUAGE]) 
 
        return explaination_text 
 
    ################################################################### SETTERS

    # WINDOW
    @log_calls
    def set_window_icon(self, icon=DEFAULT_ICON):
        file_name = icon + ".ico"
        file_path = join(PATH_ICONS, file_name)
        self.iconbitmap(file_path)

    @log_calls
    def set_window_title(self, title, event=None):
        self.title(title)

    # ICONS
    @icon.setter
    def icon(self, icon):
        self._icon = icon
        self.set_window_icon(icon)

    # PROFILE
    @profile.setter
    def profile(self, profile):
        self._profile = profile

    # STARS
    @last_lesson_stars.setter
    def last_lesson_stars(self, last_lesson_stars):
        self._last_lesson_stars = last_lesson_stars

    # CATEGORY
    @category.setter
    def category(self, category):
        self._category = category

    # QUESTION
    @question.setter
    def question(self, question):
        self._question = question

    @explainations.setter
    def explainations(self, explainations):
        self._explainations = explainations

    # LESSON
    @lessons.setter
    def lessons(self, lessons):
        self._lessons = lessons

    # LESSON
    @lesson.setter
    def lesson(self, lesson):
        self._lesson = lesson
        self.category.lesson = lesson

    ################################################################### READERS

    # IMAGES
    @log_calls
    def load_image(self, name, width, height, grey=False):
        if name in self.icons.keys():
            if width in self.icons[name].keys():
                if height in self.icons[name][width].keys():
                    if grey in self.icons[name][width][height].keys():
                        return self.icons[name][width][height][grey]

        image_name = name + ".png"
        image_path = join(PATH_ICONS, image_name)

        try:
            image = Image.open(image_path)
        except Exception as e:
            print(f'Error: Impossible to resize the image at "{image_path}" to {width}x{height}. ({e})')
            return None

        if grey:
            image = self.color_image(image)

        image = self.resize_image(image, width, height)
        image = ImageTk.PhotoImage(image)

        if name not in self.icons.keys():
            self.icons[name] = {}
        if width not in self.icons[name].keys():
            self.icons[name][width] = {}
        if height not in self.icons[name][width].keys():
            self.icons[name][width][height] = {}
        self.icons[name][width][height][grey] = image
        
        return image

    @log_calls
    def read_from_file(self, file_path, critical=True):
        with open(file_path, 'r', encoding=FILES_ENCODING) as file:
            try:
                return file.read()
            except JSONDecodeError:
                print(f"Error while reading at {file_path}.")
                if critical:
                    exit()   

    # PROFILES
    @log_calls
    def load_profiles(self):
        json_files = self.get_files(PATH_PROFILES, "json")
        for file_path in json_files:
            file_name = basename(file_path).replace(".json", "")
            if file_name not in self.profiles.keys():
                json_content = loads(self.read_from_file(file_path))
                new_profile = Profile()
                new_profile.uid = file_name
                new_profile.name = file_name.title()
                new_profile.icon = json_content["icon"]
                self.add_profile(new_profile)

    @log_calls
    def load_profile(self):
        profile_path = join(PATH_PROFILES, self.profile.uid + ".json")
        profile_content = self.read_from_file(profile_path)
        profile = loads(profile_content)
        self.icon = profile["icon"]
        for category in self.categories.values():
            for lesson in category.lessons.values():
                for question in lesson.questions.values():
                    for language in question.languages.keys():
                        try:
                            value = profile["categories"][category.uid][lesson.uid][question.uid][language]["success"]
                            self.categories[category.uid].lessons[lesson.uid].questions[question.uid].languages[language].success = value
                        except:
                            pass
                        try:
                            value = profile["categories"][category.uid][lesson.uid][question.uid][language]["tries"]
                            self.categories[category.uid].lessons[lesson.uid].questions[question.uid].languages[language].tries = value
                        except:
                            pass
        self.check_prerequisites()

    # CATEGORIES
    @log_calls
    def load_categories(self):
        json_files = self.get_files(PATH_CATEGORIES, "json")

        for file_path in json_files:
            folder_name = basename(dirname(file_path))

            if folder_name not in self.categories.keys():
                new_category = Category()
                new_category.uid = folder_name
                new_category.icon = folder_name
                new_category.name = folder_name.title()
                self.add_category(new_category)
            
            category = self.categories[folder_name] 

            json_content = loads(self.read_from_file(file_path))

            new_lesson = Lesson()
            new_lesson.uid = json_content["id"]
            new_lesson.name = json_content["name"]
            new_lesson.icon = json_content["icon"]
            new_lesson.prerequisites = json_content["prerequisites"]

            for uid, languages in json_content["questions"].items():
                new_question = Question()
                new_question.uid = uid

                for name, data in languages.items():
                    new_language = Language()
                    new_language.name = name
                    new_language.sentence = data["sentence"]
                    if "hints" in data.keys():
                        new_language.hints = data["hints"]
                    new_question.add_language(new_language)

                new_lesson.add_question(new_question)
            category.add_lesson(new_lesson)

    # QUESTIONS
    @log_calls
    def load_explainations(self):
        self.explainations = {}  # Dictionary to store the result

        for subdir, _, files in walk(PATH_EXPLAINATIONS):
            json_files = [f for f in files if f.endswith('.json')]

            for json_file in json_files:
                file_name = json_file.replace(".json", "")
                file_path = join(subdir, json_file)

                with open(file_path, 'r', encoding=FILES_ENCODING) as json_file:
                    try:
                        file_content = load(json_file)
                        self.explainations[file_name] = file_content
                    except JSONDecodeError:
                        print(f"Error decoding JSON in {file_path}")
                        exit()                

    ################################################################### WRITERS
    
    @log_calls
    def write_in_file(self, file_path, content):
        with open(file_path, 'w', encoding=FILES_ENCODING) as file:
            try:
                file.write(content)
            except JSONDecodeError:
                print(f"Error while writing {content[:15]}... in {file_path}.")   
    
    # TEMP
    @log_calls
    def remove_temp_files(self):
        # Check if the folder exists
        if exists(PATH_TEMPORARY_FILES) and isdir(PATH_TEMPORARY_FILES):
            # List all files and subdirectories in the folder
            for filename in listdir(PATH_TEMPORARY_FILES):
                file_path = join(PATH_TEMPORARY_FILES, filename)

                # Check if it's a file (not a subdirectory) and delete it
                if isfile(file_path):
                    remove(file_path)

    # PROFILES
    @log_calls
    def save_profile(self):
        profile_path = join(PATH_PROFILES, self.profile.uid + ".json")
        profile_content = self.read_from_file(profile_path)
        profile = loads(profile_content)
        for category in self.categories.values():
            for lesson in category.lessons.values():
                for question in lesson.questions.values():
                    if category.uid not in profile["categories"].keys():
                        profile["categories"][category.uid] = {}
                    if lesson.uid not in profile["categories"][category.uid].keys():
                        profile["categories"][category.uid][lesson.uid] = {}
                    if question.uid not in profile["categories"][category.uid][lesson.uid].keys():
                        profile["categories"][category.uid][lesson.uid][question.uid] = {}
                    if LEARNED_LANGUAGE not in profile["categories"][category.uid][lesson.uid][question.uid].keys():
                        profile["categories"][category.uid][lesson.uid][question.uid][LEARNED_LANGUAGE] = {}
                    profile["categories"][category.uid][lesson.uid][question.uid][LEARNED_LANGUAGE]["success"] = question.success
                    profile["categories"][category.uid][lesson.uid][question.uid][LEARNED_LANGUAGE]["tries"] = question.tries
        file_content = dumps(profile, indent=4)
        self.write_in_file(profile_path, file_content)   

    ################################################################ VALIDATORS

    # PROFILES
    @log_calls
    def validate_new_profile(self, name, icon, event=None):
        name = name.get().lower()
        if (name != "") and (name not in self.profiles.keys()):
            profile = {
                "icon": icon,
                "categories": {}
            }
            file_path = join(PATH_PROFILES, name + ".json")
            file_content = dumps(profile)
            self.write_in_file(file_path, file_content)
            self.load_profiles()
            self.display_profiles()

    # LANGUAGES
    @log_calls
    def validate_languages(self, spoken_language, learned_language, event=None):
        if (spoken_language == "") or (learned_language == ""):
            self.display_languages()
        elif spoken_language == learned_language:
            self.display_languages()
        else:
            global SPOKEN_LANGUAGE
            global LEARNED_LANGUAGE
            SPOKEN_LANGUAGE = spoken_language
            LEARNED_LANGUAGE = learned_language
            self.display_categories()

    # QUESTIONS
    @log_calls
    def validate_response(self, response, event=None):
        if self.question.propose(response):
            self.playsound(SOUND_CORRECT)
            self.display_questions()
        else:
            self.playsound(SOUND_INCORRECT)
            self.display_answer(response)
        self.save_profile()
        self.check_prerequisites()

    ################################################################# LISTENERS

    # WINDOW
    @log_calls
    def close_app(self, event=None):
        self.remove_temp_files()
        self.destroy()

    # WIDGET
    @log_calls
    def tell_text(self, text, language, event=None):
        file_path = join(PATH_TEMPORARY_FILES, "tts.mp3")
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

        if isinstance(text, StringVar):
            text = text.get()

        if text == "":
            return

        tts = gTTS(text=text, lang=languages[language]["language_code"], tld=languages[language]["accent_code"])

        if isfile(file_path):
            remove(file_path)

        tts.save(file_path)

        while not isfile(file_path):
            sleep(0.1)

        self.playsound(file_path, False)

    @log_calls
    def click_button(self, action, args=[], sound=SOUND_PAGE_FORWARDS, event=None):
        if isinstance(action, Event):
            event = action
            action = None

        elif isinstance(args, Event):
            event = args
            args = []

        elif isinstance(sound, Event):
            event = sound
            sound = SOUND_PAGE_FORWARDS

        if sound:
            self.playsound(sound)

        if type(args) != list:
            args = [args]

        if action:
            action(*args)        
    
    @log_calls
    def enter_widget(self, widget, event=None, sound=SOUND_POP):
        if sound:
            self.playsound(sound)
        widget.configure(style=f'Active.{widget["style"]}')
        for child in widget.winfo_children():
            self.enter_widget(child, sound=None)

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

        self.window_container = Frame(self)
        self.window_container.grid(column=0, row=0)
        self.window_container.columnconfigure(0, weight=1)
        self.window_container.rowconfigure(0, weight=1)

    # FRAMES
    @log_calls
    def create_frame(self, parent, text):
        new_frame = Frame(parent, style="CustomDarkFrame.TFrame")
        new_frame.pack(expand=True, fill=X, pady=10)

        new_label = Label(new_frame, text=text, style="Default.TLabel")
        new_label.pack(side=LEFT, expand=True, fill=X, padx=5, pady=5)
    
    @log_calls
    def create_stat_frame(self, parent, text, stat, alone_in_row=True):
        side = TOP if alone_in_row else LEFT
        frame = Frame(parent, style="CustomDarkFrame.TFrame")
        frame.pack(expand=True, fill=BOTH, padx=5, pady=10, side=side)

        stat_label = Label(frame, text=stat, style="Big.Default.TLabel", anchor="center")
        stat_label.pack(expand=True, fill=Y, padx=5, pady=5)

        text_label = Label(frame, text=text, wraplength=650, style="Small.Default.TLabel", anchor="center")
        text_label.pack(expand=True, fill=X, padx=5, pady=5)

    @log_calls
    def create_scrollable_frame(self, parent, text):
        frame = Frame(parent, style="CustomDarkFrame.TFrame")
        frame.pack(pady=10)

        scrolledtext = ScrolledText(frame, width=45, height=10, background=COLOR_DARK_PINK, foreground=COLOR_WHITE, font=('Calibri', 12), relief=FLAT)
        scrolledtext.pack(fill=BOTH, expand=True)
        scrolledtext.insert(INSERT, text)
        scrolledtext.configure(state="disabled")
        scrolledtext.vbar.configure(width=0)

    @log_calls
    def create_speakable_frame(self, parent, text, language, animate=True):
        new_frame = Frame(parent, style="CustomDarkFrame.TFrame")
        new_frame.pack(expand=True, fill=X, pady=10)

        new_label = Label(new_frame, text=text, style="Default.TLabel")
        new_label.pack(side=LEFT, expand=True, fill=X, padx=5, pady=5)

        if language in ["english", "french"]:
            tts_frame = Frame(new_frame, style="CustomDarkFrame.TFrame")
            tts_frame.pack(side=LEFT)

            tts = Label(tts_frame, image=self.load_image("speak", 25, 25), style="Default.TLabel")
            tts.pack(padx=10, pady=5)

            self.bind_widget(tts, partial(self.click_button, self.tell_text, [text, language], None))

            if animate:
                self.bind_widget(tts_frame, partial(self.enter_widget, tts_frame), EVENT_ENTER_WIDGET, recursive=False)
                self.bind_widget(tts_frame, partial(self.leave_widget, tts_frame), EVENT_LEAVE_WIDGET, recursive=False)

    @log_calls
    def create_image_frame(self, parent, image, text, action, arguments, sound=None, animate=True, over_title=None):
        new_frame = Frame(parent, style="CustomDarkFrame.TFrame")
        new_frame.pack(pady=5, expand=True, fill=X)

        title_frame = Frame(new_frame, style="CustomDarkFrame.TFrame")
        title_frame.pack(expand=True, fill=BOTH)

        title_frame_picture = Label(title_frame, image=self.load_image(image, 35, 35), style="Default.TLabel")
        title_frame_picture.pack(padx=15, pady=5, side=LEFT)

        title_frame_text_text = text.replace("-", " ").title()
        title_frame_text = Label(title_frame, text=title_frame_text_text, style="Default.TLabel")
        title_frame_text.pack(ipadx=15, ipady=5, side=LEFT, expand=True, fill=X)

        self.bind_widget(new_frame, partial(self.click_button, action, arguments))

        if animate:
            self.bind_widget(new_frame, partial(self.enter_widget, new_frame), EVENT_ENTER_WIDGET, recursive=False)
            self.bind_widget(new_frame, partial(self.leave_widget, new_frame), EVENT_LEAVE_WIDGET, recursive=False)

        if over_title:                
            self.bind_widget(new_frame, partial(self.set_window_title, over_title), EVENT_ENTER_WIDGET, recursive=False)
            self.bind_widget(new_frame, partial(self.set_window_title, self.title()), EVENT_LEAVE_WIDGET, recursive=False)

    @log_calls
    def create_progress_frame(self, parent, image, text, progress, stars, action=None, arguments=None, locked=False, animate=True, over_title=None):

        frame_style = "Disabled.CustomDarkFrame.TFrame" if locked else "CustomDarkFrame.TFrame"
        label_style = "Disabled.Default.TLabel" if locked else "Default.TLabel"

        new_frame = Frame(parent, style=frame_style)
        new_frame.pack(pady=5, expand=True, fill=X)

        title_frame = Frame(new_frame, style=frame_style)
        title_frame.pack(expand=True, fill=BOTH)

        image = self.load_image(image, 35, 35, grey=locked)
        title_frame_picture = Label(title_frame, image=image, style=label_style)
        title_frame_picture.pack(padx=15, pady=5, side=LEFT)

        title_frame_text_text = text.replace("-", " ").title()
        title_frame_text = Label(title_frame, text=title_frame_text_text, style=label_style)
        title_frame_text.pack(ipadx=15, ipady=5, side=LEFT, expand=True, fill=X)

        if locked:
            image = self.load_image("lock", 25, 25, True)
        else:
            image = self.load_image(f'{stars}-star', 53, 25)            

        stars_image = Label(title_frame, image=image, style=label_style)
        stars_image.pack(padx=15, pady=5, side=LEFT)
    
        frame_style = "Disabled.CustomDarkFrame.TFrame" if locked else "CustomMidFrame.TFrame"
        progressbar_frame = Frame(new_frame, style=frame_style)
        progressbar_frame.pack(expand=True, fill=X)

        self.update()

        progressbar_frame_left_width = new_frame.winfo_width() * progress
        progressbar_frame_left = Frame(progressbar_frame, height=5, width=progressbar_frame_left_width, style=frame_style)
        progressbar_frame_left.pack(side=LEFT)
        
        frame_style = "Disabled.CustomDarkFrame.TFrame" if locked else "CustomLightFrame.TFrame"
        progressbar_frame_right = Frame(progressbar_frame, height=5, style=frame_style)
        progressbar_frame_right.pack(expand=True, fill=X, side=LEFT)

        if action and not locked:
            self.bind_widget(new_frame, partial(self.click_button, action, arguments))

        if animate:
            if locked:
                self.bind_widget(new_frame, partial(self.click_button, sound=SOUND_BLOCKED), EVENT_LEFT_CLICK, recursive=True)

            self.bind_widget(new_frame, partial(self.enter_widget, new_frame), EVENT_ENTER_WIDGET, recursive=False)
            self.bind_widget(new_frame, partial(self.leave_widget, new_frame), EVENT_LEAVE_WIDGET, recursive=False)

        if over_title:                
            self.bind_widget(new_frame, partial(self.set_window_title, over_title), EVENT_ENTER_WIDGET, recursive=False)
            self.bind_widget(new_frame, partial(self.set_window_title, self.title()), EVENT_LEAVE_WIDGET, recursive=False)

    # BUTTONS
    @log_calls
    def create_button(self, parent, image, text, action, arguments=[], sound=None, image_first=True, alone_in_row=True, animate=True):
        side = TOP if alone_in_row else LEFT
        new_frame = Frame(parent, style="CustomDarkFrame.TFrame")
        new_frame.pack(padx=10, pady=10, expand=True, fill=X, side=side)

        side = LEFT if image_first else RIGHT
        
        if not text:
            anchor = CENTER
        elif image_first:
            anchor = E 
        else:
            anchor = W

        new_image = Label(new_frame, image=self.load_image(image, 25, 25), anchor=anchor, style="Default.TLabel")
        new_image.pack(side=side, padx=5, expand=True, fill=BOTH)

        if text:
            anchor = W if image_first else E
            new_label = Label(new_frame, text=text, anchor=anchor, style="Default.TLabel")
            new_label.pack(side=side, padx=5, expand=True, fill=BOTH)
        
        self.bind_widget(new_frame, partial(self.click_button, action, arguments, sound))

        if animate:
            self.bind_widget(new_frame, partial(self.enter_widget, new_frame), EVENT_ENTER_WIDGET, recursive=False)
            self.bind_widget(new_frame, partial(self.leave_widget, new_frame), EVENT_LEAVE_WIDGET, recursive=False)

    # ENTRIES
    @log_calls
    def create_entry(self, parent):
        new_frame = Frame(parent, style="CustomDarkFrame.TFrame")
        new_frame.pack(expand=True, fill=X, pady=10)
        
        new_Stringvar = StringVar()
        # The Entry widget from ttk does not support the "background" argument
        new_entry = Entry(new_frame, width=45, textvariable=new_Stringvar, background=COLOR_DARK_PINK, foreground=COLOR_WHITE, relief="flat", insertbackground=COLOR_WHITE, font=('Calibri', 12))
        new_entry.pack(side=LEFT, expand=True, fill=BOTH, padx=5, pady=5)
        new_entry.focus()

        return new_frame, new_Stringvar

    @log_calls
    def create_speakable_entry(self, parent, language):

        new_frame, new_Stringvar = self.create_entry(parent)

        if language in ["english", "french"]:
            tts_frame = Frame(new_frame, style="CustomDarkFrame.TFrame")
            tts_frame.pack(side=LEFT)

            tts = Label(tts_frame, image=self.load_image("speak", 25, 25), style="Default.TLabel")
            tts.pack(padx=10, pady=5)

            self.bind_widget(tts, partial(self.click_button, self.tell_text, [new_Stringvar, language], None))

        return new_frame, new_Stringvar

    ################################################################ DISPLAYERS
   
    # PROFILES
    @log_calls
    def display_profiles(self, page=1, event=None):
        item_by_page = 4
        total_pages = ceil(self.get_profiles_count() / item_by_page)
        current_page = 1 if (page < 1) or (page > total_pages) else page

        # Configure page grid
        self.clear_window()
        self.set_window_title("Pick your profile !")
        self.window_container.grid(column=1, row=1)

        # Initialize variables
        start_index = (current_page - 1) * item_by_page
        end_index = (start_index + item_by_page) if (self.get_profiles_count() >= (start_index + item_by_page)) else self.get_profiles_count()

        # Iterate through profiles
        for profile in list(self.profiles.values())[start_index:end_index]:
            self.create_image_frame(parent=self.window_container, 
                image=profile.icon, 
                text=profile.name,
                action=self.select_profile,
                arguments=profile)

        # NEW PROFILE BUTTON
        self.create_button(self.window_container, "plus", "New Profile", self.display_new_profile)

        # QUIT BUTTON
        self.create_button(self.window_container, "arrow_left", "Quit", self.close_app, alone_in_row=False)

        # PREVIOUS BUTTON
        if current_page > 1:
            self.create_button(self.window_container, "previous", "Previous", self.display_profiles, arguments=current_page -1, sound=SOUND_PAGE_BACKWARDS, image_first=False, alone_in_row=False)
        
        # NEXT BUTTON
        if current_page < total_pages:
            self.create_button(self.window_container, "next", "Next", self.display_profiles, arguments=current_page +1, sound=SOUND_PAGE_FORWARDS, image_first=False, alone_in_row=False)

    @log_calls
    def display_new_profile(self, event=None):
        self.clear_window()
        self.title("Write your name !")
        entry, stringvar = self.create_entry(self.window_container)

        images = self.get_files(PATH_ICONS, "png")
        bunnies = []
        for image in images:
            image = basename(image)
            image = image.replace(".png", "")
            if image[:7] == "rabbit-":
                bunnies.append(image)

        for bunny in bunnies:
            self.create_button(self.window_container, bunny, None, self.validate_new_profile, [stringvar, bunny], alone_in_row=False)

    # LANGUAGES
    @log_calls
    def display_languages(self, page=1, event=None):
        # Configure page grid
        self.clear_window()
        self.set_window_title("Pick a language to learn !")
        self.window_container.grid(column=1, row=1)

        for spoken_language in self.languages:
            for learned_language in self.languages:
                if spoken_language == learned_language:
                    continue

                frame = Frame(self.window_container, style="CustomDarkFrame.TFrame")
                frame.pack(pady=5, expand=True, fill=X)

                spoken_language_picture = Label(frame, image=self.load_image(spoken_language, 35, 35), style="Default.TLabel", anchor=CENTER)
                spoken_language_picture.pack(padx=10, pady=5, side=LEFT, expand=True, fill=X)

                arrow_picture = Label(frame, image=self.load_image("next", 35, 35), style="Default.TLabel", anchor=CENTER)
                arrow_picture.pack(padx=10, pady=5, side=LEFT)

                learned_language_picture = Label(frame, image=self.load_image(learned_language, 35, 35), style="Default.TLabel", anchor=CENTER)
                learned_language_picture.pack(padx=10, pady=5, side=LEFT, expand=True, fill=X)

                self.bind_widget(frame, partial(self.click_button, self.validate_languages, [spoken_language, learned_language]))
                self.bind_widget(frame, partial(self.enter_widget, frame), EVENT_ENTER_WIDGET, recursive=False)
                self.bind_widget(frame, partial(self.leave_widget, frame), EVENT_LEAVE_WIDGET, recursive=False)
                self.bind_widget(frame, partial(self.set_window_title, f"From {spoken_language.title()} to {learned_language.title()}"), EVENT_ENTER_WIDGET, recursive=False)
                self.bind_widget(frame, partial(self.set_window_title, self.title()), EVENT_LEAVE_WIDGET, recursive=False)

        # RETURN BUTTON
        self.create_button(self.window_container, "arrow_left", "Profiles", self.display_profiles, arguments=1, sound=SOUND_PAGE_BACKWARDS)

    # STARS
    @log_calls
    def display_new_star(self, parent, max_height, height=1):
        for child in parent.winfo_children()[1:]:
            child.destroy()
        Label(parent, image=self.load_image(f'{self.lesson.stars}-star', int(height * 2.09), height), anchor="center").pack(side="left", expand=True, fill=X)
        Label(parent, image=self.load_image(f'0-star', 105, 50), anchor="center").pack(side="left", expand=True, fill=X)
        if height < max_height:
            self.after(15, partial(self.display_new_star, parent, max_height, height+7))
    
    # CATEGORIES
    @log_calls
    def display_categories(self, page=1, event=None):
        # place the locked categories at the end
        categories = list(sorted(self.categories.values(), key=lambda category: category.is_locked))
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
            self.create_progress_frame(parent=self.window_container, 
                image=category.icon, 
                text=category.uid, 
                progress=category.progress, 
                stars=category.stars, 
                action=self.select_category, 
                arguments=category,
                locked=category.is_locked)

        # RETURN BUTTON
        self.create_button(self.window_container, "arrow_left", "Languages", self.display_languages, arguments=1, sound=SOUND_PAGE_BACKWARDS, alone_in_row=(total_pages == 1))
        
        # PREVIOUS BUTTON
        if current_page > 1:
            self.create_button(self.window_container, "previous", "Previous", self.display_categories, arguments=current_page -1, sound=SOUND_PAGE_BACKWARDS, image_first=False, alone_in_row=False)
        
        # NEXT BUTTON
        if current_page < total_pages:
            self.create_button(self.window_container, "next", "Next", self.display_categories, arguments=current_page +1, sound=SOUND_PAGE_FORWARDS, image_first=False, alone_in_row=False)

    # LESSONS
    @log_calls
    def display_lessons(self, page=1, event=None):
        # Place the locked lessons at the end
        lessons = sorted(self.category.lessons.values(), key=lambda lesson: lesson.is_locked)
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
            prerequisites_text = []
            for category, lessons in self.lessons[lesson.uid].prerequisites.items():
                for lesson_uid, stars in lessons.items():
                    prerequisites_text.append(f"{self.lessons[lesson_uid].name} {'⭐' * stars}")
            over_title = f"Requirements: " + ", ".join(prerequisites_text)
            self.create_progress_frame(parent=self.window_container, 
                image=lesson.icon, 
                text=lesson.name, 
                progress=lesson.progress, 
                stars=lesson.stars,
                action=self.select_lesson, 
                arguments=lesson,
                locked=lesson.is_locked,
                over_title=over_title)

        # RETURN BUTTON
        self.create_button(self.window_container, "arrow_left", "Categories", self.display_categories, arguments=1, sound=SOUND_PAGE_BACKWARDS, alone_in_row=(total_pages == 1))
        
        # PREVIOUS BUTTON
        if current_page > 1:
            self.create_button(self.window_container, "previous", "Previous", self.display_lessons, arguments=current_page -1, sound=SOUND_PAGE_BACKWARDS, image_first=False, alone_in_row=False)
        
        # NEXT BUTTON
        if current_page < total_pages:
            self.create_button(self.window_container, "next", "Next", self.display_lessons, arguments=current_page +1, sound=SOUND_PAGE_FORWARDS, image_first=False, alone_in_row=False)

    # QUESTIONS
    @log_calls
    def display_questions(self):
        self.next_question()

        # Configure page grid
        self.clear_window()
        self.set_window_title("Translate this sentence !")
        self.window_container.grid(column=1, row=1)

        # STARS
        stars_frame = Frame(self.window_container)
        stars_frame.pack(expand=True, fill=BOTH, pady=10) 

        Label(stars_frame, image=self.load_image(f'0-star', 105, 50), anchor="center").pack(side="left", expand=True, fill=X)
        
        if self.lesson.stars > self.last_lesson_stars:
            self.last_lesson_stars = self.lesson.stars
            self.after(350, partial(self.playsound, SOUND_NEW_STAR))
            self.after(250, partial(self.display_new_star, stars_frame, 50))
        else:
            Label(stars_frame, image=self.load_image(f'{self.lesson.stars}-star', 105, 50), anchor="center").pack(side="left", expand=True, fill=X)
            Label(stars_frame, image=self.load_image(f'0-star', 105, 50), anchor="center").pack(side="left", expand=True, fill=X)

        # STATS
        stat_frame = Frame(self.window_container)
        stat_frame.pack(expand=True, fill=X, pady=10) 

        lesson_overview = f'{ceil(self.lesson.progress * 100)}%'
        self.create_stat_frame(stat_frame, text="Lesson Overview", stat=lesson_overview, alone_in_row=False)

        lesson_success_text = f'{ceil(self.lesson.success * 100)}%'
        self.create_stat_frame(stat_frame, text="Lesson Success", stat=lesson_success_text, alone_in_row=False)
        self.create_stat_frame(stat_frame, text="Question Attempts", stat=self.question.tries, alone_in_row=False)

        question_success_text = f'{ceil(self.question.success * 100)}%'
        self.create_stat_frame(stat_frame, text="Question Success", stat=question_success_text, alone_in_row=False)

        # SENTENCE
        self.create_speakable_frame(self.window_container, self.question.sentence.capitalize(), SPOKEN_LANGUAGE)

        # HINTS
        if self.question.hints:
            self.create_frame(self.window_container, f'PS : {self.question.hints.capitalize()}')

        # ANSWER
        speakable_entry, response_Stringvar = self.create_speakable_entry(self.window_container, LEARNED_LANGUAGE)

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
        
        # SENTENCE
        self.create_speakable_frame(self.window_container, self.question.sentence.capitalize(), SPOKEN_LANGUAGE)

        # RESONSE
        new_frame = Frame(self.window_container, style="CustomDarkFrame.TFrame")
        new_frame.pack(expand=True, fill=X, pady=10)

        new_text = Text(new_frame, width=40, height=1, relief="flat", background=COLOR_DARK_PINK, foreground=COLOR_WHITE, font=('Calibri', 12))
        new_text.insert("1.0", response.capitalize())
        self.color_differences(new_text, self.question.answer.capitalize(), response.capitalize())

        # ANSWER
        self.create_speakable_frame(self.window_container, self.question.answer.capitalize(), LEARNED_LANGUAGE)                

        # EXPLAINATIONS
        explainations = self.get_question_explainations()
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
        style = Style(self) 
        style.configure(".", background=COLOR_LIGHT_GREY, font=('Calibri', 12))

        style.configure("CustomLightFrame.TFrame", background=COLOR_LIGHT_PINK)
        style.configure("CustomMidFrame.TFrame", background=COLOR_MID_PINK)

        style.configure("CustomDarkFrame.TFrame", background=COLOR_DARK_PINK)
        style.configure("Active.CustomDarkFrame.TFrame", background=COLOR_MID_PINK)
        style.configure("Disabled.CustomDarkFrame.TFrame", background=COLOR_DARK_GREY)
        style.configure("Active.Disabled.CustomDarkFrame.TFrame", background=COLOR_MID_GREY)

        style.configure("Default.TLabel", background=COLOR_DARK_PINK, foreground=COLOR_WHITE)
        style.configure("Active.Default.TLabel", background=COLOR_MID_PINK)
        style.configure("Disabled.Default.TLabel", background=COLOR_DARK_GREY)
        style.configure("Active.Disabled.Default.TLabel", background=COLOR_MID_GREY)
        style.configure("Small.Default.TLabel", font=('Calibri', 8))
        style.configure("Big.Default.TLabel", font=('Calibri', 16))

    @log_calls
    def playsound(self, sound, wait=False):
        if not isfile(sound):
            sound = join(PATH_SOUNDS, sound)
        if isfile(sound):
            Thread(target=playsound, args=(sound, wait), daemon=True).start()
    
    # WIDGETS
    @log_calls
    def bind_widget(self, widget, command, event=EVENT_LEFT_CLICK, recursive=True):
        widget.bind(event, command)
        if recursive:
            for child in widget.winfo_children():
                self.bind_widget(child, command, event)

    @log_calls
    def resize_image(self, raw_image, width, height):
        return raw_image.resize((width, height))
    
    @log_calls
    def color_image(self, image):
        image = image.convert("LA")
        return image.convert("RGBA")

    # PROFILES
    @log_calls
    def add_profile(self, profile):
        self.profiles[profile.uid] = profile

    @log_calls
    def select_profile(self, profile, event=None):
        self.profile = profile
        self.load_profile()
        self.load_explainations()
        self.display_languages()
    
    # CATEGORIES
    @log_calls
    def add_category(self, category):
        self.categories[category.uid] = category

    @log_calls
    def select_category(self, category, event=None):
        self.category = category
        self.display_lessons()

    # LESSONS
    @log_calls
    def select_lesson(self, lesson, event=None):
        self.lesson = lesson
        self.last_lesson_stars = self.lesson.stars
        self.display_questions()

    @log_calls
    def check_prerequisites(self):
        for category in self.categories.values():
            for lesson in category.lessons.values():
                lesson.is_locked = False
                for req_category_id in lesson.prerequisites:
                    for req_lesson_id, required_stars in lesson.prerequisites[req_category_id].items():
                        if self.categories[req_category_id].lessons[req_lesson_id].stars < required_stars:
                            lesson.is_locked = True
                            break
                    if lesson.is_locked:
                        break

    # QUESTIONS
    @log_calls
    def next_question(self):
        self.question = self.category.next_question()

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

        text_widget.pack(side=LEFT, expand=True, fill=X, padx=5, pady=5)
        text_widget.configure(state="disabled")

##################################################################### MAIN CODE

if __name__ == "__main__":
    Bilingual().mainloop()