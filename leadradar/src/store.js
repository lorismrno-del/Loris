/**
 * Speicher: eine JSON-Datei pro Datensatz, atomar geschrieben.
 * Bewusst ohne Datenbank - so bleibt die App installationsfrei und die Daten
 * sind für Loris jederzeit als Datei sichtbar/sicherbar.
 */
import fs from 'node:fs';
import fsp from 'node:fs/promises';
import path from 'node:path';
import { config } from './config.js';

const LEADS_FILE = () => path.join(config.dataDir, 'leads.json');
const STATE_FILE = () => path.join(config.dataDir, 'state.json');

/** @type {{leads: Map<string, any>, state: any, loaded: boolean}} */
const db = { leads: new Map(), state: defaultState(), loaded: false };

function defaultState() {
  return {
    searches: [],
    lastSearch: null,
    createdAt: new Date().toISOString(),
  };
}

export const STATUSES = [
  { id: 'neu', label: 'Neu', color: '#64748b' },
  { id: 'anrufen', label: 'Anrufen', color: '#2563eb' },
  { id: 'kontaktiert', label: 'Kontaktiert', color: '#7c3aed' },
  { id: 'followup', label: 'Wiedervorlage', color: '#ca8a04' },
  { id: 'termin', label: 'Termin', color: '#0891b2' },
  { id: 'offerte', label: 'Offerte raus', color: '#ea580c' },
  { id: 'kunde', label: 'Kunde ✅', color: '#16a34a' },
  { id: 'abgelehnt', label: 'Kein Interesse', color: '#94a3b8' },
  { id: 'nichtstoeren', label: 'Nicht kontaktieren', color: '#dc2626' },
];

const STATUS_IDS = new Set(STATUSES.map((s) => s.id));

/**
 * Was nach einem Anruf passiert sein kann.
 *
 * Jedes Ergebnis setzt den Status automatisch weiter und legt - wo sinnvoll -
 * gleich eine Wiedervorlage an. Ein Klick, alles erledigt.
 *
 * `wiedervorlageTage: 0` heisst "heute nochmal", nicht "keine Wiedervorlage".
 */
export const ANRUF_ERGEBNISSE = [
  { id: 'erreicht', label: 'Gespräch geführt', emoji: '💬', status: 'kontaktiert', farbe: '#7c3aed' },
  { id: 'termin', label: 'Termin vereinbart', emoji: '🤝', status: 'termin', farbe: '#16a34a', erfolg: true },
  { id: 'combox', label: 'Combox', emoji: '📼', status: 'anrufen', farbe: '#ca8a04', wiedervorlageTage: 1, kontaktlos: true },
  { id: 'niemand', label: 'Niemand ran', emoji: '📵', status: 'anrufen', farbe: '#94a3b8', wiedervorlageTage: 1, kontaktlos: true },
  { id: 'besetzt', label: 'Besetzt', emoji: '⏳', status: 'anrufen', farbe: '#94a3b8', wiedervorlageTage: 0, kontaktlos: true },
  { id: 'rueckruf', label: 'Rückruf abgemacht', emoji: '🔁', status: 'followup', farbe: '#0891b2', brauchtDatum: true },
  { id: 'unterlagen', label: 'Will Unterlagen', emoji: '✉️', status: 'kontaktiert', farbe: '#2563eb', wiedervorlageTage: 4 },
  { id: 'spaeter', label: 'Später nochmal', emoji: '🕓', status: 'followup', farbe: '#ca8a04', wiedervorlageTage: 90 },
  { id: 'kein_interesse', label: 'Kein Interesse', emoji: '👎', status: 'abgelehnt', farbe: '#94a3b8' },
  { id: 'nie_wieder', label: 'Nicht mehr anrufen', emoji: '🚫', status: 'nichtstoeren', farbe: '#dc2626' },
  { id: 'falsche_nummer', label: 'Nummer stimmt nicht', emoji: '❌', status: 'anrufen', farbe: '#dc2626', kontaktlos: true },
  { id: 'geschlossen', label: 'Gibt es nicht mehr', emoji: '🏚️', status: 'abgelehnt', farbe: '#dc2626' },
];

export const ERGEBNIS_BY_ID = new Map(ANRUF_ERGEBNISSE.map((e) => [e.id, e]));

/**
 * Trägt ein Anrufergebnis ein: Verlauf, Status, Zähler und Wiedervorlage.
 * @returns {{lead:any, hinweis?:string}|null}
 */
