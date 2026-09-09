#!/usr/bin/env node
/**
 * Sirat Talk – Logo Intro  →  MP4
 * ---------------------------------------------------------------------------
 * Rendert index.html frame-genau mit Playwright (Chromium) und encodet die
 * Einzelbilder mit ffmpeg zu einem MP4.
 *
 * Es wird NICHT in Echtzeit aufgenommen: die Seite wird angehalten und pro
 * Frame exakt auf currentTime = frame * (1000/fps) gesetzt. Dadurch ist das
 * Ergebnis deterministisch und laeuft exakt 8.000 s – unabhaengig davon, wie
 * schnell der Rechner ist.
 *
 * Vorbereitung (einmalig):
 *   npm install playwright
 *   npx playwright install chromium
 *   # ffmpeg muss im PATH liegen (brew install ffmpeg / apt install ffmpeg)
 *
 * Benutzung:
 *   node render.mjs                        # -> sirat-talk-intro.mp4, 60 fps
 *   node render.mjs --fps 30
 *   node render.mjs --out intro-4k.mp4 --scale 2      # 3840 x 2160
 *   node render.mjs --keep-frames          # PNG-Sequenz behalten
 *   node render.mjs --png-only             # nur PNG-Sequenz, kein MP4
 * ---------------------------------------------------------------------------
 */

import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { mkdir, rm, readdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));

// ---------- CLI ------------------------------------------------------------
const argv = process.argv.slice(2);
const flag = (name, fallback) => {
  const i = argv.indexOf('--' + name);
  return i === -1 ? fallback : argv[i + 1];
};
const has = (name) => argv.includes('--' + name);

const FPS        = Number(flag('fps', 60));
const SCALE      = Number(flag('scale', 1));            // 1 = 1920x1080, 2 = 3840x2160
const OUT        = path.resolve(HERE, flag('out', 'sirat-talk-intro.mp4'));
const HTML       = path.resolve(HERE, flag('html', 'index.html'));
const FRAME_DIR  = path.resolve(HERE, flag('frames', '.frames'));
const KEEP       = has('keep-frames') || has('png-only');
const PNG_ONLY   = has('png-only');
const FFMPEG     = process.env.FFMPEG || 'ffmpeg';

const WIDTH = 1920, HEIGHT = 1080;

if (!existsSync(HTML)) {
  console.error(`index.html nicht gefunden: ${HTML}`);
  process.exit(1);
}

// ---------- Frames rendern -------------------------------------------------
await rm(FRAME_DIR, { recursive: true, force: true });
await mkdir(FRAME_DIR, { recursive: true });

console.log(`Buehne   ${WIDTH * SCALE} x ${HEIGHT * SCALE}`);
const browser = await chromium.launch({
  args: ['--force-color-profile=srgb', '--disable-lcd-text', '--hide-scrollbars'],
});
const page = await browser.newPage({
  viewport: { width: WIDTH, height: HEIGHT },
  deviceScaleFactor: SCALE,
  colorScheme: 'light',
});

await page.goto(pathToFileURL(HTML).href + '?export=1');
await page.waitForFunction(() => !!window.INTRO);
await page.waitForTimeout(250);              // Layout + Fonts/Paths settlen lassen

const DURATION = await page.evaluate(() => window.INTRO.duration);   // 8000 ms
const TOTAL = Math.round((DURATION / 1000) * FPS);                   // 480 @ 60fps
console.log(`Dauer    ${DURATION / 1000} s @ ${FPS} fps  =  ${TOTAL} Frames`);

const nAnims = await page.evaluate(() => { window.INTRO.pause(); return window.INTRO.anims().length; });
console.log(`Angehaltene Animationen: ${nAnims}`);

const stage = page.locator('#scene');
const pad = String(TOTAL).length + 1;

for (let f = 0; f < TOTAL; f++) {
  const t = (f * DURATION) / TOTAL;                 // exakt bis 8000 ms
  // Zeit setzen und einen Renderdurchlauf abwarten.
  // WICHTIG: kein animations:'disabled' – das wuerde Playwright dazu bringen,
  // alle Animationen ans Ende zu spulen, und jeder Frame saehe gleich aus.
  await page.evaluate(async (ms) => {
    window.INTRO.seek(ms);
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  }, t);
  await stage.screenshot({
    path: path.join(FRAME_DIR, `f_${String(f).padStart(pad, '0')}.png`),
    scale: 'device',
  });
  if (f % Math.max(1, Math.round(TOTAL / 20)) === 0 || f === TOTAL - 1) {
    process.stdout.write(`\r  Frame ${f + 1}/${TOTAL}  (${(((f + 1) / TOTAL) * 100).toFixed(0)}%)   `);
  }
}
process.stdout.write('\n');
await browser.close();

const written = (await readdir(FRAME_DIR)).filter((f) => f.endsWith('.png')).length;
console.log(`${written} PNGs in ${FRAME_DIR}`);

if (PNG_ONLY) {
  console.log('--png-only gesetzt, kein MP4.');
  process.exit(0);
}

// ---------- ffmpeg ---------------------------------------------------------
const ffArgs = [
  '-y',
  '-framerate', String(FPS),
  '-start_number', '0',          // die Frames beginnen bei f_0000.png
  '-i', path.join(FRAME_DIR, `f_%0${pad}d.png`),
  '-c:v', 'libx264',
  '-preset', 'slow',
  '-crf', '16',
  '-pix_fmt', 'yuv420p',
  '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
  '-movflags', '+faststart',
  '-r', String(FPS),
  OUT,
];

console.log(`\nffmpeg ${ffArgs.join(' ')}\n`);
const code = await new Promise((resolve) => {
  const p = spawn(FFMPEG, ffArgs, { stdio: ['ignore', 'inherit', 'inherit'] });
  p.on('error', (e) => {
    console.error(`\nffmpeg konnte nicht gestartet werden (${e.message}).`);
    console.error('Installiere ffmpeg oder setze FFMPEG=/pfad/zu/ffmpeg.');
    console.error(`Die PNG-Sequenz liegt in ${FRAME_DIR}.`);
    resolve(1);
  });
  p.on('close', resolve);
});

if (code === 0) {
  if (!KEEP) await rm(FRAME_DIR, { recursive: true, force: true });
  console.log(`\nFertig: ${OUT}`);
} else {
  console.error(`\nffmpeg beendet mit Code ${code}. Frames bleiben in ${FRAME_DIR}.`);
  process.exit(code);
}
