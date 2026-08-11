/**
 * Lead-Bewertung.
 *
 * Der Score beantwortet eine Frage: "Wie gross ist die Chance, dass dieser
 * Betrieb eine neue Webseite braucht UND sie sich leisten kann?"
 *
 * Er setzt sich aus zwei Teilen zusammen:
 *  - BEDARF     (0-70): Wie schlecht ist der Web-Auftritt?
 *  - QUALITÄT   (0-30): Läuft der Betrieb gut? Ist er erreichbar?
 *
 * Wichtig für die Reihenfolge: Ein Betrieb ohne Webseite steht bewusst über
 * einem mit schlechter Webseite. Das Gespräch ist eindeutiger zu führen
 * ("Sie haben keine Seite") als eine Diskussion über eine bestehende Seite,
 * an der oft der Neffe des Chefs gebaut hat. Darum ist der Bedarf bei
 * bestehenden Seiten auf MAX_NEED_EXISTING gedeckelt.
 */

const YEAR_MS = 365.25 * 24 * 3600 * 1000;
const MAX_NEED = 70;
const MAX_NEED_EXISTING = 48;

/** Ein einzelner Bewertungsgrund - wird im UI als Chip angezeigt. */
const reason = (code, label, points, kind = 'need') => ({ code, label, points, kind });

export function scoreLead(lead) {
  const a = lead.audit || {};
  const reasons = [];
  let need = 0;
  let quality = 0;

  // ---------- BEDARF ----------
  switch (a.status) {
    case 'none':
      need += 70;
      reasons.push(reason('no_website', 'Keine Webseite', 70));
      break;
    case 'dead':
      need += 66;
      reasons.push(reason('dead_website', a.summary || 'Webseite nicht erreichbar', 66));
      break;
    case 'parked':
      need += 60;
      reasons.push(reason('parked', 'Nur Platzhalter-/Baustellenseite', 60));
      break;
    case 'social_only':
      need += 56;
      reasons.push(reason('social_only', 'Nur Facebook/Instagram statt Webseite', 56));
      break;
    case 'directory_only':
      need += 52;
      reasons.push(reason('directory_only', 'Nur local.ch-Eintrag, keine eigene Seite', 52));
      break;
    case 'ok': {
      // Webseite existiert - jetzt die Schwachstellen sammeln
      if (a.sslBroken) {
        need += 20;
        reasons.push(reason('ssl_broken', 'Zertifikatsfehler - Browser warnt "Nicht sicher"', 20));
      } else if (a.https === false) {
        need += 16;
        reasons.push(reason('no_https', 'Kein HTTPS - Google stuft die Seite ab', 16));
      }

      if (a.hasViewport === false) {
        need += 20;
        reasons.push(reason('not_mobile', 'Nicht mobiltauglich - unlesbar auf dem Handy', 20));
      }

      const age = websiteAgeYears(a);
      if (age != null && age >= 3) {
        const pts = Math.min(18, Math.round(age * 2.5));
        need += pts;
        reasons.push(
          reason('outdated', `Letzte Aktualisierung ${a.copyrightYear || `vor ${age} Jahren`}`, pts),
        );
      }

      if (a.responseMs > 3000) {
        need += 8;
        reasons.push(reason('slow', `Lädt langsam (${(a.responseMs / 1000).toFixed(1)} s)`, 8));
      }
      if (a.pageBytes > 3_000_000) {
        need += 5;
        reasons.push(reason('heavy', `Sehr schwere Seite (${mb(a.pageBytes)})`, 5));
      }

      const legacy = (a.techFlags || []).filter((f) =>
        /Frames|Flash|font|Lauftext|jQuery|Tabellen|Internet Explorer/i.test(f),
      );
      if (legacy.length) {
        const pts = Math.min(14, legacy.length * 6);
        need += pts;
        reasons.push(reason('legacy_tech', legacy.join(', '), pts));
      }

      const builder = (a.techFlags || []).find((f) => /Baukasten/i.test(f));
      if (builder) {
        need += 6;
        reasons.push(reason('builder', builder + ' - austauschbares Design', 6));
      }

      if (a.hasImpressum === false) {
        need += 6;
        reasons.push(reason('no_impressum', 'Kein Impressum (rechtliches Risiko)', 6));
      }
      if (a.hasContactForm === false) {
        need += 5;
        reasons.push(reason('no_form', 'Kein Kontaktformular - Anfragen gehen verloren', 5));
      }
      if (!a.title || a.title.length < 8) {
        need += 4;
        reasons.push(reason('no_title', 'Kein sinnvoller Seitentitel (schlecht für Google)', 4));
      }
      if (!a.description) {
        need += 3;
        reasons.push(reason('no_description', 'Keine Meta-Beschreibung für Google', 3));
      }
      // Bestehende Seiten bleiben unter "gar keine Seite"
      need = Math.min(MAX_NEED_EXISTING, need);
      break;
    }
    default:
      break;
  }

  need = Math.min(MAX_NEED, need);

  // ---------- QUALITÄT / ATTRAKTIVITÄT ----------
  const reviews = lead.googleReviews ?? 0;
  const rating = lead.googleRating ?? 0;

  if (reviews >= 40 && rating >= 4.3) {
    quality += 12;
    reasons.push(reason('strong_reputation', `Top bewertet: ${rating}★ aus ${reviews} Bewertungen`, 12, 'good'));
  } else if (reviews >= 15 && rating >= 4.0) {
    quality += 8;
    reasons.push(reason('good_reputation', `Gut bewertet: ${rating}★ aus ${reviews} Bewertungen`, 8, 'good'));
  } else if (reviews >= 5) {
    quality += 4;
    reasons.push(reason('some_reviews', `${reviews} Google-Bewertungen`, 4, 'good'));
  }

  if (lead.phone) {
    quality += 8;
    reasons.push(reason('has_phone', 'Telefonnummer vorhanden - direkt anrufbar', 8, 'good'));
  } else {
    reasons.push(reason('no_phone', 'Keine Telefonnummer gefunden', 0, 'warn'));
  }

  if (lead.email || (lead.audit?.emailsFound || []).length) {
    quality += 5;
    reasons.push(reason('has_email', 'E-Mail-Adresse vorhanden', 5, 'good'));
  }

  const inactive = inactivityYears(lead);
  if (inactive != null && inactive >= 2) {
    quality += 5;
    reasons.push(
      reason('inactive', `Seit ${inactive} Jahren keine neue Google-Bewertung`, 5, 'warn'),
    );
  }

  if (lead.businessStatus && lead.businessStatus !== 'OPERATIONAL') {
    quality -= 25;
    reasons.push(reason('closed', 'Betrieb laut Google geschlossen', -25, 'bad'));
  }

  quality = Math.max(-25, Math.min(30, quality));

  const total = Math.max(0, Math.min(100, Math.round(need + quality)));

  return {
    score: total,
    needScore: need,
    qualityScore: quality,
    tier: tierFor(total),
    reasons: reasons.sort((x, y) => y.points - x.points),
    headline: headlineFor(lead, a),
  };
}

