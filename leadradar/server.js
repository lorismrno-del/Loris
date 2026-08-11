/**
 * Lorino Leadradar - Server
 *
 * Startet mit:  node server.js
 * Danach im Browser:  http://127.0.0.1:3000
 */
import http from 'node:http';
import fs from 'node:fs';
import fsp from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { config, hasGoogle, ROOT } from './src/config.js';
import { TRADES, TRADE_BY_ID, GRUPPEN } from './src/trades.js';
import { resolvePlace, listPlaces, distanceKm, schweizRaster, alleKantone } from './src/geo.js';
import { searchOsm } from './src/providers/osm.js';
import { searchGoogle } from './src/providers/google.js';
import { searchDemo } from './src/providers/demo.js';
import { auditMany, auditWebsite } from './src/analyzer.js';
import { enrichLead } from './src/scoring.js';
import { callScript, emailTemplate, whatsappTemplate, smsTemplate, LEGAL_NOTES } from './src/outreach.js';
import { leadsToCsv } from './src/csv.js';
import * as store from './src/store.js';
import { loadSettings, saveSettings, getSettings, DEFAULT_SETTINGS } from './src/settings.js';
import { pushToWebhooks, toPayload } from './src/webhooks.js';
import {
  schutzAktiv, istAngemeldet, passwortStimmt, erstelleToken,
  setzeCookie, loescheCookie, zuVieleVersuche, versuchZaehlen,
} from './src/auth.js';
import { createJob, getJob, setStep, finishJob, failJob, stopJob, cancelJob } from './src/jobs.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PUBLIC_DIR = path.join(__dirname, 'public');

// ---------------------------------------------------------------- Hilfsmittel

function json(res, status, data) {
  const body = JSON.stringify(data);
  res.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'cache-control': 'no-store',
    'content-length': Buffer.byteLength(body),
  });
  res.end(body);
}

async function readBody(req, limit = 2_000_000) {
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > limit) throw new Error('Anfrage zu gross');
    chunks.push(chunk);
  }
  if (chunks.length === 0) return {};
  try {
    return JSON.parse(Buffer.concat(chunks).toString('utf8'));
  } catch {
    throw new Error('Ungültiges JSON im Request-Body');
  }
}

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.ico': 'image/x-icon',
  '.webmanifest': 'application/manifest+json',
};

async function serveStatic(res, urlPath) {
  const rel = urlPath === '/' ? '/index.html' : urlPath;
  // Pfad-Traversal verhindern
  const target = path.join(PUBLIC_DIR, path.normalize(rel).replace(/^(\.\.[/\\])+/, ''));
  if (!target.startsWith(PUBLIC_DIR)) {
    res.writeHead(403).end('Verboten');
    return;
  }
  try {
    const data = await fsp.readFile(target);
    res.writeHead(200, {
      'content-type': MIME[path.extname(target)] || 'application/octet-stream',
      'cache-control': 'no-cache',
    });
    res.end(data);
  } catch {
    res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' });
    res.end('Nicht gefunden');
  }
}

// ------------------------------------------------------------ Such-Verarbeitung

