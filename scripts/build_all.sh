#!/bin/bash
# build_all.sh
#
# A comprehensive build script that:
# 1. Builds the MusicOrganizer.app bundle
# 2. Signs and notarizes the app bundle
# 3. Creates a DMG
# 4. Signs and notarizes the DMG
#
# This combines build_and_notarize.sh and create_and_notarize_dmg.sh
# into a single command.

set -e  # Exit immediately if a command exits with a non-zero status

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="${ROOT_DIR}/scripts"

# Add virtual environment to path
export PYTHONPATH="${ROOT_DIR}/venv_universal2/lib/python3.13/site-packages:${PYTHONPATH}"

function header() {
    echo ""
    echo "=========================================================="
    echo "$1"
    echo "=========================================================="
    echo ""
}

header "PHASE 1: BUILDING AND NOTARIZING APP BUNDLE"
header "Running build_and_notarize.sh..."

# Run the app build and notarization script
chmod +x "${SCRIPTS_DIR}/build_and_notarize.sh"
"${SCRIPTS_DIR}/build_and_notarize.sh"

header "PHASE 2: CREATING AND NOTARIZING DMG"
header "Running create_and_notarize_dmg.sh..."

# Run the DMG creation and notarization script
chmod +x "${SCRIPTS_DIR}/create_and_notarize_dmg.sh"
"${SCRIPTS_DIR}/create_and_notarize_dmg.sh"

header "BUILD COMPLETE!"
echo "The following files have been created:"
echo "- App Bundle: ${ROOT_DIR}/dist/music_organizer.app"
echo "- DMG File:   ${ROOT_DIR}/dist/MusicOrganizer.dmg"
echo ""
echo "Both files have been signed and notarized with Apple"
echo "and are ready for distribution."
echo ""
echo "To test the app, run: open ${ROOT_DIR}/dist/music_organizer.app"
echo "To test the DMG, run: open ${ROOT_DIR}/dist/MusicOrganizer.dmg"
