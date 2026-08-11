/**
 * Tests für Website-Analyse und Bewertung.
 * Ausführen mit:  npm test
 */
import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';

import { startFixtureServer } from './fixtures.js';
import { auditWebsite, findCopyrightYear } from '../src/analyzer.js';
import { enrichLead, tierFor } from '../src/scoring.js';
import { normalizePhone, normalizeEmail, normalizeUrl, dedupe } from '../src/providers/osm.js';
import { leadsToCsv } from '../src/csv.js';

const BASE = 'http://127.0.0.1:3199';
let server;

before(async () => { server = await startFixtureServer(3199); });
after(() => server?.close());

const leadWith = (website, extra = {}) => ({ name: 'Testbetrieb', trade: 'bau', website, ...extra });

// ------------------------------------------------------------------- Analyse

test('erkennt eine veraltete Seite von 2013 mit allen Schwachstellen', async () => {
  const a = await auditWebsite(leadWith(BASE + '/alt'));
  assert.equal(a.status, 'ok');
  assert.equal(a.hasViewport, false, 'kein Viewport → nicht mobiltauglich');
  assert.equal(a.copyrightYear, 2013);
  assert.equal(a.hasImpressum, false);
  assert.equal(a.hasContactForm, false);
  assert.ok(a.techFlags.some((f) => /Tabellen-Layout/.test(f)), 'Tabellen-Layout erkannt');
  assert.ok(a.techFlags.some((f) => /font/i.test(f)), '<font>-Tags erkannt');
  assert.ok(a.techFlags.some((f) => /jQuery/.test(f)), 'altes jQuery erkannt');
  assert.ok(a.techFlags.some((f) => /Internet Explorer/.test(f)));
  assert.deepEqual(a.emailsFound, ['info@schreinerei-muster.example']);
});

test('stuft eine gepflegte moderne Seite als unauffällig ein', async () => {
  const a = await auditWebsite(leadWith(BASE + '/modern'));
  assert.equal(a.status, 'ok');
  assert.equal(a.hasViewport, true);
  assert.equal(a.hasImpressum, true);
  assert.equal(a.hasContactForm, true);
  assert.equal(a.copyrightYear, new Date().getFullYear());
  assert.ok(a.title.includes('Muster Gartenbau'));
  assert.ok(a.description.length > 10);
  assert.ok(a.socialsFound.some((s) => s.includes('instagram')));
});

test('erkennt eine geparkte Domain', async () => {
  const a = await auditWebsite(leadWith(BASE + '/parkiert'));
  assert.equal(a.status, 'parked');
});

test('erkennt eine tote Seite (404)', async () => {
  const a = await auditWebsite(leadWith(BASE + '/tot'));
  assert.equal(a.status, 'dead');
  assert.equal(a.httpStatus, 404);
  assert.match(a.summary, /404/);
});

test('erkennt Weiterleitung auf Facebook als "nur Social Media"', async () => {
  const a = await auditWebsite(leadWith(BASE + '/nurfacebook'));
  assert.equal(a.status, 'social_only');
});

test('erkennt fehlende Website', async () => {
  const a = await auditWebsite(leadWith(''));
  assert.equal(a.status, 'none');
});

test('erkennt Social-Media-Link, der als Website eingetragen ist', async () => {
  const a = await auditWebsite(leadWith('https://www.facebook.com/musterbetrieb'));
  assert.equal(a.status, 'social_only');
});

test('erkennt local.ch-Eintrag als reinen Verzeichniseintrag', async () => {
  const a = await auditWebsite(leadWith('https://www.local.ch/de/d/musterbetrieb'));
  assert.equal(a.status, 'directory_only');
});

test('findet verschleierte E-Mail auf der Kontaktseite', async () => {
  const a = await auditWebsite(leadWith(BASE + '/versteckt'));
  assert.equal(a.status, 'ok');
  assert.deepEqual(a.emailsFound, ['buero@malerei-beispiel.example']);
  assert.equal(a.hasImpressum, true, 'Impressum auf der Unterseite gefunden');
});

test('Copyright-Jahr wird aus verschiedenen Schreibweisen gelesen', () => {
  assert.equal(findCopyrightYear('<p>&copy; 2018 Firma</p>'), 2018);
  assert.equal(findCopyrightYear('<p>Copyright 2009-2016 Firma</p>'), 2016);
  assert.equal(findCopyrightYear('<p>Stand: 03.05.2011</p>'), 2011);
  assert.equal(findCopyrightYear('<p>Wir bauen seit 1978</p>'), null, 'Jahreszahl im Text zählt nicht');
});

// ---------------------------------------------------------------- Bewertung

