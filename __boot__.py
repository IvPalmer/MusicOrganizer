#!/usr/bin/env python3
# __boot__.py – Updated boot script for MusicOrganizer with early patch for charset_normalizer

import sys
import os
import traceback
import time
import types

# --- Debug Logging: Startup ---
print("DEBUG: __boot__.py has started", file=sys.stderr, flush=True)
# Pause for 10 seconds to allow attaching a debugger or viewing output.
time.sleep(10)

# --- Force Early Import and Patch for charset_normalizer ---
try:
    import charset_normalizer
    import charset_normalizer.md
    print("DEBUG: Successfully pre-imported charset_normalizer.md", file=sys.stderr, flush=True)
    # If the attribute 'md__mypyc' is missing (causing circular import issues), set it to a dummy value.
    if not hasattr(charset_normalizer, "md__mypyc"):
        setattr(charset_normalizer, "md__mypyc", None)
        print("DEBUG: Set dummy attribute md__mypyc on charset_normalizer", file=sys.stderr, flush=True)
    else:
        print("DEBUG: charset_normalizer already has attribute md__mypyc", file=sys.stderr, flush=True)
except Exception as e:
    print("DEBUG: Error pre-importing charset_normalizer.md:", e, file=sys.stderr, flush=True)

# --- Install Dummy Module for _multibytecodec ---
if "_multibytecodec" not in sys.modules:
    dummy_module = types.ModuleType("_multibytecodec")
    sys.modules["_multibytecodec"] = dummy_module
    print("DEBUG: Installed dummy _multibytecodec module", file=sys.stderr, flush=True)
else:
    print("DEBUG: _multibytecodec already in sys.modules", file=sys.stderr, flush=True)

# --- Override _ctypes_setup ---
def _ctypes_setup():
    # On macOS, Carbon is not available; override to prevent errors.
    return None

__boot__ = sys.modules.get("__boot__")
if __boot__ is None:
    __boot__ = {}
    sys.modules["__boot__"] = __boot__
__boot__["_ctypes_setup"] = _ctypes_setup

# --- Optional: argv emulation ---
def _argv_emulation():
    # Implement argv emulation if needed.
    pass

try:
    _argv_emulation()
except Exception as e:
    print("Error in argv emulation:", e, file=sys.stderr)

# --- Import and Launch the Main Application Module ---
try:
    import music_organizer
except Exception:
    traceback.print_exc()
    sys.exit(1)