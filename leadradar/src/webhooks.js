/**
 * Übergabe an andere Tools (z. B. Vertra oder Agentur-OS).
 *
 * Bewusst generisch gehalten: In den Einstellungen wird eine URL hinterlegt,
 * und der Lead geht als JSON per POST dorthin. So lässt sich jedes System
 * anbinden, ohne dass diese App dessen API kennen muss.
 */
import { fetchWithTimeout } from './http.js';
import { getSettings } from './settings.js';
import { tradeLabel } from './trades.js';
import { websiteStatusLabel } from './csv.js';

/** Reduziert einen Lead auf ein sauberes, stabiles Übergabeformat. */
export function toPayload(lead) {
  return {
    quelle: 'lorino-leadradar',
    id: lead.id,
    firma: lead.name,
    branche: tradeLabel(lead.trade),
    ansprechperson: lead.contactName || null,
    telefon: lead.customPhone || lead.phone || null,
    email: lead.customEmail || lead.email || null,
    website: lead.website || null,
    adresse: {
      strasse: lead.address?.street || null,
      plz: lead.address?.zip || null,
      ort: lead.address?.city || null,
      kanton: lead.address?.canton || null,
      land: lead.address?.country || 'CH',
    },
    koordinaten: lead.lat != null ? { lat: lead.lat, lng: lead.lng } : null,
    google: {
      sterne: lead.googleRating ?? null,
      bewertungen: lead.googleReviews ?? null,
      maps: lead.googleMapsUrl || null,
      inaktivJahre: lead.inactiveYears ?? null,
    },
    analyse: {
      websiteStatus: websiteStatusLabel(lead.audit?.status),
      problem: lead.headline || null,
      score: lead.score ?? null,
      einstufung: lead.tier?.label || null,
      gruende: (lead.reasons || []).map((r) => r.label),
      geprueftAm: lead.audit?.checkedAt || null,
    },
    status: lead.status,
    notizen: (lead.notes || []).map((n) => ({ zeit: n.ts, text: n.text })),
    erfasstAm: lead.createdAt,
  };
}

/**
 * Schickt den Lead an alle aktiven Webhooks.
 * Fehler werden gesammelt zurückgegeben, nicht geworfen - ein defekter
 * Webhook darf die App nicht blockieren.
 */
export async function pushToWebhooks(lead, { only } = {}) {
  const hooks = (getSettings().webhooks || []).filter(
    (h) => h.enabled && h.url && (!only || h.label === only),
  );
  if (hooks.length === 0) {
    return { sent: 0, results: [], hint: 'Keine aktive Übergabe konfiguriert (Einstellungen → Weitergabe).' };
  }

  const payload = toPayload(lead);
  const results = [];

  for (const hook of hooks) {
    try {
      const res = await fetchWithTimeout(
        hook.url,
        {
          method: 'POST',
          headers: {
            'content-type': 'application/json',
            ...(hook.secret ? { authorization: `Bearer ${hook.secret}` } : {}),
          },
          body: JSON.stringify(payload),
        },
        15000,
      );
      const text = (await res.text()).slice(0, 300);
      results.push({
        label: hook.label || hook.url,
        ok: res.ok,
        status: res.status,
        antwort: text,
      });
    } catch (err) {
      results.push({
        label: hook.label || hook.url,
        ok: false,
        fehler: err?.message || String(err),
      });
    }
  }

  return { sent: results.filter((r) => r.ok).length, results };
}