/** Kurzer Satz, der ganz oben in der Liste steht - das Verkaufsargument. */
function headlineFor(lead, a) {
  switch (a.status) {
    case 'none':
      return 'Hat gar keine Webseite';
    case 'dead':
      return a.summary || 'Webseite ist tot';
    case 'parked':
      return 'Nur eine Platzhalterseite';
    case 'social_only':
      return 'Nur Social Media, keine eigene Webseite';
    case 'directory_only':
      return 'Nur ein Verzeichnis-Eintrag';
    case 'ok': {
      const parts = [];
      if (a.hasViewport === false) parts.push('nicht mobiltauglich');
      if (a.sslBroken) parts.push('Zertifikatsfehler');
      else if (a.https === false) parts.push('kein HTTPS');
      const age = websiteAgeYears(a);
      if (age != null && age >= 3) parts.push(`Stand ${a.copyrightYear || `vor ${age} Jahren`}`);
      if (parts.length === 0) return 'Webseite wirkt aktuell - eher kein Bedarf';
      return 'Webseite vorhanden, aber ' + parts.join(', ');
    }
    case 'error':
      return 'Prüfung fehlgeschlagen';
    default:
      return 'Noch nicht geprüft';
  }
}

export function websiteAgeYears(audit) {
  const now = new Date();
  const thisYear = now.getFullYear();
  let years = null;

  if (audit?.copyrightYear && audit.copyrightYear >= 1996) {
    years = thisYear - audit.copyrightYear;
  }
  if (audit?.lastModified) {
    const t = Date.parse(audit.lastModified);
    if (Number.isFinite(t)) {
      const y = Math.floor((now.getTime() - t) / YEAR_MS);
      // Last-Modified nur nutzen, wenn kein Copyright-Jahr gefunden wurde
      if (years == null) years = y;
    }
  }
  return years != null && years >= 0 ? years : null;
}

export function inactivityYears(lead) {
  if (!lead.lastActivityAt) return null;
  const t = Date.parse(lead.lastActivityAt);
  if (!Number.isFinite(t)) return null;
  return Math.floor((Date.now() - t) / YEAR_MS);
}

export function tierFor(score) {
  if (score >= 75) return { key: 'hot', label: 'Sehr heiss', emoji: '🔥', color: '#dc2626' };
  if (score >= 55) return { key: 'warm', label: 'Heiss', emoji: '🌡️', color: '#ea580c' };
  if (score >= 35) return { key: 'medium', label: 'Interessant', emoji: '👀', color: '#ca8a04' };
  if (score >= 18) return { key: 'low', label: 'Schwach', emoji: '💤', color: '#64748b' };
  return { key: 'none', label: 'Kein Bedarf', emoji: '✅', color: '#16a34a' };
}

function mb(bytes) {
  return (bytes / 1_000_000).toFixed(1) + ' MB';
}

/** Score + Kontaktdaten aus dem Audit in den Lead übernehmen. */
export function enrichLead(lead) {
  const audit = lead.audit || {};

  // E-Mail aus der Webseite übernehmen, falls noch keine da ist
  if (!lead.email && audit.emailsFound?.length) {
    lead.email = audit.emailsFound[0];
    lead.emailSource = 'website';
  }
  // Social-Profile ergänzen
  if (audit.socialsFound?.length) {
    lead.socials = { ...(lead.socials || {}) };
    for (const url of audit.socialsFound) {
      if (/facebook|fb\.me/i.test(url) && !lead.socials.facebook) lead.socials.facebook = url;
      if (/instagram/i.test(url) && !lead.socials.instagram) lead.socials.instagram = url;
      if (/linkedin/i.test(url) && !lead.socials.linkedin) lead.socials.linkedin = url;
    }
  }

  const s = scoreLead(lead);
  lead.score = s.score;
  lead.needScore = s.needScore;
  lead.qualityScore = s.qualityScore;
  lead.tier = s.tier;
  lead.reasons = s.reasons;
  lead.headline = s.headline;
  lead.inactiveYears = inactivityYears(lead);
  lead.websiteAgeYears = websiteAgeYears(audit);
  return lead;
}
