import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import copy

# Constants
CANVAS_WIDTH = 600
CANVAS_HEIGHT = 400
CROP_WIDTH = 300
CROP_HEIGHT = 200
DEFAULT_SCALE = 1.0

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Image Editor")

        # History stack for undo/redo
        self.history = []
        self.future = []

        # Image variables
        self.image_path = None
        self.original_image = None
        self.tk_image = None
        self.start_x = self.start_y = None
        self.rect = None
        self.cropped_image = None

        # Load image button
        self.load_button = tk.Button(root, text="Load Image", command=self.load_image)
        self.load_button.pack(pady=5)

        # Canvas for original image
        self.canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg='grey')
        self.canvas.pack(side=tk.LEFT)

        # Canvas for cropped image
        self.crop_canvas = tk.Canvas(root, width=CROP_WIDTH, height=CROP_HEIGHT, bg='lightgrey')
        self.crop_canvas.pack(side=tk.RIGHT, padx=10)

        # Scale for resizing
        self.scale_var = tk.DoubleVar()
        self.scale_var.set(DEFAULT_SCALE)
        self.slider = tk.Scale(root, from_=0.1, to=2.0, resolution=0.1,
                               orient=tk.HORIZONTAL, label="Resize Cropped Image",
                               variable=self.scale_var, command=self.resize_crop)
        self.slider.pack(pady=5)

        # Buttons
        self.save_button = tk.Button(root, text="Save Cropped Image", command=self.save_image)
        self.save_button.pack(pady=5)

        self.grayscale_button = tk.Button(root, text="Apply Grayscale", command=self.apply_grayscale)
        self.grayscale_button.pack(pady=5)

        self.undo_button = tk.Button(root, text="Undo", command=self.undo)
        self.undo_button.pack(pady=5)

        self.redo_button = tk.Button(root, text="Redo", command=self.redo)
        self.redo_button.pack(pady=5)

        # Mouse bindings for cropping
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

        # Keyboard shortcuts
        root.bind("<Control-s>", lambda event: self.save_image())
        root.bind("<Control-z>", lambda event: self.undo())
        root.bind("<Control-y>", lambda event: self.redo())

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if file_path:
            try:
                self.image_path = file_path
                self.original_image = cv2.cvtColor(cv2.imread(file_path), cv2.COLOR_BGR2RGB)
                self.push_history(self.original_image)
                self.display_image(self.original_image)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    def display_image(self, image_array):
        self.resized_image = cv2.resize(image_array, (CANVAS_WIDTH, CANVAS_HEIGHT))
        image = Image.fromarray(self.resized_image)
        self.tk_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def on_mouse_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_mouse_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_mouse_release(self, event):
        end_x, end_y = event.x, event.y
        x1, y1 = min(self.start_x, end_x), min(self.start_y, end_y)
        x2, y2 = max(self.start_x, end_x), max(self.start_y, end_y)
        crop = self.resized_image[y1:y2, x1:x2]
        if crop.size != 0:
            self.cropped_image = crop
            self.display_cropped_image(crop)

    def display_cropped_image(self, crop_array):
        image = Image.fromarray(crop_array)
        image = image.resize((CROP_WIDTH, CROP_HEIGHT))
        tk_crop = ImageTk.PhotoImage(image)
        self.crop_canvas.create_image(0, 0, anchor=tk.NW, image=tk_crop)
        self.crop_canvas.image = tk_crop

    def resize_crop(self, value):
        if self.cropped_image is not None:
            try:
                scale = float(value)
                h, w = self.cropped_image.shape[:2]
                new_w, new_h = int(w * scale), int(h * scale)
                resized = cv2.resize(self.cropped_image, (new_w, new_h))
                image = Image.fromarray(resized)
                image = image.resize((CROP_WIDTH, CROP_HEIGHT))
                tk_resized = ImageTk.PhotoImage(image)
                self.crop_canvas.create_image(0, 0, anchor=tk.NW, image=tk_resized)
                self.crop_canvas.image = tk_resized
            except Exception as e:
                messagebox.showerror("Error", f"Resize failed: {e}")

    def save_image(self):
        if self.cropped_image is None:
            messagebox.showerror("Error", "No cropped image to save.")
            return
        try:
            scale = self.scale_var.get()
            h, w = self.cropped_image.shape[:2]
            new_w, new_h = int(w * scale), int(h * scale)
            resized = cv2.resize(self.cropped_image, (new_w, new_h))
            save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"),
                                                                ("JPEG files", "*.jpg"),
                                                                ("All files", "*.*")])
            if save_path:
                cv2.imwrite(save_path, cv2.cvtColor(resized, cv2.COLOR_RGB2BGR))
                messagebox.showinfo("Success", f"Image saved to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {e}")

    def apply_grayscale(self):
        if self.original_image is not None:
            try:
                gray = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
                gray_rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
                self.push_history(gray_rgb)
                self.display_image(gray_rgb)
            except Exception as e:
                messagebox.showerror("Error", f"Grayscale failed: {e}")

    def push_history(self, image_array):
        self.history.append(copy.deepcopy(image_array))
        self.future.clear()

    def undo(self):
        if len(self.history) > 1:
            self.future.append(self.history.pop())
            self.display_image(self.history[-1])

    def redo(self):
        if self.future:
            image = self.future.pop()
            self.history.append(image)
            self.display_image(image)

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()
