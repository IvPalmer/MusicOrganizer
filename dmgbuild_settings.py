# dmgbuild_settings.py

# The volume name (what the DMG will display when mounted)
volume_name = "Music Organizer"

# The final DMG format; UDZO is a compressed, read-only DMG
format = "UDZO"

# The background image. Replace with your actual background filename.
background = "background.png"

# Show an Applications symlink for drag-and-drop
applications_link = True

# Icon size in the DMG window
icon_size = 128

# The window_rect sets the DMG window position and size on screen.
# Adjust these values to match your background image dimensions.
# Format: ((x, y), (width, height))
window_rect = ((100, 100), (600, 400))

# Files or folders to include in the DMG. Typically just your .app
files = ["dist/music_organizer.app"]

# Additional symlinks. This creates an "Applications" folder alias if you prefer manual control
symlinks = { "Applications": "/Applications" }

# icon_locations places each icon (the .app and the Applications symlink)
# at specific (x, y) coordinates in the DMG window.
# Adjust these coordinates to position icons over your background's design.
icon_locations = {
    "music_organizer.app": (140, 120),
    "Applications": (360, 120)
}