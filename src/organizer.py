# organizer.py
import os
import shutil
import time
from discogs_utils import fetch_release_info

def organize_files(discogs_client, folder, action, log_callback=None, progress_callback=None):
    """
    Organizes music files in the given folder using the provided Discogs client.
    
    Parameters:
      - discogs_client: A properly initialized Discogs client.
      - folder: The directory containing the music files.
      - action: "move" or "copy" files into organized subfolders.
      - log_callback: (Optional) A function that receives log messages.
      - progress_callback: (Optional) A function that receives progress updates as (current, total).
    """
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    # Collect audio files (case-insensitive extension matching).
    files = [f for f in os.listdir(folder) if f.lower().endswith((".mp3", ".flac", ".wav", ".m4a", ".aiff"))]
    total_files = len(files)
    if total_files == 0:
        log("No audio files found in the selected folder.")
        return

    not_categorized_folder = os.path.join(folder, "Not categorized")
    os.makedirs(not_categorized_folder, exist_ok=True)

    missing_count = 0
    max_attempts = 3

    for i, file in enumerate(files):
        file_path = os.path.join(folder, file)
        attempt = 0
        while attempt < max_attempts and not os.path.exists(file_path):
            if attempt == 0:
                log(f"File not found, trying again: {file} (attempt {attempt+1})")
            else:
                log(f"File still not found, trying again: {file} (attempt {attempt+1})")
            time.sleep(1)  # Wait 1 second before retrying.
            attempt += 1

        if not os.path.exists(file_path):
            log(f"File not found after {max_attempts} attempts: {file}")
            missing_count += 1
            if progress_callback:
                progress_callback(i+1, total_files)
            continue

        try:
            file_name, _ = os.path.splitext(file)
            release_info = fetch_release_info(discogs_client, file_path, file_name)
            if release_info:
                folder_structure = os.path.join(
                    folder,
                    release_info.get("Label", "Unknown Label"),
                    f"{release_info.get('Catalog Number', 'Unknown')} - {release_info.get('Artist', 'Unknown')} - {release_info.get('Title', 'Unknown')} - {release_info.get('Year', 'Unknown')}",
                )
                os.makedirs(folder_structure, exist_ok=True)
                dest = os.path.join(folder_structure, file)
            else:
                dest = os.path.join(not_categorized_folder, file)
            
            if action == "move":
                shutil.move(file_path, dest)
            elif action == "copy":
                shutil.copy(file_path, dest)
            else:
                log(f"Unknown action '{action}' for file: {file}")
                continue

            log(f"Processed: {file} ({i+1}/{total_files})")
            if progress_callback:
                progress_callback(i+1, total_files)
        except Exception as e:
            log(f"Error processing {file}: {e}")
        # Pause briefly to help avoid hitting Discogs API rate limits.
        time.sleep(2)

    log("Organization complete!")
    log(f"Total files not found: {missing_count}")