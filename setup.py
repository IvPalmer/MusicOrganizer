from setuptools import setup
import py2app.util
import plistlib
import os
from distutils.cmd import Command
import shutil

# Monkey-patch py2app’s adhoc signing routine so it does nothing.
py2app.util.codesign_adhoc = lambda bundle: None

APP = ['src/music_organizer.py']
DATA_FILES = [('', ['__boot__.py'])]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['discogs_client', 'mutagen', 'charset_normalizer', 'chardet'],
    'includes': ['discogs_client'],
    'excludes': ['packaging'],
    'iconfile': 'logo.icns',
    'strip': False,
    'plist': {
        'LSEnvironment': {
            'PYTHONHOME': '@executable_path/../Resources',
            'PYTHONPATH': '@executable_path/../Resources/lib/python3.13',
            'LC_ALL': 'en_US.UTF-8',
            'LANG': 'en_US.UTF-8',
            'LC_TIME': 'en_US.UTF-8',
            'TK_MAC_NO_MENUBAR': '1',
            'TK_SILENCE_DEPRECATION': '1'
        },
        'NSMainNibFile': '',
        'CFBundleIdentifier': 'com.raphaelpalmer.musicorganizer',
        'LSMinimumSystemVersion': '11.0',
        'NSHighResolutionCapable': True,
        # Set initial values (which may be overwritten by py2app)
        'PythonInfoDict': {
            'PythonExecutable': '@executable_path/../Frameworks/Python.framework/Versions/3.13/Python',
            'PythonLongVersion': '3.13.1 (v3.13.1:06714517797, Dec  3 2024, 14:00:22) [Clang 15.0.0 (clang-1500.3.9.4)]',
            'PythonShortVersion': '3.13'
        }
    }
}

# Define a custom command to patch the Info.plist after building the app
class PatchPlist(Command):
    description = "Patch the Info.plist in the built app bundle to force the correct PythonInfoDict."
    user_options = []  # No options for this command

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        app_bundle = os.path.join('dist', 'music_organizer.app')
        plist_path = os.path.join(app_bundle, 'Contents', 'Info.plist')
        print("Patching Info.plist at:", plist_path)
        try:
            with open(plist_path, 'rb') as f:
                plist_data = plistlib.load(f)
        except Exception as e:
            print("Error reading Info.plist:", e)
            return
        # Force the correct Python runtime information.
        plist_data['PythonInfoDict'] = {
            'PythonExecutable': '@executable_path/../Frameworks/Python.framework/Versions/3.13/Python',
            'PythonShortVersion': '3.13',
            'PythonLongVersion': '3.13.1 (v3.13.1:06714517797, Dec  3 2024, 14:00:22) [Clang 15.0.0 (clang-1500.3.9.4)]'
        }
        try:
            with open(plist_path, 'wb') as f:
                plistlib.dump(plist_data, f)
            print("Info.plist patched successfully.")
        except Exception as e:
            print("Error writing Info.plist:", e)

# Define a custom command to remove the problematic _multibytecodec.so file.
class RemoveMbcodec(Command):
    description = "Remove _multibytecodec.so from the bundle (workaround for sandbox denial)."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        mbcodec_path = os.path.join(
            'dist',
            'music_organizer.app',
            'Contents',
            'Resources',
            'lib',
            'python3.13',
            'lib-dynload',
            '_multibytecodec.so'
        )
        if os.path.exists(mbcodec_path):
            print("Removing _multibytecodec.so at:", mbcodec_path)
            try:
                os.remove(mbcodec_path)
                print("_multibytecodec.so removed successfully.")
            except Exception as e:
                print("Error removing _multibytecodec.so:", e)
        else:
            print("_multibytecodec.so not found; nothing to remove.")

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    cmdclass={
        'patch_plist': PatchPlist,
        'remove_mbcodec': RemoveMbcodec
    },
)