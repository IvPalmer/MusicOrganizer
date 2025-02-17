#!/bin/bash
# build_and_notarize.sh
#
# This script automates the process of cleaning, building, patching, signing,
# notarizing, and then launching the MusicOrganizer app in boot mode.
#
# Requirements:
#   - Your setup.py must include the custom commands 'patch_plist' and 'remove_mbcodec'.
#   - The sign_app.sh script must be in the project root and executable.
#   - Your keychain profile (here "MyNotaryProfile") must be configured for notarization.
#
# Usage:
#   chmod +x build_and_notarize.sh
#   ./build_and_notarize.sh
#
# If any command fails, the script will exit immediately (set -e).

set -e

# Function to print a header for each step.
function header() {
    echo ""
    echo "========================================"
    echo "$1"
    echo "========================================"
    echo ""
}

# 1. Clean previous builds.
header "Cleaning previous builds..."
rm -rf build dist

# 2. Build the app bundle with py2app.
header "Building the app bundle with py2app..."
python setup.py py2app

# 3. Patch the Info.plist.
header "Patching Info.plist..."
python setup.py patch_plist

# 4. Remove _multibytecodec (if present).
header "Removing _multibytecodec (if present)..."
python setup.py remove_mbcodec

# 5. Sign the app bundle.
header "Signing the app bundle..."
chmod +x sign_app.sh
./sign_app.sh

# 6. Package the app into a ZIP archive.
header "Packaging the app into a ZIP archive..."
ditto -c -k --sequesterRsrc --keepParent dist/music_organizer.app dist/music_organizer.zip

# 7. Submit the ZIP for notarization.
header "Submitting the app for notarization..."
xcrun notarytool submit --keychain-profile "MyNotaryProfile" --wait dist/music_organizer.zip

# 8. Staple the notarization ticket.
header "Stapling the notarization ticket..."
xcrun stapler staple dist/music_organizer.app

# 9. Verify the signed app using spctl.
header "Verifying the app signature..."
spctl -a -vv dist/music_organizer.app

# 10. Launch the app in boot mode (execute __boot__.py) instead of using 'open'.
header "Launching the app in boot mode (debug mode)..."
dist/music_organizer.app/Contents/MacOS/python __boot__.py

echo ""
echo "Build, notarization, and launch process completed successfully!"