export function anrufErgebnis(id, ergebnisId, { notiz, datum } = {}) {
  const lead = db.leads.get(id);
  if (!lead) return null;

  const ergebnis = ERGEBNIS_BY_ID.get(ergebnisId);
  if (!ergebnis) return { error: 'Unbekanntes Anrufergebnis' };

  const jetzt = new Date();

  lead.anrufVersuche = (lead.anrufVersuche || 0) + 1;
  lead.letzterAnrufAt = jetzt.toISOString();
  lead.letztesErgebnis = ergebnisId;
  if (!ergebnis.kontaktlos) lead.erreichtAt = jetzt.toISOString();

  addActivity(
    lead,
    'call',
    `${ergebnis.emoji} ${ergebnis.label}${notiz ? ' – ' + notiz : ''}`,
  );
  if (notiz) addNote(id, notiz);

  lead.status = ergebnis.status;
  lead.doNotContact = ergebnis.status === 'nichtstoeren';

  // Wiedervorlage automatisch setzen
  if (ergebnis.brauchtDatum && datum) {
    lead.followUpAt = new Date(datum).toISOString();
  } else if (typeof ergebnis.wiedervorlageTage === 'number') {
    const ziel = new Date(jetzt);
    ziel.setDate(ziel.getDate() + ergebnis.wiedervorlageTage);
    ziel.setHours(9, 0, 0, 0);
    lead.followUpAt = ziel.toISOString();
  } else if (['abgelehnt', 'nichtstoeren'].includes(ergebnis.status)) {
    lead.followUpAt = null;
  }

  lead.updatedAt = jetzt.toISOString();

  // Nach mehreren erfolglosen Versuchen lohnt sich ein anderer Kanal
  let hinweis;
  const erfolglos = (lead.activities || [])
    .slice(0, 4)
    .filter((a) => /Combox|Niemand ran|Besetzt/.test(a.text)).length;
  if (ergebnis.kontaktlos && erfolglos >= 3) {
    hinweis =
      `${lead.name} war jetzt ${erfolglos}× nicht erreichbar. ` +
      (lead.email || lead.customEmail
        ? 'Versuch es per E-Mail oder WhatsApp – die Vorlage ist bereit.'
        : 'Versuch es per WhatsApp oder früher am Morgen (07:00–08:00 erwischt man Handwerker am besten).');
  }

  return { lead, hinweis, ergebnis };
}

export async function load() {
  if (db.loaded) return;
  await fsp.mkdir(config.dataDir, { recursive: true });

  db.leads = new Map();
  try {
    const raw = await fsp.readFile(LEADS_FILE(), 'utf8');
    const arr = JSON.parse(raw);
    if (Array.isArray(arr)) for (const l of arr) db.leads.set(l.id, l);
  } catch (err) {
    if (err.code !== 'ENOENT') {
      console.warn('[store] leads.json konnte nicht gelesen werden:', err.message);
      await backupCorrupt(LEADS_FILE());
    }
  }

  try {
    const raw = await fsp.readFile(STATE_FILE(), 'utf8');
    db.state = { ...defaultState(), ...JSON.parse(raw) };
  } catch (err) {
    if (err.code !== 'ENOENT') console.warn('[store] state.json:', err.message);
  }

  db.loaded = true;
}

async function backupCorrupt(file) {
  try {
    await fsp.rename(file, file + '.kaputt-' + Date.now());
  } catch { /* egal */ }
}

/** Atomar schreiben: erst .tmp, dann umbenennen. Verhindert halbe Dateien. */
let writeQueue = Promise.resolve();
function queueWrite(fn) {
  writeQueue = writeQueue.then(fn, fn);
  return writeQueue;
}

async function writeJson(file, data) {
  const tmp = file + '.tmp';
  await fsp.writeFile(tmp, JSON.stringify(data, null, 2), 'utf8');
  await fsp.rename(tmp, file);
}

export function saveLeads() {
  return queueWrite(() => writeJson(LEADS_FILE(), [...db.leads.values()]));
}

export function saveState() {
  return queueWrite(() => writeJson(STATE_FILE(), db.state));
}

export function allLeads() {
  return [...db.leads.values()];
}

export function getLead(id) {
  return db.leads.get(id) || null;
}

export function getState() {
  return db.state;
}

