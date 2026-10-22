#!/usr/bin/env python3
"""Bygger iPad-appen (docs/) fra src/snekkerblokk.html.

src/snekkerblokk.html er samme fil som publiseres som Claude-artefakt.
Her pakkes den inn i et fullt HTML-dokument med manifest, ikoner og
service worker, slik at den kan legges på Hjem-skjermen og virke uten nett.

Kjør:  python3 build.py
"""
import hashlib
import json
from datetime import datetime
import math
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / 'src' / 'snekkerblokk.html'
OUT = ROOT / 'docs'

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="D-Rafter">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#13212e" media="(prefers-color-scheme: dark)">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-180.png">
<link rel="icon" href="icon-192.png">
<style>body{margin:0}</style>
"""

# Når en ny service worker tar over en side som allerede kjører, er en ny versjon lastet ned.
SW_REGISTER = """<script>
if ('serviceWorker' in navigator) addEventListener('load', () => {
  const hadController = !!navigator.serviceWorker.controller;
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (hadController && window.snekkerblokkUpdateReady) window.snekkerblokkUpdateReady();
  });
  navigator.serviceWorker.register('sw.js').then(reg => reg.update()).catch(() => {});
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') navigator.serviceWorker.getRegistration().then(r => r && r.update()).catch(() => {});
  });
});
</script>
"""

SW = """// Snekkerblokk offline: selve siden hentes fra nettet først (lageret er reserve uten nett),
// resten vises fra lageret med en gang og fornyes i bakgrunnen. version.json går alltid til nettet.
const CACHE = 'snekkerblokk-%s';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'icon-180.png', 'icon-192.png', 'icon-512.png'];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL.map(u => new Request(u, { cache: 'reload' })))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  if (new URL(e.request.url).pathname.endsWith('version.json')) return;
  if (e.request.mode === 'navigate') {
    e.respondWith(fetch(e.request, { cache: 'no-store' }).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put('./', copy)); }
      return res;
    }).catch(() => caches.match('./').then(hit => hit || caches.match('index.html'))));
    return;
  }
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then(hit => {
    const net = fetch(e.request).then(res => {
      if (res.ok || res.type === 'opaque') { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
      return res;
    }).catch(() => hit);
    return hit || net;
  }));
});
"""

MANIFEST = {
    'name': 'D-Rafter',
    'short_name': 'D-Rafter',
    'description': 'Grid paper with dimensions, angles and constraints for woodworking projects.',
    'lang': 'en',
    'start_url': './',
    'scope': './',
    'display': 'standalone',
    'orientation': 'any',
    'background_color': '#0f1c29',
    'theme_color': '#13212e',
    'icons': [
        {'src': 'icon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
        {'src': 'icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
        {'src': 'icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
    ],
}


def png(path, w, h, pixels):
    raw = b''.join(b'\x00' + bytes(pixels[y * w * 3:(y + 1) * w * 3]) for y in range(h))
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
                     + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


def icon(size):
    """Blåkopi-rutepapir med en gavlvegg; ett sperre i aksentfarge."""
    bg, grid, ink, accent = (19, 33, 46), (33, 58, 82), (230, 238, 245), (93, 223, 189)
    s = size / 100
    segs = [  # (x0, y0, x1, y1, farge) i et 100x100-rutenett
        (24, 78, 76, 78, ink), (24, 78, 24, 48, ink), (76, 78, 76, 48, ink),
        (24, 48, 76, 48, ink), (76, 48, 50, 24, ink), (24, 48, 50, 24, accent),
    ]
    half = 3.2 * s
    px = bytearray(size * size * 3)
    for y in range(size):
        for x in range(size):
            u, v = x / s, y / s
            col = grid if (u % 10 < 0.9 or v % 10 < 0.9) else bg
            col = list(col)
            for x0, y0, x1, y1, c in segs:
                X0, Y0, X1, Y1 = x0 * s, y0 * s, x1 * s, y1 * s
                dx, dy = X1 - X0, Y1 - Y0
                t = max(0.0, min(1.0, ((x + .5 - X0) * dx + (y + .5 - Y0) * dy) / (dx * dx + dy * dy)))
                d = math.hypot(x + .5 - (X0 + t * dx), y + .5 - (Y0 + t * dy))
                a = max(0.0, min(1.0, half - d + .5))
                if a > 0:
                    col = [round(col[i] * (1 - a) + c[i] * a) for i in range(3)]
            i = (y * size + x) * 3
            px[i:i + 3] = bytes(col)
    return px


def main():
    src = SRC.read_text(encoding='utf-8')
    split = src.index('<div id="app">')
    head, body = src[:split], src[split:]
    version = hashlib.sha1(src.encode()).hexdigest()[:7]
    label = datetime.now().strftime('%d.%m.%Y %H:%M')
    stamp = '<script>window.SNEKKERBLOKK_VERSION = %s;</script>\n' % json.dumps({'id': version, 'label': label})
    html = HEAD + stamp + head + '</head>\n<body>\n' + body + SW_REGISTER + '</body>\n</html>\n'
    OUT.mkdir(exist_ok=True)
    (OUT / 'index.html').write_text(html, encoding='utf-8')
    (OUT / 'sw.js').write_text(SW % version, encoding='utf-8')
    (OUT / 'version.json').write_text(json.dumps({'id': version, 'label': label}), encoding='utf-8')
    (OUT / 'manifest.webmanifest').write_text(json.dumps(MANIFEST, ensure_ascii=False, indent=2), encoding='utf-8')
    for n in (180, 192, 512):
        f = OUT / f'icon-{n}.png'
        if not f.exists():
            png(f, n, n, icon(n))
    print(f'Bygget docs/ (versjon {label}, {version})')


if __name__ == '__main__':
    main()
