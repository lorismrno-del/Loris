/**
 * Webseite-Analyse: prüft die Webseite eines Betriebs und liefert konkrete
 * Verkaufsargumente ("kein HTTPS", "nicht mobiltauglich", "Stand 2014", ...).
 *
 * Zusätzlich werden E-Mail-Adressen und Social-Media-Profile ausgelesen -
 * damit auf der Anrufliste möglichst vollständige Kontaktdaten stehen.
 */
import { config } from './config.js';
import { fetchWithTimeout, readTextLimited, classifyNetworkError, NET, pool } from './http.js';

const SOCIAL_HOSTS = [
  'facebook.com', 'fb.me', 'instagram.com', 'linkedin.com', 'tiktok.com',
  'youtube.com', 'twitter.com', 'x.com', 'pinterest.com',
];

const DIRECTORY_HOSTS = [
  'local.ch', 'search.ch', 'gelbeseiten', 'yelp.', 'linkedin.com/company',
  'houzz.', 'renovero.ch', 'ofri.ch', 'buildigo.ch', 'jobs.ch',
];

const PARKING_MARKERS = [
  'diese domain wurde registriert', 'this domain is for sale', 'domain kaufen',
  'parkingcrew', 'sedoparking', 'godaddy.com/domainsearch', 'hostpoint.ch/domain',
  'website coming soon', 'diese seite befindet sich im aufbau', 'under construction',
  'baustelle', 'in kürze für sie da', 'platzhalterseite', 'default web site page',
  'apache2 ubuntu default page', 'welcome to nginx', 'it works!',
  'diese domain ist reserviert',
];

const BUILDER_SIGNATURES = [
  [/jimdo/i, 'Jimdo-Baukasten'],
  [/wix\.com|_wixCssImports|wixstatic/i, 'Wix-Baukasten'],
  [/squarespace/i, 'Squarespace'],
  [/weebly/i, 'Weebly'],
  [/webnode/i, 'Webnode'],
  [/1and1|ionos.*mywebsite|website-builder/i, 'IONOS-Baukasten'],
  [/homepage-baukasten|hostpoint\s*sitebuilder/i, 'Hoster-Baukasten'],
  [/joomla/i, 'Joomla (oft veraltet)'],
  [/typo3/i, 'TYPO3'],
  [/wordpress|wp-content/i, 'WordPress'],
];