async function runSearch(job, params) {
  const {
    source = 'osm',
    trades = [],
    place = config.defaults.region,
    radiusKm,
    limit = 120,
    doAudit = true,
  } = params;

  const validTrades = trades.filter((t) => TRADE_BY_ID.has(t));
  if (validTrades.length === 0) throw new Error('Bitte mindestens eine Branche auswählen.');

  let center = { name: place, lat: null, lng: null, radiusKm: radiusKm || config.defaults.radiusKm };
  if (source !== 'demo') {
    setStep(job, `Ort "${place}" wird bestimmt …`);
    center = await resolvePlace(place, { radiusKm });
  }

  setStep(job, `Suche Betriebe (${source === 'google' ? 'Google Places' : source === 'demo' ? 'Demo-Daten' : 'OpenStreetMap'}) …`);

  let found = [];
  if (source === 'google') {
    found = await searchGoogle({
      trades: validTrades,
      place: center.name,
      lat: center.lat,
      lng: center.lng,
      radiusKm: center.radiusKm,
      limit,
    });
  } else if (source === 'demo') {
    found = searchDemo({ trades: validTrades, limit });
  } else {
    found = await searchOsm({
      trades: validTrades,
      lat: center.lat,
      lng: center.lng,
      radiusKm: center.radiusKm,
      limit,
    });
  }

  // Entfernung zum Suchmittelpunkt berechnen
  if (center.lat != null) {
    for (const lead of found) {
      lead.distanceKm = distanceKm(center, { lat: lead.lat, lng: lead.lng });
    }
  }

  setStep(job, `${found.length} Betriebe gefunden`, { total: found.length });

  if (found.length === 0) {
    return {
      added: 0,
      updated: 0,
      found: 0,
      hint:
        source === 'osm'
          ? 'OpenStreetMap kennt in diesem Gebiet keine passenden Einträge. Tipp: Radius erhöhen, andere Branche wählen – oder Google Places als Quelle nutzen (deutlich mehr Betriebe).'
          : 'Keine Treffer. Versuche einen grösseren Radius oder eine andere Branche.',
    };
  }

  // Bereits geprüfte Leads nicht erneut analysieren (spart Zeit)
  if (doAudit) {
    const needAudit = found.filter((l) => !l.audit);
    setStep(job, `Websites werden geprüft (0/${needAudit.length}) …`, {
      total: needAudit.length,
      done: 0,
    });

    const audits = await auditMany(needAudit, (done, total) => {
      job.done = done;
      job.total = total;
      job.step = `Websites werden geprüft (${done}/${total}) …`;
    });
    needAudit.forEach((lead, i) => {
      lead.audit = audits[i];
    });
  }

  setStep(job, 'Bewertung wird berechnet …');
  for (const lead of found) enrichLead(lead);

  const { added, updated } = store.upsertLeads(found);
  store.recordSearch({ source, trades: validTrades, place: center.name, radiusKm: center.radiusKm, found: found.length, added });
  await Promise.all([store.saveLeads(), store.saveState()]);

  return { added, updated, found: found.length, place: center.name, radiusKm: center.radiusKm };
}

/**
 * Schweiz-weiter Scan: sucht Ort für Ort das ganze Raster ab.
 *
 * Läuft je nach Umfang eine Weile - deshalb jederzeit abbrechbar, und was
 * bis dahin gefunden wurde, ist bereits gespeichert.
 */
