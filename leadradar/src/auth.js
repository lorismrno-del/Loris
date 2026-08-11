/**
 * Passwortschutz.
 *
 * Sobald die App nicht mehr nur auf dem eigenen Rechner läuft (Handy im WLAN,
 * oder gar im Internet), müssen die Leads geschützt sein. Das ist bewusst
 * schlank gehalten: ein Passwort, ein signiertes Cookie, kein Benutzerkonto.
 *
 * Ohne gesetztes APP_PASSWORD ist der Schutz aus - dann sollte die App aber
 * auch nur auf 127.0.0.1 laufen.
 */
import crypto from 'node:crypto';
import { config } from './config.js';

const COOKIE = 'leadradar_session';
const GUELTIG_MS = 30 * 24 * 3600 * 1000; // 30 Tage - Handy soll nicht täglich fragen

export const schutzAktiv = () => Boolean(config.auth.password);

/** Signiert einen Ablaufzeitpunkt mit dem Passwort als Schlüssel. */
function signiere(ablauf) {
  return crypto
    .createHmac('sha256', config.auth.password)
    .update(String(ablauf))
    .digest('base64url');
}

export function erstelleToken() {
  const ablauf = Date.now() + GUELTIG_MS;
  return `${ablauf}.${signiere(ablauf)}`;
}

export function tokenGueltig(token) {
  if (!token || typeof token !== 'string') return false;
  const [ablaufTeil, signatur] = token.split('.');
  const ablauf = Number(ablaufTeil);
  if (!Number.isFinite(ablauf) || ablauf < Date.now()) return false;

  const erwartet = signiere(ablauf);
  return zeitgleichVergleichen(signatur || '', erwartet);
}

/** Vergleich ohne Zeitunterschied - verhindert das Erraten Zeichen für Zeichen. */
export function zeitgleichVergleichen(a, b) {
  const bufA = Buffer.from(String(a));
  const bufB = Buffer.from(String(b));
  if (bufA.length !== bufB.length) {
    // Trotzdem vergleichen, damit die Dauer nicht die Länge verrät
    crypto.timingSafeEqual(bufA, bufA);
    return false;
  }
  return crypto.timingSafeEqual(bufA, bufB);
}

export function passwortStimmt(eingabe) {
  return zeitgleichVergleichen(String(eingabe || ''), config.auth.password);
}

function leseCookie(req, name) {
  const header = req.headers.cookie;
  if (!header) return null;
  for (const teil of header.split(';')) {
    const [k, ...rest] = teil.trim().split('=');
    if (k === name) return decodeURIComponent(rest.join('='));
  }
  return null;
}

export function istAngemeldet(req) {
  if (!schutzAktiv()) return true;
  return tokenGueltig(leseCookie(req, COOKIE));
}

export function setzeCookie(res, token, sicher) {
  const teile = [
    `${COOKIE}=${encodeURIComponent(token)}`,
    'Path=/',
    'HttpOnly',
    'SameSite=Lax',
    `Max-Age=${Math.floor(GUELTIG_MS / 1000)}`,
  ];
  // Secure nur bei HTTPS - sonst kommt das Cookie im WLAN nie an
  if (sicher) teile.push('Secure');
  res.setHeader('set-cookie', teile.join('; '));
}

export function loescheCookie(res) {
  res.setHeader('set-cookie', `${COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0`);
}

/** Einfache Bremse gegen Durchprobieren: pro IP max. 10 Versuche in 15 Minuten. */
const versuche = new Map();
const FENSTER_MS = 15 * 60 * 1000;
const MAX_VERSUCHE = 10;

export function zuVieleVersuche(ip) {
  const eintrag = versuche.get(ip);
  if (!eintrag) return false;
  if (Date.now() - eintrag.seit > FENSTER_MS) {
    versuche.delete(ip);
    return false;
  }
  return eintrag.anzahl >= MAX_VERSUCHE;
}

export function versuchZaehlen(ip, erfolgreich) {
  if (erfolgreich) {
    versuche.delete(ip);
    return;
  }
  const eintrag = versuche.get(ip);
  if (!eintrag || Date.now() - eintrag.seit > FENSTER_MS) {
    versuche.set(ip, { anzahl: 1, seit: Date.now() });
  } else {
    eintrag.anzahl++;
  }
}
