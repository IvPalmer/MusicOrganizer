from setuptools import setup

# (Optional) Override py2app’s adhoc signing function if needed.
try:
    import py2app.util
    py2app.util.codesign_adhoc = lambda bundle: None
    print("Overriding py2app.util.codesign_adhoc")
except Exception as e:
    print("Error overriding py2app.util.codesign_adhoc:", e)

APP = ['src/music_organizer.py']

# DATA_FILES entry ensures our custom __boot__.py is placed into Resources.
DATA_FILES = [('', ['__boot__.py'])]

OPTIONS = {
    'argv_emulation': True,
    'packages': ['discogs_client', 'mutagen'],
    'includes': ['discogs_client'],  # <-- Add this line
    'excludes': ['packaging'],
    'iconfile': 'logo.icns',
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
        'NSMainNibFile': ''
    },
    # 'codesign_identity': ''  # leave this commented or empty if present
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)