/**
 * Datenquelle: OpenStreetMap via Overpass API.
 * Gratis, kein API-Key nötig. Gute Abdeckung von Handwerksbetrieben in der CH.
 *
 * Achtung: Overpass ist ein Gemeinschaftsdienst - fair benutzen (nicht im Sekundentakt abfragen).
 */
import { config } from '../config.js';
import { fetchWithTimeout } from '../http.js';
import { TRADE_BY_ID } from '../trades.js';

const CANTON_BY_NAME = {
  zürich: 'ZH', zurich: 'ZH', bern: 'BE', luzern: 'LU', uri: 'UR', schwyz: 'SZ',
  obwalden: 'OW', nidwalden: 'NW', glarus: 'GL', zug: 'ZG', freiburg: 'FR',
  fribourg: 'FR', solothurn: 'SO', 'basel-stadt': 'BS', 'basel-landschaft': 'BL',
  schaffhausen: 'SH', 'appenzell ausserrhoden': 'AR', 'appenzell innerrhoden': 'AI',
  'st. gallen': 'SG', 'sankt gallen': 'SG', graubünden: 'GR', aargau: 'AG',
  thurgau: 'TG', ticino: 'TI', tessin: 'TI', vaud: 'VD', waadt: 'VD',
  valais: 'VS', wallis: 'VS', neuchâtel: 'NE', genève: 'GE', genf: 'GE', jura: 'JU',
};

