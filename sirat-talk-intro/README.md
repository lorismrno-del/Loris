# Sirat Talk – 12 s Logo Intro

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

→ `sirat-talk-intro.mp4`, 1920 × 1080, 60 fps, exakt 12,000 s, H.264 / CRF 16.

Optionen:

| Befehl | Ergebnis |
|---|---|
| `node render.mjs --fps 30` | 30 fps (360 Frames) |
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

Der Weg ist nicht als Strich gezeichnet — es ist die **echte Weg-Fläche aus dem
Logo**: perspektivisch verjüngt, vorne breit, hinten schmal. Sie rollt sich vom
Betrachter zum Horizont aus, die Kamera fährt dabei zurück und richtet sich auf,
bis der Weg genau seine Größe und Lage im Logo hat. Dann wächst das Logo aus ihm.

Alle Animationen hängen an **einer** Master-Dauer (`--dur: 12s`); die komplette
Timeline steckt in den Keyframe-Prozenten, damit nichts auseinanderläuft.

| Zeit | Was passiert |
|---|---|
| 0,00 – 0,20 s | Dunkles Bild, leer. Die Kamera fährt bereits |
| 0,20 – 4,60 s | Der Weg rollt sich vom Betrachter zum Horizont aus (`clip-path`-Rechteck, `scaleY` von unten) |
| 0,50 – 7,05 s | Die Markierungen laufen auf den Betrachter zu. Konstante Straßengeschwindigkeit, die zum Schluss ausrollt |
| 0,20 – 6,00 s | Kamera fährt zurück, Maßstab 15,0 → 4,95, um −24° gekippt |
| 6,00 – 7,05 s | Der Weg fährt auf Logo-Größe und richtet sich auf |
| 6,35 – 6,95 s | Weißer Wisch mit schräger Kante, unten voraus wie die Fahrtrichtung. Er kommt, **solange der Weg noch Größe hat** — der Weg steht nie klein und allein im leeren Bild. Er deckt Weg und Markierungen ab, die müssen also nicht extra ausgeblendet werden |
| 6,88 – 8,25 s | Die rote Blase wächst aus dem Weg (Scale 0,62 → 1, minimaler Overshoot). Das Logo liegt in derselben Kamera, kommt also mit ihrer letzten Bewegung zur Ruhe |
| 7,95 – 8,65 s | „SIRAT" wird per `clip-path` von links nach rechts freigelegt |
| 8,40 – 9,30 s | „TALK" fährt 30px von links ein und blendet auf |
| 9,30 – 10,60 s | Nachfedern Scale 1,02 → 1,0 |
| 10,60 – 12,00 s | Ruhe |

Die Überlappungen sind Absicht: keine Bewegung kommt zum Stillstand, bevor die
nächste anfängt. Gemessen über alle 720 Frames bleiben nur zwei Standbilder
übrig, beide gewollt: der leere Auftakt (0,28 s) und die Schlussruhe (1,67 s).

### Aufbau

```
#camA   ← der Weg (Fläche + Markierungen)
#wipe   ← weißer Wisch, Bildschirmraum, liegt zwischen den Kameras
#camB   ← das Logo
```

`#camA` und `#camB` tragen dieselbe Kamera-Animation. Zwei Gruppen sind nötig,
weil der Wisch dazwischen liegen muss: er gehört in den Bildschirmraum, nicht in
die Kamera. Läge er über beiden, verdeckte er das Logo dauerhaft.

Der Hintergrundwechsel ist ein Wisch mit harter Kante, kein Blitz und keine
Überblendung. So entstehen keine Zwischenfarben.

## Logo

Das Logo ist **unverändert**. Es wurde aus der Vorlage in Pfade übernommen
(rote Sprechblase inkl. Weg-Aussparung, „SIRAT" weiß, „TALK" rot) und liegt als
`logo.svg` bei. Der Endframe des Intros deckt sich mit dem statisch gerenderten
Logo bis auf Kantenglättung (< 0,01 % abweichende Pixel).

Der weiße Weg im Logo ist die Blasenspitze – im Intro ist er das Leitmotiv.
Die animierte Fläche ist **dieselbe Fläche**, nur groß und gekippt: aus der
Vorlage getract, eine geschlossene Kurve. Die Markierungen laufen auf ihrer
gemessenen Mittellinie (mittlere Abweichung 1,8px bei 1024px Vorlagenbreite).

Weil Anfangs- und Endzustand dieselbe Geometrie sind, ist die Landung eine reine
Transformation: kein Morph, keine exotischen CSS-Eigenschaften, nichts, was in
einem Browser anders interpoliert.

## Farben

| | |
|---|---|
| Rot | `#E1272C` |
| Weiß | `#FFFFFF` |
| Start-Hintergrund | `#2B0507` |

Keine Verläufe. Jede Bewegung hat ein Easing, keine einzige ist linear
(Ausnahme: reine Halte-Segmente zwischen zwei identischen Keyframes).
