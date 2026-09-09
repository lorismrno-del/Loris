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

Eine einzige Geste: der Weg aus dem Logo zeichnet sich groß über das Bild, fährt
in einer Bewegung auf seine Größe im Logo zurück, und das Logo wächst aus ihm
heraus. Keine Streuelemente, kein Blitz.

Alle Animationen hängen an **einer** Master-Dauer (`--dur: 8s`); die komplette
Timeline steckt in den Keyframe-Prozenten, damit nichts auseinanderläuft.

| Zeit | Was passiert |
|---|---|
| 0,00 – 0,40 s | Dunkles Bild, leer |
| 0,40 – 3,30 s | Der Weg zeichnet sich groß über das Bild (`stroke-dasharray`, ein langer ease-in-out). Es ist **exakt die Kurve des Wegs im Logo**, nur 5,25-fach — deshalb ist die Landung später eine reine Bewegung und kein Formwechsel |
| 3,20 – 4,30 s | Er fährt in einer Bewegung auf seine Größe im Logo zurück |
| 3,70 – 4,15 s | Ein weißer Wisch mit schräger Kante läuft durchs Bild, unten voraus wie die Fahrtrichtung des Wegs. Er kommt, **solange die Linie noch Größe hat** — sie steht nie klein und allein im leeren Bild |
| 4,10 – 5,05 s | Die rote Blase wächst aus dem Weg heraus (Scale 0,62 → 1, minimaler Overshoot). Die weiße Aussparung der Blase *ist* die gelandete Linie |
| 4,72 – 5,28 s | „SIRAT" wird per `clip-path` von links nach rechts freigelegt |
| 5,02 – 5,65 s | „TALK" fährt 30px von links ein und blendet auf |
| 5,65 – 6,70 s | Nachfedern Scale 1,02 → 1,0 |
| 6,70 – 8,00 s | Ruhe |

Die Überlappungen sind Absicht: keine Bewegung kommt zum Stillstand, bevor die
nächste anfängt. Es laufen insgesamt sieben Animationen — die Bühne bleibt lesbar.

Der Hintergrundwechsel ist ein Wisch mit harter Kante, kein Blitz und keine
Überblendung. So entstehen keine Zwischenfarben.

## Logo

Das Logo ist **unverändert**. Es wurde aus der Vorlage in Pfade übernommen
(rote Sprechblase inkl. Weg-Aussparung, „SIRAT" weiß, „TALK" rot) und liegt als
`logo.svg` bei. Der Endframe des Intros deckt sich mit dem statisch gerenderten
Logo bis auf Kantenglättung (< 0,01 % abweichende Pixel).

Der weiße Weg im Logo ist die Blasenspitze – im Intro ist er das Leitmotiv.
Die animierte Linie ist **dieselbe Kurve**, nur groß: sie wurde aus der
Weg-Fläche im Logo gemessen (Mittellinie), nicht geschätzt — mittlere Abweichung
1,8px bei 1024px Vorlagenbreite, 595 von 600 Kurvenpunkten liegen innerhalb der
Weg-Fläche. Weil Anfangs- und Endzustand dieselbe Kurve sind, ist die Landung
eine reine Transformation: kein Morph, keine exotischen CSS-Eigenschaften,
nichts, was in einem Browser anders interpoliert.

## Farben

| | |
|---|---|
| Rot | `#E1272C` |
| Weiß | `#FFFFFF` |
| Start-Hintergrund | `#2B0507` |

Keine Verläufe. Jede Bewegung hat ein Easing, keine einzige ist linear
(Ausnahme: reine Halte-Segmente zwischen zwei identischen Keyframes).