test('Betrieb ohne Website steht über Betrieb mit schlechter Website', async () => {
  const ohne = enrichLead({
    ...leadWith(''), googleRating: 4.5, googleReviews: 20, phone: '+41445550000',
    audit: await auditWebsite(leadWith('')),
  });
  const schlecht = enrichLead({
    ...leadWith(BASE + '/alt'), googleRating: 4.5, googleReviews: 20, phone: '+41445550000',
    audit: await auditWebsite(leadWith(BASE + '/alt')),
  });

  assert.ok(ohne.score > schlecht.score,
    `ohne Website (${ohne.score}) muss über schlechter Website (${schlecht.score}) liegen`);
  assert.equal(ohne.tier.key, 'hot');
  assert.match(ohne.headline, /keine Webseite/i);
});

test('gepflegte Seite bekommt niedrigen Score', async () => {
  const audit = await auditWebsite(leadWith(BASE + '/modern'));
  audit.https = true; // Der Testserver läuft über http - im Echtbetrieb wäre das https
  const lead = enrichLead({
    ...leadWith(BASE + '/modern'), googleRating: 4.8, googleReviews: 50, phone: '+41445550000',
    audit,
  });
  assert.ok(lead.score < 45, `sollte niedrig sein, war ${lead.score}`);
  assert.match(lead.headline, /aktuell/i);
});

test('mehr Bewertungen = attraktiverer Lead bei gleichem Problem', async () => {
  const audit = await auditWebsite(leadWith(''));
  const gross = enrichLead({ ...leadWith(''), googleRating: 4.8, googleReviews: 60, phone: '+4144', audit });
  const klein = enrichLead({ ...leadWith(''), googleRating: 4.8, googleReviews: 2, phone: '+4144', audit });
  assert.ok(gross.score > klein.score);
});

test('geschlossener Betrieb wird stark abgewertet', async () => {
  const audit = await auditWebsite(leadWith(''));
  const zu = enrichLead({ ...leadWith(''), businessStatus: 'CLOSED_PERMANENTLY', audit });
  const offen = enrichLead({ ...leadWith(''), businessStatus: 'OPERATIONAL', audit });
  assert.ok(zu.score < offen.score);
});

test('Einstufungen decken den ganzen Bereich ab', () => {
  assert.equal(tierFor(90).key, 'hot');
  assert.equal(tierFor(60).key, 'warm');
  assert.equal(tierFor(40).key, 'medium');
  assert.equal(tierFor(20).key, 'low');
  assert.equal(tierFor(5).key, 'none');
});

// --------------------------------------------------------------- Normalisierung

test('Telefonnummern werden ins internationale Format gebracht', () => {
  assert.equal(normalizePhone('044 555 00 00'), '+41445550000');
  assert.equal(normalizePhone('+41 44 555 00 00'), '+41445550000');
  assert.equal(normalizePhone('0041 44 555 00 00'), '+41445550000');
  assert.equal(normalizePhone('044 555 00 00; 079 555 11 11'), '+41445550000', 'erste Nummer');
  assert.equal(normalizePhone(''), '');
});

test('E-Mails und URLs werden bereinigt', () => {
  assert.equal(normalizeEmail('mailto:Info@Firma.CH'), 'info@firma.ch');
  assert.equal(normalizeEmail('kein-email'), '');
  assert.equal(normalizeUrl('firma.ch'), 'https://firma.ch');
  assert.equal(normalizeUrl('http://firma.ch/'), 'http://firma.ch');
  assert.equal(normalizeUrl('unsinn'), '');
});

test('Doppelte Betriebe werden zusammengeführt und Lücken gefüllt', () => {
  const merged = dedupe([
    { id: 'a', name: 'Muster AG', address: { city: 'Bern' }, phone: '+41310000000', website: '' },
    { id: 'b', name: 'Muster AG', address: { city: 'Bern' }, phone: '', website: 'https://muster.ch' },
  ]);
  assert.equal(merged.length, 1);
  assert.equal(merged[0].phone, '+41310000000');
  assert.equal(merged[0].website, 'https://muster.ch');
});

// --------------------------------------------------------------------- Export

test('CSV enthält Kopfzeile, BOM und maskiert Formeln', () => {
  const csv = leadsToCsv([{
    name: '=SUM(A1)', trade: 'bau', phone: '+41440000000', status: 'neu',
    address: { city: 'Zürich' }, notes: [], score: 80,
  }]);
  assert.ok(csv.startsWith('﻿'), 'BOM für Excel');
  assert.ok(csv.includes('"Firma";"Branche"'));
  assert.ok(csv.includes(`"'=SUM(A1)"`), 'Formel wird entschärft');
});
