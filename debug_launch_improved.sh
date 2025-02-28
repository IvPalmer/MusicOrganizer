#!/bin/bash
# debug_launch_improved.sh - Improved debug launch script for MusicOrganizer

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directory to save logs
LOGS_DIR="logs"
mkdir -p "$LOGS_DIR"
LOG_FILE="$LOGS_DIR/launch_debug_$(date +%Y%m%d_%H%M%S).log"

# Log both to console and to file
exec > >(tee -a "$LOG_FILE") 2>&1

echo -e "${BLUE}=== Starting Music Organizer Debug Launch (Improved) ===${NC}"
echo "Current directory: $(pwd)"
echo "Date and time: $(date)"
echo "Log file: $LOG_FILE"
echo ""

APP_PATH="dist/music_organizer.app"

# Check if app exists
if [ ! -d "$APP_PATH" ]; then
    echo -e "${RED}ERROR: App bundle not found at $APP_PATH${NC}"
    echo "Please run ./build_fixed_app.sh first"
    exit 1
fi

# Set environment variables that might help
export CHARDET_DISABLE_CHARSET_NORMALIZER=1
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

echo -e "${YELLOW}Setting environment variables:${NC}"
echo "CHARDET_DISABLE_CHARSET_NORMALIZER=1"
echo "PYTHONDONTWRITEBYTECODE=1"
echo "PYTHONUNBUFFERED=1"
echo ""

# Create a custom bootloader script for direct launch
TEMP_BOOT_SCRIPT="/tmp/music_organizer_boot_$(date +%s).py"
cat > "$TEMP_BOOT_SCRIPT" <<EOF
#!/usr/bin/env python3
import os
import sys
import traceback

# Force chardet instead of charset_normalizer
os.environ['CHARDET_DISABLE_CHARSET_NORMALIZER'] = '1'

print("DEBUG: Starting custom bootloader with CHARDET_DISABLE_CHARSET_NORMALIZER=1")

# Find the Python version in the app bundle
app_path = "$APP_PATH"
resources_path = os.path.join(app_path, "Contents", "Resources")
print(f"DEBUG: Resources path: {resources_path}")

# Add the resources path to Python path
sys.path.insert(0, resources_path)

# Try to create dummy modules for charset_normalizer
try:
    import charset_normalizer.md
    print("DEBUG: charset_normalizer.md imported successfully")
except ImportError:
    print("DEBUG: Creating dummy charset_normalizer.md module")
    import types
    
    # Create dummy modules with required functions
    md_module = types.ModuleType('charset_normalizer.md')
    md_module.__file__ = 'dummy_md_module'
    
    # Add the required function that seems to be missing
    def is_suspiciously_successive_range(first_range, second_range):
        return False
    
    md_module.is_suspiciously_successive_range = is_suspiciously_successive_range
    sys.modules['charset_normalizer.md'] = md_module
    
    # Also create the mypyc version
    md_mypyc_module = types.ModuleType('charset_normalizer.md__mypyc')
    md_mypyc_module.__file__ = 'dummy_md_mypyc_module'
    sys.modules['charset_normalizer.md__mypyc'] = md_mypyc_module

# Also handle missing _multibytecodec
try:
    import _multibytecodec
    print("DEBUG: _multibytecodec imported successfully")
except ImportError:
    print("DEBUG: Installing dummy _multibytecodec module")
    multibytecodec_module = types.ModuleType('_multibytecodec')
    multibytecodec_module.__file__ = 'dummy_multibytecodec_module'
    sys.modules['_multibytecodec'] = multibytecodec_module

# Add lib paths
py_lib_path = None
for root, dirs, files in os.walk(os.path.join(resources_path, "lib")):
    if root.endswith("site-packages"):
        py_lib_path = root
        break

if py_lib_path:
    print(f"DEBUG: Found Python lib path: {py_lib_path}")
    sys.path.insert(0, py_lib_path)
    # Also add the parent directories
    parent = os.path.dirname(py_lib_path)
    sys.path.insert(0, parent)
    sys.path.insert(0, os.path.dirname(parent))

# Try to find and execute music_organizer.py
try:
    main_script = os.path.join(resources_path, "music_organizer.py")
    print(f"DEBUG: Attempting to execute: {main_script}")
    
    if os.path.exists(main_script):
        print("DEBUG: Script exists, will now execute it")
        with open(main_script, 'rb') as fp:
            code = compile(fp.read(), main_script, 'exec')
            exec(code, {'__name__': '__main__'})
    else:
        print(f"ERROR: Can't find {main_script}")
except Exception as e:
    print(f"ERROR in bootloader: {e}")
    traceback.print_exc()
EOF

echo -e "${YELLOW}Created custom bootloader at:${NC} $TEMP_BOOT_SCRIPT"

# Try to get all the Python executables in the app bundle
echo -e "${YELLOW}Checking Python executables in app bundle:${NC}"
PYTHON_EXECUTABLES=$(find "$APP_PATH" -name "Python" -type f -o -name "python" -type f -o -name "python3" -type f | sort)

for py_exec in $PYTHON_EXECUTABLES; do
    echo -e "${BLUE}Found Python executable:${NC} $py_exec"
done

# Try different launch methods
echo -e "\n${YELLOW}Attempting launch with different methods:${NC}"

if [[ -n "$PYTHON_EXECUTABLES" ]]; then
    # Get the first Python executable
    FIRST_PYTHON=$(echo "$PYTHON_EXECUTABLES" | head -1)
    
    echo -e "\n${BLUE}Method 1: Direct launch with custom bootloader${NC}"
    echo "Command: $FIRST_PYTHON $TEMP_BOOT_SCRIPT"
    echo "Output:"
    "$FIRST_PYTHON" "$TEMP_BOOT_SCRIPT" || true
    echo "App process exited with method 1"
fi

echo -e "\n${BLUE}Method 2: Launch with open command${NC}"
echo "Command: open $APP_PATH"
echo "Output:"
open $APP_PATH
sleep 3

echo -e "\n${BLUE}Method 3: Launch via Python executable directly${NC}"
MACOS_PYTHON="$APP_PATH/Contents/MacOS/python"
BOOT_PY="$APP_PATH/Contents/Resources/__boot__.py"
if [[ -f "$MACOS_PYTHON" && -f "$BOOT_PY" ]]; then
    echo "Command: $MACOS_PYTHON $BOOT_PY"
    echo "Output:"
    $MACOS_PYTHON $BOOT_PY 2>&1 &
    PID3=$!
    sleep 3
    if ps -p $PID3 > /dev/null 2>&1; then
        echo -e "${GREEN}App process is still running with method 3${NC}"
    else
        echo -e "${RED}App process exited with method 3${NC}"
    fi
else
    echo -e "${RED}Python executable or __boot__.py not found for method 3${NC}"
fi

echo -e "\n${BLUE}Checking running processes:${NC}"
ps -ef | grep -i "music_organizer" | grep -v grep

echo -e "\n${BLUE}Debug launch completed${NC}"
echo "Check $LOG_FILE for the full log"