async function runSchweizScan(job, params) {
  const { source = 'osm', trades = [], kantone = [], limitProOrt = 60, doAudit = true } = params;

  const validTrades = trades.filter((t) => TRADE_BY_ID.has(t));
  if (validTrades.length === 0) throw new Error('Bitte mindestens eine Branche auswählen.');

  const orte = schweizRaster({ kantone });
  if (orte.length === 0) throw new Error('Keine Orte im gewählten Gebiet.');

  let gesamtNeu = 0;
  let gesamtAktualisiert = 0;
  let gesamtGefunden = 0;
  const fehler = [];
  job.total = orte.length;

  for (let i = 0; i < orte.length; i++) {
    if (job.abbruch) {
      const teilergebnis = { added: gesamtNeu, updated: gesamtAktualisiert, found: gesamtGefunden, orte: i, orteTotal: orte.length, fehler };
      await Promise.all([store.saveLeads(), store.saveState()]);
      cancelJob(job, teilergebnis);
      return teilergebnis;
    }

    const ort = orte[i];
    job.done = i;
    job.step = `${ort.name} (${ort.canton}) – Ort ${i + 1} von ${orte.length} · ${gesamtNeu} neue Leads`;

    try {
      let treffer = [];
      if (source === 'google') {
        treffer = await searchGoogle({
          trades: validTrades, place: ort.name, lat: ort.lat, lng: ort.lng,
          radiusKm: ort.radiusKm, limit: limitProOrt,
          // Beim Flächenscan nur die erste Seite - sonst explodieren die Kosten
          maxPages: 1,
        });
      } else if (source === 'demo') {
        treffer = searchDemo({ trades: validTrades, limit: limitProOrt });
      } else {
        treffer = await searchOsm({
          trades: validTrades, lat: ort.lat, lng: ort.lng,
          radiusKm: ort.radiusKm, limit: limitProOrt,
        });
        // Overpass ist ein Gemeinschaftsdienst - zwischen den Orten kurz warten
        await new Promise((r) => setTimeout(r, 1200));
      }

      gesamtGefunden += treffer.length;

      // Nur Betriebe prüfen, die wir noch nicht kennen
      const neue = treffer.filter((l) => !store.getLead(l.id) && !l.audit);
      if (doAudit && neue.length) {
        job.step = `${ort.name}: ${neue.length} Webseiten werden geprüft …`;
        const audits = await auditMany(neue);
        neue.forEach((lead, k) => { lead.audit = audits[k]; });
      }

      for (const lead of treffer) enrichLead(lead);
      const { added, updated } = store.upsertLeads(treffer);
      gesamtNeu += added;
      gesamtAktualisiert += updated;

      // Nach jedem Ort speichern - ein Abbruch kostet dann höchstens einen Ort
      await store.saveLeads();
    } catch (err) {
      fehler.push(`${ort.name}: ${err.message}`);
      // Ein kaputter Ort darf den ganzen Scan nicht stoppen
    }
  }

  job.done = orte.length;
  store.recordSearch({
    source, trades: validTrades, place: `Schweiz-Scan (${orte.length} Orte)`,
    found: gesamtGefunden, added: gesamtNeu,
  });
  await Promise.all([store.saveLeads(), store.saveState()]);

  return {
    added: gesamtNeu, updated: gesamtAktualisiert, found: gesamtGefunden,
    orte: orte.length, orteTotal: orte.length, fehler,
  };
}

// ------------------------------------------------------------------- Filterung

function filterLeads(query) {
  let leads = store.allLeads();

  const q = (query.get('q') || '').trim().toLowerCase();
  if (q) {
    leads = leads.filter((l) =>
      [l.name, l.address?.city, l.address?.street, l.phone, l.email, l.website, l.contactName]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
        .includes(q),
    );
  }

  const status = query.get('status');
  if (status && status !== 'alle') leads = leads.filter((l) => l.status === status);

  const trade = query.get('trade');
  if (trade && trade !== 'alle') leads = leads.filter((l) => l.trade === trade);

  const tier = query.get('tier');
  if (tier && tier !== 'alle') leads = leads.filter((l) => l.tier?.key === tier);

  const websiteStatus = query.get('websiteStatus');
  if (websiteStatus && websiteStatus !== 'alle') {
    if (websiteStatus === 'problem') {
      leads = leads.filter((l) => l.audit && l.audit.status !== 'ok');
    } else {
      leads = leads.filter((l) => l.audit?.status === websiteStatus);
    }
  }

  if (query.get('onlyPhone') === '1') leads = leads.filter((l) => l.phone || l.customPhone);
  if (query.get('onlyEmail') === '1') leads = leads.filter((l) => l.email || l.customEmail);
  if (query.get('onlyStarred') === '1') leads = leads.filter((l) => l.starred);
  if (query.get('hideDone') === '1') {
    leads = leads.filter((l) => !['kunde', 'abgelehnt', 'nichtstoeren'].includes(l.status));
  }

  const minScore = Number(query.get('minScore'));
  if (Number.isFinite(minScore) && minScore > 0) leads = leads.filter((l) => (l.score ?? 0) >= minScore);

  const city = query.get('city');
  if (city && city !== 'alle') leads = leads.filter((l) => l.address?.city === city);

  const canton = query.get('canton');
  if (canton && canton !== 'alle') leads = leads.filter((l) => l.address?.canton === canton);

  // Google-Präsenz: genau das, was den Aufhänger fürs Gespräch liefert
  const reviews = query.get('reviews');
  if (reviews && reviews !== 'alle') leads = leads.filter((l) => l.bewertungsKlasse === reviews);

  const rating = query.get('rating');
  if (rating && rating !== 'alle') leads = leads.filter((l) => l.sterneKlasse === rating);

  const sort = query.get('sort') || 'score';
  const cmp = {
    score: (a, b) => (b.score ?? 0) - (a.score ?? 0),
    name: (a, b) => String(a.name).localeCompare(String(b.name), 'de'),
    city: (a, b) => String(a.address?.city || '').localeCompare(String(b.address?.city || ''), 'de'),
    reviews: (a, b) => (b.googleReviews ?? 0) - (a.googleReviews ?? 0),
    distance: (a, b) => (a.distanceKm ?? 9e9) - (b.distanceKm ?? 9e9),
    newest: (a, b) => String(b.createdAt).localeCompare(String(a.createdAt)),
    followup: (a, b) => String(a.followUpAt || '9999').localeCompare(String(b.followUpAt || '9999')),
  }[sort] || ((a, b) => (b.score ?? 0) - (a.score ?? 0));

  return leads.sort(cmp);
}

