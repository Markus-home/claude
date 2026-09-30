# Trainingsplan

Web-App für das iPhone: Wochenplan mit Übungen (Sätze, Wiederholungen, Gewicht oder Dauer und Distanz), Sätze im Training abhaken, Verlauf der letzten 8 Wochen.

## Aufbau

- `src/app.html`: die ganze App (HTML, CSS, JavaScript in einer Datei, ohne Abhängigkeiten).
- `build.py`: baut daraus in `docs/` die eigenständige Web-App mit iOS-Home-Bildschirm-Tags, Manifest, App-Icon und Offline-Cache.

```sh
python3 build.py
```

## Speicherung

- Als Claude-Artifact: im privaten Bereich deines Claude-Kontos, auf allen Geräten gleich.
- Als eigenständige Web-App (`docs/`): im Browser-Speicher des iPhones. Löschst du die Website-Daten in Safari, ist der Plan weg.

## Aufs iPhone

1. `docs/` über HTTPS bereitstellen, z. B. mit GitHub Pages (Settings → Pages → Branch `main`, Ordner `/docs`).
2. Die Seite in Safari öffnen, auf „Teilen“ tippen und „Zum Home-Bildschirm“ wählen.
