/**
 * Baut aus den Demo-Betrieben eine einzelne HTML-Datei, die überall läuft –
 * ohne Server, ohne Installation. Gedacht zum Herzeigen: auf dem Handy
 * öffnen, jemandem zeigen, verschicken.
 *
 *     node tools/demo-seite-bauen.js [zieldatei]
 *
 * Die Daten kommen durch denselben Code wie in der richtigen App
 * (Bewertung, Gesprächsleitfaden, Vorlagen) – die Seite verhält sich also
 * genau wie das Original, nur ohne Suche und Webseiten-Prüfung.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { searchDemo } from '../src/providers/demo.js';
import { enrichLead } from '../src/scoring.js';
import { callScript, emailTemplate, whatsappTemplate, smsTemplate, LEGAL_NOTES } from '../src/outreach.js';
import { loadSettings, getSettings } from '../src/settings.js';
import { TRADES, GRUPPEN, tradeLabel } from '../src/trades.js';
import { ANRUF_ERGEBNISSE, STATUSES } from '../src/store.js';

const hier = path.dirname(fileURLToPath(import.meta.url));
const vorlageDatei = path.join(hier, 'demo-seite.html');
const zielDatei = process.argv[2] || path.join(hier, '..', 'leadradar-demo.html');

await loadSettings();

const leads = searchDemo({ trades: TRADES.map((t) => t.id), limit: 100 })
  .map(enrichLead)
  .map((l) => ({
    id: l.id,
    name: l.name,
    trade: l.trade,
    tradeLabel: tradeLabel(l.trade),
    address: l.address,
    phone: l.phone,
    email: l.email,
    website: l.website,
    googleRating: l.googleRating,
    googleReviews: l.googleReviews,
    openingHours: l.openingHours,
    score: l.score,
    tier: l.tier,
    headline: l.headline,
    reasons: l.reasons,
    inactiveYears: l.inactiveYears,
    websiteAgeYears: l.websiteAgeYears,
    bewertungsKlasse: l.bewertungsKlasse,
    sterneKlasse: l.sterneKlasse,
    audit: l.audit,
    script: callScript(l),
    email_v: emailTemplate(l),
    whatsapp: whatsappTemplate(l),
    sms: smsTemplate(l),
  }))
  .sort((a, b) => b.score - a.score);

const daten = {
  leads,
  ergebnisse: ANRUF_ERGEBNISSE,
  statuses: STATUSES,
  gruppen: GRUPPEN,
  trades: TRADES.map((t) => ({ id: t.id, label: t.label, emoji: t.emoji, gruppe: t.gruppe })),
  legal: LEGAL_NOTES,
  agentur: getSettings(),
};

// "</" maskieren, sonst würde ein Text im JSON das <script>-Tag beenden
const alsText = JSON.stringify(daten).replace(/<\//g, '<\\/');

const vorlage = fs.readFileSync(vorlageDatei, 'utf8');
if (!vorlage.includes('__DATEN__')) {
  console.error('In der Vorlage fehlt der Platzhalter __DATEN__.');
  process.exit(1);
}

fs.writeFileSync(zielDatei, vorlage.replace('__DATEN__', alsText));

const kb = (fs.statSync(zielDatei).size / 1024).toFixed(0);
console.log(`✓ ${leads.length} Betriebe → ${zielDatei} (${kb} KB)`);
console.log('  Die Datei ist eigenständig: einfach im Browser öffnen.');
