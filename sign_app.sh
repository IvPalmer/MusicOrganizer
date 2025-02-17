#!/bin/bash
# sign_app.sh – Revised signing script that signs each component individually,
# but deep-signs the problematic _multibytecodec.so dynamic library.

# === Configuration ===
APP_BUNDLE="dist/music_organizer.app"
SIGN_IDENTITY="Developer ID Application: Raphael Palmer (C4SJBQAUZY)"
ENTITLEMENTS="entitlements.plist"

echo "Removing extended attributes from ${APP_BUNDLE}..."
xattr -rc "$APP_BUNDLE"

# --- Sign internal frameworks and libraries ---
echo "Signing all dylibs in Contents/Frameworks..."
find "$APP_BUNDLE/Contents/Frameworks" -type f -name "*.dylib" -print0 | while IFS= read -r -d '' file; do
    echo "Signing framework/library: $file"
    codesign --force --options runtime --timestamp --sign "$SIGN_IDENTITY" "$file"
done

# --- Sign framework bundles ---
echo "Signing framework bundles..."
find "$APP_BUNDLE/Contents/Frameworks" -type d -name "*.framework" | while read -r framework; do
    FRAMEWORK_NAME=$(basename "$framework" .framework)
    if [[ "$FRAMEWORK_NAME" == "Tk" || "$FRAMEWORK_NAME" == "Tcl" ]]; then
         echo "Deep signing framework: $framework"
         codesign --force --deep --options runtime --timestamp --sign "$SIGN_IDENTITY" "$framework"
    else
         EXECUTABLE_PATH="$framework/Versions/Current/$FRAMEWORK_NAME"
         if [ -f "$EXECUTABLE_PATH" ]; then
              echo "Signing executable in $framework: $EXECUTABLE_PATH"
              codesign --force --options runtime --timestamp --sign "$SIGN_IDENTITY" "$EXECUTABLE_PATH"
         fi
    fi
done

# --- Sign resource binaries (e.g. .so files) in Contents/Resources ---
echo "Signing all binaries in Contents/Resources (e.g. .so files)..."
find "$APP_BUNDLE/Contents/Resources" -type f \( -name "*.so" -o -name "*.dylib" \) -print0 | while IFS= read -r -d '' file; do
    BASENAME=$(basename "$file")
    echo "Signing resource binary: $file"
    if [[ "$BASENAME" == "_multibytecodec.so" ]]; then
        echo "Deep signing _multibytecodec.so: $file"
        codesign --force --deep --options runtime --timestamp --sign "$SIGN_IDENTITY" "$file"
    else
        codesign --force --options runtime --timestamp --sign "$SIGN_IDENTITY" "$file"
    fi
done

# --- Sign the main executable (music_organizer) ---
MAIN_EXEC="$APP_BUNDLE/Contents/MacOS/music_organizer"
echo "Signing main executable: $MAIN_EXEC"
codesign --force --options runtime --timestamp --entitlements "$ENTITLEMENTS" --sign "$SIGN_IDENTITY" "$MAIN_EXEC"

# --- Sign additional executables in Contents/MacOS (e.g. the bundled python) ---
echo "Signing additional executables in Contents/MacOS..."
for exec_file in "$APP_BUNDLE/Contents/MacOS"/*; do
    if [ "$exec_file" != "$MAIN_EXEC" ]; then
        if [ -x "$exec_file" ]; then
            if [ -L "$exec_file" ]; then
                TARGET=$(readlink "$exec_file")
                if [[ "$TARGET" != /* ]]; then
                    TARGET="$(dirname "$exec_file")/$TARGET"
                fi
                exec_file_resolved="$TARGET"
            else
                exec_file_resolved="$exec_file"
            fi
            if file "$exec_file_resolved" | grep -q "Mach-O"; then
                echo "Signing additional executable: $exec_file (resolved as $exec_file_resolved)"
                codesign --force --options runtime --timestamp --entitlements "$ENTITLEMENTS" --sign "$SIGN_IDENTITY" "$exec_file_resolved"
            fi
        fi
    fi
done

# --- Finally, sign the app bundle container itself ---
echo "Signing the app bundle container..."
codesign --force --options runtime --timestamp --entitlements "$ENTITLEMENTS" --sign "$SIGN_IDENTITY" "$APP_BUNDLE"

# --- Verification ---
echo "Verifying the signature..."
codesign --verify --strict --verbose=4 "$APP_BUNDLE"
spctl -a -vv "$APP_BUNDLE"

echo "App bundle has been signed."