/**
 * Fügt gefundene Leads hinzu. Bereits vorhandene Leads behalten ihren
 * Status/Notizen, bekommen aber frische Analyse-Daten.
 * @returns {{added:number, updated:number, leads:any[]}}
 */
export function upsertLeads(incoming) {
  let added = 0;
  let updated = 0;
  const result = [];

  for (const lead of incoming) {
    const existing = db.leads.get(lead.id) || findByFingerprint(lead);

    if (existing) {
      // Nutzerdaten schützen, Rechercheergebnisse aktualisieren
      const merged = {
        ...existing,
        ...lead,
        id: existing.id,
        status: existing.status,
        notes: existing.notes || [],
        activities: existing.activities || [],
        starred: existing.starred || false,
        contactName: existing.contactName || lead.contactName || '',
        customPhone: existing.customPhone || '',
        customEmail: existing.customEmail || '',
        followUpAt: existing.followUpAt || null,
        createdAt: existing.createdAt,
        updatedAt: new Date().toISOString(),
      };
      // Manuell erfasste Kontaktdaten nicht überschreiben
      if (existing.emailSource === 'manuell') merged.email = existing.email;
      db.leads.set(merged.id, merged);
      result.push(merged);
      updated++;
    } else {
      const fresh = {
        status: 'neu',
        notes: [],
        activities: [],
        starred: false,
        contactName: '',
        followUpAt: null,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        ...lead,
      };
      db.leads.set(fresh.id, fresh);
      result.push(fresh);
      added++;
    }
  }

  return { added, updated, leads: result };
}

/** Erkennt denselben Betrieb, auch wenn er aus einer anderen Quelle kommt. */
function findByFingerprint(lead) {
  const fp = fingerprint(lead);
  if (!fp) return null;
  for (const existing of db.leads.values()) {
    if (fingerprint(existing) === fp) return existing;
  }
  return null;
}

function fingerprint(lead) {
  const name = String(lead.name || '')
    .toLowerCase()
    .replace(/\b(gmbh|ag|sa|sarl|co|kg|und|&|\+)\b/g, '')
    .replace(/[^a-z0-9äöü]/g, '');
  if (!name) return null;
  const city = String(lead.address?.city || '').toLowerCase().replace(/[^a-z0-9äöü]/g, '');
  const phone = String(lead.phone || '').replace(/\D/g, '').slice(-9);
  return phone ? `p:${phone}` : `n:${name}|${city}`;
}

/** Ändert Felder eines Leads (nur erlaubte Felder). */
export function updateLead(id, patch) {
  const lead = db.leads.get(id);
  if (!lead) return null;

  const allowed = [
    'status', 'starred', 'contactName', 'customPhone', 'customEmail',
    'followUpAt', 'email', 'phone', 'website', 'trade',
  ];
  for (const key of allowed) {
    if (key in patch) lead[key] = patch[key];
  }

  if ('status' in patch) {
    if (!STATUS_IDS.has(patch.status)) return { error: 'Unbekannter Status' };
    addActivity(lead, 'status', `Status → ${statusLabel(patch.status)}`);
    if (patch.status === 'nichtstoeren') lead.doNotContact = true;
    if (patch.status !== 'nichtstoeren') lead.doNotContact = false;
  }
  if ('email' in patch && patch.email) lead.emailSource = 'manuell';

  lead.updatedAt = new Date().toISOString();
  return lead;
}

export function statusLabel(id) {
  return STATUSES.find((s) => s.id === id)?.label || id;
}

export function addActivity(lead, type, text) {
  lead.activities = lead.activities || [];
  lead.activities.unshift({
    id: 'a' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
    ts: new Date().toISOString(),
    type,
    text,
  });
  lead.activities = lead.activities.slice(0, 200);
  lead.updatedAt = new Date().toISOString();
  return lead.activities[0];
}

export function addNote(id, text) {
  const lead = db.leads.get(id);
  if (!lead) return null;
  const note = {
    id: 'n' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
    ts: new Date().toISOString(),
    text: String(text || '').slice(0, 5000),
  };
  lead.notes = lead.notes || [];
  lead.notes.unshift(note);
  lead.updatedAt = new Date().toISOString();
  return note;
}

export function deleteLead(id) {
  return db.leads.delete(id);
}

/** Löscht alle Leads mit einem bestimmten Status (z. B. Aufräumen). */
export function deleteByStatus(status) {
  let n = 0;
  for (const [id, lead] of db.leads) {
    if (lead.status === status) {
      db.leads.delete(id);
      n++;
    }
  }
  return n;
}

