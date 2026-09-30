#!/usr/bin/env python3
"""Builds the standalone iPhone web app into docs/ from src/app.html.

src/app.html is the page body (it is also published as-is as a claude.ai artifact).
This script wraps it in a full HTML document with the iOS home-screen meta tags,
writes the web app manifest, the app icon and a small offline service worker.
"""
import json
import pathlib
import struct
import zlib

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "docs"
BLUE = (31, 79, 224)
WHITE = (255, 255, 255)

HEAD = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Training">
<meta name="theme-color" content="#eef1f5" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0d1118" media="(prefers-color-scheme: dark)">
<link rel="apple-touch-icon" href="icon-180.png">
<link rel="icon" type="image/png" href="icon-192.png">
<link rel="manifest" href="manifest.webmanifest">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}[hidden]{display:none!important}</style>
</head>
<body>
"""

FOOT = """
<script>
if ("serviceWorker" in navigator && location.protocol === "https:") {
  navigator.serviceWorker.register("sw.js").catch(() => {});
}
</script>
</body>
</html>
"""

SW = """const CACHE = "trainingsplan-v1";
const FILES = ["./", "index.html", "manifest.webmanifest", "icon-180.png", "icon-192.png", "icon-512.png"];
self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
// Network first, cache as fallback, so updates arrive whenever the phone is online.
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  e.respondWith(
    fetch(e.request)
      .then((res) => {
        if (res.ok && new URL(e.request.url).origin === location.origin) {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(e.request, copy));
        }
        return res;
      })
      .catch(() => caches.match(e.request).then((r) => r || caches.match("index.html")))
  );
});
"""


def png(size: int) -> bytes:
    """Draws a white dumbbell on the accent blue, as a plain RGB PNG."""
    s = size / 180

    def inside(x, y):
        cx, cy = x / s, y / s
        rects = [
            (52, 86, 128, 94),   # bar
            (38, 58, 52, 122),   # inner plates
            (128, 58, 142, 122),
            (26, 70, 38, 110),   # outer plates
            (142, 70, 154, 110),
        ]
        return any(x0 <= cx < x1 and y0 <= cy < y1 for x0, y0, x1, y1 in rects)

    rows = bytearray()
    for y in range(size):
        rows.append(0)
        for x in range(size):
            rows.extend(WHITE if inside(x + 0.5, y + 0.5) else BLUE)

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(rows), 9))
            + chunk(b"IEND", b""))


def main():
    OUT.mkdir(exist_ok=True)
    body = (ROOT / "src" / "app.html").read_text(encoding="utf-8")
    (OUT / "index.html").write_text(HEAD + body + FOOT, encoding="utf-8")
    (OUT / "sw.js").write_text(SW, encoding="utf-8")
    manifest = {
        "name": "Trainingsplan",
        "short_name": "Training",
        "lang": "de",
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "background_color": "#eef1f5",
        "theme_color": "#eef1f5",
        "icons": [
            {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
    }
    (OUT / "manifest.webmanifest").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    for size in (180, 192, 512):
        (OUT / f"icon-{size}.png").write_bytes(png(size))
    (OUT / ".nojekyll").write_text("")
    print("Built", ", ".join(sorted(p.name for p in OUT.iterdir())))


if __name__ == "__main__":
    main()
