/**
 * Ortsauflösung für die Schweiz.
 *
 * Eingebautes Verzeichnis der grössten Städte + aller Kantone, damit die App
 * ohne externe Geocoding-Anfrage funktioniert. Unbekannte Orte werden über
 * Nominatim (OpenStreetMap) nachgeschlagen.
 */
import { config } from './config.js';
import { fetchJson } from './http.js';

/** [name, lat, lng, empfohlener Radius km, Kantonskürzel] */
const PLACES = [
  ['Zürich', 47.3769, 8.5417, 12, 'ZH'],
  ['Winterthur', 47.5, 8.7241, 10, 'ZH'],
  ['Uster', 47.3474, 8.7204, 8, 'ZH'],
  ['Dübendorf', 47.3971, 8.6187, 6, 'ZH'],
  ['Dietikon', 47.4017, 8.4004, 6, 'ZH'],
  ['Wetzikon', 47.3264, 8.7981, 7, 'ZH'],
  ['Horgen', 47.2597, 8.5983, 7, 'ZH'],
  ['Bülach', 47.5211, 8.5397, 8, 'ZH'],
  ['Wädenswil', 47.2296, 8.6739, 7, 'ZH'],
  ['Kloten', 47.4517, 8.585, 6, 'ZH'],
  ['Bern', 46.948, 7.4474, 12, 'BE'],
  ['Thun', 46.7581, 7.628, 10, 'BE'],
  ['Biel/Bienne', 47.1368, 7.2467, 10, 'BE'],
  ['Köniz', 46.9242, 7.4142, 7, 'BE'],
  ['Burgdorf', 47.0576, 7.6303, 8, 'BE'],
  ['Interlaken', 46.6863, 7.8632, 12, 'BE'],
  ['Langenthal', 47.2135, 7.7896, 9, 'BE'],
  ['Basel', 47.5596, 7.5886, 12, 'BS'],
  ['Liestal', 47.4845, 7.7346, 9, 'BL'],
  ['Allschwil', 47.5514, 7.5378, 6, 'BL'],
  ['Luzern', 47.0502, 8.3093, 12, 'LU'],
  ['Emmen', 47.0796, 8.2758, 7, 'LU'],
  ['Kriens', 47.0341, 8.2789, 6, 'LU'],
  ['Sursee', 47.1712, 8.1114, 9, 'LU'],
  ['St. Gallen', 47.4245, 9.3767, 12, 'SG'],
  ['Rapperswil-Jona', 47.2266, 8.8183, 9, 'SG'],
  ['Wil', 47.4633, 9.0451, 9, 'SG'],
  ['Buchs SG', 47.1679, 9.4767, 9, 'SG'],
  ['Genève', 46.2044, 6.1432, 12, 'GE'],
  ['Lausanne', 46.5197, 6.6323, 12, 'VD'],
  ['Yverdon-les-Bains', 46.7785, 6.6411, 10, 'VD'],
  ['Montreux', 46.4312, 6.9107, 9, 'VD'],
  ['Nyon', 46.383, 6.2394, 8, 'VD'],
  ['Vevey', 46.4628, 6.8419, 7, 'VD'],
  ['Lugano', 46.0037, 8.9511, 12, 'TI'],
  ['Bellinzona', 46.1944, 9.0175, 10, 'TI'],
  ['Locarno', 46.1712, 8.7994, 9, 'TI'],
  ['Chiasso', 45.8318, 9.0299, 7, 'TI'],
  ['Aarau', 47.3925, 8.0442, 10, 'AG'],
  ['Baden', 47.4735, 8.3064, 8, 'AG'],
  ['Wettingen', 47.4681, 8.3167, 6, 'AG'],
  ['Wohlen AG', 47.3506, 8.2789, 8, 'AG'],
  ['Rheinfelden', 47.5541, 7.7938, 8, 'AG'],
  ['Zug', 47.1662, 8.5155, 9, 'ZG'],
  ['Baar', 47.1958, 8.5296, 6, 'ZG'],
  ['Cham', 47.1817, 8.4636, 6, 'ZG'],
  ['Winterthur Seen', 47.4813, 8.7549, 5, 'ZH'],
  ['Chur', 46.8499, 9.5329, 12, 'GR'],
  ['Davos', 46.8027, 9.8360, 12, 'GR'],
  ['St. Moritz', 46.4908, 9.8355, 12, 'GR'],
  ['Sion', 46.2331, 7.3606, 12, 'VS'],
  ['Martigny', 46.1028, 7.0722, 10, 'VS'],
  ['Brig-Glis', 46.3159, 7.9877, 10, 'VS'],
  ['Visp', 46.2939, 7.8817, 8, 'VS'],
  ['Monthey', 46.2542, 6.9542, 8, 'VS'],
  ['Neuchâtel', 46.9924, 6.931, 10, 'NE'],
  ['La Chaux-de-Fonds', 47.0996, 6.8258, 10, 'NE'],
  ['Fribourg', 46.8065, 7.1615, 11, 'FR'],
  ['Bulle', 46.6194, 7.0577, 10, 'FR'],
  ['Solothurn', 47.2088, 7.5323, 10, 'SO'],
  ['Olten', 47.3497, 7.9036, 9, 'SO'],
  ['Grenchen', 47.1924, 7.3956, 7, 'SO'],
  ['Schaffhausen', 47.6959, 8.6342, 10, 'SH'],
  ['Frauenfeld', 47.5536, 8.8988, 10, 'TG'],
  ['Kreuzlingen', 47.6503, 9.1747, 8, 'TG'],
  ['Amriswil', 47.5478, 9.2986, 7, 'TG'],
  ['Arbon', 47.5163, 9.4325, 7, 'TG'],
  ['Herisau', 47.3861, 9.2792, 8, 'AR'],
  ['Appenzell', 47.3306, 9.4092, 8, 'AI'],
  ['Glarus', 47.0404, 9.0679, 12, 'GL'],
  ['Schwyz', 47.0207, 8.6533, 10, 'SZ'],
  ['Einsiedeln', 47.1275, 8.7452, 9, 'SZ'],
  ['Küssnacht', 47.0855, 8.4405, 7, 'SZ'],
  ['Pfäffikon SZ', 47.2033, 8.7803, 7, 'SZ'],
  ['Stans', 46.9578, 8.3663, 8, 'NW'],
  ['Sarnen', 46.8958, 8.2456, 9, 'OW'],
  ['Altdorf', 46.8804, 8.6444, 10, 'UR'],
  ['Delémont', 47.3646, 7.3444, 10, 'JU'],
  ['Porrentruy', 47.4155, 7.0752, 9, 'JU'],
  ['Vaduz', 47.141, 9.5215, 8, 'FL'],
];

