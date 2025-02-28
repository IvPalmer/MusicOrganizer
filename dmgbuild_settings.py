# dmgbuild_settings.py

# The volume name (what the DMG will display when mounted)
volume_name = "Music Organizer"

# The final DMG format; UDZO is a compressed, read-only DMG
format = "UDZO"

# The background image (optional). Put a background.png or .jpg in your project folder.
background = "background.png"

# Show an Applications symlink for drag-and-drop
applications_link = True

# Icon size in the DMG window
icon_size = 128

# Files or folders to include in the DMG. Typically just your .app
files = [ "dist/music_organizer.app" ]

# Additional symlinks. This creates an "Applications" folder alias if you prefer manual control
symlinks = { "Applications": "/Applications" }