/**
 * Tests für Anrufergebnisse, Warteschlange, Bewertungs-Signale und Kartenmathematik.
 */
import { test, before, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import fsp from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';

import { config } from '../src/config.js';
import { enrichLead, bewertungsKlasse, sterneKlasse, hatBewertungsDaten } from '../src/scoring.js';

// Eigener Datenordner, damit die Tests echte Leads nicht anfassen
config.dataDir = await fsp.mkdtemp(path.join(os.tmpdir(), 'leadradar-test-'));
const store = await import('../src/store.js');

const audit = (status) => ({ checkedAt: new Date().toISOString(), status });

// Jeder Test-Lead braucht eine eigene Nummer und einen eigenen Namen:
// die Speicherung führt Betriebe mit gleicher Telefonnummer bewusst zusammen
// (damit man niemanden zweimal anruft).
let zaehler = 0;
function lead(überschreiben = {}) {
  zaehler++;
  return enrichLead({
    id: 'test:' + zaehler,
    source: 'google',
    name: `Testbetrieb ${zaehler} AG`,
    trade: 'bau',
    address: { city: 'Zürich', canton: 'ZH' },
    phone: '+4144555' + String(1000 + zaehler),
    website: '',
    audit: audit('none'),
    ...überschreiben,
  });
}

before(async () => { await store.load(); });
beforeEach(() => {
  for (const l of store.allLeads()) store.deleteLead(l.id);
});

// ------------------------------------------------------- Anrufergebnisse

test('Combox setzt Wiedervorlage auf morgen und lässt den Lead in der Pipeline', () => {
  const { leads } = store.upsertLeads([lead()]);
  const { lead: nachher } = store.anrufErgebnis(leads[0].id, 'combox');

  assert.equal(nachher.status, 'anrufen', 'bleibt zum Anrufen vorgemerkt');
  assert.equal(nachher.anrufVersuche, 1);
  assert.equal(nachher.letztesErgebnis, 'combox');

  const morgen = new Date();
  morgen.setDate(morgen.getDate() + 1);
  assert.equal(new Date(nachher.followUpAt).toDateString(), morgen.toDateString());
  assert.match(nachher.activities[0].text, /Combox/);
});

test('Termin setzt den Status auf "termin" und hält die Notiz fest', () => {
  const { leads } = store.upsertLeads([lead()]);
  const { lead: nachher } = store.anrufErgebnis(leads[0].id, 'termin', {
    notiz: 'Mittwoch 14 Uhr',
  });

  assert.equal(nachher.status, 'termin');
  assert.equal(nachher.notes[0].text, 'Mittwoch 14 Uhr');
  assert.ok(nachher.erreichtAt, 'gilt als erreicht');
});

test('"Nicht mehr anrufen" sperrt den Lead dauerhaft', () => {
  const { leads } = store.upsertLeads([lead()]);
  const { lead: nachher } = store.anrufErgebnis(leads[0].id, 'nie_wieder');

  assert.equal(nachher.status, 'nichtstoeren');
  assert.equal(nachher.doNotContact, true);
  assert.equal(nachher.followUpAt, null);
  assert.equal(store.anrufWarteschlange().length, 0, 'taucht nie wieder in der Anrufliste auf');
});

test('Rückruf übernimmt das vereinbarte Datum', () => {
  const { leads } = store.upsertLeads([lead()]);
  const ziel = new Date(Date.now() + 5 * 86400000);
  const { lead: nachher } = store.anrufErgebnis(leads[0].id, 'rueckruf', {
    datum: ziel.toISOString(),
  });

  assert.equal(nachher.status, 'followup');
  assert.equal(new Date(nachher.followUpAt).toDateString(), ziel.toDateString());
});

test('nach drei erfolglosen Versuchen kommt der Hinweis auf einen anderen Kanal', () => {
  const { leads } = store.upsertLeads([lead()]);
  const id = leads[0].id;

  assert.equal(store.anrufErgebnis(id, 'combox').hinweis, undefined);
  assert.equal(store.anrufErgebnis(id, 'niemand').hinweis, undefined);
  const dritter = store.anrufErgebnis(id, 'combox');
  assert.match(dritter.hinweis || '', /nicht erreichbar/);
});

test('unbekanntes Ergebnis wird abgelehnt', () => {
  const { leads } = store.upsertLeads([lead()]);
  assert.ok(store.anrufErgebnis(leads[0].id, 'quatsch').error);
  assert.equal(store.anrufErgebnis('gibtsnicht', 'combox'), null);
});

// -------------------------------------------------------- Warteschlange

test('Warteschlange überspringt, was heute schon versucht wurde', () => {
  const { leads } = store.upsertLeads([lead(), lead()]);
  assert.equal(store.anrufWarteschlange().length, 2);

  store.anrufErgebnis(leads[0].id, 'combox');
  assert.equal(store.anrufWarteschlange().length, 1, 'heute versuchte fallen raus');
});

test('Warteschlange lässt Leads ohne Telefonnummer aus', () => {
  store.upsertLeads([lead({ phone: '' }), lead()]);
  assert.equal(store.anrufWarteschlange().length, 1);
});

test('fällige Wiedervorlagen stehen vor besseren Leads', () => {
  const stark = lead({ name: 'Stark AG' });
  const schwach = lead({ name: 'Schwach AG', audit: audit('ok'), googleReviews: 2, googleRating: 4 });
  const { leads } = store.upsertLeads([stark, schwach]);

  // Dem schwächeren Lead eine fällige Wiedervorlage geben
  const schwachId = leads.find((l) => l.name === 'Schwach AG').id;
  store.updateLead(schwachId, { followUpAt: new Date(Date.now() - 86400000).toISOString() });

  const reihe = store.anrufWarteschlange();
  assert.equal(reihe[0].name, 'Schwach AG', 'Zusagen einhalten geht vor Potenzial');
});

test('Warteschlange lässt sich nach Kanton und Score filtern', () => {
  store.upsertLeads([
    lead({ address: { city: 'Bern', canton: 'BE' } }),
    lead({ address: { city: 'Zürich', canton: 'ZH' } }),
  ]);
  assert.equal(store.anrufWarteschlange({ canton: 'BE' }).length, 1);
  assert.equal(store.anrufWarteschlange({ canton: 'alle' }).length, 2);
  assert.equal(store.anrufWarteschlange({ minScore: 200 }).length, 0);
});

test('Tagesstatistik zählt Anrufe, Combox und Termine', () => {
  const { leads } = store.upsertLeads([lead(), lead(), lead()]);
  store.anrufErgebnis(leads[0].id, 'combox');
  store.anrufErgebnis(leads[1].id, 'termin');
  store.anrufErgebnis(leads[2].id, 'kein_interesse');

  const heute = store.tagesStatistik();
  assert.equal(heute.anrufe, 3);
  assert.equal(heute.combox, 1);
  assert.equal(heute.termine, 1);
  assert.equal(heute.abgelehnt, 1);
  assert.ok(heute.quote > 0, 'Trefferquote wird berechnet');
});

// ------------------------------------------------- Bewertungen als Signal

test('fehlende Bewertungen erhöhen den Bedarf', () => {
  const ohne = lead({ audit: audit('ok'), googleReviews: 0, googleRating: null });
  const mit = lead({ audit: audit('ok'), googleReviews: 40, googleRating: 4.6 });
  assert.ok(
    ohne.reasons.some((r) => r.code === 'keine_bewertungen'),
    'wird als Grund genannt',
  );
  assert.ok(!mit.reasons.some((r) => r.code === 'keine_bewertungen'));
});

test('schlechte Sterne werden erkannt, gute nicht fälschlich bemängelt', () => {
  const schlecht = lead({ audit: audit('ok'), googleReviews: 20, googleRating: 2.9 });
  const gut = lead({ audit: audit('ok'), googleReviews: 20, googleRating: 4.7 });
  assert.ok(schlecht.reasons.some((r) => r.code === 'schlechte_bewertung'));
  assert.ok(!gut.reasons.some((r) => r.code === 'schlechte_bewertung'));
});

test('OpenStreetMap-Leads bekommen keine Bewertungs-Abzüge', () => {
  // OSM liefert keine Bewertungen. "0 Bewertungen" hiesse dort nur
  // "unbekannt" - dafür darf niemand Punkte bekommen.
  const osmLead = lead({ source: 'osm', googleReviews: null, googleRating: null, audit: audit('ok') });
  assert.equal(hatBewertungsDaten(osmLead), false);
  assert.ok(!osmLead.reasons.some((r) => /bewertung/i.test(r.code)));
  assert.equal(bewertungsKlasse(osmLead), 'unbekannt');
  assert.equal(sterneKlasse(osmLead), 'unbekannt');
});

test('Bewertungsklassen stimmen', () => {
  assert.equal(bewertungsKlasse(lead({ googleReviews: 0 })), 'keine');
  assert.equal(bewertungsKlasse(lead({ googleReviews: 8 })), 'wenige');
  assert.equal(bewertungsKlasse(lead({ googleReviews: 50 })), 'viele');
  assert.equal(sterneKlasse(lead({ googleReviews: 10, googleRating: 3.1 })), 'schlecht');
  assert.equal(sterneKlasse(lead({ googleReviews: 10, googleRating: 3.9 })), 'mittel');
  assert.equal(sterneKlasse(lead({ googleReviews: 10, googleRating: 4.8 })), 'gut');
});

test('ein Betrieb ohne Webseite bleibt trotz Top-Bewertungen ganz oben', () => {
  const ohneWebseite = lead({ audit: audit('none'), googleReviews: 60, googleRating: 4.9 });
  const schlechteSeite = lead({
    audit: { ...audit('ok'), hasViewport: false, https: false, copyrightYear: 2012 },
    googleReviews: 0, googleRating: null,
  });
  assert.ok(ohneWebseite.score > schlechteSeite.score,
    `ohne Webseite (${ohneWebseite.score}) muss vor schlechter Seite (${schlechteSeite.score}) liegen`);
});

// ------------------------------------------------------ Kartenmathematik

// Dieselbe Umrechnung wie in public/app.js. Die Karte lässt sich hier nicht
// mit echten Kacheln prüfen, die Mathematik dahinter aber sehr wohl.
const KACHEL = 256;
const lngZuX = (lng, z) => ((lng + 180) / 360) * Math.pow(2, z) * KACHEL;
const latZuY = (lat, z) => {
  const s = Math.sin((lat * Math.PI) / 180);
  return (0.5 - Math.log((1 + s) / (1 - s)) / (4 * Math.PI)) * Math.pow(2, z) * KACHEL;
};

test('Kachelkoordinaten treffen die richtige Stelle der Weltkarte', () => {
  // Nullpunkt liegt in der Mitte
  assert.equal(lngZuX(0, 0), 128);
  assert.ok(Math.abs(latZuY(0, 0) - 128) < 0.001);

  // Zürich muss auf Zoom 8 in Kachel 134/89 liegen (Standard-Kachelraster)
  assert.equal(Math.floor(lngZuX(8.5417, 8) / KACHEL), 134);
  assert.equal(Math.floor(latZuY(47.3769, 8) / KACHEL), 89);

  // Genf liegt westlich von Zürich, Basel nördlich von Lugano
  assert.ok(lngZuX(6.1432, 10) < lngZuX(8.5417, 10), 'Genf westlich von Zürich');
  assert.ok(latZuY(47.5596, 10) < latZuY(46.0037, 10), 'Basel nördlich von Lugano');
});

test('Rückrechnung der Kartenmitte trifft den Ausgangspunkt', () => {
  // Das braucht die Karte beim Verschieben mit dem Finger
  const z = 12;
  for (const [lat, lng] of [[47.3769, 8.5417], [46.2044, 6.1432], [46.0037, 8.9511]]) {
    const x = lngZuX(lng, z);
    const y = latZuY(lat, z);
    const zurueckLng = (x / (Math.pow(2, z) * KACHEL)) * 360 - 180;
    const anteil = 0.5 - y / (Math.pow(2, z) * KACHEL);
    const zurueckLat = (Math.atan(Math.sinh(anteil * 2 * Math.PI)) * 180) / Math.PI;
    assert.ok(Math.abs(zurueckLng - lng) < 0.0001, `Länge ${lng}`);
    assert.ok(Math.abs(zurueckLat - lat) < 0.0001, `Breite ${lat}`);
  }
});