const LEGACY_SIGNATURES = [
  [/<frameset|<frame\s/i, 'Frames (Technik der 90er)'],
  [/\.swf["'\s>]|application\/x-shockwave-flash/i, 'Flash (funktioniert nicht mehr)'],
  [/<font\s+(face|color|size)=/i, '<font>-Tags (veralteter Code)'],
  [/<marquee|<blink/i, 'Lauftext / Blinktext'],
  [/jquery[.-]1\.\d/i, 'jQuery 1.x (uralt)'],
  [/<table[^>]*(width=|border=)[^>]*>[\s\S]{0,2000}<table/i, 'Tabellen-Layout'],
  [/optimiert für internet explorer|best viewed with/i, '"Optimiert für Internet Explorer"'],
];

const EMAIL_RE = /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/gi;
const OBFUSCATED_RE =
  /([a-z0-9._%+-]+)\s*(?:\(at\)|\[at\]|\{at\}|\s+at\s+)\s*([a-z0-9-]+(?:\.[a-z0-9-]+)*?)\s*(?:\(dot\)|\[dot\]|\{dot\}|\s+dot\s+|\.)\s*([a-z]{2,})\b/gi;

/**
 * Aussortieren von Treffern, die keine echten Kontaktadressen sind.
 *
 * Bewusst exakt statt per Teilstring: Ein Filter auf "muster" würde sonst
 * "info@schreinerei-muster.ch" wegwerfen - also genau die Betriebe, die wir
 * suchen. Geprüft werden darum nur der lokale Teil bzw. die ganze Domain.
 */
// Bildnamen, die beim Parsen wie E-Mails aussehen (logo@2x.png)
const IMAGE_TLDS = new Set(['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'ico', 'avif']);
// Technische Absender, keine Ansprechpartner
const BAD_LOCAL_PARTS = new Set([
  'noreply', 'no-reply', 'donotreply', 'postmaster', 'webmaster', 'hostmaster',
  'abuse', 'ihre-email', 'your-email', 'email', 'name', 'vorname.nachname',
  'max.mustermann', 'mustermann', 'beispiel', 'test',
]);
// Infrastruktur-Domains von Baukästen, Trackern und Platzhaltertexten
const BAD_DOMAINS = [
  'example.com', 'example.org', 'example.net', 'domain.tld', 'muster.de',
  'sentry.io', 'wixpress.com', 'godaddy.com', 'squarespace.com', 'sentry-cdn.com',
];

const CONTACT_PATHS = [
  '/kontakt', '/impressum', '/contact', '/ueber-uns', '/about', '/kontakt.html',
  '/impressum.html', '/kontakt.php', '/contact.html',
];

export function isSocialUrl(url) {
  if (!url) return false;
  try {
    const host = new URL(url).hostname.replace(/^www\./, '');
    return SOCIAL_HOSTS.some((h) => host === h || host.endsWith('.' + h) || host.includes(h));
  } catch {
    return false;
  }
}

export function isDirectoryUrl(url) {
  if (!url) return false;
  const s = url.toLowerCase();
  return DIRECTORY_HOSTS.some((h) => s.includes(h));
}

/** Analysiert die Webseite eines Leads. Wirft nie - Fehler landen im Ergebnis. */
export async function auditWebsite(lead) {
  const started = Date.now();
  const url = lead.website;

  if (!url) {
    return {
      checkedAt: new Date().toISOString(),
      status: 'none',
      summary: 'Keine Webseite hinterlegt',
    };
  }

  if (isSocialUrl(url)) {
    return {
      checkedAt: new Date().toISOString(),
      status: 'social_only',
      finalUrl: url,
      summary: 'Nur Social-Media-Profil statt eigener Webseite',
    };
  }

  if (isDirectoryUrl(url)) {
    return {
      checkedAt: new Date().toISOString(),
      status: 'directory_only',
      finalUrl: url,
      summary: 'Nur Verzeichnis-Eintrag (local.ch o. ä.), keine eigene Webseite',
    };
  }

  let res;
  let netError = null;
  let redirectTarget = null;
  try {
    ({ response: res, redirectTarget } = await followRedirects(url));
  } catch (err) {
    netError = classifyNetworkError(err);
    // Bei SSL-Problem: nochmals über http versuchen, um zu unterscheiden
    // zwischen "Seite tot" und "Seite lebt, aber ohne gültiges Zertifikat".
    if (netError === NET.SSL && url.startsWith('https://')) {
      try {
        ({ response: res, redirectTarget } = await followRedirects(url.replace(/^https:/, 'http:')));
        netError = null;
      } catch {
        /* bleibt Fehler */
      }
    }
  }

  // Domain leitet auf Social Media oder ein Verzeichnis weiter. Das erkennen
  // wir am Location-Header, ohne die Zielseite überhaupt zu laden - Facebook
  // & Co. antworten Bots ohnehin oft mit einer Loginwand.
  if (redirectTarget) {
    return {
      checkedAt: new Date().toISOString(),
      status: isSocialUrl(redirectTarget) ? 'social_only' : 'directory_only',
      finalUrl: redirectTarget,
      responseMs: Date.now() - started,
      summary: isSocialUrl(redirectTarget)
        ? 'Domain leitet direkt auf ein Social-Media-Profil weiter'
        : 'Domain leitet auf einen Verzeichnis-Eintrag weiter',
    };
  }

  if (!res) {
    return {
      checkedAt: new Date().toISOString(),
      status: 'dead',
      reason: netError,
      finalUrl: url,
      responseMs: Date.now() - started,
      summary: {
        [NET.DNS]: 'Domain existiert nicht mehr (kein DNS-Eintrag)',
        [NET.TIMEOUT]: 'Webseite antwortet nicht (Zeitüberschreitung)',
        [NET.REFUSED]: 'Server verweigert die Verbindung',
        [NET.RESET]: 'Verbindung wird abgebrochen',
        [NET.SSL]: 'Zertifikatsfehler - Browser zeigt Warnung "Nicht sicher"',
      }[netError] || 'Webseite nicht erreichbar',
    };
  }

  const responseMs = Date.now() - started;
  const finalUrl = res.url || url;
  const https = finalUrl.startsWith('https://');
  const sslBroken = netError === NET.SSL || (url.startsWith('https://') && !https);

  if (res.status >= 400) {
    return {
      checkedAt: new Date().toISOString(),
      status: 'dead',
      reason: 'http_' + res.status,
      httpStatus: res.status,
      finalUrl,
      responseMs,
      summary:
        res.status === 404
          ? 'Webseite liefert Fehler 404 - Seite existiert nicht mehr'
          : `Webseite liefert Serverfehler (HTTP ${res.status})`,
    };
  }

  // Weiterleitung auf Social Media / Verzeichnis?
  if (isSocialUrl(finalUrl)) {
    return {
      checkedAt: new Date().toISOString(),
      status: 'social_only',
      finalUrl,
      httpStatus: res.status,
      responseMs,
      summary: 'Domain leitet auf ein Social-Media-Profil weiter',
    };
  }

  const { text: html, bytes } = await readTextLimited(res);
  const lower = html.toLowerCase();

  // Platzhalter- / Baustellenseite erkennen
  const textOnly = stripHtml(html);
  const isParked =
    PARKING_MARKERS.some((m) => lower.includes(m)) ||
    (textOnly.trim().length < 220 && !/<img|<video/i.test(html));

  const audit = {
    checkedAt: new Date().toISOString(),
    status: isParked ? 'parked' : 'ok',
    httpStatus: res.status,
    finalUrl,
    responseMs,
    pageBytes: bytes,
    https: https && !sslBroken,
    sslBroken,
    title: (/<title[^>]*>([\s\S]{0,200}?)<\/title>/i.exec(html)?.[1] || '').trim(),
    description: (
      /<meta[^>]+name=["']description["'][^>]+content=["']([\s\S]{0,300}?)["']/i.exec(html)?.[1] ||
      ''
    ).trim(),
    hasViewport: /<meta[^>]+name=["']viewport["']/i.test(html),
    hasImpressum: /impressum|rechtliches|mentions l[ée]gales/i.test(lower),
    hasContactForm: /<form[\s\S]{0,3000}?(type=["']email|name=["']email|<textarea)/i.test(html),
    hasCookieBanner: /cookie|datenschutz/i.test(lower),
    copyrightYear: findCopyrightYear(html),
    lastModified: res.headers.get('last-modified') || null,
    generator: (/<meta[^>]+name=["']generator["'][^>]+content=["']([^"']{0,120})["']/i.exec(html)?.[1] || '').trim(),
    techFlags: [],
    emailsFound: [],
    socialsFound: extractSocials(html, finalUrl),
    truncated: bytes >= config.audit.maxBytes,
  };

  if (isParked) audit.summary = 'Platzhalter-/Baustellenseite ohne echten Inhalt';

  for (const [re, label] of BUILDER_SIGNATURES) {
    if (re.test(html)) {
      audit.techFlags.push(label);
      break; // ein Baukasten reicht
    }
  }
  for (const [re, label] of LEGACY_SIGNATURES) {
    if (re.test(html)) audit.techFlags.push(label);
  }

  audit.emailsFound = extractEmails(html, finalUrl);

  // Wenn auf der Startseite keine E-Mail steht: Kontakt-/Impressumsseite nachladen
  if (config.audit.followImpressum && audit.emailsFound.length === 0) {
    const target = findContactLink(html, finalUrl);
    if (target) {
      try {
        const r2 = await fetchWithTimeout(target, {}, config.audit.timeoutMs);
        if (r2.ok) {
          const { text: html2 } = await readTextLimited(r2, 800_000);
          audit.emailsFound = extractEmails(html2, target);
          if (!audit.hasImpressum && /impressum/i.test(html2)) audit.hasImpressum = true;
          const y2 = findCopyrightYear(html2);
          if (y2 && (!audit.copyrightYear || y2 > audit.copyrightYear)) audit.copyrightYear = y2;
          if (audit.socialsFound.length === 0) {
            audit.socialsFound = extractSocials(html2, target);
          }
        }
      } catch {
        /* Kontaktseite optional */
      }
    }
  }

  return audit;
}

/**
 * Folgt Weiterleitungen selbst, statt fetch machen zu lassen.
 * Grund: Wir wollen erkennen, WOHIN weitergeleitet wird - landet die Domain
 * auf Facebook oder local.ch, ist das die eigentliche Erkenntnis.
 *
 * @returns {Promise<{response: Response|null, redirectTarget: string|null}>}
 */
async function followRedirects(startUrl, maxHops = 5) {
  let current = startUrl;

  for (let hop = 0; hop <= maxHops; hop++) {
    const response = await fetchWithTimeout(
      current,
      { redirect: 'manual' },
      config.audit.timeoutMs,
    );

    const location = response.headers.get('location');
    if (response.status < 300 || response.status >= 400 || !location) {
      // Die tatsächlich abgerufene Adresse festhalten (fetch kennt sie bei
      // redirect:'manual' nicht zuverlässig).
      Object.defineProperty(response, 'url', { value: current, configurable: true });
      return { response, redirectTarget: null };
    }

    let next;
    try {
      next = new URL(location, current).toString();
    } catch {
      return { response, redirectTarget: null };
    }

    if (isSocialUrl(next) || isDirectoryUrl(next)) {
      return { response: null, redirectTarget: next };
    }
    current = next;
  }

  // Zu viele Weiterleitungen - als tot behandeln
  throw Object.assign(new Error('Zu viele Weiterleitungen'), { code: 'ETOOMANYREDIRECTS' });
}

function stripHtml(html) {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/\s+/g, ' ');
}

/** Sucht das Copyright-Jahr im Footer - guter Indikator für "seit Jahren nicht angefasst". */
export function findCopyrightYear(html) {
  const text = stripHtml(html);
  const thisYear = new Date().getFullYear();
  const years = [];

  const patterns = [
    /(?:©|&copy;|copyright|\(c\))\s*(?:\d{4}\s*[-–]\s*)?(\d{4})/gi,
    /(\d{4})\s*(?:©|&copy;)/gi,
    /(?:stand|letzte aktualisierung|zuletzt aktualisiert)\s*:?\s*(?:\d{1,2}\.\d{1,2}\.)?(\d{4})/gi,
  ];
  for (const re of patterns) {
    let m;
    while ((m = re.exec(text))) {
      const y = Number(m[1]);
      if (y >= 1996 && y <= thisYear + 1) years.push(y);
    }
  }
  if (years.length === 0) return null;
  return Math.max(...years);
}

function extractEmails(html, baseUrl) {
  const found = new Set();
  let host = '';
  try {
    host = new URL(baseUrl).hostname.replace(/^www\./, '');
  } catch { /* egal */ }

  // mailto-Links bevorzugen (zuverlässigster Treffer)
  const mailtoRe = /mailto:([^"'?>\s]+)/gi;
  let m;
  while ((m = mailtoRe.exec(html))) addEmail(found, decodeURIComponent(m[1]));

  // Klartext im sichtbaren Text
  const text = stripHtml(html);
  const plain = text.match(EMAIL_RE) || [];
  for (const e of plain) addEmail(found, e);

  // Verschleierte Schreibweisen: "info (at) firma (dot) ch" oder "info [at] firma.ch"
  //
  // Das "at" MUSS umschrieben sein. Liesse man auch ein echtes "@" zu, würde
  // "info@firma.ch. Wir freuen uns" fälschlich zu "info@firma.ch.wir" - eine
  // Adresse, die es nie gab.
  while ((m = OBFUSCATED_RE.exec(text))) addEmail(found, `${m[1]}@${m[2]}.${m[3]}`);
  OBFUSCATED_RE.lastIndex = 0;

  const list = [...found];
  // E-Mails auf der eigenen Domain zuerst, dann "info@"/"kontakt@"
  return list.sort((a, b) => rankEmail(b, host) - rankEmail(a, host)).slice(0, 5);
}

function addEmail(set, raw) {
  const e = String(raw || '').trim().toLowerCase().replace(/[.,;:)]+$/, '');
  if (!/^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$/.test(e)) return;

  const [local, domain] = e.split('@');
  const tld = domain.split('.').pop();

  if (IMAGE_TLDS.has(tld)) return;
  if (BAD_LOCAL_PARTS.has(local)) return;
  if (BAD_DOMAINS.some((bad) => domain === bad || domain.endsWith('.' + bad))) return;

  set.add(e);
}

function rankEmail(email, host) {
  let score = 0;
  if (host && email.endsWith('@' + host)) score += 10;
  if (host && email.includes(host.split('.')[0])) score += 4;
  if (/^(info|kontakt|contact|mail|office|buero|bureau)@/.test(email)) score += 5;
  if (/^(noreply|no-reply|webmaster|admin|postmaster)@/.test(email)) score -= 6;
  return score;
}

function extractSocials(html, baseUrl) {
  const out = new Set();
  const re = /href=["'](https?:\/\/[^"']+)["']/gi;
  let m;
  while ((m = re.exec(html))) {
    const href = m[1];
    if (isSocialUrl(href) && href.length < 160) out.add(href.split('?')[0]);
    if (out.size >= 6) break;
  }
  return [...out];
}

function findContactLink(html, baseUrl) {
  // 1. Link, dessen Text auf Kontakt/Impressum hindeutet
  const re = /<a[^>]+href=["']([^"'#]+)["'][^>]*>([\s\S]{0,120}?)<\/a>/gi;
  let m;
  const candidates = [];
  while ((m = re.exec(html))) {
    const href = m[1];
    const label = stripHtml(m[2]).toLowerCase();
    if (/impressum|kontakt|contact|über uns|ueber uns/i.test(label + ' ' + href)) {
      candidates.push(href);
    }
  }
  for (const href of candidates) {
    try {
      const u = new URL(href, baseUrl);
      if (u.protocol.startsWith('http')) return u.toString();
    } catch { /* nächster */ }
  }
  // 2. Übliche Pfade raten
  try {
    const base = new URL(baseUrl);
    return new URL(CONTACT_PATHS[0], base).toString();
  } catch {
    return null;
  }
}

/** Analysiert viele Leads parallel (begrenzt). onProgress(fertig, total). */
export async function auditMany(leads, onProgress) {
  let done = 0;
  const results = await pool(leads, config.audit.concurrency, async (lead) => {
    let audit;
    try {
      audit = await auditWebsite(lead);
    } catch (err) {
      audit = {
        checkedAt: new Date().toISOString(),
        status: 'error',
        summary: 'Prüfung fehlgeschlagen: ' + (err?.message || String(err)),
      };
    }
    done++;
    onProgress?.(done, leads.length);
    return audit;
  });
  return results;
}