// ---------------------------------------------------------------------- Router

async function handleApi(req, res, url) {
  const { pathname } = url;
  const method = req.method;

  // ---- Anmeldung
  if (pathname === '/api/login' && method === 'POST') {
    if (!schutzAktiv()) return json(res, 200, { ok: true, hinweis: 'Kein Passwort gesetzt' });

    const ip = clientIp(req);
    if (zuVieleVersuche(ip)) {
      return json(res, 429, { error: 'Zu viele Fehlversuche. Bitte 15 Minuten warten.' });
    }

    const { password } = await readBody(req);
    const richtig = passwortStimmt(password);
    versuchZaehlen(ip, richtig);

    if (!richtig) return json(res, 401, { error: 'Passwort stimmt nicht.' });

    setzeCookie(res, erstelleToken(), istHttps(req));
    return json(res, 200, { ok: true });
  }

  if (pathname === '/api/logout' && method === 'POST') {
    loescheCookie(res);
    return json(res, 200, { ok: true });
  }

  // Ab hier: alles geschützt
  if (!istAngemeldet(req)) {
    return json(res, 401, { error: 'Nicht angemeldet', login: true });
  }

  // ---- Stammdaten fürs UI
  if (pathname === '/api/meta' && method === 'GET') {
    return json(res, 200, {
      agency: config.agency,
      settings: getSettings(),
      schutzAktiv: schutzAktiv(),
      trades: TRADES,
      gruppen: GRUPPEN,
      statuses: store.STATUSES,
      anrufErgebnisse: store.ANRUF_ERGEBNISSE,
      kantone: alleKantone(),
      places: listPlaces(),
      sources: [
        { id: 'osm', label: 'OpenStreetMap (gratis)', available: true,
          note: 'Kein Key nötig. Gute Abdeckung bei Handwerk, aber nicht jeder Betrieb ist erfasst.' },
        { id: 'google', label: 'Google Places', available: hasGoogle(),
          note: hasGoogle() ? 'Beste Abdeckung inkl. Bewertungen.' : 'GOOGLE_PLACES_API_KEY in der .env fehlt.' },
        { id: 'demo', label: 'Demo-Daten (zum Ausprobieren)', available: true,
          note: 'Erfundene Betriebe. Nicht anrufen!' },
      ],
      legal: LEGAL_NOTES,
      defaults: config.defaults,
    });
  }

  // ---- Kennzahlen
  if (pathname === '/api/stats' && method === 'GET') {
    return json(res, 200, store.stats());
  }

  // ---- Suche starten
  if (pathname === '/api/search' && method === 'POST') {
    const params = await readBody(req);
    const job = createJob('Suche');
    runSearch(job, params)
      .then((result) => finishJob(job, result))
      .catch((err) => {
        console.error('[suche]', err);
        failJob(job, err);
      });
    return json(res, 202, { jobId: job.id });
  }

  // ---- Schweiz-weiter Scan
  if (pathname === '/api/scan-schweiz' && method === 'POST') {
    const params = await readBody(req);
    const job = createJob('Schweiz-Scan');
    runSchweizScan(job, params)
      .then((result) => { if (!job.abgebrochen) finishJob(job, result); })
      .catch((err) => {
        console.error('[schweiz-scan]', err);
        failJob(job, err);
      });
    return json(res, 202, { jobId: job.id });
  }

  // ---- Umfang eines Scans abschätzen (bevor er Geld kostet)
  if (pathname === '/api/scan-schweiz/vorschau' && method === 'POST') {
    const { kantone = [], trades = [], source = 'osm' } = await readBody(req);
    const orte = schweizRaster({ kantone });
    const anzahlBranchen = trades.filter((t) => TRADE_BY_ID.has(t)).length || 1;
    // Google: ein Aufruf je Suchbegriff und Ort; OSM: ein Aufruf je Ort
    const suchbegriffe = trades
      .map((t) => TRADE_BY_ID.get(t)?.google.length || 0)
      .reduce((a, b) => a + b, 0) || anzahlBranchen;

    const anfragen = source === 'google' ? orte.length * suchbegriffe : orte.length;
    // Erfahrungswert: OSM ca. 4 s pro Ort inkl. Pause, Google ca. 1.5 s je Anfrage
    const sekunden = source === 'google' ? anfragen * 1.5 : orte.length * 4;

    return json(res, 200, {
      orte: orte.length,
      kantone: [...new Set(orte.map((o) => o.canton))].length,
      anfragen,
      minutenGeschaetzt: Math.ceil(sekunden / 60),
      kostenHinweis: source === 'google'
        ? `Rund ${anfragen} Google-Anfragen. Prüfe dein Guthaben in der Google Cloud Console, bevor du startest.`
        : 'OpenStreetMap ist gratis. Zwischen den Orten wird bewusst kurz gewartet, damit der Gemeinschaftsdienst nicht überlastet wird.',
    });
  }

  // ---- Job-Fortschritt
  const jobMatch = /^\/api\/jobs\/([\w]+)$/.exec(pathname);
  if (jobMatch && method === 'GET') {
    const job = getJob(jobMatch[1]);
    if (!job) return json(res, 404, { error: 'Job nicht gefunden' });
    return json(res, 200, {
      id: job.id, state: job.state, step: job.step, done: job.done,
      total: job.total, result: job.result, error: job.error,
      abgebrochen: job.abgebrochen || false,
    });
  }

  if (jobMatch && method === 'DELETE') {
    const ok = stopJob(jobMatch[1]);
    return json(res, ok ? 200 : 404, { gestoppt: ok });
  }

  // ---- Leads auflisten
  if (pathname === '/api/leads' && method === 'GET') {
    const leads = filterLeads(url.searchParams);
    const page = Math.max(1, Number(url.searchParams.get('page')) || 1);
    const perPage = Math.min(500, Math.max(10, Number(url.searchParams.get('perPage')) || 100));
    const alle = store.allLeads();
    const cities = [...new Set(alle.map((l) => l.address?.city).filter(Boolean))].sort(
      (a, b) => a.localeCompare(b, 'de'),
    );
    const cantons = [...new Set(alle.map((l) => l.address?.canton).filter(Boolean))].sort();
    return json(res, 200, {
      total: leads.length,
      page,
      perPage,
      cities,
      cantons,
      leads: leads.slice((page - 1) * perPage, page * perPage),
    });
  }

  // ---- Punkte für die Kartenansicht (schlank gehalten, alle auf einmal)
  if (pathname === '/api/karte' && method === 'GET') {
    const leads = filterLeads(url.searchParams).filter((l) => l.lat != null && l.lng != null);
    return json(res, 200, {
      total: leads.length,
      punkte: leads.slice(0, 3000).map((l) => ({
        id: l.id,
        name: l.name,
        lat: l.lat,
        lng: l.lng,
        score: l.score ?? 0,
        farbe: l.tier?.color || '#64748b',
        ort: l.address?.city || '',
        problem: l.headline || '',
        telefon: l.customPhone || l.phone || '',
      })),
    });
  }

  // ---- Einzelner Lead inkl. Gesprächsleitfaden
  const leadMatch = /^\/api\/leads\/([^/]+)$/.exec(pathname);
  if (leadMatch && method === 'GET') {
    const lead = store.getLead(decodeURIComponent(leadMatch[1]));
    if (!lead) return json(res, 404, { error: 'Lead nicht gefunden' });
    return json(res, 200, {
      lead,
      script: callScript(lead),
      email: emailTemplate(lead),
      whatsapp: whatsappTemplate(lead),
      sms: smsTemplate(lead),
    });
  }

  if (leadMatch && method === 'PATCH') {
    const patch = await readBody(req);
    const updated = store.updateLead(decodeURIComponent(leadMatch[1]), patch);
    if (!updated) return json(res, 404, { error: 'Lead nicht gefunden' });
    if (updated.error) return json(res, 400, updated);
    await store.saveLeads();
    return json(res, 200, { lead: updated });
  }

  if (leadMatch && method === 'DELETE') {
    const ok = store.deleteLead(decodeURIComponent(leadMatch[1]));
    if (ok) await store.saveLeads();
    return json(res, ok ? 200 : 404, { ok });
  }

  // ---- Notiz hinzufügen
  const noteMatch = /^\/api\/leads\/([^/]+)\/notes$/.exec(pathname);
  if (noteMatch && method === 'POST') {
    const { text } = await readBody(req);
    if (!String(text || '').trim()) return json(res, 400, { error: 'Notiz ist leer' });
    const note = store.addNote(decodeURIComponent(noteMatch[1]), text);
    if (!note) return json(res, 404, { error: 'Lead nicht gefunden' });
    await store.saveLeads();
    return json(res, 200, { note });
  }

  // ---- Aktivität protokollieren (Anruf, E-Mail, WhatsApp)
  const actMatch = /^\/api\/leads\/([^/]+)\/activity$/.exec(pathname);
  if (actMatch && method === 'POST') {
    const { type, text } = await readBody(req);
    const lead = store.getLead(decodeURIComponent(actMatch[1]));
    if (!lead) return json(res, 404, { error: 'Lead nicht gefunden' });
    const allowed = ['call', 'call_noanswer', 'email', 'whatsapp', 'note', 'meeting'];
    if (!allowed.includes(type)) return json(res, 400, { error: 'Unbekannter Aktivitätstyp' });

    const labels = {
      call: '📞 Angerufen – erreicht',
      call_noanswer: '📞 Angerufen – nicht erreicht',
      email: '✉️ E-Mail geschickt',
      whatsapp: '💬 WhatsApp geschickt',
      meeting: '🤝 Termin durchgeführt',
      note: '📝 Notiz',
    };
    const activity = store.addActivity(lead, type, text || labels[type]);

    // Status automatisch nachziehen
    if (lead.status === 'neu' || lead.status === 'anrufen') {
      if (type === 'call' || type === 'email' || type === 'whatsapp') {
        lead.status = 'kontaktiert';
      }
    }
    if (type === 'meeting') lead.status = 'termin';

    lead.lastContactAt = new Date().toISOString();
    await store.saveLeads();
    return json(res, 200, { activity, lead });
  }

  // ---- Anrufergebnis festhalten (Combox, Termin, kein Interesse …)
  const ergebnisMatch = /^\/api\/leads\/([^/]+)\/anruf$/.exec(pathname);
  if (ergebnisMatch && method === 'POST') {
    const { ergebnis, notiz, datum } = await readBody(req);
    const antwort = store.anrufErgebnis(decodeURIComponent(ergebnisMatch[1]), ergebnis, { notiz, datum });
    if (!antwort) return json(res, 404, { error: 'Lead nicht gefunden' });
    if (antwort.error) return json(res, 400, antwort);
    await store.saveLeads();
    return json(res, 200, antwort);
  }

  // ---- Anruf-Warteschlange: wer ist als Nächstes dran?
  if (pathname === '/api/warteschlange' && method === 'GET') {
    const leads = store.anrufWarteschlange({
      trade: url.searchParams.get('trade'),
      city: url.searchParams.get('city'),
      canton: url.searchParams.get('canton'),
      minScore: Number(url.searchParams.get('minScore')) || 0,
    });
    return json(res, 200, {
      total: leads.length,
      leads: leads.slice(0, 200),
      heute: store.tagesStatistik(),
    });
  }

  // ---- Website erneut prüfen
  const reauditMatch = /^\/api\/leads\/([^/]+)\/reaudit$/.exec(pathname);
  if (reauditMatch && method === 'POST') {
    const lead = store.getLead(decodeURIComponent(reauditMatch[1]));
    if (!lead) return json(res, 404, { error: 'Lead nicht gefunden' });
    lead.audit = await auditWebsite(lead);
    enrichLead(lead);
    lead.updatedAt = new Date().toISOString();
    await store.saveLeads();
    return json(res, 200, { lead });
  }

  // ---- Lead manuell erfassen
  if (pathname === '/api/leads' && method === 'POST') {
    const body = await readBody(req);
    if (!String(body.name || '').trim()) return json(res, 400, { error: 'Firmenname fehlt' });

    const lead = {
      id: 'manuell:' + Date.now().toString(36),
      source: 'manuell',
      name: String(body.name).trim(),
      trade: TRADE_BY_ID.has(body.trade) ? body.trade : 'bau',
      address: {
        street: body.street || '', zip: body.zip || '',
        city: body.city || '', canton: body.canton || '', country: 'CH',
      },
      phone: body.phone || '',
      email: body.email || '',
      website: body.website || '',
      socials: {},
      googleRating: null,
      googleReviews: null,
      lastActivityAt: null,
    };
    lead.audit = await auditWebsite(lead);
    enrichLead(lead);
    const { leads } = store.upsertLeads([lead]);
    await store.saveLeads();
    return json(res, 200, { lead: leads[0] });
  }

  // ---- Einstellungen (Agentur-Profil, Verkaufsargumente, Weitergabe)
  if (pathname === '/api/settings' && method === 'GET') {
    return json(res, 200, { settings: getSettings(), defaults: DEFAULT_SETTINGS });
  }
  if (pathname === '/api/settings' && method === 'PUT') {
    const patch = await readBody(req);
    const saved = await saveSettings(patch);
    return json(res, 200, { settings: saved });
  }

  // ---- Lead an ein anderes Tool übergeben (Vertra / Agentur-OS / eigenes)
  const pushMatch = /^\/api\/leads\/([^/]+)\/push$/.exec(pathname);
  if (pushMatch && method === 'POST') {
    const lead = store.getLead(decodeURIComponent(pushMatch[1]));
    if (!lead) return json(res, 404, { error: 'Lead nicht gefunden' });
    const body = await readBody(req).catch(() => ({}));
    const result = await pushToWebhooks(lead, { only: body.label });
    if (result.sent > 0) {
      store.addActivity(lead, 'note', `📤 An ${result.results.filter((r) => r.ok).map((r) => r.label).join(', ')} übergeben`);
      await store.saveLeads();
    }
    return json(res, 200, result);
  }

  // ---- Lead als JSON (zum Kopieren in ein anderes Tool)
  const payloadMatch = /^\/api\/leads\/([^/]+)\/payload$/.exec(pathname);
  if (payloadMatch && method === 'GET') {
    const lead = store.getLead(decodeURIComponent(payloadMatch[1]));
    if (!lead) return json(res, 404, { error: 'Lead nicht gefunden' });
    return json(res, 200, toPayload(lead));
  }

  // ---- CSV-Export
  if (pathname === '/api/export.csv' && method === 'GET') {
    const leads = filterLeads(url.searchParams);
    const csv = leadsToCsv(leads);
    const stamp = new Date().toISOString().slice(0, 10);
    res.writeHead(200, {
      'content-type': 'text/csv; charset=utf-8',
      'content-disposition': `attachment; filename="leadradar-${stamp}.csv"`,
    });
    return res.end(csv);
  }

  return json(res, 404, { error: 'Unbekannter API-Endpunkt: ' + pathname });
}

