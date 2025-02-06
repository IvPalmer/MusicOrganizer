#!/usr/bin/env python3
import os
import sys
import traceback
import datetime
import locale
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import queue

from discogs_utils import create_discogs_client
import organizer

# --- Resource Path Setup ---
if getattr(sys, 'frozen', False):
    # In a py2app bundle, sys.executable is in Contents/MacOS.
    # Go up two levels to reach Contents, then join "Resources"
    app_contents = os.path.dirname(os.path.dirname(sys.executable))
    resource_path = os.path.join(app_contents, "Resources")
else:
    # When running in development (non-frozen)
    resource_path = os.path.join(os.getcwd(), "dist", "music_organizer.app", "Contents", "Resources")

print("Computed resource_path:", resource_path)
# We use absolute paths; do not change the working directory.

# --- Error Logging Setup ---
def log_exception(exc):
    """Log the exception traceback to a file in the Resources folder."""
    log_file = os.path.join(resource_path, "error_log.txt")
    try:
        with open(log_file, "a") as f:
            f.write(f"{datetime.datetime.now()} - Exception occurred:\n")
            f.write(traceback.format_exc())
            f.write("\n")
    except Exception as log_exc:
        print("Failed to write error log:", log_exc)

# --- Application Functions ---
def open_soundcloud():
    """Opens the SoundCloud page in the default web browser."""
    webbrowser.open("https://soundcloud.com/ivpalmer")

def open_folder(folder_path):
    """Opens the given folder using the OS default file explorer."""
    try:
        if os.name == "nt":
            os.startfile(folder_path)
        elif os.name == "posix":
            os.system(f"open '{folder_path}'")
        else:
            messagebox.showinfo("Notification", "Your OS is not supported for opening folders.")
    except Exception as e:
        print(f"Error opening folder: {e}")

# --- Main GUI Application ---
def main():
    # Set the locale explicitly to avoid nil localized strings.
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except Exception as e:
        print("Error setting locale:", e)

    # Initialize the main Tk window.
    root = tk.Tk()
    root.title("Music Organizer")
    root.geometry("700x700")
    root.resizable(False, False)

    # Workaround: force Tcl/Tk to use a valid menu title.
    try:
        # Set the global Tcl variable "tk::mac::MenuBarTitle" to a non-nil value.
        root.tk.eval('global tk::mac::MenuBarTitle; set tk::mac::MenuBarTitle "Music Organizer"')
    except Exception as e:
        print("Error setting tk::mac::MenuBarTitle:", e)

    # Attempt to override the default Apple menu initialization.
    try:
        root.tk.eval('proc tk::mac::initAppleMenu {} {}')
    except Exception as e:
        print("Error overriding tk::mac::initAppleMenu:", e)

    # Also, disable any native Apple menubar integration via Tcl variables.
    try:
        root.tk.call("set", "tk::mac::useAppleMenu", "0")
    except Exception as e:
        print("Error setting tk::mac::useAppleMenu:", e)
    try:
        root.tk.call("set", "tk::mac::useMenuBar", "0")
    except Exception as e:
        print("Error setting tk::mac::useMenuBar:", e)

    # Assign a simple menubar to the window.
    try:
        simple_menu = tk.Menu(root)
        # Optionally, add at least one dummy command to ensure no nil values are passed.
        simple_menu.add_command(label="Music Organizer")
        root.config(menu=simple_menu)
    except Exception as e:
        print("Error creating simple menubar:", e)

    selected_folder = tk.StringVar(value="No folder selected")
    log_queue = queue.Queue()

    def scale_font(size):
        return size

    # Main container for UI elements.
    container = tk.Frame(root)
    container.pack(expand=True, fill="both")

    # Discogs API token input.
    tk.Label(container, text="Discogs API Token:", font=("Helvetica", scale_font(16))).pack(pady=(20, 10))
    token_entry = tk.Entry(container, width=40, font=("Helvetica", scale_font(14)))
    token_entry.pack(pady=(0, 15))

    def open_discogs_link():
        webbrowser.open("https://www.discogs.com/settings/developers")
    tk.Button(container, text="Find Your Token Here", command=open_discogs_link, font=("Helvetica", scale_font(14))).pack(pady=(0, 25))

    # Radio buttons for selecting action.
    tk.Label(container, text="Select Action:", font=("Helvetica", scale_font(16))).pack(pady=(5, 5))
    action_var = tk.StringVar(value="move")
    options_frame = tk.Frame(container)
    options_frame.pack(pady=(0, 15))
    tk.Radiobutton(options_frame, text="Move Files", variable=action_var, value="move", font=("Helvetica", scale_font(14))).grid(row=0, column=0, padx=10)
    tk.Radiobutton(options_frame, text="Copy Files", variable=action_var, value="copy", font=("Helvetica", scale_font(14))).grid(row=0, column=1, padx=10)

    tk.Label(container, text="WARNING: DJ Softwares might lose reference if you move files",
             font=("Helvetica", scale_font(12)), fg="red").pack(pady=(0, 15))

    # Folder selection UI.
    folder_frame = tk.Frame(container)
    folder_frame.pack(pady=(5, 15))
    tk.Button(folder_frame, text="Select Music Folder", command=lambda: select_folder(selected_folder),
              font=("Helvetica", scale_font(14))).grid(row=0, column=0, padx=15)
    tk.Label(folder_frame, textvariable=selected_folder, font=("Helvetica", scale_font(12)), wraplength=600, anchor="w", justify="left").grid(row=0, column=1, sticky="w")

    # Progress bar.
    progress = ttk.Progressbar(container, orient="horizontal", length=600, mode="determinate")
    progress.pack(pady=(10, 15))

    # Log display window.
    log_window = tk.Text(container, height=15, width=80, state="disabled", bg="black", fg="white", font=("Helvetica", scale_font(12)))
    log_window.pack(pady=(5, 15))

    def log_message(message):
        log_queue.put(message)
        print(f"[DEBUG]: {message}")

    def update_log():
        while not log_queue.empty():
            message = log_queue.get_nowait()
            log_window.config(state="normal")
            log_window.insert("end", f"{message}\n")
            log_window.config(state="disabled")
            log_window.see("end")
        root.after(100, update_log)

    def select_folder(selected_folder_var):
        folder = filedialog.askdirectory(title="Select your music folder")
        if folder:
            selected_folder_var.set(folder)

    def progress_callback(current, total):
        progress["maximum"] = total
        progress["value"] = current
        root.update_idletasks()

    def start_organizing_threaded(user_token, folder, action):
        start_button.config(state=tk.DISABLED)
        def task():
            try:
                client = create_discogs_client(user_token)
            except Exception as e:
                log_message(f"Error initializing Discogs client: {e}")
                start_button.config(state=tk.NORMAL)
                return
            organizer.organize_files(client, folder, action, log_callback=log_message, progress_callback=progress_callback)
            open_folder(folder)
            start_button.config(state=tk.NORMAL)
        threading.Thread(target=task).start()

    start_button = tk.Button(container, text="Start Organizing",
                             command=lambda: start_organizing_threaded(token_entry.get(), selected_folder.get(), action_var.get()),
                             font=("Helvetica", scale_font(14)))
    start_button.pack(pady=(5, 15))

    tk.Button(container, text="Follow Me on SoundCloud", command=open_soundcloud, font=("Helvetica", scale_font(14))).pack(pady=(0, 15))

    update_log()
    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("An unhandled exception occurred:")
        traceback.print_exc()
        log_exception(e)
        raise