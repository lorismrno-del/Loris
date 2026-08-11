/**
 * CSV-Export für Excel/Numbers (Semikolon-getrennt + BOM, damit Umlaute stimmen).
 */
import { tradeLabel } from './trades.js';
import { statusLabel } from './store.js';

const COLUMNS = [
  ['Firma', (l) => l.name],
  ['Branche', (l) => tradeLabel(l.trade)],
  ['Telefon', (l) => l.customPhone || l.phone || ''],
  ['E-Mail', (l) => l.customEmail || l.email || ''],
  ['Ansprechperson', (l) => l.contactName || ''],
  ['Strasse', (l) => l.address?.street || ''],
  ['PLZ', (l) => l.address?.zip || ''],
  ['Ort', (l) => l.address?.city || ''],
  ['Kanton', (l) => l.address?.canton || ''],
  ['Webseite', (l) => l.website || ''],
  ['Webseite-Status', (l) => websiteStatusLabel(l.audit?.status)],
  ['Problem', (l) => l.headline || ''],
  ['Score', (l) => l.score ?? ''],
  ['Einstufung', (l) => l.tier?.label || ''],
  ['Google Sterne', (l) => l.googleRating ?? ''],
  ['Google Bewertungen', (l) => l.googleReviews ?? ''],
  ['Inaktiv (Jahre)', (l) => l.inactiveYears ?? ''],
  ['Webseite Stand', (l) => l.audit?.copyrightYear ?? ''],
  ['Status', (l) => statusLabel(l.status)],
  ['Wiedervorlage', (l) => (l.followUpAt ? l.followUpAt.slice(0, 10) : '')],
  ['Notizen', (l) => (l.notes || []).map((n) => n.text).join(' | ')],
  ['Google Maps', (l) => l.googleMapsUrl || ''],
  ['Quelle', (l) => l.source],
  ['Erfasst am', (l) => (l.createdAt || '').slice(0, 10)],
];

export function websiteStatusLabel(status) {
  return {
    none: 'Keine Webseite',
    dead: 'Webseite tot',
    parked: 'Platzhalterseite',
    social_only: 'Nur Social Media',
    directory_only: 'Nur Verzeichnis',
    ok: 'Webseite vorhanden',
    error: 'Prüfung fehlgeschlagen',
  }[status] || 'Nicht geprüft';
}

function escapeCell(value) {
  const s = value == null ? '' : String(value);
  // Formel-Injection in Excel verhindern
  const safe = /^[=+\-@\t\r]/.test(s) ? "'" + s : s;
  return '"' + safe.replace(/"/g, '""').replace(/\r?\n/g, ' ') + '"';
}

export function leadsToCsv(leads) {
  const header = COLUMNS.map(([title]) => escapeCell(title)).join(';');
  const rows = leads.map((l) => COLUMNS.map(([, get]) => escapeCell(get(l))).join(';'));
  return '﻿' + [header, ...rows].join('\r\n');
}