// ----------------------------------------------------------------------- Start

/** Dateien, die auch ohne Anmeldung ausgeliefert werden (Login-Seite + Zubehör). */
const OEFFENTLICH = new Set([
  '/login.html', '/styles.css', '/manifest.webmanifest',
  '/icons/icon-192.png', '/icons/icon-512.png', '/icons/apple-touch-icon.png',
]);

function clientIp(req) {
  return req.socket?.remoteAddress || 'unbekannt';
}

/** Läuft die Verbindung über HTTPS? Wichtig fürs Secure-Cookie hinter einem Proxy. */
function istHttps(req) {
  return (
    req.socket?.encrypted === true ||
    String(req.headers['x-forwarded-proto'] || '').split(',')[0].trim() === 'https'
  );
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);

  try {
    if (url.pathname.startsWith('/api/')) {
      await handleApi(req, res, url);
    } else if (schutzAktiv() && !istAngemeldet(req) && !OEFFENTLICH.has(url.pathname)) {
      // Nicht angemeldet: Login-Seite ausliefern, egal welche Adresse aufgerufen wurde
      await serveStatic(res, '/login.html');
    } else {
      await serveStatic(res, url.pathname);
    }
  } catch (err) {
    console.error('[server]', err);
    if (!res.headersSent) json(res, 500, { error: err?.message || 'Interner Fehler' });
    else res.end();
  }
});

