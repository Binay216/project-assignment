# Created by Group Members :
# ====================================
# Dodik Kurniawan - s391213
# Binay Siwakoti - s387596
# Bibek Chhantyal - s390276
# Govinda Debnath - s388937
# ====================================

import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
import sys

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ImageX - HIT134")

        window_width = 1340
        window_height = 650

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = (screen_width - window_width) // 2
        center_y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.root.resizable(False, False)

        self.original_img = None
        self.original_img_for_crop = None
        self.display_img = None
        self.cropped_img = None
        self.resized_for_save = None
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.rect_coords = None
        self.history = []
        self.redo_stack = []

        self.canvas_width = 800
        self.canvas_height = 600

        self.status_var = tk.StringVar()
        self.zoom_label_var = tk.StringVar()

        self.img_offset_x = 0
        self.img_offset_y = 0
        self.displayed_img_size = (0, 0)

        self.init_gui()
        self.bind_shortcuts()
    def init_gui(self):
        self.create_menu()

        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True, fill='both')

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=False)

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(left_frame, width=self.canvas_width, height=self.canvas_height, bg='grey')
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        tk.Label(right_frame, text="Cropped Preview:").pack(anchor='w')
        self.cropped_label = tk.Label(right_frame)
        self.cropped_label.pack(pady=10)

        bottom_right = tk.Frame(right_frame)
        bottom_right.pack(side='bottom', fill='x', pady=10)

        tk.Label(bottom_right, text="Resize Cropped Image:").pack(anchor='w')
        self.slider = ttk.Scale(bottom_right, from_=0.1, to=2.0, orient='horizontal', command=self.resize_image)
        self.slider.set(1.0)
        self.slider.pack(fill='x', padx=10)

        self.zoom_label = tk.Label(bottom_right, textvariable=self.zoom_label_var, anchor='e')
        self.zoom_label.pack(fill='x', padx=10)
        self.zoom_label_var.set("Zoom: 100%")

        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief='sunken', anchor='w')
        status_bar.pack(side='bottom', fill='x')
        self.status_var.set("No image loaded.")

    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.clear_canvas, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.load_image, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_image, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_program)
        menu_bar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)

        effect_menu = tk.Menu(edit_menu, tearoff=0)
        effect_menu.add_command(label="Grayscale", command=self.apply_grayscale)
        effect_menu.add_command(label="Find Edges", command=self.apply_find_edges)
        edit_menu.add_cascade(label="Effect", menu=effect_menu)

        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="About", command=self.show_about_window)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)
        
    def apply_grayscale(self):
        if self.cropped_img is not None:
            self.history.append(self.cropped_img.copy())
            gray = cv2.cvtColor(self.cropped_img, cv2.COLOR_RGB2GRAY)
            gray_rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            self.cropped_img = gray_rgb
            self.resized_for_save = gray_rgb
            self.redo_stack.clear()
            self.update_cropped_display()

    def apply_find_edges(self):
        if self.cropped_img is not None:
            self.history.append(self.cropped_img.copy())
            gray = cv2.cvtColor(self.cropped_img, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
            self.cropped_img = edges_rgb
            self.resized_for_save = edges_rgb
            self.redo_stack.clear()
            self.update_cropped_display()

    def bind_shortcuts(self):
        self.root.bind_all("<Control-n>", lambda event: self.clear_canvas())
        self.root.bind_all("<Control-o>", lambda event: self.load_image())
        self.root.bind_all("<Control-s>", lambda event: self.save_image())

    def clear_canvas(self):
        self.canvas.delete("all")
        self.cropped_label.config(image='')
        self.original_img = None
        self.original_img_for_crop = None
        self.display_img = None
        self.cropped_img = None
        self.resized_for_save = None
        self.rect_id = None
        self.rect_coords = None
        self.history.clear()
        self.redo_stack.clear()
        self.slider.set(1.0)
        self.zoom_label_var.set("Zoom: 100%")
        self.status_var.set("Canvas cleared. No image loaded.")

    def show_user_guide(self):
        guide = (
            "1. Go to File > Open to load an image.\n"
            "2. Click and drag on the image to create a crop selection.\n"
            "3. Drag the crop box to reposition it.\n"
            "4. Use the slider to zoom the cropped image.\n"
            "5. Go to File > Save to save the cropped (and possibly zoomed or edited) image.\n"
            "6. Use Edit > Undo / Redo to revert or reapply previous crop/zoom/effect actions.\n"
            "7. Use Edit > Effect to apply effects to the cropped image:\n"
            "   - Grayscale: Converts the image to black and white.\n"
            "   - Find Edges: Highlights the edges in the image.\n"
            "   These effects are applied to the cropped image and can also be undone or redone.\n"
        )
        messagebox.showinfo("User Guide", guide)

    def show_about_window(self):
        about_win = Toplevel(self.root)
        about_win.title("About")
        about_win.geometry("400x200")
        about_win.resizable(False, False)

        about_win.update_idletasks()
        w = 400
        h = 200
        x = (about_win.winfo_screenwidth() // 2) - (w // 2)
        y = (about_win.winfo_screenheight() // 2) - (h // 2)
        about_win.geometry(f"{w}x{h}+{x}+{y}")

        canvas = tk.Canvas(about_win, bg='gray')
        canvas.pack(fill='both', expand=True)

        names = ["Members :", "Dodik Kurniawan - s391213", "Binay Siwakoti - s387596", "Bibek Chhantyal - s390276", "Govinda Debnath - s388937"]
        texts = []

        for i, name in enumerate(names):
            y = 200 + i * 40
            t = canvas.create_text(200, y, text=name, fill="white", font=('Arial', 16))
            texts.append(t)

        def scroll():
            for t in texts:
                canvas.move(t, 0, -1)
                if canvas.coords(t)[1] < -20:
                    canvas.move(t, 0, 240)
            about_win.after(50, scroll)

        scroll()
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if file_path:
            image = cv2.cvtColor(cv2.imread(file_path), cv2.COLOR_BGR2RGB)
            self.original_img_for_crop = image.copy()
            self.original_img = self.resize_to_fit_canvas(image)
            self.history.clear()
            self.redo_stack.clear()
            self.display_image(self.original_img)

            h, w = self.original_img_for_crop.shape[:2]
            try:
                dpi = Image.open(file_path).info.get('dpi', (72, 72))
                dpi_str = f"{dpi[0]}x{dpi[1]} dpi"
            except:
                dpi_str = "Unknown DPI"
            self.status_var.set(f"Loaded: {os.path.basename(file_path)} | Size: {w}x{h} | DPI: {dpi_str}")

    def resize_to_fit_canvas(self, img):
        h, w = img.shape[:2]
        if w <= self.canvas_width and h <= self.canvas_height:
            return img
        scale = min(self.canvas_width / w, self.canvas_height / h)
        new_size = (int(w * scale), int(h * scale))
        return cv2.resize(img, new_size)

    def display_image(self, img):
        self.canvas.delete("all")
        img_pil = Image.fromarray(img)
        self.display_img = ImageTk.PhotoImage(img_pil)

        x_offset = (self.canvas_width - img.shape[1]) // 2
        y_offset = (self.canvas_height - img.shape[0]) // 2

        self.img_offset_x = x_offset
        self.img_offset_y = y_offset
        self.displayed_img_size = (img.shape[1], img.shape[0])

        self.canvas.create_image(x_offset, y_offset, anchor="nw", image=self.display_img)
    def on_mouse_down(self, event):
        if self.rect_coords:
            x1, y1, x2, y2 = self.rect_coords
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.dragging = True
                self.drag_offset_x = event.x - x1
                self.drag_offset_y = event.y - y1
                return
        self.start_x = event.x
        self.start_y = event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_coords = None

    def on_mouse_drag(self, event):
        if self.dragging and self.rect_coords:
            dx = event.x - self.drag_offset_x
            dy = event.y - self.drag_offset_y
            width = self.rect_coords[2] - self.rect_coords[0]
            height = self.rect_coords[3] - self.rect_coords[1]
            self.rect_coords = (dx, dy, dx + width, dy + height)
            self.canvas.coords(self.rect_id, *self.rect_coords)
        else:
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            self.rect_coords = (self.start_x, self.start_y, event.x, event.y)
            self.rect_id = self.canvas.create_rectangle(*self.rect_coords, outline='red')
        self.update_crop_preview()

    def on_mouse_up(self, event):
        self.dragging = False
    def update_crop_preview(self):
        if self.original_img_for_crop is not None and self.rect_coords and self.displayed_img_size:
            x1, y1, x2, y2 = self.rect_coords
            x1_adj = x1 - self.img_offset_x
            y1_adj = y1 - self.img_offset_y
            x2_adj = x2 - self.img_offset_x
            y2_adj = y2 - self.img_offset_y

            if x2_adj < 0 or y2_adj < 0:
                return

            scale_x = self.original_img_for_crop.shape[1] / self.displayed_img_size[0]
            scale_y = self.original_img_for_crop.shape[0] / self.displayed_img_size[1]

            x1_real = int(min(x1_adj, x2_adj) * scale_x)
            y1_real = int(min(y1_adj, y2_adj) * scale_y)
            x2_real = int(max(x1_adj, x2_adj) * scale_x)
            y2_real = int(max(y1_adj, y2_adj) * scale_y)

            cropped = self.original_img_for_crop[y1_real:y2_real, x1_real:x2_real]
            if cropped.size > 0:
                self.cropped_img = cropped
                self.resized_for_save = cropped
                self.update_cropped_display()

    def update_cropped_display(self):
        if self.cropped_img is not None:
            img = Image.fromarray(self.cropped_img)
            img.thumbnail((300, 200))
            self.tk_cropped_img = ImageTk.PhotoImage(img)
            self.cropped_label.config(image=self.tk_cropped_img)
    def resize_image(self, val):
        if self.cropped_img is not None:
            factor = float(val)
            percent = int(factor * 100)
            self.zoom_label_var.set(f"Zoom: {percent}%")
            width = int(self.cropped_img.shape[1] * factor)
            height = int(self.cropped_img.shape[0] * factor)
            resized = cv2.resize(self.cropped_img, (width, height))
            self.resized_for_save = resized
            img = Image.fromarray(resized)
            img.thumbnail((300, 200))
            self.tk_cropped_img = ImageTk.PhotoImage(img)
            self.cropped_label.config(image=self.tk_cropped_img)

    def save_image(self):
        if self.resized_for_save is not None:
            save_img = self.resized_for_save
        elif self.cropped_img is not None:
            save_img = self.cropped_img
        else:
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            cv2.imwrite(file_path, cv2.cvtColor(save_img, cv2.COLOR_RGB2BGR))
            messagebox.showinfo("Saved", "Image saved successfully!")

    def undo(self):
        if self.history:
            self.redo_stack.append(self.cropped_img.copy())
            self.cropped_img = self.history.pop()
            self.resized_for_save = self.cropped_img
            self.update_cropped_display()

    def redo(self):
        if self.redo_stack:
            self.history.append(self.cropped_img.copy())
            self.cropped_img = self.redo_stack.pop()
            self.resized_for_save = self.cropped_img
            self.update_cropped_display()

    def exit_program(self):
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()
