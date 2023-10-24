import tkinter as tk
import json
import random
import os

from math import ceil
from tkinter import ttk
from PIL import Image, ImageTk

speaken_language = "english"
learned_language = "french"

def resize_image(path, width, height):
    image = Image.open(path)
    resize_img = image.resize((width, height))
    img = ImageTk.PhotoImage(resize_img)
    return img


class Questions:
    def __init__(self, parent, categories):
        self.parent = parent
        self.categories = categories

    def select_category(self, category):
        self.category = category

    def choose_question(self, category):
        # Select a random question
        questions = []
        for question_list in self.categories[category].values():
            questions += question_list
        print(questions)
        choice = random.choice(questions)

        self.question = choice[speaken_language]["sentence"]
        self.answer = choice[learned_language]["sentence"]
        
        if "hints" in choice[speaken_language].keys():
            self.hints = choice[speaken_language]["hints"]
        
        if "explaination" in choice[learned_language].keys():
            self.explaination = choice[learned_language]["explaination"]

    def validate_response(self, response):
        response = response.lower().strip()
        answer = self.answer.lower().strip()

        if response == answer:
            self.display_page()
        else:
            self.question_label.text = self.hints
            self.show = self.answer

    def display_page(self):
        self.choose_question(self.category)

        container = ttk.Frame(self.parent.root)
        container.grid(column=0, row=0, padx=30, pady=20)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)
        container.rowconfigure(2, weight=1)

        self.question_label = ttk.Label(container, text=self.question)
        self.question_label.grid(column=0, row=0, pady=10, ipadx=5)
        
        response = tk.StringVar()
        self.entry = ttk.Entry(container, width=100, textvariable=response)
        self.entry.focus()
        self.entry.grid(column=0, row=1, pady=10, ipadx=5)

        self.icon = resize_image('./assets/icons/leave.png', 20, 20)
        leave_button = ttk.Button(container, image=self.icon, text="  Leave", compound="left", command=lambda: self.parent.display_categories_page())
        leave_button.grid(column=0, row=2, pady=10, ipadx=5, sticky=tk.W)

        self.icon2 = resize_image('./assets/icons/check.png', 20, 20)
        validate_button = ttk.Button(container, image=self.icon2, text="  Validate", compound="left", command=lambda: self.validate_response(response.get()))
        validate_button.grid(column=0, row=2, pady=10, ipadx=5, sticky=tk.E)


class Categories:
    def __init__(self, parent, categories):
        self.parent = parent
        self.categories = categories
        self.tiles_by_line = 4
        self.lines_by_page = 3
        self.tiles_by_page = self.tiles_by_line * self.lines_by_page
        self.total_pages = ceil(len(self.categories) / self.tiles_by_page)
        self.current_page = 1

    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.parent.clear_window()
            self.display_page()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.parent.clear_window()
            self.display_page()

    def display_page(self):
        container = ttk.Frame(self.parent.root)
        container.grid(column=0, row=0, padx=30, pady=20)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=4)
        container.rowconfigure(1, weight=1)

        tiles_container = ttk.Frame(container)
        tiles_container.grid(column=0, row=0)

        categories_title = list(self.categories.keys())
        start_index = (self.current_page -1) * self.tiles_by_page
        x = 0
        y = 0
        self.icon = tk.PhotoImage(file='./assets/icons/beach.png')

        for c in categories_title[start_index:]:
            tile = ttk.Button(tiles_container, image=self.icon, command=lambda: self.parent.display_questions_page(c))
            tile.grid(column=x, row=y, padx=15, pady=10, ipadx=10, ipady=10)
            #tile.columnconfigure(0, weight=1)
            #tile.rowconfigure(0, weight=1)

            if x < (self.tiles_by_line -1):
                x += 1
            else:
                x = 0
                if y < (self.lines_by_page -1):
                    y +=1
                else:
                    break

        buttons_container = ttk.Frame(container)
        buttons_container.grid(column=0, row=1)
        buttons_container.columnconfigure(0, weight=1)
        buttons_container.columnconfigure(1, weight=1)

        button = ttk.Button(buttons_container, text="< Previous", command=self.previous_page)
        button.grid(column=0, row=0, padx=30, pady=20)

        button = ttk.Button(buttons_container, text="Next >", command=self.next_page)
        button.grid(column=1, row=0, padx=30, pady=20)


class Application():
    def __init__(self):
        self.load_categories()
        self.root = tk.Tk()
        self.total_pages = {}
        self.total_pages["categories"] = Categories(self, self.categories)
        self.total_pages["questions"] = Questions(self, self.categories)
        self.display_window()
        self.display_categories_page()
        self.root.mainloop()

    def load_categories(self):
        self.categories = {}  # Dictionary to store the result

        for subdir, _, files in os.walk("./assets/categories"):
            folder_name = os.path.basename(subdir)
            json_files = [f for f in files if f.endswith('.json')]

            if json_files:
                self.categories[folder_name] = {}

                for json_file in json_files:
                    file_name = os.path.splitext(json_file)[0]  # Remove the .json extension
                    file_path = os.path.join(subdir, json_file)

                    with open(file_path, 'r', encoding='utf-8') as json_file:
                        try:
                            file_content = json.load(json_file)
                            self.categories[folder_name][file_name] = file_content
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON in {file_path}")
                            exit()

    def display_window(self):
        self.root.title("Train Me...")
        self.root.iconbitmap('./assets/icons/icon.ico')

        self.window_width = 1200
        self.window_height = 800

        # get the screen dimension
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # find the center point
        center_x = int((screen_width  /2) - (self.window_width  /2))
        center_y = int((screen_height /2) - (self.window_height /2))

        # set the position of the window to the center of the screen
        self.root.geometry(f'{self.window_width}x{self.window_height}+{center_x}+{center_y}')
        self.root.resizable(False, False)

        # configure the style
        #self.root.configure(bg="blue")
        
        # configure the grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def clear_window(self):
        # Destroy all widgets in the window
        for widget in self.root.winfo_children():
            widget.destroy()

    def display_categories_page(self):
        self.clear_window()
        self.total_pages["categories"].display_page()

    def display_questions_page(self, category):
        self.clear_window()
        self.total_pages["questions"].select_category(category)
        self.total_pages["questions"].display_page()


if __name__ == "__main__":
    app = Application()