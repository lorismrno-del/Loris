/**
 * Zentrale Konfiguration. Alles über Umgebungsvariablen steuerbar,
 * mit sinnvollen Defaults, damit die App ohne Setup startet.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const ROOT = path.resolve(__dirname, '..');

// .env einlesen (kein externes Paket nötig)
loadDotEnv(path.join(ROOT, '.env'));

function loadDotEnv(file) {
  if (!fs.existsSync(file)) return;
  const text = fs.readFileSync(file, 'utf8');
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith('#')) continue;
    const eq = line.indexOf('=');
    if (eq === -1) continue;
    const key = line.slice(0, eq).trim();
    let value = line.slice(eq + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    if (process.env[key] === undefined) process.env[key] = value;
  }
}

const num = (v, fallback) => {
  const n = Number(v);
  return Number.isFinite(n) ? n : fallback;
};
const bool = (v, fallback) => {
  if (v === undefined || v === '') return fallback;
  return /^(1|true|yes|ja|on)$/i.test(String(v));
};

export const config = {
  port: num(process.env.PORT, 3000),
  // 0.0.0.0 = auch vom Handy im gleichen WLAN erreichbar.
  // Dann bitte unbedingt APP_PASSWORD setzen.
  host: process.env.HOST || '127.0.0.1',
  dataDir: process.env.DATA_DIR || path.join(ROOT, 'data'),

  auth: {
    password: process.env.APP_PASSWORD || '',
  },

  // Agentur-Stammdaten (für Anrufskript, E-Mail-Vorlagen, WhatsApp)
  agency: {
    name: process.env.AGENCY_NAME || 'Lorino Co.',
    owner: process.env.AGENCY_OWNER || 'Loris Marino',
    phone: process.env.AGENCY_PHONE || '+41 76 520 10 46',
    email: process.env.AGENCY_EMAIL || 'info@lorinoweb.ch',
    website: process.env.AGENCY_WEBSITE || 'https://lorino-co.ch',
    instagram: process.env.AGENCY_INSTAGRAM || '@lorino_co',
  },

  // Datenquellen
  google: {
    apiKey: process.env.GOOGLE_PLACES_API_KEY || '',
    // Reviews kosten mehr (Enterprise SKU). Ausschaltbar.
    includeReviews: bool(process.env.GOOGLE_INCLUDE_REVIEWS, true),
    maxPages: num(process.env.GOOGLE_MAX_PAGES, 3), // 3 Seiten = bis 60 Treffer
  },
  overpass: {
    endpoint: process.env.OVERPASS_URL || 'https://overpass-api.de/api/interpreter',
    timeoutMs: num(process.env.OVERPASS_TIMEOUT_MS, 90000),
  },
  nominatim: {
    endpoint: process.env.NOMINATIM_URL || 'https://nominatim.openstreetmap.org/search',
  },

  // Website-Analyse
  audit: {
    timeoutMs: num(process.env.AUDIT_TIMEOUT_MS, 12000),
    concurrency: num(process.env.AUDIT_CONCURRENCY, 6),
    maxBytes: num(process.env.AUDIT_MAX_BYTES, 2_500_000),
    followImpressum: bool(process.env.AUDIT_FOLLOW_IMPRESSUM, true),
    userAgent:
      process.env.AUDIT_USER_AGENT ||
      'Mozilla/5.0 (compatible; LorinoLeadradar/1.0; +https://lorinoweb.ch)',
  },

  // Verhalten
  defaults: {
    country: process.env.DEFAULT_COUNTRY || 'CH',
    region: process.env.DEFAULT_REGION || 'Zürich',
    radiusKm: num(process.env.DEFAULT_RADIUS_KM, 15),
  },
};

export const hasGoogle = () => Boolean(config.google.apiKey);
