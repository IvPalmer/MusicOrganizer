"""
setup.py script for building music_organizer.app with py2app
"""
import os
import sys
import shutil
import glob
import subprocess
from setuptools import setup

# Override py2app's adhoc signing - we'll handle signing ourselves
import py2app.util
py2app.util.codesign_adhoc = lambda bundle: None

# Get the root directory (one level up from the config directory where this file is located)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(root_dir, 'src'))

APP_NAME = 'music_organizer'
APP = [os.path.join(root_dir, 'src/music_organizer.py')]
DATA_FILES = [
    # Include icon files
    (os.path.join('icons'), glob.glob(os.path.join(root_dir, 'resources/icons/*.png'))),
    (os.path.join('icons'), glob.glob(os.path.join(root_dir, 'resources/icons/*.icns'))),
    # Include any other resources needed by your app
    (os.path.join('images'), glob.glob(os.path.join(root_dir, 'resources/images/*'))),
]

# Define the options dictionary
OPTIONS = {
    'argv_emulation': True,
    'packages': ['mutagen', 'PIL'],
    'includes': ['tkinter', 'discogs_client', 'requests', 'urllib3'],
    'excludes': ['packaging'],
    'iconfile': os.path.join(root_dir, 'resources/icons/logo.icns'),
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': 'Music Organizer',
        'CFBundleGetInfoString': 'A tool for organizing music files',
        'CFBundleIdentifier': 'com.raphpalmer.musicorganizer',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0',
        'NSHumanReadableCopyright': ' 2023 Raphael Palmer, All Rights Reserved',
    }
}

# Command-line arguments handling
def main():
    """Handles different setup.py commands"""
    if len(sys.argv) == 1:
        sys.argv.append('py2app')
    
    # py2app command
    if sys.argv[1] == 'py2app':
        setup(
            app=APP,
            data_files=DATA_FILES,
            options={'py2app': OPTIONS},
            setup_requires=['py2app'],
        )

    # patch_plist command - modify Info.plist after py2app
    elif sys.argv[1] == 'patch_plist':
        plist_path = os.path.join(root_dir, 'dist', f'{APP_NAME}.app', 'Contents', 'Info.plist')
        if os.path.exists(plist_path):
            # Use PlistBuddy to set additional properties
            subprocess.call([
                '/usr/libexec/PlistBuddy', '-c', 
                'Add :NSHighResolutionCapable bool true', 
                plist_path
            ])
            print(f"Patched Info.plist at {plist_path}")
        else:
            print(f"Error: Info.plist not found at {plist_path}")

    # remove_mbcodec command - fix issue with _multibytecodec.so
    elif sys.argv[1] == 'remove_mbcodec':
        mbcodec_path = os.path.join(
            root_dir, 'dist', f'{APP_NAME}.app', 'Contents', 'Resources', 'lib', 
            'python3.13', 'lib-dynload', '_multibytecodec.so'
        )
        if os.path.exists(mbcodec_path):
            os.remove(mbcodec_path)
            print(f"Removed {mbcodec_path}")
        else:
            print(f"Warning: {mbcodec_path} not found")
    
    else:
        print(f"Unknown command: {sys.argv[1]}")
        print("Available commands: py2app, patch_plist, remove_mbcodec")
        sys.exit(1)

if __name__ == '__main__':
    main()