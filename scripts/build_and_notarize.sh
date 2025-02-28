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
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PYTHON="${ROOT_DIR}/venv_universal2/bin/python3"

# 1. Clean previous builds
header "Cleaning previous builds..."
rm -rf ${ROOT_DIR}/build ${ROOT_DIR}/dist

# 2. Build the app bundle with py2app
header "Building the app bundle with py2app..."
cd ${ROOT_DIR} && ${VENV_PYTHON} -m config.setup py2app

# 3. Patch the Info.plist (if needed)
header "Patching Info.plist..."
cd ${ROOT_DIR} && ${VENV_PYTHON} -m config.setup patch_plist

# 4. Remove _multibytecodec (if present)
header "Removing _multibytecodec.so (if present)..."
cd ${ROOT_DIR} && ${VENV_PYTHON} -m config.setup remove_mbcodec

# 5. Sign the app
header "Signing the app bundle..."
chmod +x ${ROOT_DIR}/scripts/sign_app.sh
${ROOT_DIR}/scripts/sign_app.sh

# 6. Package the app into a ZIP archive
header "Packaging the app into a ZIP archive..."
ditto -c -k --sequesterRsrc --keepParent "${ROOT_DIR}/dist/${APP_NAME}" "${ROOT_DIR}/dist/${ZIP_NAME}"

# 7. Submit the ZIP for notarization
header "Submitting the ZIP for notarization..."
xcrun notarytool submit --keychain-profile "$SIGN_PROFILE" --wait "${ROOT_DIR}/dist/${ZIP_NAME}"

# 8. Staple the notarization ticket
header "Stapling the notarization ticket..."
xcrun stapler staple "${ROOT_DIR}/dist/${APP_NAME}"

# 9. Verify with spctl
header "Verifying the app signature..."
spctl -a -vv "${ROOT_DIR}/dist/${APP_NAME}"

# 10. (Optional) Launch the app in debug mode
# header "Launching the app in debug mode..."
# "${ROOT_DIR}/dist/${APP_NAME}/Contents/MacOS/python" "${ROOT_DIR}/dist/${APP_NAME}/Contents/Resources/__boot__.py"

echo ""
echo "Build, notarization, and launch process completed successfully!"