/** Baut die Overpass-QL-Abfrage für die gewählten Branchen. */
function buildQuery({ trades, lat, lng, radiusKm, limit }) {
  const radiusM = Math.round(radiusKm * 1000);
  const clauses = [];

  for (const tradeId of trades) {
    const trade = TRADE_BY_ID.get(tradeId);
    if (!trade) continue;
    for (const [key, values] of trade.osm) {
      const regex = values.map((v) => v.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|');
      clauses.push(`  nwr["${key}"~"^(${regex})$"](around:${radiusM},${lat},${lng});`);
    }
  }

  if (clauses.length === 0) throw new Error('Keine gültige Branche gewählt.');

  return [
    `[out:json][timeout:${Math.round(config.overpass.timeoutMs / 1000)}];`,
    '(',
    ...clauses,
    ');',
    `out center tags ${Math.max(1, Math.min(limit, 800))};`,
  ].join('\n');
}

/** OSM-Element -> unser Lead-Format. */
function toLead(el, tradeId) {
  const t = el.tags || {};
  const name = t.name || t['operator'] || t['brand'];
  if (!name) return null; // Ohne Namen ist der Eintrag für die Akquise wertlos

  const lat = el.lat ?? el.center?.lat;
  const lng = el.lon ?? el.center?.lon;

  const street = [t['addr:street'], t['addr:housenumber']].filter(Boolean).join(' ');
  const city = t['addr:city'] || t['addr:place'] || '';
  const zip = t['addr:postcode'] || '';
  const cantonKey = String(t['addr:state'] || '').toLowerCase();

  const website =
    t.website || t['contact:website'] || t.url || t['website:official'] || '';
  const facebook = t['contact:facebook'] || t.facebook || '';
  const instagram = t['contact:instagram'] || t.instagram || '';

  return {
    id: `osm:${el.type}/${el.id}`,
    source: 'osm',
    sourceUrl: `https://www.openstreetmap.org/${el.type}/${el.id}`,
    name: name.trim(),
    trade: tradeId,
    osmTags: pickInterestingTags(t),
    address: {
      street: street || '',
      zip,
      city,
      canton: CANTON_BY_NAME[cantonKey] || '',
      country: t['addr:country'] || 'CH',
    },
    lat,
    lng,
    phone: normalizePhone(t.phone || t['contact:phone'] || t['contact:mobile'] || t.mobile),
    email: normalizeEmail(t.email || t['contact:email']),
    website: normalizeUrl(website),
    socials: {
      facebook: normalizeSocial(facebook, 'facebook.com'),
      instagram: normalizeSocial(instagram, 'instagram.com'),
    },
    openingHours: t.opening_hours || '',
    googleRating: null,
    googleReviews: null,
    googleMapsUrl:
      lat && lng ? `https://www.google.com/maps/search/?api=1&query=${lat}%2C${lng}` : '',
    lastActivityAt: null,
  };
}

function pickInterestingTags(t) {
  const keep = ['craft', 'shop', 'office', 'amenity', 'healthcare', 'description', 'operator'];
  const out = {};
  for (const k of keep) if (t[k]) out[k] = t[k];
  return out;
}

export function normalizePhone(v) {
  if (!v) return '';
  // Mehrfachnummern: erste nehmen
  const first = String(v).split(/[;,]/)[0].trim();
  const digits = first.replace(/[^\d+]/g, '');
  if (!digits) return '';
  if (digits.startsWith('00')) return '+' + digits.slice(2);
  if (digits.startsWith('0') && digits.length >= 9) return '+41' + digits.slice(1);
  if (!digits.startsWith('+') && digits.length >= 9) return '+41' + digits;
  return digits;
}

export function normalizeEmail(v) {
  if (!v) return '';
  const first = String(v).split(/[;,\s]/)[0].trim().replace(/^mailto:/i, '');
  return /^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i.test(first) ? first.toLowerCase() : '';
}

export function normalizeUrl(v) {
  if (!v) return '';
  let s = String(v).split(/[;\s]/)[0].trim();
  if (!s) return '';
  if (!/^https?:\/\//i.test(s)) s = 'https://' + s.replace(/^\/\//, '');
  try {
    const u = new URL(s);
    if (!u.hostname.includes('.')) return '';
    return u.toString().replace(/\/$/, '');
  } catch {
    return '';
  }
}

function normalizeSocial(v, host) {
  if (!v) return '';
  const s = String(v).trim();
  if (/^https?:\/\//i.test(s)) return s;
  return `https://${host}/${s.replace(/^@/, '')}`;
}

/** Führt die Overpass-Suche aus. */
export async function searchOsm({ trades, lat, lng, radiusKm, limit = 200 }) {
  const query = buildQuery({ trades, lat, lng, radiusKm, limit });

  const res = await fetchWithTimeout(
    config.overpass.endpoint,
    {
      method: 'POST',
      headers: { 'content-type': 'application/x-www-form-urlencoded' },
      body: 'data=' + encodeURIComponent(query),
    },
    config.overpass.timeoutMs,
  );

  if (res.status === 429 || res.status === 504) {
    throw new Error(
      'Overpass ist gerade überlastet (Gratis-Dienst). Kurz warten und nochmals versuchen, oder Google Places als Quelle nutzen.',
    );
  }
  if (!res.ok) {
    const body = (await res.text()).slice(0, 300);
    throw new Error(`Overpass-Fehler HTTP ${res.status}: ${body}`);
  }

  const data = await res.json();
  const elements = Array.isArray(data.elements) ? data.elements : [];

  // Branche pro Element bestimmen (welches Preset passt?)
  const leads = [];
  for (const el of elements) {
    const tradeId = matchTrade(el.tags || {}, trades) || trades[0];
    const lead = toLead(el, tradeId);
    if (lead) leads.push(lead);
  }
  return dedupe(leads);
}

function matchTrade(tags, tradeIds) {
  for (const id of tradeIds) {
    const trade = TRADE_BY_ID.get(id);
    if (!trade) continue;
    for (const [key, values] of trade.osm) {
      if (tags[key] && values.includes(tags[key])) return id;
    }
  }
  return null;
}

/** Doppelte Einträge (gleicher Name + Ort) zusammenführen. */
export function dedupe(leads) {
  const byKey = new Map();
  for (const lead of leads) {
    const key = `${lead.name.toLowerCase().replace(/\s+/g, '')}|${(lead.address?.city || '').toLowerCase()}`;
    const existing = byKey.get(key);
    if (!existing) {
      byKey.set(key, lead);
      continue;
    }
    // Den vollständigeren Datensatz behalten und Lücken auffüllen
    const merged = { ...existing };
    for (const field of ['phone', 'email', 'website', 'openingHours']) {
      if (!merged[field] && lead[field]) merged[field] = lead[field];
    }
    if (!merged.address?.street && lead.address?.street) merged.address = lead.address;
    if (merged.googleReviews == null && lead.googleReviews != null) {
      merged.googleRating = lead.googleRating;
      merged.googleReviews = lead.googleReviews;
      merged.googleMapsUrl = lead.googleMapsUrl || merged.googleMapsUrl;
      merged.lastActivityAt = lead.lastActivityAt || merged.lastActivityAt;
    }
    byKey.set(key, merged);
  }
  return [...byKey.values()];
}
