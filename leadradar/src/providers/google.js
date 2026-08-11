/**
 * Datenquelle: Google Places API (New) - Text Search.
 *
 * Braucht einen API-Key (GOOGLE_PLACES_API_KEY). Liefert deutlich mehr Betriebe
 * als OSM und zusätzlich Bewertungen + Datum der letzten Bewertung -> daraus
 * leiten wir "seit X Jahren keine Aktivität" ab.
 *
 * Doku: https://developers.google.com/maps/documentation/places/web-service/text-search
 */
import { config } from '../config.js';
import { fetchJson } from '../http.js';
import { TRADE_BY_ID } from '../trades.js';
import { normalizePhone, normalizeEmail, normalizeUrl, dedupe } from './osm.js';

const ENDPOINT = 'https://places.googleapis.com/v1/places:searchText';

const BASE_FIELDS = [
  'places.id',
  'places.displayName',
  'places.formattedAddress',
  'places.addressComponents',
  'places.location',
  'places.nationalPhoneNumber',
  'places.internationalPhoneNumber',
  'places.websiteUri',
  'places.googleMapsUri',
  'places.rating',
  'places.userRatingCount',
  'places.businessStatus',
  'places.primaryTypeDisplayName',
  'places.regularOpeningHours.weekdayDescriptions',
];

const REVIEW_FIELDS = ['places.reviews.publishTime', 'places.reviews.relativePublishTimeDescription'];

function fieldMask() {
  const fields = [...BASE_FIELDS];
  if (config.google.includeReviews) fields.push(...REVIEW_FIELDS);
  return fields.join(',') + ',nextPageToken';
}

function component(place, type) {
  const c = place.addressComponents?.find((x) => x.types?.includes(type));
  return c?.shortText || c?.longText || '';
}

function toLead(place, tradeId) {
  const name = place.displayName?.text?.trim();
  if (!name) return null;

  const reviews = Array.isArray(place.reviews) ? place.reviews : [];
  const newest = reviews
    .map((r) => r.publishTime)
    .filter(Boolean)
    .sort()
    .pop();

  return {
    id: `google:${place.id}`,
    source: 'google',
    sourceUrl: place.googleMapsUri || '',
    name,
    trade: tradeId,
    address: {
      street: [component(place, 'route'), component(place, 'street_number')]
        .filter(Boolean)
        .join(' '),
      zip: component(place, 'postal_code'),
      city:
        component(place, 'locality') ||
        component(place, 'postal_town') ||
        component(place, 'administrative_area_level_2'),
      canton: component(place, 'administrative_area_level_1'),
      country: component(place, 'country') || 'CH',
      formatted: place.formattedAddress || '',
    },
    lat: place.location?.latitude,
    lng: place.location?.longitude,
    phone: normalizePhone(place.internationalPhoneNumber || place.nationalPhoneNumber),
    email: '',
    website: normalizeUrl(place.websiteUri),
    socials: {},
    openingHours: (place.regularOpeningHours?.weekdayDescriptions || []).join(' | '),
    googleRating: place.rating ?? null,
    googleReviews: place.userRatingCount ?? null,
    googleMapsUrl: place.googleMapsUri || '',
    businessStatus: place.businessStatus || '',
    lastActivityAt: newest || null,
    googleCategory: place.primaryTypeDisplayName?.text || '',
  };
}

async function searchOnce({ textQuery, lat, lng, radiusKm, pageToken }) {
  const body = {
    textQuery,
    languageCode: 'de',
    regionCode: config.defaults.country,
    maxResultCount: 20,
    locationBias: {
      circle: {
        center: { latitude: lat, longitude: lng },
        // Google erlaubt max. 50'000 m
        radius: Math.min(50000, Math.round(radiusKm * 1000)),
      },
    },
  };
  if (pageToken) body.pageToken = pageToken;

  return fetchJson(
    ENDPOINT,
    {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'X-Goog-Api-Key': config.google.apiKey,
        'X-Goog-FieldMask': fieldMask(),
      },
      body: JSON.stringify(body),
    },
    30000,
  );
}

/** Führt für jede Branche mehrere Suchbegriffe aus und führt die Treffer zusammen. */
export async function searchGoogle({ trades, place, lat, lng, radiusKm, limit = 200 }) {
  if (!config.google.apiKey) {
    throw new Error(
      'Kein Google-API-Key hinterlegt. Trage GOOGLE_PLACES_API_KEY in die .env ein oder wähle OpenStreetMap als Quelle.',
    );
  }

  const leads = [];
  const seen = new Set();

  outer: for (const tradeId of trades) {
    const trade = TRADE_BY_ID.get(tradeId);
    if (!trade) continue;

    for (const term of trade.google) {
      const textQuery = `${term} ${place}`.trim();
      let pageToken;
      for (let page = 0; page < config.google.maxPages; page++) {
        let data;
        try {
          data = await searchOnce({ textQuery, lat, lng, radiusKm, pageToken });
        } catch (err) {
          if (err.status === 403 || err.status === 401) {
            throw new Error(
              'Google lehnt den API-Key ab (403). Prüfe: Places API (New) aktiviert? Abrechnung aktiv? Key-Einschränkungen?',
            );
          }
          if (err.status === 429) {
            throw new Error('Google-Kontingent erschöpft (429). Später nochmals versuchen.');
          }
          throw err;
        }

        for (const p of data.places || []) {
          if (seen.has(p.id)) continue;
          seen.add(p.id);
          const lead = toLead(p, tradeId);
          if (lead) leads.push(lead);
          if (leads.length >= limit) break outer;
        }

        pageToken = data.nextPageToken;
        if (!pageToken) break;
      }
    }
  }

  return dedupe(leads);
}
