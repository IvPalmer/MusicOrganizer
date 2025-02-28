#!/bin/bash
# debug_launch_improved.sh
# A simple debug script to launch the MusicOrganizer app and capture logs.

set -e

LOGS_DIR="logs"
mkdir -p "$LOGS_DIR"
LOG_FILE="$LOGS_DIR/debug_launch_$(date +%Y%m%d_%H%M%S).log"

exec > >(tee -a "$LOG_FILE") 2>&1

APP_PATH="dist/music_organizer.app"

echo "=== Debug Launch for MusicOrganizer ==="
echo "Timestamp: $(date)"
echo "Log file: $LOG_FILE"
echo ""

if [ ! -d "$APP_PATH" ]; then
    echo "ERROR: $APP_PATH not found. Please build the app first."
    exit 1
fi

echo "Running spctl check..."
spctl -a -vv "$APP_PATH" || true
echo ""

echo "Launching via 'open' command..."
open "$APP_PATH"
sleep 3

echo "If the app didn't stay open, check $LOG_FILE or Console.app for crash logs."