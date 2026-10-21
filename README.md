# Snekkerblokk

Rutepapir for iPad og penn: tegn streker, rektangler, sirkler og buer, sett mål og regler som i Fusion-sketch, og les av lengder, vinkler og sagvinkler.

## Filer

- `src/snekkerblokk.html` – selve appen. Samme fil publiseres som Claude-artefakt.
- `build.py` – bygger `docs/` (installerbar webapp med ikon og offline-støtte).
- `docs/` – det som legges ut på nett (GitHub Pages serverer denne mappen).

## Bygge

```bash
python3 build.py
```

## Legge den på iPad

1. Åpne adressen til appen i **Safari** på iPad.
2. Trykk Del-knappen og velg **Legg til på Hjem-skjerm**.
3. Åpne Snekkerblokk fra Hjem-skjermen. Den starter i fullskjerm og virker uten nett etter første gang.

Tegningene lagres i appen på iPad-en. Bruk **Lagre fil** for å legge en kopi i Filer eller iCloud, og **Åpne fil** for å hente den inn igjen.