/** Kantone mit Zentrum + Radius, der den Kanton grob abdeckt. */
const CANTONS = {
  ZH: ['Kanton Zürich', 47.4, 8.65, 30],
  BE: ['Kanton Bern', 46.87, 7.62, 55],
  LU: ['Kanton Luzern', 47.07, 8.13, 28],
  UR: ['Kanton Uri', 46.79, 8.66, 25],
  SZ: ['Kanton Schwyz', 47.06, 8.72, 25],
  OW: ['Kanton Obwalden', 46.85, 8.24, 20],
  NW: ['Kanton Nidwalden', 46.93, 8.4, 15],
  GL: ['Kanton Glarus', 46.98, 9.05, 25],
  ZG: ['Kanton Zug', 47.16, 8.52, 12],
  FR: ['Kanton Freiburg', 46.72, 7.12, 35],
  SO: ['Kanton Solothurn', 47.28, 7.63, 30],
  BS: ['Kanton Basel-Stadt', 47.56, 7.59, 8],
  BL: ['Kanton Basel-Landschaft', 47.45, 7.75, 22],
  SH: ['Kanton Schaffhausen', 47.7, 8.6, 18],
  AR: ['Appenzell Ausserrhoden', 47.38, 9.28, 15],
  AI: ['Appenzell Innerrhoden', 47.33, 9.41, 12],
  SG: ['Kanton St. Gallen', 47.35, 9.3, 40],
  GR: ['Kanton Graubünden', 46.66, 9.58, 60],
  AG: ['Kanton Aargau', 47.39, 8.13, 32],
  TG: ['Kanton Thurgau', 47.56, 9.05, 28],
  TI: ['Kanton Tessin', 46.24, 8.9, 40],
  VD: ['Kanton Waadt', 46.6, 6.55, 45],
  VS: ['Kanton Wallis', 46.22, 7.55, 55],
  NE: ['Kanton Neuenburg', 47.0, 6.83, 25],
  GE: ['Kanton Genf', 46.21, 6.13, 15],
  JU: ['Kanton Jura', 47.35, 7.15, 25],
  FL: ['Liechtenstein', 47.14, 9.55, 12],
};