export function recordSearch(entry) {
  db.state.searches.unshift({ ...entry, ts: new Date().toISOString() });
  db.state.searches = db.state.searches.slice(0, 50);
  db.state.lastSearch = entry;
}

/** Kennzahlen fürs Dashboard. */
export function stats() {
  const leads = allLeads();
  const byStatus = {};
  for (const s of STATUSES) byStatus[s.id] = 0;
  let hot = 0;
  let noWebsite = 0;
  let withPhone = 0;
  let withEmail = 0;

  for (const l of leads) {
    byStatus[l.status] = (byStatus[l.status] || 0) + 1;
    if ((l.score ?? 0) >= 75) hot++;
    if (l.audit?.status === 'none') noWebsite++;
    if (l.phone || l.customPhone) withPhone++;
    if (l.email || l.customEmail) withEmail++;
  }

  const dueFollowUps = leads.filter(
    (l) => l.followUpAt && Date.parse(l.followUpAt) <= Date.now() && l.status !== 'kunde',
  ).length;

  return {
    total: leads.length,
    hot,
    noWebsite,
    withPhone,
    withEmail,
    dueFollowUps,
    byStatus,
    kunden: byStatus.kunde || 0,
    heute: tagesStatistik(),
  };
}

/** Kennzahlen für den heutigen Anruftag - motiviert und zeigt die Trefferquote. */
export function tagesStatistik() {
  const start = new Date();
  start.setHours(0, 0, 0, 0);
  const ab = start.getTime();

  let anrufe = 0;
  let erreicht = 0;
  let combox = 0;
  let termine = 0;
  let abgelehnt = 0;

  for (const lead of db.leads.values()) {
    for (const a of lead.activities || []) {
      if (a.type !== 'call' || Date.parse(a.ts) < ab) continue;
      anrufe++;
      if (/Combox/.test(a.text)) combox++;
      else if (/Gespräch geführt|Termin vereinbart|Will Unterlagen|Rückruf abgemacht/.test(a.text)) erreicht++;
      if (/Termin vereinbart/.test(a.text)) termine++;
      if (/Kein Interesse|Nicht mehr anrufen/.test(a.text)) abgelehnt++;
    }
  }

  return {
    anrufe,
    erreicht,
    combox,
    termine,
    abgelehnt,
    quote: anrufe ? Math.round((erreicht / anrufe) * 100) : 0,
  };
}

/**
 * Die Anrufliste für den Anruf-Modus: wer ist als Nächstes dran?
 *
 * Reihenfolge:
 *  1. fällige Wiedervorlagen (Zusagen einhalten geht vor)
 *  2. danach nach Potenzial
 *
 * Ausgeschlossen: ohne Telefonnummer, abgelehnt, Kunde, nicht kontaktieren,
 * und alles, was heute schon versucht wurde.
 */
export function anrufWarteschlange(filter = {}) {
  const jetzt = Date.now();
  const heuteStart = new Date();
  heuteStart.setHours(0, 0, 0, 0);

  return allLeads()
    .filter((l) => {
      if (!(l.customPhone || l.phone)) return false;
      if (['abgelehnt', 'kunde', 'nichtstoeren'].includes(l.status)) return false;
      if (l.letzterAnrufAt && Date.parse(l.letzterAnrufAt) >= heuteStart.getTime()) return false;
      if (l.followUpAt && Date.parse(l.followUpAt) > jetzt) return false;
      if (filter.trade && filter.trade !== 'alle' && l.trade !== filter.trade) return false;
      if (filter.city && filter.city !== 'alle' && l.address?.city !== filter.city) return false;
      if (filter.canton && filter.canton !== 'alle' && l.address?.canton !== filter.canton) return false;
      if (filter.minScore && (l.score ?? 0) < filter.minScore) return false;
      return true;
    })
    .sort((a, b) => {
      const aFaellig = a.followUpAt ? 0 : 1;
      const bFaellig = b.followUpAt ? 0 : 1;
      if (aFaellig !== bFaellig) return aFaellig - bFaellig;
      return (b.score ?? 0) - (a.score ?? 0);
    });
}

/** Synchrones Laden beim Start (für den Server-Boot). */
export function existsData() {
  return fs.existsSync(LEADS_FILE());
}
