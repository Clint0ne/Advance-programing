import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import os

#  API LINKS 
# Search meal by name
SEARCH_URL = "https://www.themealdb.com/api/json/v1/1/search.php?s="

# Get a random meal
RANDOM_URL = "https://www.themealdb.com/api/json/v1/1/random.php"

# Filter meals by category
FILTER_URL = "https://www.themealdb.com/api/json/v1/1/filter.php?c="


class ClintApp:
    def __init__(self, root):
        # Main app window
        self.root = root
        self.root.title("Clint's Recipe Workspace")

        # Get folder where this file is saved
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        #  APP ICON 
        # Try to set window icon (logo)
        try:
            icon_path = os.path.join(self.script_dir, "logo.ico")
            icon_img = Image.open(icon_path)
            self.icon_photo = ImageTk.PhotoImage(icon_img)
            self.root.iconphoto(True, self.icon_photo)
            self.icon_ref = self.icon_photo  # keep icon from disappearing
        except Exception as e:
            print("Icon error:", e)

        # Window size and lock resize
        self.root.geometry("850x650")
        self.root.resizable(False, False)

        # File where favorites are saved
        self.fav_file = "favorites.txt"

        # Current recipe name
        self.current_meal_name = None

        # COLORS 
        self.clr_bg = "#1A1A1A"
        self.clr_gray = "#333333"
        self.clr_accent = "#00ADB5"
        self.clr_hover = "#00FFF5"
        self.clr_text = "#EEEEEE"
        self.clr_danger = "#E94560"

        #  CANVAS 
        # Canvas is used for background and layout
        self.canvas = tk.Canvas(root, width=850, height=650, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Background image
        try:
            bg_path = os.path.join(self.script_dir, "monitor.png")
            bg_img = Image.open(bg_path).resize((850, 650), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_img)
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        except:
            self.canvas.config(bg=self.clr_bg)

        #  TOP BAR 

        # Search input box
        self.searchbox = tk.Entry(
            root, font=("Helvetica", 10), width=15,
            bg=self.clr_gray, fg="white", bd=0,
            insertbackground="white"
        )
        self.canvas.create_window(235, 108, window=self.searchbox, height=22)

        # Category dropdown
        self.cat_var = tk.StringVar(value="Select Category")
        self.category_menu = ttk.Combobox(
            root, textvariable=self.cat_var,
            state="readonly", width=14
        )
        self.category_menu['values'] = (
            "Beef", "Chicken", "Dessert",
            "Pasta", "Seafood", "Starter",
            "Vegan", "Vegetarian"
        )
        self.canvas.create_window(365, 108, window=self.category_menu)

        # Buttons
        self.make_button("SEARCH", self.run_search, 460, 108)
        self.make_button("RANDOM", self.run_random, 540, 108)
        self.make_button("FILTER", self.run_filter, 620, 108, accent=True)
        self.make_button("MY LIST", self.show_favorites_window, 715, 108, gray=True)

        # Save button
        self.make_button("SAVE", self.save_favorite, 715, 140, accent=True)

        # -------- OUTPUT AREA --------
        self.display_frame = tk.Frame(root, bg=self.clr_bg)
        self.canvas.create_window(425, 305, window=self.display_frame, width=580, height=280)

        # Image output
        self.img_output = tk.Label(self.display_frame, bg=self.clr_bg)
        self.img_output.pack(side="right", padx=10)

        # Text output
        self.text_output = tk.Text(
            self.display_frame, font=("Helvetica", 9),
            bg=self.clr_bg, fg=self.clr_text,
            bd=0, wrap="word"
        )
        self.text_output.pack(side="left", fill="both", expand=True)

    #  BUTTON CREATOR 
    def make_button(self, text, cmd, x, y, accent=False, gray=False):
        # Pick button color
        bg_color = self.clr_accent if accent else self.clr_gray if gray else "#444"

        # Create button
        btn = tk.Button(
            self.root, text=text, command=cmd,
            bg=bg_color, fg="white",
            relief="flat", font=("Helvetica", 7, "bold"),
            width=9, cursor="hand2"
        )

        # Hover effect
        btn.bind("<Enter>", lambda e: btn.config(bg=self.clr_hover, fg="black"))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg_color, fg="white"))

        # Place button on canvas
        self.canvas.create_window(x, y, window=btn)

    # API ACTIONS
    def run_search(self):
        # Search by name
        q = self.searchbox.get()
        if q:
            self.fetch_data(SEARCH_URL + q)
        else:
            messagebox.showwarning("Warning", "Enter a food name.")

    def run_random(self):
        # Get random recipe
        self.fetch_data(RANDOM_URL)

    def run_filter(self):
        # Filter by category
        cat = self.cat_var.get()
        if cat == "Select Category":
            messagebox.showwarning("Warning", "Please pick a category first!")
            return
        self.fetch_data(FILTER_URL + cat)

    def fetch_data(self, url):
        # Get data from API
        try:
            res = requests.get(url, timeout=5).json()

            if not res or not res['meals']:
                messagebox.showinfo("Not Found", "No results found.")
                return

            item = res['meals'][0]

            # If filtered, get full details
            if "strInstructions" not in item:
                item = requests.get(
                    f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={item['idMeal']}"
                ).json()['meals'][0]

            self.display_meal(item)

        except:
            messagebox.showerror("Connection Error", "API unreachable.")

    def display_meal(self, item):
        # Show recipe text
        self.current_meal_name = item["strMeal"]
        self.text_output.delete(1.0, "end")

        self.text_output.insert("end", f"{item['strMeal'].upper()}\n", "title")
        self.text_output.insert("end", f"{item['strCategory']} | {item['strArea']}\n\n")
        self.text_output.insert("end", "INSTRUCTIONS:\n", "bold")
        self.text_output.insert("end", item["strInstructions"])

        # Text styles
        self.text_output.tag_configure("title", font=("Helvetica", 12, "bold"), foreground=self.clr_accent)
        self.text_output.tag_configure("bold", font=("Helvetica", 10, "bold"), foreground=self.clr_accent)

        # Show recipe image
        try:
            img_res = requests.get(item["strMealThumb"]).content
            img = Image.open(BytesIO(img_res)).resize((220, 220), Image.Resampling.LANCZOS)
            self.current_img = ImageTk.PhotoImage(img)
            self.img_output.config(image=self.current_img)
        except:
            self.img_output.config(image='')

    def save_favorite(self):
        # Save recipe name to file
        if self.current_meal_name:
            with open(self.fav_file, "a+") as f:
                f.seek(0)
                if self.current_meal_name not in f.read():
                    f.write(self.current_meal_name + "\n")
                    messagebox.showinfo("Saved", "Added to favorites!")

    #  FAVORITES WINDOW 
    def show_favorites_window(self):
        win = tk.Toplevel(self.root)
        win.title("My Favorites")
        win.geometry("300x450")

        try:
            win.iconphoto(True, self.icon_ref)
        except:
            pass

        win.config(bg=self.clr_bg)

        tk.Label(
            win, text="Double-click to load recipe",
            bg=self.clr_bg, fg=self.clr_accent,
            font=("Helvetica", 8)
        ).pack(pady=5)

        # Listbox for favorites
        lb = tk.Listbox(
            win, bg=self.clr_gray, fg="white",
            bd=0, font=("Helvetica", 10),
            selectbackground=self.clr_accent
        )
        lb.pack(fill="both", expand=True, padx=10, pady=5)

        def refresh_list():
            lb.delete(0, tk.END)
            if os.path.exists(self.fav_file):
                with open(self.fav_file, "r") as f:
                    for line in f:
                        if line.strip():
                            lb.insert(tk.END, line.strip())

        refresh_list()

        def remove_item():
            selection = lb.curselection()
            if not selection:
                return

            meal = lb.get(selection)

            if os.path.exists(self.fav_file):
                with open(self.fav_file, "r") as f:
                    lines = f.readlines()
                with open(self.fav_file, "w") as f:
                    for line in lines:
                        if line.strip() != meal:
                            f.write(line)

            refresh_list()
            messagebox.showinfo("Removed", f"Deleted {meal}")

        # Remove button
        tk.Button(
            win, text="REMOVE SELECTED",
            command=remove_item,
            bg=self.clr_danger, fg="white",
            relief="flat", font=("Helvetica", 8, "bold")
        ).pack(fill="x", padx=10, pady=10)

        def load(e):
            # Load recipe on double click
            if lb.curselection():
                self.searchbox.delete(0, "end")
                self.searchbox.insert(0, lb.get(lb.curselection()))
                self.run_search()
                win.destroy()

        lb.bind("<Double-Button-1>", load)


#  START APP 
if __name__ == "__main__":
    root = tk.Tk()
    app = ClintApp(root)
    root.mainloop()
