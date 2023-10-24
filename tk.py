import tkinter as tk
import json
import random
import os

from math import ceil
from tkinter import ttk
from PIL import Image, ImageTk
from functools import partial

spoken_language = "english"
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
        self.icons = {}

    def select_category(self, category):
        self.questions = []
        for question_list in self.categories[category].values():
            self.questions += question_list
        random.shuffle(self.questions)

    def choose_question(self):
        # Select a random question
        choice = self.questions.pop()
        self.question = choice[spoken_language]["sentence"]
        self.answer = choice[learned_language]["sentence"]
        self.hints = None
        self.explaination = None

        if "hints" in choice[spoken_language].keys():
            self.hints = choice[spoken_language]["hints"]
        
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
        self.choose_question()

        container = ttk.Frame(self.parent)
        container.grid(column=0, row=0, padx=30, pady=20)

        self.question_text = f"Translate from {spoken_language.capitalize()} to {learned_language.capitalize()}:\n\n{self.question.capitalize()}"
        self.question_label = ttk.Label(container, text=self.question_text, font=("Roboto", 14), justify=tk.CENTER)
        self.question_label.grid(column=0, row=0, pady=10, ipadx=5)

        if self.hints:
            self.hints_text = f"Hints: {self.hints.capitalize()}"
            self.hints_label = ttk.Label(container, text=self.hints_text, justify=tk.CENTER)
            self.hints_label.grid(column=0, row=1, pady=10, ipadx=5)
        
        response_var = tk.StringVar()
        self.entry = ttk.Entry(container, width=50, textvariable=response_var)
        self.entry.focus()
        self.entry.grid(column=0, row=2, pady=10, ipadx=5)

        self.icons["leave"] = resize_image('./assets/icons/leave.png', 20, 20)
        leave_button = ttk.Button(container, width=10, image=self.icons["leave"], text="   Leave", compound="left", command=lambda: self.parent.master.display_categories_page())
        leave_button.grid(column=0, row=3, pady=10, ipadx=5, sticky=tk.W)

        self.icons["check"] = resize_image('./assets/icons/check.png', 20, 20)
        check_button = ttk.Button(container, width=10, image=self.icons["check"], text="  Validate", compound="left", command=lambda: self.validate_response(response_var.get()))
        check_button.grid(column=0, row=3, pady=10, ipadx=5, sticky=tk.E)


class CategoriesPage(ttk.Frame):

    def __init__(self, parent, data):
        super().__init__(parent)
        self.parent = parent
        self.data = data
        self.tiles_by_line = 4
        self.lines_by_page = 3
        self.tiles_by_page = self.tiles_by_line * self.lines_by_page
        self.total_pages = ceil(len(self.data) / self.tiles_by_page)
        self.current_page = 1
        self.icons = {}

    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            #self.parent.master.clear_window()
            self.display_page()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            #self.parent.master.clear_window()
            self.display_page()

    def display_page(self):
        self.grid(column=0, row=0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=4)
        self.rowconfigure(1, weight=1)

        # Create a sub-container for tiles
        tiles_container = ttk.Frame(self)
        tiles_container.grid(column=0, row=0)

        # Get category titles and initialize variables
        categories_title = list(self.data.keys())
        start_index = (self.current_page - 1) * self.tiles_by_page
        tile_column, tile_row = 0, 0

        # Iterate through categories
        for category in categories_title[start_index:]:
            self.icons[category] = resize_image(f'./assets/icons/{category}.png', width=50, height=50)

            new_tile = ttk.Button(tiles_container, image=self.icons[category], text=category.capitalize(), compound="top", command=partial(self.parent.master.display_questions_page, category))
            new_tile.grid(column=tile_column, row=tile_row, padx=15, pady=10, ipadx=2, ipady=2)

            # Define the position of the next tile if any
            tile_column += 1
            if tile_column >= self.tiles_by_line:
                tile_column = 0
                tile_row += 1
                if tile_row >= self.lines_by_page:
                    break

        buttons_container = ttk.Frame(self)
        buttons_container.grid(column=0, row=1)
        buttons_container.columnconfigure(0, weight=1)
        buttons_container.columnconfigure(1, weight=1)

        buttons_state = "disabled" if self.total_pages != 1 else "!disabled"

        self.icons["previous"] = resize_image(f'./assets/icons/previous.png', width=20, height=20)
        previous_button = ttk.Button(buttons_container, state=buttons_state, image=self.icons["previous"], compound="left", text="Previous", command=self.previous_page)
        previous_button.grid(column=0, row=0, padx=30, pady=20)

        self.icons["next"] = resize_image(f'./assets/icons/next.png', width=20, height=20)
        next_button = ttk.Button(buttons_container, state=buttons_state, image=self.icons["next"], compound="right", text="Next", command=self.next_page)
        next_button.grid(column=1, row=0, padx=30, pady=20)


class Bilingual(tk.Tk):

    def __init__(self):
        super().__init__()
        self.load_data()
        self.define_styles()
        self.create_window()
        self.pages = {}
        self.pages["categories"] = CategoriesPage(self.window_container, self.data)
        self.pages["questions"] = Questions(self.window_container, self.data)
        self.display_categories_page()

    def define_styles(self):
        self.style = ttk.Style(self)
        self.style.configure("TButton", font=('Calibri', 12))
        self.style.configure("TFrame", font=('Calibri', 12))
        self.style.configure("TLabel", font=('Calibri', 12))
        self.style.configure("TEntry", font=('Calibri', 12))

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

    def create_window(self):
        self.title("Train Me...")
        self.iconbitmap('./assets/icons/icon.ico')

        window_width = 600
        window_height = 400

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
        self.rowconfigure(0, weight=1)

        self.window_container = ttk.Frame(self)
        self.window_container.grid(column=0, row=0)
        self.window_container.columnconfigure(0, weight=1)
        self.window_container.rowconfigure(0, weight=1)

    def clear_window(self):
        # Destroy all widgets in the window
        for widget in self.window_container.winfo_children():
            widget.destroy()

    def display_categories_page(self):
        #self.clear_window()
        self.pages["categories"].display_page()

    def display_questions_page(self, category):
        #self.clear_window()
        self.pages["questions"].select_category(category)
        self.pages["questions"].display_page()


if __name__ == "__main__":
    app = Bilingual()
    app.mainloop()