#!/bin/bash
# build_and_notarize.sh
#
# A simplified script to build, sign, notarize, and staple the MusicOrganizer app.

set -e

function header() {
    echo ""
    echo "========================================"
    echo "$1"
    echo "========================================"
    echo ""
}

SIGN_PROFILE="MyNotaryProfile"
APP_NAME="music_organizer.app"
ZIP_NAME="music_organizer.zip"

# 1. Clean previous builds
header "Cleaning previous builds..."
rm -rf build dist

# 2. Build the app bundle with py2app
header "Building the app bundle with py2app..."
python setup.py py2app

# 3. Patch the Info.plist (if needed)
header "Patching Info.plist..."
python setup.py patch_plist

# 4. Remove _multibytecodec (if present)
header "Removing _multibytecodec.so (if present)..."
python setup.py remove_mbcodec

# 5. Sign the app
header "Signing the app bundle..."
chmod +x sign_app.sh
./sign_app.sh

# 6. Package the app into a ZIP archive
header "Packaging the app into a ZIP archive..."
ditto -c -k --sequesterRsrc --keepParent "dist/${APP_NAME}" "dist/${ZIP_NAME}"

# 7. Submit the ZIP for notarization
header "Submitting the ZIP for notarization..."
xcrun notarytool submit --keychain-profile "$SIGN_PROFILE" --wait "dist/${ZIP_NAME}"

# 8. Staple the notarization ticket
header "Stapling the notarization ticket..."
xcrun stapler staple "dist/${APP_NAME}"

# 9. Verify with spctl
header "Verifying the app signature..."
spctl -a -vv "dist/${APP_NAME}"

# 10. (Optional) Launch the app in debug mode
header "Launching the app in debug mode..."
"dist/${APP_NAME}/Contents/MacOS/python" "dist/${APP_NAME}/Contents/Resources/__boot__.py"

echo ""
echo "Build, notarization, and launch process completed successfully!"