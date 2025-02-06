# discogs_utils.py
import time
import difflib
import discogs_client
from mutagen import File as MutagenFile

def create_discogs_client(user_token):
    """
    Initializes and returns a Discogs client using the provided user token.
    Raises a RuntimeError if initialization fails.
    """
    try:
        client = discogs_client.Client("DiscogsMusicOrganizer/1.0", user_token=user_token)
        return client
    except Exception as e:
        raise RuntimeError(f"Error initializing Discogs client: {e}")

def fetch_release_info(d, file_path, file_name):
    """
    Extracts the artist and title from the audio file metadata (or filename) and searches Discogs for a matching release.
    
    New two-stage matching logic:
      1. **Strict Matching:**  
         Uses a higher threshold (0.7) when comparing the file’s track title (if available) and artist.
      2. **Broad Matching:**  
         If no strict match is found, uses a lower threshold (0.5) as a fallback.
         
    If a match is found (in either mode), returns a dictionary with release details.
    If no match is found, returns None.
    """
    try:
        # Attempt to extract metadata via mutagen.
        audio = MutagenFile(file_path)
        if audio and "TPE1" in audio and "TIT2" in audio:
            artist = audio["TPE1"].text[0]
            title = audio["TIT2"].text[0]
        else:
            # Fallback: try splitting the filename on " - "
            if " - " in file_name:
                artist, title = file_name.split(" - ", 1)
            else:
                artist, title = None, None

        if not (artist and title):
            return None

        artist = artist.strip()
        title = title.strip()

        # Use a combined query.
        query = f"{artist} {title}"
        results = d.search(query, type="release")
        time.sleep(1)  # Allow a brief pause for the API response

        if results.count == 0:
            return None

        # Define thresholds.
        strict_threshold = 0.7
        broad_threshold = 0.5

        strict_match = None
        strict_score = 0.0
        broad_match = None
        broad_score = 0.0

        for release in results:
            # Get release artist(s) as a string.
            release_artists = " ".join(a.name for a in release.artists) if hasattr(release, "artists") else ""
            artist_score = difflib.SequenceMatcher(None, artist.lower(), release_artists.lower()).ratio()

            # If the release has a tracklist, compare the file's title to each track title.
            if hasattr(release, "tracklist") and release.tracklist:
                best_track_score = 0.0
                for track in release.tracklist:
                    track_title = track.title if hasattr(track, "title") else ""
                    track_score = difflib.SequenceMatcher(None, title.lower(), track_title.lower()).ratio()
                    if track_score > best_track_score:
                        best_track_score = track_score
                # Combined score: 70% from best track match and 30% from artist match.
                combined_score = (0.7 * best_track_score) + (0.3 * artist_score)
            else:
                # Fallback: compare file title with release title.
                release_title = release.title if hasattr(release, "title") else ""
                title_score = difflib.SequenceMatcher(None, title.lower(), release_title.lower()).ratio()
                combined_score = (0.7 * title_score) + (0.3 * artist_score)

            # Update strict match if threshold met.
            if combined_score >= strict_threshold and combined_score > strict_score:
                strict_score = combined_score
                strict_match = release

            # Also update broad match if threshold met.
            if combined_score >= broad_threshold and combined_score > broad_score:
                broad_score = combined_score
                broad_match = release

        # Choose the strict match if available; otherwise, use the broad match.
        best_release = strict_match if strict_match is not None else broad_match
        if best_release is None:
            return None

        label = best_release.labels[0].name if best_release.labels else "Unknown Label"
        return {
            "Year": best_release.year if hasattr(best_release, "year") else "Unknown",
            "Catalog Number": best_release.data.get("catno", "Unknown"),
            "Artist": ", ".join(a.name for a in best_release.artists),
            "Title": best_release.title,
            "Label": label,
        }
    except Exception as e:
        print(f"Error fetching release info: {e}")
        return None