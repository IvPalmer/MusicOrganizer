#!/usr/bin/env python3
# __boot__.py – Custom boot script for MusicOrganizer

import sys
import os
import traceback

# --- Custom Initialization Code ---
# Override _ctypes_setup so that we never attempt to load Carbon.
def _ctypes_setup():
    # On modern macOS, Carbon is not available.
    return None

# Ensure the boot namespace exists and override _ctypes_setup.
__boot__ = sys.modules.get("__boot__")
if __boot__ is None:
    __boot__ = {}
    sys.modules["__boot__"] = __boot__
__boot__["_ctypes_setup"] = _ctypes_setup

# --- Optional: argv emulation (if needed) ---
def _argv_emulation():
    # If you require argv emulation, implement it here.
    pass

try:
    _argv_emulation()
except Exception as e:
    print("Error in argv emulation:", e)

# End of custom boot script.