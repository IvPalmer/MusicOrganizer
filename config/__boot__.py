#!/usr/bin/env python3
"""
Simplified __boot__.py for MusicOrganizer
"""

import os
import sys
import traceback
import time

# Force Python not to write .pyc files
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

# Force use of chardet instead of charset_normalizer
os.environ['CHARDET_DISABLE_CHARSET_NORMALIZER'] = '1'
sys.frozen = True

print("DEBUG: __boot__.py has started", file=sys.stderr, flush=True)
time.sleep(1)  # Short pause for debugging if needed

current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
src_dir = os.path.join(current_dir, "src")
if os.path.isdir(src_dir):
    sys.path.insert(0, src_dir)

try:
    import music_organizer
    music_organizer.main()
except Exception as e:
    traceback.print_exc()
    sys.exit(1)