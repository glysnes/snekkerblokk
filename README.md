# Snekkerblokk

Grid paper for iPad and Apple Pencil: draw lines, rectangles, circles and arcs, set dimensions and constraints like a Fusion sketch, and read off lengths, angles and saw settings.

## Files

- `src/snekkerblokk.html` – the app itself. The same file is published as a Claude artifact.
- `build.py` – builds `docs/` (installable web app with icon and offline support).
- `docs/` – what goes online (GitHub Pages serves this folder).

## Build

```bash
python3 build.py
```

## Put it on the iPad

1. Open the app's address in **Safari** on the iPad.
2. Tap the Share button and choose **Add to Home Screen**.
3. Open Snekkerblokk from the Home Screen. It runs full screen and works offline after the first visit.

Drawings are stored in the app on the iPad. Use **Save file** to keep a copy in Files or iCloud, and **Open file** to load it again.
