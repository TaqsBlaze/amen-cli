import os
import tkinter as tk
from tkinter import filedialog, messagebox

def edit_file(file_path):
    """
    A simple text editor using Tkinter.
    """
    root = tk.Tk()
    root.title("Ring Editor")
    
    text_area = tk.Text(root, wrap=tk.WORD)
    text_area.pack(expand=True, fill='both')
    
    try:
        with open(file_path, "r") as f:
            content = f.read()
            text_area.insert(tk.END, content)
    except FileNotFoundError:
        messagebox.showerror("Error", "File not found.")
    
    def save_file():
        try:
            with open(file_path, "w") as f:
                f.write(text_area.get("1.0", tk.END))
            messagebox.showinfo("Info", "File saved.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def open_file():
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                    text_area.delete("1.0", tk.END)
                    text_area.insert(tk.END, content)
            except FileNotFoundError:
                messagebox.showerror("Error", "File not found.")

    # Menu bar
    menu_bar = tk.Menu(root)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Open", command=open_file)
    file_menu.add_command(label="Save", command=save_file)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)
    root.config(menu=menu_bar)
    
    # Syntax highlighting
    def highlight_syntax(event=None):
        keywords = {
            'def': 'purple',
            'class': 'purple',
            'import': 'orange',
            'from': 'orange',
            'as': 'orange',
            'return': 'blue',
            'if': 'blue',
            'else': 'blue',
            'for': 'blue',
            'while': 'blue',
            'try': 'blue',
            'except': 'blue',
            'with': 'blue',
            'open': 'blue',
            'True': 'green',
            'false': 'green',
            'SECRET_KEY': 'red',
            'API_KEY': 'red',
            'DATABASE_URL': 'red',
            'DEBUG': 'red',
        }

        # Remove existing tags
        for tag in text_area.tag_names():
            text_area.tag_remove(tag, "1.0", tk.END)

        # Add tags for keywords
        for keyword, color in keywords.items():
            start = "1.0"
            while True:
                start = text_area.search(r'\m' + keyword + r'\M', start, stopindex=tk.END, regexp=True)
                if not start:
                    break
                end = f"{start}+{len(keyword)}c"
                text_area.tag_add(keyword, start, end)
                text_area.tag_config(keyword, foreground=color)
                start = end

    text_area.bind("<KeyRelease>", highlight_syntax)
    
    root.mainloop()

