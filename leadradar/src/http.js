/**
 * Kleiner HTTP-Helfer mit Timeout, Grössen-Limit und sauberer Fehler-Klassifizierung.
 * Nutzt das eingebaute fetch von Node (>= 18) - keine externen Pakete.
 */
import { config } from './config.js';

/** Fehlercodes, die wir für die Website-Analyse unterscheiden wollen. */
export const NET = {
  DNS: 'dns',
  TIMEOUT: 'timeout',
  SSL: 'ssl',
  REFUSED: 'refused',
  RESET: 'reset',
  OTHER: 'other',
};

export function classifyNetworkError(err) {
  const code = err?.cause?.code || err?.code || '';
  const name = err?.name || '';
  const msg = String(err?.message || '');

  if (name === 'AbortError' || /timeout|timed out/i.test(msg)) return NET.TIMEOUT;
  if (code === 'ENOTFOUND' || code === 'EAI_AGAIN') return NET.DNS;
  if (code === 'ECONNREFUSED') return NET.REFUSED;
  if (code === 'ECONNRESET' || code === 'EPIPE') return NET.RESET;
  if (
    /CERT|SSL|self.signed|ERR_TLS|UNABLE_TO_VERIFY|HOSTNAME_MISMATCH|DEPTH_ZERO/i.test(
      code + ' ' + msg,
    )
  ) {
    return NET.SSL;
  }
  return NET.OTHER;
}

/**
 * fetch mit Timeout.
 * @returns {Promise<Response>}
 */
export async function fetchWithTimeout(url, options = {}, timeoutMs = 15000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, {
      redirect: 'follow',
      ...options,
      signal: controller.signal,
      headers: {
        'user-agent': config.audit.userAgent,
        'accept-language': 'de-CH,de;q=0.9,en;q=0.6',
        ...(options.headers || {}),
      },
    });
  } finally {
    clearTimeout(timer);
  }
}

/**
 * Lädt Text, bricht bei maxBytes ab (schützt vor riesigen Seiten).
 * @returns {Promise<{text:string, bytes:number, truncated:boolean}>}
 */
export async function readTextLimited(response, maxBytes = config.audit.maxBytes) {
  if (!response.body) {
    const text = await response.text();
    return { text, bytes: Buffer.byteLength(text), truncated: false };
  }
  const chunks = [];
  let bytes = 0;
  let truncated = false;
  for await (const chunk of response.body) {
    const buf = Buffer.from(chunk);
    bytes += buf.length;
    if (bytes > maxBytes) {
      chunks.push(buf.subarray(0, Math.max(0, buf.length - (bytes - maxBytes))));
      truncated = true;
      break;
    }
    chunks.push(buf);
  }
  const raw = Buffer.concat(chunks);
  return { text: decodeHtml(raw, response.headers.get('content-type') || ''), bytes: truncated ? maxBytes : raw.length, truncated };
}

/**
 * Zeichensatz bestimmen. Reihenfolge bewusst so gewählt:
 *
 * 1. Ist der Inhalt gültiges UTF-8? Dann UTF-8 - unabhängig davon, was der
 *    Server behauptet. Sehr viele alte Seiten deklarieren ISO-8859-1, liefern
 *    aber längst UTF-8 aus; würde man dem Header blind glauben, käme "fÃ¼r"
 *    statt "für" heraus und Prüfungen auf deutsche Begriffe schlügen fehl.
 * 2. Sonst der deklarierte Zeichensatz (Header oder <meta charset>).
 * 3. Sonst Windows-1252 - der übliche Fall bei echten Altlasten.
 */
export function decodeHtml(raw, contentType = '') {
  try {
    return new TextDecoder('utf-8', { fatal: true }).decode(raw);
  } catch {
    /* kein gültiges UTF-8 - unten weiter */
  }

  const head = raw.subarray(0, 2048).toString('latin1');
  const declared =
    /charset=["']?([\w-]+)/i.exec(contentType)?.[1] ||
    /<meta[^>]+charset=["']?([\w-]+)/i.exec(head)?.[1] ||
    '';

  const normalized = declared.toLowerCase();
  const charset =
    !normalized || ['iso-8859-1', 'latin1', 'iso8859-1', 'utf-8'].includes(normalized)
      ? 'windows-1252'
      : normalized;

  try {
    return new TextDecoder(charset, { fatal: false }).decode(raw);
  } catch {
    return new TextDecoder('windows-1252', { fatal: false }).decode(raw);
  }
}

/** JSON-Request mit Timeout und aussagekräftigem Fehler. */
export async function fetchJson(url, options = {}, timeoutMs = 30000) {
  const res = await fetchWithTimeout(url, options, timeoutMs);
  const text = await res.text();
  if (!res.ok) {
    const snippet = text.slice(0, 400).replace(/\s+/g, ' ');
    const err = new Error(`HTTP ${res.status} von ${new URL(url).host}: ${snippet}`);
    err.status = res.status;
    err.body = text;
    throw err;
  }
  try {
    return JSON.parse(text);
  } catch {
    throw new Error(`Ungültiges JSON von ${new URL(url).host}: ${text.slice(0, 200)}`);
  }
}

/** Führt Aufgaben mit begrenzter Parallelität aus. */
export async function pool(items, limit, worker) {
  const results = new Array(items.length);
  let cursor = 0;
  const runners = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (true) {
      const i = cursor++;
      if (i >= items.length) return;
      try {
        results[i] = await worker(items[i], i);
      } catch (err) {
        results[i] = { __error: err?.message || String(err) };
      }
    }
  });
  await Promise.all(runners);
  return results;
}
