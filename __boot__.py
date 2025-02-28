#!/usr/bin/env python3
"""
Simplified __boot__.py for MusicOrganizer

This boot script:
  - Sets the environment variable to force chardet.
  - Marks the app as frozen.
  - Adds the Resources folder (and its 'src' subfolder if present) to sys.path.
  - Imports the main module (music_organizer) and calls its main() function.
"""

import os
import sys
import traceback
import time

# Force use of chardet instead of charset_normalizer
os.environ['CHARDET_DISABLE_CHARSET_NORMALIZER'] = '1'
sys.frozen = True

print("DEBUG: __boot__.py has started", file=sys.stderr, flush=True)
time.sleep(1)  # Short pause for debugging if needed

# Add the Resources directory (where __boot__.py resides) to sys.path
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    print("DEBUG: Added Resources directory to sys.path:", current_dir, file=sys.stderr)

# If a 'src' subfolder exists, add it to sys.path so that modules inside it can be imported.
src_dir = os.path.join(current_dir, "src")
if os.path.isdir(src_dir):
    sys.path.insert(0, src_dir)
    print("DEBUG: Added src directory to sys.path:", src_dir, file=sys.stderr)

# Now import the main module and call its main() function explicitly.
try:
    import music_organizer
    # Explicitly call main() so that the GUI is started.
    music_organizer.main()
except Exception as e:
    traceback.print_exc()
    sys.exit(1)