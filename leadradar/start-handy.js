/**
 * Startet die App so, dass sie auch vom Handy im gleichen WLAN erreichbar ist.
 *
 *     npm run handy
 *
 * Funktioniert unter Windows, macOS und Linux gleichermassen - deshalb ein
 * kleines Skript statt "HOST=0.0.0.0 node server.js" (das kennt Windows nicht).
 *
 * Das Passwort kommt aus der .env (APP_PASSWORD). Ist keins gesetzt, bricht
 * das Skript ab - ohne Passwort wären die Leads für jeden im WLAN sichtbar.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const hier = path.dirname(fileURLToPath(import.meta.url));
const envDatei = path.join(hier, '.env');

// Passwort aus der .env lesen, bevor der Server startet
let passwortGesetzt = Boolean(process.env.APP_PASSWORD);
if (!passwortGesetzt && fs.existsSync(envDatei)) {
  const inhalt = fs.readFileSync(envDatei, 'utf8');
  passwortGesetzt = /^\s*APP_PASSWORD\s*=\s*\S+/m.test(inhalt);
}

if (!passwortGesetzt) {
  console.log('');
  console.log('  ╭────────────────────────────────────────────────────────────╮');
  console.log('  │  Kein Passwort gesetzt – Start abgebrochen                 │');
  console.log('  ╰────────────────────────────────────────────────────────────╯');
  console.log('');
  console.log('  Sobald die App vom Handy erreichbar ist, kann sie jeder im');
  console.log('  gleichen WLAN öffnen – also auch deine Leads und Notizen.');
  console.log('');
  console.log('  So gehts:');
  console.log('    1. Datei .env anlegen (Vorlage: .env.example)');
  console.log('    2. Zeile eintragen:   APP_PASSWORD=deinPasswort');
  console.log('    3. npm run handy');
  console.log('');
  process.exit(1);
}

process.env.HOST = '0.0.0.0';
await import('./server.js');
