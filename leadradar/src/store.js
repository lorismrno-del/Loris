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
  };
}

/** Synchrones Laden beim Start (für den Server-Boot). */
export function existsData() {
  return fs.existsSync(LEADS_FILE());
}
