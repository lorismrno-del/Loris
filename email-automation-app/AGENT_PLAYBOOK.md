# Agent Playbook: Automatisierter E-Mail-Lauf

Diese Datei ist die Ausführungsanleitung für Claude, wenn eine der geplanten Routinen
(siehe `create_trigger`-Einträge, eine pro Uhrzeit aus `server/data/config.json`) feuert.
Ziel: 10 (bzw. `companiesPerRun`) neue Handwerksbetriebe in der Schweiz recherchieren,
je nach Webseiten-Status personalisierte E-Mail-Entwürfe in Gmail anlegen und **nichts
automatisch versenden** — der Nutzer prüft und versendet selbst.

## Standing-Autorisierung

Der Nutzer hat am 2026-07-09 in diesem Chat explizit zugestimmt, dass die Apollo.io-Tools
(Firmensuche, Enrichment, People-Suche) bei diesen automatisierten Läufen **ohne erneute
Rückfrage** aufgerufen werden dürfen. Die Obergrenze pro Lauf ist `companiesPerRun` aus der
Config (Default 10) — das ersetzt ein festes Credit-Limit. Diese Autorisierung gilt nur für
den hier beschriebenen Ablauf, nicht für sonstige Apollo-Nutzung.

## Ablauf pro Trigger-Fire

1. **Repo aktualisieren**: `git pull origin claude/email-automation-agent-koizrm` (bzw. den
   dann aktuellen Ziel-Branch/main, falls der PR schon gemergt ist), damit Änderungen aus der
   App (Zeiten, Templates, PDFs) berücksichtigt werden.
2. **Config laden**: `email-automation-app/server/data/config.json` lesen
   (`firmenname`, `targetIndustry`, `targetRegion`, `companiesPerRun`, `driveFolderUrl`,
   `templateA`, `templateB`).
3. **Bereits kontaktierte Firmen laden**: `email-automation-app/server/data/contacted.json`
   (Liste von `{name, domain, template, date}`). Domains hieraus sind tabu.
4. **PDFs prüfen**: Dateien in `email-automation-app/server/data/pdfs/*.pdf` auflisten.
   - Wenn `driveFolderUrl` leer ist: keine PDF-Links einfügen, `{{pdf_link}}` durch einen leeren
     String ersetzen (ggf. den Satz mit dem Platzhalter ganz weglassen).
   - Sonst: Ordner-ID aus der URL extrahieren. Für jede PDF-Datei, die noch nicht in
     `email-automation-app/server/data/drive_uploads.json` (Cache `{filename: {fileId, link}}`)
     vorhanden ist, per `mcp__Google_Drive__create_file` hochladen
     (`parentId` = Ordner-ID, `contentMimeType: "application/pdf"`,
     `disableConversionToGoogleType: true`, `base64Content` = Dateiinhalt). Ergebnis-Link
     (`webViewLink` bzw. äquivalentes Feld aus der Antwort) im Cache speichern. Cache-Datei
     anlegen, falls sie noch nicht existiert.
   - Alle Links zu einem Textblock zusammenfassen, der `{{pdf_link}}` ersetzt.
5. **Firmen recherchieren**: `mcp__Apollo_io__apollo_mixed_companies_search` mit
   `organization_locations: ["Switzerland"]` und Keyword-/Branchenfiltern passend zu
   `targetIndustry` (z.B. Handwerk, Bau, Sanitär, Elektro, Schreinerei — je nach Trefferlage
   anpassen). `per_page` großzügig wählen, um nach Abzug bereits kontaktierter Firmen genug
   neue zu haben. Ergebnisse gegen `contacted.json` filtern, bis `companiesPerRun` neue Firmen
   feststehen.
6. **Webseiten-Status prüfen**: Pro Firma aus dem Suchergebnis das Feld für Website/Domain
   prüfen (z.B. `website_url` / `primary_domain`). Vorhanden → Template A, leer/fehlend →
   Template B.
7. **Ansprechpartner + E-Mail ermitteln**: Für jede der Firmen eine Personensuche
   (z.B. `mcp__Apollo_io__apollo_mixed_people_api_search`, gefiltert auf die Organisation und
   Senioritäts-/Titel-Keywords wie Inhaber, Geschäftsführer, Owner) durchführen, um eine
   valide Kontakt-E-Mail zu bekommen. Firmen ohne auffindbare Kontakt-E-Mail überspringen,
   in der Zusammenfassung am Ende erwähnen, nicht als "kontaktiert" loggen.
8. **E-Mail personalisieren**: Template A/B aus der Config nehmen, Platzhalter ersetzen:
   - `{{firma}}` → Firmenname
   - `{{absender}}` → Vorname/Name des Gmail-Kontoinhabers, sonst `firmenname`
   - `{{firmenname}}` → `config.firmenname`
   - `{{pdf_link}}` → siehe Schritt 4
9. **Gmail-Entwurf anlegen**: `mcp__Gmail__create_draft` mit `to`, `subject`, `body` (kein
   `attachments`-Feld nutzen — wird laut Tool-Beschreibung nicht unterstützt).
10. **Log aktualisieren**: Für jede erfolgreich als Entwurf angelegte Firma einen Eintrag an
    `contacted.json` anhängen (`name`, `domain`, `template: "A"|"B"`, `date` im ISO-Format,
    optional `draftId`).
11. **Commit & Push**: `contacted.json` (und ggf. `drive_uploads.json`) committen und auf den
    Arbeits-Branch pushen, damit der Stand bei zukünftigen (evtl. frischen) Sessions erhalten
    bleibt.
12. **Kurze Zusammenfassung** im Chat hinterlassen: Anzahl neuer Entwürfe, Templates A/B-
    Verteilung, übersprungene Firmen (kein Kontakt gefunden), evtl. Fehler.

## Nicht tun

- Keine E-Mails tatsächlich versenden (`send`-Funktion existiert im Gmail-Tool ohnehin nicht,
  nur `create_draft`).
- Keine Firma doppelt anschreiben (immer gegen `contacted.json` prüfen).
- Keine Apollo-People-/Email-Reveal-Aufrufe über `companiesPerRun` hinaus in einem Lauf.
- Wenn `config.json` fehlerhaft/unlesbar ist oder kein Template ausgefüllt wurde: Lauf
  abbrechen, im Chat kurz begründen, keine Entwürfe mit Platzhalter-Text verschicken.

## Wenn sich Uhrzeiten in der App ändern

Die App speichert neue Zeiten nur lokal/im Repo (`config.json`). Die tatsächlichen
Trigger-Zeiten (`create_trigger`/`update_trigger`) müssen danach manuell abgeglichen werden —
entweder der Nutzer meldet sich im Chat, oder bei jedem Lauf wird geprüft, ob
`config.json.times` noch mit den aktiven Routinen übereinstimmt, und bei Abweichung im Chat
darauf hingewiesen.
