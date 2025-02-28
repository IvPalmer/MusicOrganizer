#!/bin/bash
# create_and_notarize_dmg.sh
#
# This script creates a DMG from the already built and notarized MusicOrganizer.app,
# signs the DMG, then submits the DMG for notarization, staples the notarization ticket,
# and finally verifies the DMG signature.
#
# Requirements:
#  - Your MusicOrganizer.app must be in dist/music_organizer.app.
#  - dmgbuild_settings.py must be properly configured.
#  - Your keychain profile (here "MyNotaryProfile") must be set up.
#
# Usage:
#   chmod +x create_and_notarize_dmg.sh
#   ./create_and_notarize_dmg.sh

set -e

# Configuration
SIGN_PROFILE="MyNotaryProfile"
SIGN_IDENTITY="Developer ID Application: Raphael Palmer (C4SJBQAUZY)"
DMG_NAME="MusicOrganizer.dmg"
VOLUME_NAME="Music Organizer"  # This is what appears when the DMG is mounted

echo "========================================"
echo "Building DMG using dmgbuild..."
echo "========================================"
# Use dmgbuild to create the DMG from the notarized .app.
dmgbuild -s dmgbuild_settings.py "$VOLUME_NAME" "$DMG_NAME"

echo ""
echo "========================================"
echo "Signing DMG..."
echo "========================================"
# Sign the DMG so that it contains a valid code signature.
codesign --force --timestamp --sign "$SIGN_IDENTITY" "$DMG_NAME"

echo ""
echo "========================================"
echo "Notarizing DMG..."
echo "========================================"
# Submit the DMG for notarization.
xcrun notarytool submit --keychain-profile "$SIGN_PROFILE" --wait "$DMG_NAME"

echo ""
echo "========================================"
echo "Stapling the notarization ticket to the DMG..."
echo "========================================"
xcrun stapler staple "$DMG_NAME"

echo ""
echo "========================================"
echo "Verifying the DMG signature..."
echo "========================================"
spctl -a -vv "$DMG_NAME"

echo ""
echo "DMG creation, signing, notarization, and stapling completed successfully!"