Here’s a `README.md` file for your project:

---

# Music Organizer

Music Organizer is a Python-based application designed to help you organize your music files using metadata fetched from the Discogs API. It provides a simple user interface where you can move or copy music files into a structured folder hierarchy based on metadata like **Label**, **Catalog Number**, **Artist**, **Title**, and **Year**.

---

## Features

- **Discogs API Integration**: Fetches metadata for your music files using the Discogs database.
- **Custom Folder Structure**: Organizes music into folders by `Label / "CAT NUMBER" - "ARTIST" - "TITLE" - "YEAR"`.
- **File Action Options**: Choose to either move or copy the files.
- **Progress Bar**: Displays real-time progress of the organization process.
- **Error Handling**: Files with incomplete metadata are moved to a "Not categorized" folder.
- **Cross-Platform**: Works on both Windows and macOS.

---

## Requirements

1. Python 3.9 or later
2. The following Python libraries:
   - `discogs-client`
   - `mutagen`
   - `tkinter` (included with Python but must be installed separately on some systems)
3. A valid Discogs API token (get yours [here](https://www.discogs.com/settings/developers)).

---

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/IvPalmer/MusicOrganizer.git
   cd MusicOrganizer
   ```

2. **Install Dependencies**:

   Create a virtual environment (optional but recommended):

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

   Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

---

## How to Use

1. Run the application:

   ```bash
   python music_organizer.py
   ```

2. **Enter your Discogs API Token** in the provided field.

3. **Select an Action**:
   - `Move Files`: Moves the music files to the organized folder structure.
   - `Copy Files`: Creates copies of the files in the organized folder structure.

4. **Choose a Music Folder**:
   Click on the "Select Music Folder" button and navigate to the folder containing your music files.

5. **Start Organizing**:
   Press the "Start Organizing" button. The progress bar and log window will show the real-time progress.

6. Once complete, a message box will notify you that the organization is finished.

---

## Folder Structure

Organized music will follow this structure:

```
Label/
  CAT NUMBER - ARTIST - TITLE - YEAR/
    Track 1.mp3
    Track 2.mp3
```

Files without enough metadata will be moved to a `Not categorized` folder in the root directory.

---

## Building Executables

To create standalone executables:

### macOS

```bash
pyinstaller --onefile --windowed --hidden-import=tkinter music_organizer.py
```

### Windows

Use a Windows machine or Docker to build the executable.

---

## Contributing

Feel free to open issues or create pull requests if you have suggestions or improvements.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.

---

## Follow Me!

Follow me on SoundCloud for some great music: [https://soundcloud.com/ivpalmer](https://soundcloud.com/ivpalmer)

---

Let me know if you need any updates!