await loadSettings();
await store.load();

/** Alle IPv4-Adressen dieses Rechners im lokalen Netz (für den Handy-Zugriff). */
function netzwerkAdressen() {
  const gefunden = [];
  for (const eintraege of Object.values(os.networkInterfaces())) {
    for (const e of eintraege || []) {
      if (e.family === 'IPv4' && !e.internal) gefunden.push(e.address);
    }
  }
  return gefunden;
}

server.listen(config.port, config.host, () => {
  const n = store.allLeads().length;
  const oeffentlich = config.host === '0.0.0.0' || config.host === '::';

  console.log('');
  console.log('  ╭──────────────────────────────────────────────╮');
  console.log('  │   Lorino Leadradar läuft                     │');
  console.log('  ╰──────────────────────────────────────────────╯');
  console.log(`  Auf diesem Rechner:  http://127.0.0.1:${config.port}`);

  if (oeffentlich) {
    const adressen = netzwerkAdressen();
    if (adressen.length) {
      console.log('');
      console.log('  📱 Auf dem Handy (gleiches WLAN) – diese Adresse eintippen:');
      for (const ip of adressen) console.log(`      http://${ip}:${config.port}`);
    } else {
      console.log('  ⚠️  Keine Netzwerkadresse gefunden – ist der Rechner im WLAN?');
    }
  } else {
    console.log('');
    console.log('  ℹ️  Nur auf diesem Rechner erreichbar.');
    console.log('      Für den Zugriff vom Handy: APP_PASSWORD in die .env');
    console.log('      eintragen und dann starten mit   npm run handy');
  }

  console.log('');
  console.log(`  Passwortschutz:  ${schutzAktiv() ? 'aktiv ✓' : 'AUS'}`);
  console.log(`  Gespeicherte Leads:  ${n}`);
  console.log(`  Google Places:  ${hasGoogle() ? 'aktiv' : 'nicht konfiguriert (OpenStreetMap wird genutzt)'}`);

  if (oeffentlich && !schutzAktiv()) {
    console.log('');
    console.log('  ╭──────────────────────────────────────────────────────────╮');
    console.log('  │  ⚠️  WARNUNG: kein Passwort gesetzt!                      │');
    console.log('  │  Jeder im gleichen WLAN sieht deine Leads und Notizen.   │');
    console.log('  │  Beenden und mit APP_PASSWORD=… neu starten.             │');
    console.log('  ╰──────────────────────────────────────────────────────────╯');
  }

  console.log('');
  console.log('  Beenden mit Strg + C');
  console.log('');
});

for (const sig of ['SIGINT', 'SIGTERM']) {
  process.on(sig, async () => {
    console.log('\n  Speichere und beende …');
    try {
      await store.saveLeads();
      await store.saveState();
    } catch { /* egal */ }
    process.exit(0);
  });
}
