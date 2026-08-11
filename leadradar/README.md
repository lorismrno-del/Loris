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
nicht drauf. Es gibt drei Wege – der erste ist in einer Minute erledigt.

### Weg 0: Die Demo-Seite (zum Herzeigen)

```bash
npm run demo-seite
```

Baut eine einzelne HTML-Datei mit den 30 Demo-Betrieben. Die kannst du
verschicken, auf den Desktop legen oder auf dem Handy öffnen – sie braucht
keinen Server und kein Internet. Anrufergebnisse werden im Browser gespeichert.

Was fehlt: die echte Suche, die Webseiten-Prüfung, der Schweiz-Scan und die
Karte. Dafür braucht es den Server – also Weg 1 oder 2.

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

Dazu kommt die **Google-Präsenz** als eigenes Verkaufsargument:

| Situation | Punkte |
|---|---|
| Keine einzige Bewertung | +12 |
| Unter 5 Bewertungen | +9 |
| Unter 15 Bewertungen | +5 |
| Bewertung unter 3.5★ | +8 |
| Bewertung 3.5–4.0★ | +4 |

Das zählt nur, wenn die Datenquelle überhaupt Bewertungen kennt. Bei
OpenStreetMap hiesse „0 Bewertungen" bloss „wir wissen es nicht" – dafür
bekommt niemand Punkte.

**Qualität (0–30) – lohnt sich der Aufwand?**

Viele gute Google-Bewertungen (+12), Telefonnummer vorhanden (+8),
E-Mail vorhanden (+5), lange keine neue Bewertung (+5).
Laut Google geschlossener Betrieb: −25.

Dass viele Bewertungen hier Punkte *geben* und oben Punkte *nehmen*, ist kein
Widerspruch: Ein Betrieb mit 60 guten Bewertungen läuft gut und kann zahlen –
einer mit dreien hat online mehr Nachholbedarf. Beides ist wahr, beides fliesst
ein.

**Einstufungen:** 🔥 ab 75 · 🌡️ ab 55 · 👀 ab 35 · 💤 ab 18 · ✅ darunter

---

## Bedienung

### 📞 Anrufen – der Arbeitsmodus

Zeigt genau **einen** Lead: Name, Ort, das Problem, die Nummer als grosser
Knopf und darunter der Einstiegssatz. Nach dem Gespräch tippst du auf ein
Ergebnis – gespeichert, nächster Lead. Kein Zurückblättern, kein Suchen.

Die Ergebnisse:

| | | Was passiert |
|---|---|---|
| 💬 | Gespräch geführt | Status → Kontaktiert, Notiz möglich |
| 🤝 | Termin vereinbart | Status → Termin |
| 📼 | Combox | Wiedervorlage **morgen**, bleibt in der Liste |
| 📵 | Niemand ran | Wiedervorlage morgen |
| ⏳ | Besetzt | Wiedervorlage **heute** |
| 🔁 | Rückruf abgemacht | Datum eingeben, Wiedervorlage gesetzt |
| ✉️ | Will Unterlagen | Wiedervorlage in 4 Tagen |
| 🕓 | Später nochmal | Wiedervorlage in 3 Monaten |
| 👎 | Kein Interesse | Status → Abgelehnt |
| 🚫 | Nicht mehr anrufen | Dauerhaft gesperrt |
| ❌ | Nummer stimmt nicht | Bleibt drin, Nummer prüfen |
| 🏚️ | Gibt es nicht mehr | Status → Abgelehnt |

War jemand **dreimal** nicht erreichbar, weist die App darauf hin und schlägt
WhatsApp oder E-Mail vor – dort liegt die Vorlage schon bereit.

**Die Reihenfolge** macht die App selbst: zuerst fällige Wiedervorlagen
(Zugesagtes einhalten geht vor), danach nach Potenzial. Wer heute schon dran
war, keine Nummer hat, abgelehnt hat oder Kunde ist, taucht gar nicht erst auf.

**Tastenkürzel** (am Rechner): `1`–`9` für die Ergebnisknöpfe, `a` zum Anrufen,
`→` oder `s` zum Überspringen.

Oben läuft der Tageszähler mit: Anrufe, erreicht, Combox, Termine, Trefferquote.

### Liste, Karte, Finden

**Liste** – alle Leads mit allen Filtern. Klick öffnet rechts das Detail mit
vollem Leitfaden, Vorlagen, Notizen und der technischen Analyse.

**Karte** – alle Leads geografisch, eingefärbt nach Potenzial. Klick auf einen
Punkt öffnet den Lead. Praktisch, um eine Tour zu planen oder ein Gebiet
abzugrasen.

**Filter** – neben Status und Branche auch: Kanton, Webseiten-Problem,
**Anzahl Bewertungen** (keine / wenige / viele) und **Sterne**
(schlecht / mittel / gut). Damit findest du gezielt Betriebe, die online
schwach dastehen.

**Status-Pipeline:** Neu → Anrufen → Kontaktiert → Wiedervorlage → Termin →
Offerte raus → Kunde ✅ (oder Kein Interesse / Nicht kontaktieren)

**Einstellungen** – dein Profil, deine Verkaufsargumente und die Weitergabe an
andere Tools. Alles, was du hier änderst, landet sofort in den Skripten.

---

## 🇨🇭 Schweiz-Scan

Sucht die gewählten Branchen im **ganzen Land** ab – Ort für Ort durch alle
26 Kantone (80 Orte im eingebauten Verzeichnis). Doppelte Treffer zwischen
Nachbarorten filtert die App selbst heraus.

Vor dem Start siehst du eine Abschätzung: wie viele Orte, wie viele Anfragen,
wie lange es dauert – bei Google auch der Hinweis aufs Guthaben. Beim
Flächenscan lädt Google bewusst nur die erste Ergebnisseite pro Ort, sonst
explodieren die Kosten.

Du kannst auf einzelne Kantone einschränken oder mit einem Klick die ganze
Deutschschweiz wählen. **Abbrechen geht jederzeit** – nach jedem Ort wird
gespeichert, es geht also höchstens ein Ort verloren.

> Bei OpenStreetMap wartet die App zwischen den Orten gut eine Sekunde. Das ist
> Absicht: Overpass ist ein Gemeinschaftsdienst, den man nicht überrennt.

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

37 Tests decken ab:

- **Webseiten-Analyse** – veraltete Seite, tote Seite, geparkte Domain,
  Weiterleitung auf Facebook, versteckte E-Mail-Schreibweisen, Zeichensätze
- **Bewertung** – Rangfolge der Problemfälle, Bewertungs-Signale, und dass
  OpenStreetMap-Leads keine Abzüge für unbekannte Bewertungen bekommen
- **Anrufergebnisse** – Combox setzt die Wiedervorlage auf morgen, „nicht mehr
  anrufen" sperrt dauerhaft, der Kanalwechsel-Hinweis nach drei Fehlversuchen
- **Warteschlange** – heute Versuchte fallen raus, fällige Wiedervorlagen
  kommen vor besseren Leads
- **Kartenmathematik** – Kachelkoordinaten und die Rückrechnung beim Verschieben
- **CSV-Export** – Kopfzeile, Umlaute, Schutz vor Formeln in Excel

Die Testseiten laufen auf einem lokalen Server – es wird nichts von aussen
abgerufen.

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
