/**
 * Agentur-Profil: Stammdaten + Verkaufsargumente.
 *
 * Die Werte stammen aus dem echten Auftritt von Lorino Co. und lassen sich in
 * der App unter "Einstellungen" jederzeit anpassen (gespeichert in
 * data/settings.json). Sie fliessen in Anrufskript, E-Mail und WhatsApp ein.
 */
import fsp from 'node:fs/promises';
import path from 'node:path';
import { config } from './config.js';

const FILE = () => path.join(config.dataDir, 'settings.json');

export const DEFAULT_SETTINGS = {
  // ---- Stammdaten
  agencyName: 'Lorino Co.',
  ownerName: 'Loris Marino',
  phone: '+41 76 520 10 46',
  email: 'info@lorinoweb.ch',
  website: 'https://lorino-co.ch',
  instagram: '@lorino_co',
  region: 'Deutschschweiz',

  // ---- Positionierung
  slogan: 'Handwerk trifft Highspeed.',
  pitch:
    'Individuelle Premium-Webseiten für Bauunternehmen und Handwerksbetriebe in der Deutschschweiz. Kein Baukasten. Keine Vorlage.',

  // ---- Das Argument, das den Abschluss bringt
  freePreview: true,
  freePreviewLine:
    'Sie sehen Ihre neue Webseite fixfertig, bevor Sie irgendetwas zahlen. Gefällt sie Ihnen nicht, kostet es Sie nichts.',

  // ---- Verkaufsargumente (werden im Skript als Munition angezeigt)
  usps: [
    'Kostenlose Vorschau – Sie zahlen erst, wenn Sie überzeugt sind',
    'Kein Baukasten, keine Vorlage – individuell für Ihren Betrieb gebaut',
    '1:1 Betreuung direkt mit mir – kein Callcenter, keine Warteschlange',
    'Hosting, Sicherheit und Updates übernehme ich komplett',
    'Mobile-First – über 60 % Ihrer Besucher kommen vom Handy',
    'Google Maps und Google-Unternehmensprofil richte ich mit ein',
    'Kontaktformular mit WhatsApp-Anbindung',
    'Fertig in 1–3 Wochen',
  ],

  // ---- Ablauf (für Einwandbehandlung)
  processSteps: [
    'Kontakt – Sie erzählen mir kurz von Ihrem Betrieb',
    'Kostenloses Beratungsgespräch (ca. 15 Minuten)',
    'Kostenlose Vorschau Ihrer Webseite',
    'Veröffentlichung + laufende Betreuung',
  ],

  // ---- Referenzen, die im Gespräch genannt werden dürfen
  references: ['Baumanagement GmbH – Unternehmenswebseite mit Projektanfragen'],

  // ---- Kalender-/Buchungslink (optional, landet in der E-Mail)
  bookingUrl: '',

  // ---- Ziele fürs Dashboard
  goals: {
    callsPerDay: 20,
    meetingsPerWeek: 5,
  },

  // ---- Weitergabe an andere Tools (z. B. Vertra / Agentur-OS)
  webhooks: [
    // { label: 'Agentur-OS', url: 'https://…/api/leads', enabled: false, secret: '' }
  ],
};

let current = { ...DEFAULT_SETTINGS };

export async function loadSettings() {
  try {
    const raw = await fsp.readFile(FILE(), 'utf8');
    const saved = JSON.parse(raw);
    current = mergeSettings(DEFAULT_SETTINGS, saved);
  } catch (err) {
    if (err.code !== 'ENOENT') console.warn('[settings]', err.message);
    current = { ...DEFAULT_SETTINGS };
  }
  syncConfig();
  return current;
}

export async function saveSettings(patch) {
  current = mergeSettings(current, patch);
  syncConfig();
  await fsp.mkdir(config.dataDir, { recursive: true });
  const tmp = FILE() + '.tmp';
  await fsp.writeFile(tmp, JSON.stringify(current, null, 2), 'utf8');
  await fsp.rename(tmp, FILE());
  return current;
}

export function getSettings() {
  return current;
}

/** Nur bekannte Felder übernehmen - kein wildes Überschreiben. */
function mergeSettings(base, patch) {
  const out = { ...base };
  for (const [key, value] of Object.entries(patch || {})) {
    if (!(key in DEFAULT_SETTINGS)) continue;
    if (Array.isArray(DEFAULT_SETTINGS[key])) {
      out[key] = Array.isArray(value) ? value.filter((v) => v !== '' && v != null) : base[key];
    } else if (typeof DEFAULT_SETTINGS[key] === 'object' && DEFAULT_SETTINGS[key] !== null) {
      out[key] = { ...base[key], ...(value || {}) };
    } else if (typeof DEFAULT_SETTINGS[key] === 'boolean') {
      out[key] = Boolean(value);
    } else {
      out[key] = value == null ? base[key] : String(value).slice(0, 2000);
    }
  }
  return out;
}

/** Hält config.agency mit den Einstellungen im Gleichklang. */
function syncConfig() {
  config.agency = {
    name: current.agencyName,
    owner: current.ownerName,
    phone: current.phone,
    email: current.email,
    website: current.website,
    instagram: current.instagram,
  };
}
