# 📡 Lorino Leadradar

Findet Bau- und Handwerksbetriebe in deiner Region, **prüft automatisch deren
Webseite** und gibt dir eine nach Potenzial sortierte Anrufliste – mit Telefon,
E-Mail und einem fertigen Gesprächsleitfaden pro Betrieb.

Gebaut für [Lorino Co.](https://lorino-co.ch) – Webseiten für Bauunternehmen
und Handwerksbetriebe in der Deutschschweiz.

---

## Was die App macht

1. **Suchen** – Branche + Ort wählen (z. B. „Schreiner" + „Kanton Aargau")
2. **Prüfen** – jede gefundene Webseite wird automatisch analysiert:
   - Gibt es überhaupt eine? Ist sie erreichbar?
   - Nur eine Facebook-Seite oder ein local.ch-Eintrag?
   - Mobiltauglich? HTTPS? Wie alt ist der Inhalt?
   - Kontaktformular, Impressum, Ladezeit, verwendete Technik
3. **Bewerten** – jeder Betrieb bekommt einen Score von 0–100
4. **Anrufen** – Liste nach Potenzial sortiert, mit Telefonnummer,
   E-Mail und einem auf das konkrete Problem zugeschnittenen Skript

---

## Starten

Du brauchst nur [Node.js](https://nodejs.org) ab Version 20. **Keine Installation
von Paketen nötig** – die App kommt ohne externe Abhängigkeiten aus.

```bash
cd leadradar
node server.js
```

Dann im Browser öffnen: **http://127.0.0.1:3000**

Zum Ausprobieren: Reiter *Leads finden* → Datenquelle **„Demo-Daten"** → Suche
starten. Das funktioniert sofort und ohne Internet.

---

## 📱 Auf dem Handy nutzen

So gestartet läuft die App **nur auf deinem Rechner**. Vom Handy kommst du da
nicht drauf. Es gibt zwei Wege.

### Weg 1: Gleiches WLAN (2 Minuten, gratis)

Der schnellste Weg. Bedingung: Rechner läuft und Handy ist im selben WLAN.

**1.** Passwort festlegen. Datei `.env` anlegen (Vorlage: `.env.example`) und
eintragen:

```
APP_PASSWORD=deinPasswort
```

Das ist Pflicht – ohne Passwort könnte jeder im WLAN deine Leads lesen.
Das Skript startet sonst gar nicht erst.

**2.** So starten:

```bash
npm run handy
```

**3.** Im Terminal steht jetzt die Adresse fürs Handy:

```
📱 Auf dem Handy (gleiches WLAN) – diese Adresse eintippen:
    http://192.168.1.42:3000
```

Diese Adresse im Handy-Browser eingeben, Passwort eintippen – fertig.

**4.** Als App-Icon speichern:
- **iPhone:** Safari → Teilen-Symbol → *Zum Home-Bildschirm*
- **Android:** Chrome → Menü (⋮) → *App installieren*

Danach startet Leadradar wie eine normale App, ohne Browserleiste.

> Die IP-Adresse kann sich ändern, wenn der Router neu startet. Steht dann
> einfach wieder im Terminal.

**Grenze dieses Wegs:** Sobald du das WLAN verlässt – also genau dann, wenn du
unterwegs anrufen willst – funktioniert es nicht mehr. Dafür Weg 2.

### Weg 2: Online stellen (überall erreichbar)

Damit läuft die App auf einem Server und ist von überall erreichbar – auch
unterwegs, auch wenn dein Rechner aus ist.

Es braucht einen Anbieter, der Node.js ausführt. Gut geeignet und mit
Gratis-Kontingent: **[Render](https://render.com)**, **[Railway](https://railway.app)**
oder **[Fly.io](https://fly.io)**.

Bei Render zum Beispiel:

1. Neuer *Web Service* → dieses Repository verbinden
2. **Root Directory:** `leadradar`
3. **Build Command:** leer lassen (keine Abhängigkeiten)
4. **Start Command:** `node server.js`
5. Unter *Environment* eintragen:
   - `APP_PASSWORD` = dein Passwort
   - `HOST` = `0.0.0.0`
   - `GOOGLE_PLACES_API_KEY` = dein Key (falls vorhanden)

Du bekommst eine feste Adresse wie `https://leadradar.onrender.com`. Die aufs
Handy legen wie oben. Über HTTPS läuft dann auch das Anmelde-Cookie abgesichert.

**Zwei Dinge, die du wissen solltest:**

- **Die Daten liegen im `data`-Ordner.** Viele Hoster löschen den bei jedem
  Neustart. Bei Render heisst die Lösung *Persistent Disk*, gemountet auf
  `/opt/render/project/src/leadradar/data`. Ohne das sind deine Leads nach dem
  nächsten Deploy weg.
- **Gratis-Pläne schlafen ein.** Der erste Aufruf nach einer Pause dauert dann
  30–60 Sekunden.

### Wenn du nur schnell mal draufschauen willst

Für einen kurzen Test ohne Hosting geht auch ein Tunnel, der deinen laufenden
Rechner vorübergehend ins Internet stellt:

```bash
npx localtunnel --port 3000
```

Gibt eine öffentliche Adresse für die Dauer der Sitzung. **Nur mit gesetztem
`APP_PASSWORD` benutzen** – die Adresse ist für jeden erreichbar, der sie kennt.

---

## Datenquellen

| Quelle | Key nötig | Abdeckung | Bemerkung |
|---|---|---|---|
| **OpenStreetMap** | nein | gut bei Handwerk | Gratis. Fair benutzen – Gemeinschaftsdienst. |
| **Google Places** | ja | am besten | Inklusive Bewertungen und Datum der letzten Bewertung. |
| **Demo-Daten** | nein | 24 erfundene Betriebe | Zum Ausprobieren. **Nicht anrufen** – die gibt es nicht. |

### Google Places einrichten (empfohlen)

1. [Google Cloud Console](https://console.cloud.google.com) → Projekt erstellen
2. **Places API (New)** aktivieren
3. Abrechnung aktivieren (es gibt monatliches Gratis-Guthaben)
4. Anmeldedaten → API-Schlüssel erstellen
5. `.env.example` nach `.env` kopieren und den Schlüssel eintragen:

```bash
cp .env.example .env
```

```
GOOGLE_PLACES_API_KEY=dein-schlüssel-hier
```

Server neu starten – im Reiter *Leads finden* steht Google Places dann zur Auswahl.

**Kosten im Blick behalten:** Jede Suche löst mehrere API-Anfragen aus (ein
Suchbegriff pro Branche, bis zu 3 Seiten). Wenn du sparen willst, setze
`GOOGLE_INCLUDE_REVIEWS=false` und `GOOGLE_MAX_PAGES=1`.

---

## Der Score – wie er entsteht

Der Score besteht aus zwei Teilen:

**Bedarf (0–70) – wie schlecht ist der Web-Auftritt?**

| Situation | Punkte |
|---|---|
| Gar keine Webseite | 70 |
| Webseite tot (DNS weg, 404, Timeout) | 66 |
| Nur Platzhalter-/Baustellenseite | 60 |
| Nur Facebook/Instagram | 56 |
| Nur local.ch-Eintrag | 52 |
| Webseite vorhanden, aber mit Mängeln | max. 48 |

Bei bestehenden Webseiten summieren sich die Mängel: nicht mobiltauglich (20),
Zertifikatsfehler (20), kein HTTPS (16), veralteter Inhalt (bis 18), alte
Technik (bis 14), langsam (8), kein Impressum (6), kein Kontaktformular (5) …

Der Deckel bei 48 ist Absicht: **Ein Betrieb ohne Webseite steht immer über
einem mit schlechter Webseite.** Das Gespräch ist eindeutiger zu führen – bei
einer bestehenden Seite hat sie oft der Neffe des Chefs gebaut.

**Qualität (0–30) – lohnt sich der Aufwand?**

Viele gute Google-Bewertungen (+12), Telefonnummer vorhanden (+8),
E-Mail vorhanden (+5), lange keine neue Bewertung (+5).
Laut Google geschlossener Betrieb: −25.

**Einstufungen:** 🔥 ab 75 · 🌡️ ab 55 · 👀 ab 35 · 💤 ab 18 · ✅ darunter

---

## Bedienung

**Anrufliste** – deine tägliche Arbeitsfläche. Klick auf einen Lead öffnet
rechts das Detail: grosser Anruf-Button, WhatsApp, E-Mail mit fertiger Vorlage,
Gesprächsleitfaden, Notizen und Statuswechsel.

Die Buttons funktionieren auch auf dem Handy – `tel:` startet den Anruf direkt,
WhatsApp öffnet den Chat mit vorgeschriebenem Text.

**Status-Pipeline:** Neu → Anrufen → Kontaktiert → Wiedervorlage → Termin →
Offerte raus → Kunde ✅ (oder Kein Interesse / Nicht kontaktieren)

**Nach einem „Nein"** den Status auf *Nicht kontaktieren* setzen. Der Lead wird
dann ausgegraut und aus den Listen gefiltert – so rufst du nie versehentlich
zweimal an.

**Einstellungen** – dein Profil, deine Verkaufsargumente und die Weitergabe an
andere Tools. Alles, was du hier änderst, landet sofort in den Skripten.

---

## Weitergabe an andere Tools

Unter *Einstellungen → Weitergabe* kannst du eine oder mehrere Adressen
hinterlegen. Ein Klick auf **„An anderes Tool übergeben"** schickt den Lead als
JSON per `POST` dorthin:

```json
{
  "quelle": "lorino-leadradar",
  "firma": "Muster Schreinerei AG",
  "branche": "Schreiner / Zimmerei",
  "telefon": "+41 44 555 01 01",
  "email": "info@muster.ch",
  "adresse": { "plz": "8400", "ort": "Winterthur", "kanton": "ZH" },
  "analyse": {
    "websiteStatus": "Keine Webseite",
    "problem": "Hat gar keine Webseite",
    "score": 88,
    "einstufung": "Sehr heiss",
    "gruende": ["Keine Webseite", "Top bewertet: 4.8★ aus 47 Bewertungen"]
  },
  "status": "neu"
}
```

Wird ein Schlüssel hinterlegt, geht er als `Authorization: Bearer …` mit.

Alternativ: **„{ } JSON kopieren"** im Detail, oder der CSV-Export oben rechts
(Semikolon-getrennt, öffnet sich direkt in Excel und Numbers).

---

## Wo liegen meine Daten?

Alles bleibt in `data/`:

- `data/leads.json` – deine Leads inkl. Status, Notizen, Verlauf
- `data/settings.json` – dein Profil und deine Argumente

Nichts geht an Dritte. Für ein Backup einfach den `data`-Ordner kopieren.
Beide Dateien stehen in `.gitignore` – sie landen nie im Repository.

## Passwortschutz

Ist `APP_PASSWORD` gesetzt, verlangt die App beim ersten Aufruf ein Passwort
und merkt sich die Anmeldung 30 Tage lang – auf dem Handy musst du also nicht
täglich neu eintippen. Abmelden über das ⏻-Symbol oben rechts.

Technisch: signiertes HttpOnly-Cookie (HMAC-SHA256 mit dem Passwort als
Schlüssel), Passwortvergleich ohne Zeitunterschied, und nach 10 Fehlversuchen
pro IP ist 15 Minuten Pause. Ohne gesetztes Passwort ist der Schutz aus – dann
sollte die App aber auch nur auf `127.0.0.1` laufen.

---

## Rechtliches (Schweiz)

Kurz zusammengefasst – Details findest du in der App unter *⚖️ Rechtliche Hinweise*:

- **Telefon-Kaltakquise B2B** ist grundsätzlich erlaubt. Aber: Wer im
  Telefonbuch einen **Stern-Eintrag (\*)** hat, will keine Werbeanrufe
  (Art. 3 Abs. 1 lit. u UWG). Im Detail gibt es dafür einen direkten
  local.ch-Link zum Nachprüfen.
- **Kalte Werbe-E-Mails**: Massenwerbung ohne Einwilligung ist untersagt
  (Art. 3 Abs. 1 lit. o UWG). Einzelne, individuell geschriebene B2B-Mails mit
  klarem Bezug zum Betrieb sind die sichere Variante – die Vorlage enthält
  Absender und Abmeldehinweis.
- **OpenStreetMap** steht unter ODbL, **Google-Places-Daten** dürfen nur
  begrenzt zwischengespeichert werden. Für die eigene Akquiseliste
  unproblematisch, ein Weiterverkauf wäre es nicht.

Das ist eine Orientierungshilfe, keine Rechtsberatung.

---

## Tests

```bash
npm test
```

19 Tests decken die Webseiten-Analyse (veraltete Seite, tote Seite, geparkte
Domain, Facebook-Weiterleitung, versteckte E-Mails), die Bewertungslogik und
den CSV-Export ab. Die Testseiten laufen auf einem lokalen Server – es wird
nichts von aussen abgerufen.

---

## Aufbau

```
leadradar/
├── server.js              HTTP-Server und API
├── src/
│   ├── config.js          Konfiguration (.env)
│   ├── settings.js        Agentur-Profil und Verkaufsargumente
│   ├── trades.js          17 Branchen (Google- und OSM-Zuordnung)
│   ├── geo.js             Orte der Schweiz + Kantone, Geocoding
│   ├── providers/
│   │   ├── osm.js         OpenStreetMap / Overpass
│   │   ├── google.js      Google Places API (New)
│   │   └── demo.js        Beispieldaten
│   ├── analyzer.js        Webseiten-Prüfung  ← das Herzstück
│   ├── scoring.js         Bewertung und Einstufung
│   ├── outreach.js        Anrufskript, E-Mail, WhatsApp
│   ├── webhooks.js        Weitergabe an andere Tools
│   ├── store.js           Speicherung (JSON-Dateien)
│   ├── http.js            HTTP-Hilfsfunktionen
│   ├── jobs.js            Hintergrund-Jobs mit Fortschritt
│   └── csv.js             Export
├── public/                Oberfläche (HTML, CSS, JS – kein Build)
└── test/                  Tests
```
