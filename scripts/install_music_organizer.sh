#!/bin/bash

APP_NAME="Music Organizer"
DMG_NAME="MusicOrganizer.dmg"
APP_VOLUME_NAME="Music Organizer"
APP_BUNDLE_NAME="music_organizer.app"
INSTALL_DIR="/Applications"
INSTALLER_DIR=$(pwd)

echo "Installing $APP_NAME..."

# Check if the DMG file exists
if [ ! -f "$INSTALLER_DIR/$DMG_NAME" ]; then
    echo "Error: $DMG_NAME not found in $INSTALLER_DIR."
    exit 1
fi

# Mount the DMG
echo "Mounting $DMG_NAME..."
MOUNT_POINT=$(hdiutil attach "$INSTALLER_DIR/$DMG_NAME" -nobrowse -quiet | grep -o '/Volumes/.*')
if [ -z "$MOUNT_POINT" ]; then
    echo "Error: Failed to mount $DMG_NAME."
    exit 1
fi

# Copy the app to /Applications
echo "Copying $APP_NAME to $INSTALL_DIR..."
cp -R "$MOUNT_POINT/$APP_BUNDLE_NAME" "$INSTALL_DIR/"

if [ $? -ne 0 ]; then
    echo "Error: Failed to copy $APP_BUNDLE_NAME to $INSTALL_DIR."
    hdiutil detach "$MOUNT_POINT" -quiet
    exit 1
fi

# Remove quarantine attribute
echo "Removing Gatekeeper quarantine attribute..."
xattr -d com.apple.quarantine "$INSTALL_DIR/$APP_BUNDLE_NAME" 2>/dev/null

# Unmount the DMG
echo "Unmounting $DMG_NAME..."
hdiutil detach "$MOUNT_POINT" -quiet

echo "$APP_NAME has been successfully installed and is ready to use!"
echo "You can find it in your $INSTALL_DIR folder."

exit 0