# E-Mail-Automatisierung – Lorino Co.

Dashboard zur Konfiguration der automatisierten Firmenrecherche + personalisierten
E-Mail-Entwürfe (Handwerker Schweiz). Die App selbst versendet nichts — sie verwaltet nur
die Konfiguration (Zeiten, Templates, PDFs, Zielgruppe). Die eigentliche Recherche und das
Anlegen der Gmail-Entwürfe übernimmt Claude über geplante Routinen, siehe
[`AGENT_PLAYBOOK.md`](./AGENT_PLAYBOOK.md).

## Setup

```bash
cd server && npm install && npm start   # startet API auf http://localhost:4000
```

In einem zweiten Terminal:

```bash
cd client && npm install && npm run dev # Dashboard auf http://localhost:5173
```

## Wie die Konfiguration wirksam wird

Alle Einstellungen liegen als Dateien in `server/data/` (`config.json`, `contacted.json`,
`pdfs/`). Nach dem Speichern im Dashboard müssen diese Dateien **committed und gepusht**
werden, damit der geplante Ablauf (der in einer separaten, ggf. neu gestarteten Session
läuft) die aktuellen Werte sieht:

```bash
git add email-automation-app/server/data
git commit -m "Konfiguration aktualisieren"
git push
```

Alternativ: im Chat kurz Bescheid geben, dann wird das mit übernommen.

## Ordnerstruktur

```
email-automation-app/
  server/           Express-API (Config, PDF-Upload, Log)
    data/
      config.json     Zeiten, Templates, Zielgruppe, Drive-Ordner
      contacted.json  Log bereits kontaktierter Firmen (Dubletten-Schutz)
      pdfs/           Hochgeladene PDF-Dateien
  client/           React-Dashboard (Vite)
  AGENT_PLAYBOOK.md Ausführungsanleitung für die geplanten Claude-Routinen
```

## Bekannte Einschränkungen

- Gmail-Entwürfe unterstützen aktuell keine echten Anhänge → PDFs werden stattdessen zu
  Google Drive hochgeladen, ein Freigabe-Link landet im E-Mail-Text. Dafür einmalig einen
  Drive-Ordner mit Freigabe "Jeder mit dem Link" anlegen und die URL im Dashboard unter
  "Google-Drive-Ordner für PDF-Links" eintragen.
- Es wird nie automatisch versendet — jeder Lauf legt nur Entwürfe an.
