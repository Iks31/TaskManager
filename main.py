import customtkinter as ctk
from PIL import Image
from pygame import mixer
import os
import sys

# Set up modern window theme
ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue") 
class task:
    def __init__(self, name):
        self.name = name
        self.completed = False
    
    def mark_completed(self):
        self.completed = True

    def mark_uncompleted(self):
        self.completed = False
    
    def __str__(self):
        return f"{'[X]' if self.completed else '[ ]'} {self.name}"
    
    def delete(self):
        del self

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        # setting page limit
        self.all_tasks = [] 
        self.TASKS_PER_PAGE = 4
        self.current_page = 0

        # initialising mixer and loading sound
        mixer.init() 
        self.pop_sound = self.load_sound("pop.mp3")
        self.delete_sound = self.load_sound("delete.mp3")
        self.close_app_sound = self.load_sound("close_app.mp3")

        # Window Setup
        self.geometry("500x600")
        self.title("My Artistic To-Do List")
        
        # Remove the standard OS title bar and borders
        self.overrideredirect(True)
        
        self.TRANSPARENT_COLOR = "#8072a6" 
        if sys.platform.startswith("win"):
            self.wm_attributes("-transparentcolor", self.TRANSPARENT_COLOR)
            
        # Set the background to our transparent color
        self.configure(fg_color=self.TRANSPARENT_COLOR)
        
        # Locate the assets folder safely
        current_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(current_dir, "assets", "bg.png")
        close_path = os.path.join(current_dir, "assets", "close.png")
        textbox_path = os.path.join(current_dir, "assets", "textbox.png")
        empty_todo_path = os.path.join(current_dir,"assets", "empty_todo.png")
        remove_path = os.path.join(current_dir,"assets", "remove.png")
        done_path = os.path.join(current_dir, "assets", "Done.png")
        left_path = os.path.join(current_dir, "assets", "left.png")
        right_path = os.path.join(current_dir, "assets", "right.png")
        # Load all custom artwork 
        try:
            self.bg_image = ctk.CTkImage(
                light_image=Image.open(bg_path),
                dark_image=Image.open(bg_path),
                size=(500, 600)  
            )
            self.close_img = Image.open(close_path)  
            self.close = ctk.CTkImage(
                light_image=self.close_img,
                dark_image=self.close_img, 
                size=(33, 33)
            )
            self.empty_todo_img = Image.open(empty_todo_path)
            self.empty_todo = ctk.CTkImage(
                light_image=self.empty_todo_img,
                dark_image=self.empty_todo_img, 
                size=(33, 33)
            )
            self.remove_img = Image.open(remove_path)
            self.remove = ctk.CTkImage(
                light_image=self.remove_img,
                dark_image=self.remove_img, 
                size=(22, 22)
            )
            self.done_img = Image.open(done_path)
            self.done = ctk.CTkImage(
                light_image=self.done_img,
                dark_image=self.done_img, 
                size=(33, 33)
            )
            self.left_img = Image.open(left_path)
            self.left = ctk.CTkImage(
                light_image=self.left_img,
                dark_image=self.left_img, 
                size=(30, 40)
            )
            self.right_img = Image.open(right_path)
            self.right = ctk.CTkImage(
                light_image=self.right_img,
                dark_image=self.right_img, 
                size=(30, 40)
            )
            self.textbox_img = Image.open(textbox_path)
            self.textbox = ctk.CTkImage(
                light_image=self.textbox_img,
                dark_image=self.textbox_img,
                size=(260, 50)
            )
            # Place it absolute bottom, filling the screen
            self.bg_label = ctk.CTkLabel(self, text="", image=self.bg_image, fg_color=self.TRANSPARENT_COLOR)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            
            # Bind the mouse clicks so clicking the art moves the app
            self.bg_label.bind("<ButtonPress-1>", self.start_move)
            self.bg_label.bind("<B1-Motion>", self.do_move)
            
        except FileNotFoundError:
            self.fallback_label = ctk.CTkLabel(self, text="[Drop my_art.png in assets!]", font=("Arial", 14), fg_color="black")
            self.fallback_label.pack(pady=20)
        
        self.close_button = ctk.CTkButton(
            self,
            text="",
            fg_color="#6d80de", 
            hover_color="#6d80de",  
            width=40, 
            height=40,
            corner_radius=0,
            image=self.close,
            command=self.quit
        )
        self.close_button.place(relx=0.2, rely=0.172, anchor="center")  # Place it at the top-right corner of the content frame
        # Pagination Buttons (Placed on the main window 'self')
        self.prev_button = ctk.CTkButton(
            self,
            text="",
            image=self.left,
            width=30,
            height=40,
            fg_color="#9e8fca", 
            hover_color="#9e8fca", # Matches your close button hover
            bg_color="#9e8fca",
            command=self.prev_page
        )
        # Positioned to the left of the central content frame, aligned with the tasks
        self.prev_button.place(relx=0.22, rely=0.65, anchor="center")

        self.next_button = ctk.CTkButton(
            self,
            text="",
            image=self.right,
            width=30,
            height=40,
            fg_color="#9e8fca", 
            hover_color="#9e8fca", 
            bg_color="#9e8fca",
            command=self.next_page
        )
        # Positioned to the right of the central content frame
        self.next_button.place(relx=0.80, rely=0.65, anchor="center")
        # 4. Create a transparent frame to hold your UI over the image
        self.content_frame = ctk.CTkFrame(
            self, 
            width=250, 
            height=410, 
            corner_radius=0, 
            border_width=0,
            fg_color="#9e8fca",  # The visible color of the frame
            bg_color="#9e8fca"   # MATCH the fg_color to stop the green/transparent bleeding!
        )
        self.content_frame.pack_propagate(False) 
        # Place it perfectly in the center of the window
        self.content_frame.place(relx=0.515, rely=0.60, anchor="center")
     
        self.title_label = ctk.CTkLabel(self.content_frame, text="My Tasks", font=("Terminal", 24, "bold"), text_color="white")
        self.title_label.pack(pady=(20, 10))

        self.entry_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.entry_container.pack(pady=10)
        self.entry_bg_label = ctk.CTkLabel(self.entry_container, text="", image=self.textbox)
        self.entry_bg_label.pack()

        self.task_input = ctk.CTkEntry(
            self.entry_container, 
            placeholder_text="Type a new task here...",
            text_color="#223A80",
            font=("Terminal",14),
            width=210, 
            height=29,
            fg_color="#d8dfff",
            bg_color="#d8dfff",
            corner_radius=0,
            border_width=0,
            border_color="#d8dfff")
        self.task_input.place(relx=0.5, rely=0.5, anchor="center")
        self.task_input.bind("<Return>", self.add_task)

        self.tasks_page = ctk.CTkFrame(self.content_frame, 
            width=250, 
            height=250, 
            corner_radius=0, 
            border_width=0,
            fg_color="#9e8fca",  
            bg_color="#9e8fca"
            )
        self.tasks_page.pack(fill="both", expand=True)
    
    def next_page(self):
        future_page = (self.current_page + 1) * self.TASKS_PER_PAGE

        if len(self.all_tasks) > future_page:
            self.current_page = self.current_page + 1
            self.render_task()
            self.play_sound(self.close_app_sound)
        else:
            return 
    
    def prev_page(self):
        future_page = (self.current_page - 1) * self.TASKS_PER_PAGE

        if len(self.all_tasks) > future_page and future_page >= 0:
            self.current_page = self.current_page - 1
            self.render_task()
            self.play_sound(self.close_app_sound)
        else:
            return 


    def render_task(self):
        for widget in self.tasks_page.winfo_children():
            widget.destroy()

        start_point = self.current_page * self.TASKS_PER_PAGE
        end_point = start_point + self.TASKS_PER_PAGE

        current_view = self.all_tasks[start_point: end_point]

        for task in current_view:
            task_frame = ctk.CTkFrame(
                self.tasks_page,
                width=225, 
                height=50, 
                corner_radius=0, 
                border_width=0,
                fg_color="#9e8fca"
                )
            task_frame.pack(side="top", pady=5, fill="x", anchor="w")

            current_image = self.done if task.completed else self.empty_todo

            task_done_button = ctk.CTkButton(
                task_frame,
                width=33,
                height=33,
                image=current_image,
                text="",
                fg_color="#9e8fca",
                hover_color="#9e8fca",
                border_width=0,
                corner_radius=0,
            )
          
            task_done_button.configure(command=lambda  t=task: self.toggle_task(t))
            task_done_button.pack(side="left", padx=(10, 5), pady=3)

            task_remove_button = ctk.CTkButton(
                task_frame,
                width=22,
                height=22,
                image=self.remove,
                text="",
                fg_color="#9e8fca",
                hover_color="#9e8fca",
                border_width=0,
                corner_radius=0,
            )
            task_remove_button.configure(command=lambda t=task: self.remove_task(t))
            task_remove_button.pack(side="right", padx=(5, 10), pady=9)
            
            task_label = ctk.CTkLabel(
                task_frame,
                text=task.name,
                font=("Terminal",16),
                wraplength=210,    
                anchor="w",      
                justify="center",
                text_color="#223A80")
            task_label.pack(side="left", fill="both", expand=True, padx=5)

    def add_task(self, event=None):  
        new_task = self.task_input.get() 
        if new_task != "":
            print(f"Task Added: {new_task}") 
            self.task_input.delete(0, 'end')
            n_task = task(new_task)
            self.all_tasks.append(n_task)
            self.render_task()
            self.play_sound(self.pop_sound)
    
    def toggle_task(self, clicked_task):
        # 1. Flip the data state
        if clicked_task.completed == False:
            clicked_task.completed = True
        else:
            clicked_task.completed = False
            
        self.render_task()

    def play_sound(self, filename):
        try:
              mixer.music.load(filename)
              mixer.music.play()
        except Exception as e:
            print(f"Error playing sound: {e}")


    def load_sound(self, filename):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sound_path = os.path.join(current_dir, "assets", filename)
        if os.path.exists(sound_path):
            return sound_path
        else:
            print(f"Sound file not found: {sound_path}")
            return None
        
    def remove_task(self, task):
        self.all_tasks.remove(task)
        self.render_task()
        self.play_sound(self.delete_sound)
    # 6. Window Dragging Logic Methods
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        x = self.winfo_x() - self.x + event.x
        y = self.winfo_y() - self.y + event.y
        self.geometry(f"+{x}+{y}")

# 7. Actually run the app
if __name__ == "__main__":
    app = App()
    app.mainloop()