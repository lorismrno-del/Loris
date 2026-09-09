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
| 0,00 s | Das Bild startet **leer**. Kein Element ist vorher da. |
| 0,16 – 1,72 s | Neun Elemente (Wellenlinie, Strich, Punkt, Kreisumriss, Kreuz, in zwei Größen) tauchen nacheinander auf, je 0,13 s Versatz. Deckkraft echt von 0 auf 100, dazu blur 10px → 0 und Scale 1,4 → 1, `cubic-bezier(.16,1,.3,1)` |
| 1,5 – 3,0 s | Die Elemente driften Richtung Mitte. Jedes läuft auf einer eigenen Bahn und **dreht sich dabei automatisch in seine Bewegungsrichtung** (`offset-rotate: auto`). Kamera zoomt 1,0 → 1,06 |
| 3,0 – 4,75 s | Der Weg zeichnet sich als weiße S-Kurve von unten links nach oben (`stroke-dasharray`, ease-in-out), 6px → 16px. Ein **Strich reitet auf der Linienspitze** und führt sie; die übrigen Elemente ordnen sich links und rechts am Weg an |
| 4,75 – 5,25 s | Der Strich legt sich per `d`-Morph **genau auf den Weg im Logo**. Quelle und Ziel haben denselben Aufbau (M + 3 C), also interpoliert die Kurve Punkt für Punkt. Der Leitstrich landet am Anfang dieses Wegs |
| 5,16 – 5,48 s | Weißer Flash (0 → 1 → 0), Hintergrund schaltet im Scheitel hart auf Weiß |
| 5,40 – 6,40 s | Logoaufbau: die rote Blase wächst mit Overshoot **aus genau diesem Weg** heraus (Scale 0,6 → 1) — die weiße Aussparung der Blase ist der gelandete Strich. „SIRAT" wird per `clip-path` von links nach rechts freigelegt (0,4 s), „TALK" fährt 0,15 s später 30px von links ein |
| 5,42 – 6,55 s | Die kleinen Elemente fliegen in Rot durch die Mitte nach außen und blenden aus — versetzt, jedes auf seiner Bahn weiter, ohne Richtungsknick |
| 6,6 – 8,0 s | Nachfedern Scale 1,02 → 1,0, letzte 0,5 s ruhig |

Hintergrund startet auf `#2B0507` und wechselt im Flash-Peak hart auf Weiß –
so entsteht kein Verlauf durch Zwischenfarben.

### Wie die Elemente bewegt werden

Jedes Element steckt in drei ineinander liegenden Gruppen, damit jede Ebene ihr
eigenes Easing bekommt:

| Ebene | Aufgabe |
|---|---|
| `.eo` | Deckkraft und Farbe — der echte Übergang von 0 auf 100 |
| `.ep` | die Reise: `offset-path` mit der eigenen Bahn des Elements, `offset-distance` animiert, `offset-rotate: auto` dreht in Bewegungsrichtung |
| `.es` | Auftauch-Scale und Bewegungsunschärfe |

Die Bahnen sind zentripetale Catmull-Rom-Splines durch Start → Drift → Position
am Weg → Mitte → Ausgang. Weil jedes Element **durch** die Mitte fliegt statt
dort umzukehren, gibt es beim Rausgehen keinen Richtungsknick.

## Logo

Das Logo ist **unverändert**. Es wurde aus der Vorlage in Pfade übernommen
(rote Sprechblase inkl. Weg-Aussparung, „SIRAT" weiß, „TALK" rot) und liegt als
`logo.svg` bei. Der Endframe des Intros deckt sich mit dem statisch gerenderten
Logo bis auf Kantenglättung (< 0,01 % abweichende Pixel).

Der weiße Weg im Logo ist die Blasenspitze – im Intro ist er das Leitmotiv:
er wird gezeichnet, legt sich per Morph exakt auf den Weg im Logo, und die Blase
wächst genau aus ihm heraus. Die Ziel-Kurve wurde aus der Weg-Fläche im Logo
gemessen (Mittellinie), nicht geschätzt: mittlere Abweichung 1,8px bei 1024px
Vorlagenbreite, 595 von 600 Kurvenpunkten liegen innerhalb der Weg-Fläche.

### Browser

Die Datei nutzt zwei neuere CSS-Bausteine: `offset-path` / `offset-rotate`
(Motion Path) für die Bahnen und die Animation der `d`-Eigenschaft für den
Übergang vom Strich zum Weg im Logo. Beides trägt in Chromium und Firefox;
gerendert wird ohnehin mit Chromium. In älteren Browsern springt der Morph
statt zu interpolieren — der Flash deckt die Stelle ab.

## Farben

| | |
|---|---|
| Rot | `#E1272C` |
| Weiß | `#FFFFFF` |
| Start-Hintergrund | `#2B0507` |

Keine Verläufe. Jede Bewegung hat ein Easing, keine einzige ist linear
(Ausnahme: reine Halte-Segmente zwischen zwei identischen Keyframes).
