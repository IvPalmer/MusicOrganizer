import os
import shutil
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import discogs_client
from mutagen import File as MutagenFile
import threading
import time
import queue  # To communicate between threads


def open_soundcloud():
    webbrowser.open("https://soundcloud.com/ivpalmer")


def main():
    # Initialize Tkinter
    root = tk.Tk()
    root.title("Music Organizer")
    root.geometry("600x550")  # Increased height to fit all elements
    root.resizable(False, False)

    selected_folder = tk.StringVar(value="No folder selected")
    log_queue = queue.Queue()

    # Discogs Token Input with Guidance
    tk.Label(root, text="Discogs API Token:", font=("Helvetica", 10)).pack(pady=(10, 5))
    tk.Label(root, text="(Find your token at: https://www.discogs.com/settings/developers)", 
             font=("Helvetica", 8)).pack(pady=(0, 10))
    token_entry = tk.Entry(root, width=60)
    token_entry.pack(pady=(0, 10))

    # Move/Copy Selection
    tk.Label(root, text="Select Action:", font=("Helvetica", 10)).pack(pady=(10, 5))
    action_var = tk.StringVar(value="move")
    options_frame = tk.Frame(root)
    options_frame.pack(pady=(0, 5))
    move_radio = tk.Radiobutton(options_frame, text="Move Files", variable=action_var, value="move", 
                                font=("Helvetica", 10))
    copy_radio = tk.Radiobutton(options_frame, text="Copy Files", variable=action_var, value="copy", 
                                font=("Helvetica", 10))
    move_radio.grid(row=0, column=0, padx=10)
    copy_radio.grid(row=0, column=1, padx=10)

    # Warning Label
    tk.Label(root, text="WARNING: DJ Softwares might lose reference if you move files", 
             font=("Helvetica", 8), fg="red").pack(pady=(5, 10))

    # Folder Selection
    folder_frame = tk.Frame(root)
    folder_frame.pack(pady=(10, 5))
    tk.Button(folder_frame, text="Select Music Folder", command=lambda: select_folder(selected_folder), 
              font=("Helvetica", 10)).grid(row=0, column=0, padx=10)
    tk.Label(folder_frame, textvariable=selected_folder, font=("Helvetica", 8), wraplength=400, anchor="w", justify="left").grid(row=0, column=1, sticky="w")

    # Progress Bar
    progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
    progress.pack(pady=(10, 5))

    # Log Window
    log_window = tk.Text(root, height=10, width=80, state="disabled", bg="black", fg="white")
    log_window.pack(pady=(10, 5))

    def log_message(message):
        log_queue.put(message)

    def update_log():
        while not log_queue.empty():
            message = log_queue.get_nowait()
            log_window["state"] = "normal"
            log_window.insert("end", f"{message}\n")
            log_window["state"] = "disabled"
            log_window.see("end")
        root.after(100, update_log)

    # Start Button
    tk.Button(root, text="Start Organizing", command=lambda: start_organizing_threaded(
              token_entry.get(), selected_folder.get(), action_var.get()), font=("Helvetica", 10)).pack(pady=(10, 5))

    # Follow SoundCloud Button
    tk.Button(root, text="Follow Me on SoundCloud", command=open_soundcloud, font=("Helvetica", 10)).pack(pady=(5, 10))

    # Folder Selection Function
    def select_folder(selected_folder_var):
        folder = filedialog.askdirectory(title="Select your music folder")
        if folder:
            selected_folder_var.set(folder)

    # Start Organizing Function
    def start_organizing_with_feedback(user_token, folder, action):
        if not user_token:
            log_message("Error: Please enter your Discogs API token.")
            return
        if folder == "No folder selected":
            log_message("Error: Please select a music folder.")
            return

        # Initialize Discogs API client
        try:
            d = discogs_client.Client("DiscogsMusicOrganizer/1.0", user_token=user_token)
        except Exception as e:
            log_message(f"Error initializing Discogs client: {e}")
            return

        files = [file for file in os.listdir(folder) if file.endswith((".mp3", ".flac", ".wav", ".m4a", ".aiff"))]
        total_files = len(files)
        if total_files == 0:
            log_message("No audio files found in the selected folder.")
            return

        progress["maximum"] = total_files
        not_categorized_folder = os.path.join(folder, "Not categorized")
        os.makedirs(not_categorized_folder, exist_ok=True)

        for i, file in enumerate(files):
            try:
                file_path = os.path.join(folder, file)
                file_name, _ = os.path.splitext(file)
                release_info = fetch_release_info(d, file_path, file_name)
                if release_info:
                    folder_structure = os.path.join(
                        folder,
                        release_info.get("Label", "Unknown Label"),
                        f"{release_info.get('Catalog Number', 'Unknown')} - {release_info.get('Artist', 'Unknown')} - {release_info.get('Title', 'Unknown')} - {release_info.get('Year', 'Unknown')}",
                    )
                    os.makedirs(folder_structure, exist_ok=True)
                    if action == "move":
                        shutil.move(file_path, os.path.join(folder_structure, file))
                    elif action == "copy":
                        shutil.copy(file_path, os.path.join(folder_structure, file))
                else:
                    target_path = os.path.join(not_categorized_folder, file)
                    if action == "move":
                        shutil.move(file_path, target_path)
                    elif action == "copy":
                        shutil.copy(file_path, target_path)

                log_message(f"Processed: {file} ({i + 1}/{total_files})")
                progress["value"] = i + 1
                root.update_idletasks()

            except Exception as e:
                log_message(f"Error processing {file}: {e}")

        log_message("Organization complete!")

    def fetch_release_info(d, file_path, file_name):
        try:
            audio = MutagenFile(file_path)
            if audio and "TPE1" in audio and "TIT2" in audio:
                artist = audio["TPE1"].text[0] if "TPE1" in audio else None
                title = audio["TIT2"].text[0] if "TIT2" in audio else None
            else:
                if " - " in file_name:
                    artist, title = file_name.split(" - ", 1)
                else:
                    artist, title = None, None

            if artist and title:
                results = d.search(title.strip(), artist=artist.strip(), type="release")
                time.sleep(1)
                if results.count > 0:
                    release = results[0]
                    label = release.labels[0].name if release.labels else "Unknown Label"
                    return {
                        "Year": release.year if hasattr(release, "year") else "Unknown",
                        "Catalog Number": release.data.get("catno", "Unknown"),
                        "Artist": ", ".join(a.name for a in release.artists),
                        "Title": release.title,
                        "Label": label,
                    }
            return None
        except Exception as e:
            log_message(f"Error fetching release info: {e}")
            return None

    def start_organizing_threaded(user_token, folder, action):
        threading.Thread(
            target=start_organizing_with_feedback, args=(user_token, folder, action)
        ).start()

    update_log()
    root.mainloop()


if __name__ == "__main__":
    main()