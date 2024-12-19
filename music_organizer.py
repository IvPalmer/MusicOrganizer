import os
import shutil
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
import queue
import discogs_client
from mutagen import File as MutagenFile


# Open SoundCloud function
def open_soundcloud():
    webbrowser.open("https://soundcloud.com/ivpalmer")


# Open folder based on OS
def open_folder(folder_path):
    try:
        if os.name == "nt":  # Windows
            os.startfile(folder_path)
        elif os.name == "posix":  # macOS or Linux
            os.system(f"open '{folder_path}'")
        else:
            messagebox.showinfo("Notification", "Your OS is not supported for opening folders.")
    except Exception as e:
        print(f"Error opening folder: {e}")


# Debugging function to print logs
def log_debug(message):
    print(f"[DEBUG]: {message}")


def main():
    # Initialize Tkinter
    root = tk.Tk()
    root.title("Music Organizer")
    root.geometry("700x700")  # Adjusted height for buttons and layout
    root.resizable(False, False)

    selected_folder = tk.StringVar(value="No folder selected")
    log_queue = queue.Queue()

    def scale_font(size):
        return size  # No scaling for simplicity in debugging

    # UI Layout
    container = tk.Frame(root)
    container.pack(expand=True, fill="both")

    tk.Label(container, text="Discogs API Token:", font=("Helvetica", scale_font(16))).pack(pady=(20, 10))
    token_entry = tk.Entry(container, width=40, font=("Helvetica", scale_font(14)))
    token_entry.pack(pady=(0, 15))

    def open_discogs_link():
        webbrowser.open("https://www.discogs.com/settings/developers")

    tk.Button(container, text="Find Your Token Here", command=open_discogs_link,
              font=("Helvetica", scale_font(14))).pack(pady=(0, 25))

    tk.Label(container, text="Select Action:", font=("Helvetica", scale_font(16))).pack(pady=(5, 5))
    action_var = tk.StringVar(value="move")
    options_frame = tk.Frame(container)
    options_frame.pack(pady=(0, 15))
    move_radio = tk.Radiobutton(options_frame, text="Move Files", variable=action_var, value="move", font=("Helvetica", scale_font(14)))
    copy_radio = tk.Radiobutton(options_frame, text="Copy Files", variable=action_var, value="copy", font=("Helvetica", scale_font(14)))
    move_radio.grid(row=0, column=0, padx=10)
    copy_radio.grid(row=0, column=1, padx=10)

    tk.Label(container, text="WARNING: DJ Softwares might lose reference if you move files", 
             font=("Helvetica", scale_font(12)), fg="red").pack(pady=(0, 15))

    folder_frame = tk.Frame(container)
    folder_frame.pack(pady=(5, 15))
    tk.Button(folder_frame, text="Select Music Folder", command=lambda: select_folder(selected_folder),
              font=("Helvetica", scale_font(14))).grid(row=0, column=0, padx=15)
    tk.Label(folder_frame, textvariable=selected_folder, font=("Helvetica", scale_font(12)), wraplength=600, anchor="w", justify="left").grid(row=0, column=1, sticky="w")

    progress = ttk.Progressbar(container, orient="horizontal", length=600, mode="determinate")
    progress.pack(pady=(10, 15))

    log_window = tk.Text(container, height=15, width=80, state="disabled", bg="black", fg="white", font=("Helvetica", scale_font(12)))
    log_window.pack(pady=(5, 15))

    def log_message(message):
        log_queue.put(message)
        log_debug(message)

    def update_log():
        while not log_queue.empty():
            message = log_queue.get_nowait()
            log_window["state"] = "normal"
            log_window.insert("end", f"{message}\n")
            log_window["state"] = "disabled"
            log_window.see("end")
        root.after(100, update_log)

    def select_folder(selected_folder_var):
        folder = filedialog.askdirectory(title="Select your music folder")
        if folder:
            selected_folder_var.set(folder)

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

            except FileNotFoundError as e:
                log_message(f"Error processing {file}: {e}")
            except Exception as e:
                log_message(f"Error processing {file}: {e}")
                log_debug(f"Exception: {e}")

            # Add a delay to avoid hitting Discogs API rate limits
            time.sleep(2)

        log_message("Organization complete!")
        open_folder(folder)

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

    tk.Button(container, text="Start Organizing", command=lambda: start_organizing_threaded(
              token_entry.get(), selected_folder.get(), action_var.get()), font=("Helvetica", scale_font(14))).pack(pady=(5, 15))

    tk.Button(container, text="Follow Me on SoundCloud", command=open_soundcloud, font=("Helvetica", scale_font(14))).pack(pady=(0, 15))

    update_log()
    root.mainloop()


if __name__ == "__main__":
    main()