const normalize = (s) =>
  String(s || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();

const PLACE_INDEX = new Map();
for (const [name, lat, lng, radius, canton] of PLACES) {
  PLACE_INDEX.set(normalize(name), { name, lat, lng, radiusKm: radius, canton, kind: 'city' });
}
for (const [code, [name, lat, lng, radius]] of Object.entries(CANTONS)) {
  const entry = { name, lat, lng, radiusKm: radius, canton: code, kind: 'canton' };
  PLACE_INDEX.set(normalize(name), entry);
  PLACE_INDEX.set(normalize(code), entry);
  PLACE_INDEX.set(normalize(name.replace(/^Kanton /, '')), entry);
}

/**
 * Raster für den Schweiz-weiten Scan.
 *
 * Statt die Schweiz mit einem Riesenkreis abzudecken (dabei gehen bei jeder
 * Datenquelle Treffer verloren, weil ein Limit greift), wird Ort für Ort
 * gesucht. Das eingebaute Städteverzeichnis deckt alle 26 Kantone ab und
 * liegt dort, wo auch die Betriebe sind.
 *
 * Doppelte Treffer zwischen benachbarten Orten fängt die Speicherung ab.
 */
export function schweizRaster({ kantone } = {}) {
  const gewuenscht = kantone && kantone.length ? new Set(kantone) : null;

  const orte = PLACES
    .filter(([, , , , canton]) => !gewuenscht || gewuenscht.has(canton))
    .map(([name, lat, lng, radiusKm, canton]) => ({ name, lat, lng, radiusKm, canton }));

  // Kantone ohne Stadt im Verzeichnis über ihr Zentrum abdecken
  const abgedeckt = new Set(orte.map((o) => o.canton));
  for (const [code, [name, lat, lng, radiusKm]] of Object.entries(CANTONS)) {
    if (gewuenscht && !gewuenscht.has(code)) continue;
    if (abgedeckt.has(code)) continue;
    orte.push({ name, lat, lng, radiusKm, canton: code });
  }

  return orte;
}

/** Alle Kantonskürzel, für die Auswahl im UI. */
export function alleKantone() {
  return Object.entries(CANTONS).map(([code, [name]]) => ({ code, name }));
}

/** Liste für die Autovervollständigung im UI. */
export function listPlaces() {
  return {
    cities: PLACES.map(([name, , , , canton]) => ({ name, canton })),
    cantons: Object.entries(CANTONS).map(([code, [name]]) => ({ code, name })),
  };
}

/**
 * Ort -> Koordinaten. Erst im eingebauten Verzeichnis, sonst über Nominatim.
 * @returns {Promise<{name:string, lat:number, lng:number, radiusKm:number, canton?:string, source:string}>}
 */
export async function resolvePlace(query, { radiusKm } = {}) {
  const q = String(query || '').trim();
  if (!q) throw new Error('Bitte einen Ort angeben (z. B. "Zürich" oder "Kanton Aargau").');

  // Direkte Koordinaten erlauben: "47.37, 8.54"
  const coord = /^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$/.exec(q);
  if (coord) {
    return {
      name: q,
      lat: Number(coord[1]),
      lng: Number(coord[2]),
      radiusKm: radiusKm || config.defaults.radiusKm,
      source: 'koordinaten',
    };
  }

  const hit = PLACE_INDEX.get(normalize(q));
  if (hit) {
    return { ...hit, radiusKm: radiusKm || hit.radiusKm, source: 'verzeichnis' };
  }

  // Fallback: Nominatim
  const url = new URL(config.nominatim.endpoint);
  url.searchParams.set('q', q);
  url.searchParams.set('format', 'jsonv2');
  url.searchParams.set('limit', '1');
  url.searchParams.set('countrycodes', 'ch,li,de,at,fr,it');
  const results = await fetchJson(url.toString(), {}, 20000);
  if (!Array.isArray(results) || results.length === 0) {
    throw new Error(
      `Ort "${q}" nicht gefunden. Tipp: Stadt (z. B. "Winterthur"), Kanton (z. B. "Aargau") oder Koordinaten "47.37, 8.54".`,
    );
  }
  const r = results[0];
  return {
    name: r.display_name?.split(',')[0] || q,
    lat: Number(r.lat),
    lng: Number(r.lon),
    radiusKm: radiusKm || config.defaults.radiusKm,
    source: 'nominatim',
  };
}

/** Distanz in km zwischen zwei Punkten (Haversine). */
export function distanceKm(a, b) {
  if (!a || !b || !isFinite(a.lat) || !isFinite(b.lat)) return null;
  const R = 6371;
  const dLat = ((b.lat - a.lat) * Math.PI) / 180;
  const dLng = ((b.lng - a.lng) * Math.PI) / 180;
  const lat1 = (a.lat * Math.PI) / 180;
  const lat2 = (b.lat * Math.PI) / 180;
  const h =
    Math.sin(dLat / 2) ** 2 + Math.sin(dLng / 2) ** 2 * Math.cos(lat1) * Math.cos(lat2);
  return Math.round(2 * R * Math.asin(Math.sqrt(h)) * 10) / 10;
}
