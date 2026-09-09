# Sirat Talk – 8 s Logo Intro

Eine einzelne HTML-Datei, SVG + CSS-Keyframes, 1920 × 1080, gedacht für 60 fps.
Kein Framework, keine externen Fonts, keine externen Assets – alles inline.

```
sirat-talk-intro/
├── index.html     ← das Intro (Doppelklick reicht)
├── render.mjs     ← Export als MP4
├── logo.svg       ← das Logo als eigenständige Datei
└── package.json
```

## Ansehen

`index.html` im Browser öffnen. Der **Replay**-Button liegt unterhalb der Bühne,
also außerhalb des gerenderten Bildes. `R` oder `Leertaste` starten ebenfalls neu.
In der Vorschau wird die Bühne per CSS-Skalierung in den Viewport eingepasst –
das ändert nichts am Timing und nichts am Export.

## Als MP4 exportieren

```bash
npm install playwright
npx playwright install chromium
# ffmpeg muss im PATH liegen (brew install ffmpeg / apt install ffmpeg)

node render.mjs
```

→ `sirat-talk-intro.mp4`, 1920 × 1080, 60 fps, exakt 8,000 s, H.264 / CRF 16.

Optionen:

| Befehl | Ergebnis |
|---|---|
| `node render.mjs --fps 30` | 30 fps (240 Frames) |
| `node render.mjs --scale 2 --out intro-4k.mp4` | 3840 × 2160 |
| `node render.mjs --png-only` | nur die PNG-Sequenz in `.frames/` |
| `node render.mjs --keep-frames` | MP4 **und** PNG-Sequenz behalten |
| `FFMPEG=/pfad/zu/ffmpeg node render.mjs` | anderer ffmpeg-Binary |

Der Export nimmt **nicht** in Echtzeit auf. Die Seite wird angehalten und pro Frame
exakt auf `currentTime = frame · 1000/fps` gesetzt (Web Animations API). Das
Ergebnis ist deterministisch und auf jedem Rechner bildgleich.

Wer die Frames selbst encodieren will:

```bash
node render.mjs --png-only
ffmpeg -y -framerate 60 -start_number 0 -i .frames/f_%04d.png \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -movflags +faststart sirat-talk-intro.mp4
```

## Timeline

Alle Animationen hängen an **einer** Master-Dauer (`--dur: 8s`); die komplette
Timeline steckt in den Keyframe-Prozenten, damit nichts auseinanderläuft.

| Zeit | Was passiert |
|---|---|
| 0,0 – 1,5 s | Wellenlinie, Strich, Punkt, Kreisumriss, Kreuz tauchen nacheinander auf, je 0,15 s Versatz, blur 10px → 0, Scale 1,4 → 1, `cubic-bezier(.16,1,.3,1)` |
| 1,5 – 3,0 s | Elemente driften langsam Richtung Mitte, leichte Rotation, Restunschärfe; Kamera zoomt 1,0 → 1,06 |
| 3,0 – 5,0 s | Der Weg zeichnet sich als weiße S-Kurve von unten links nach oben (`stroke-dasharray`, ease-in-out), Strichstärke 6px → 16px; die Elemente ordnen sich links und rechts am Weg an |
| 5,0 – 5,4 s | Der Weg schießt in die Bildmitte zusammen, weißer Flash (0 → 1 → 0 in 0,35 s), Hintergrund wechselt auf Weiß |
| 5,4 – 6,6 s | Logoaufbau: die rote Blase wächst mit Overshoot aus dem Weg heraus (Scale 0,6 → 1), „SIRAT" wird per `clip-path` von links nach rechts freigelegt (0,4 s), „TALK" fährt 0,15 s später 30px von links ein; gleichzeitig fliegen die kleinen Elemente in Rot nach außen und blenden aus |
| 6,6 – 8,0 s | Nachfedern Scale 1,02 → 1,0, letzte 0,5 s ruhig |

Hintergrund startet auf `#2B0507` und wechselt im Flash-Peak hart auf Weiß –
so entsteht kein Verlauf durch Zwischenfarben.

## Logo

Das Logo ist **unverändert**. Es wurde aus der Vorlage in Pfade übernommen
(rote Sprechblase inkl. Weg-Aussparung, „SIRAT" weiß, „TALK" rot) und liegt als
`logo.svg` bei. Der Endframe des Intros deckt sich mit dem statisch gerenderten
Logo bis auf Kantenglättung (< 0,01 % abweichende Pixel).

Der weiße Weg im Logo ist die Blasenspitze – im Intro ist er das Leitmotiv:
er wird gezeichnet, kollabiert zur Mitte, und die Blase wächst genau aus ihm heraus.

## Farben

| | |
|---|---|
| Rot | `#E1272C` |
| Weiß | `#FFFFFF` |
| Start-Hintergrund | `#2B0507` |

Keine Verläufe. Jede Bewegung hat ein Easing, keine einzige ist linear
(Ausnahme: reine Halte-Segmente zwischen zwei identischen Keyframes).
