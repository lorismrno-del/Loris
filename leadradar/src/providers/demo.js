/**
 * Demo-Datenquelle: erfundene Beispielbetriebe, damit die App sofort ohne
 * Internet/API-Key ausprobiert werden kann.
 *
 * WICHTIG: Alle Namen, Nummern und Domains sind frei erfunden (555er-Nummern,
 * .example-Domains). Diese Einträge nie anrufen - sie existieren nicht.
 */

const DEMO = [
  // [name, trade, city, zip, phone, website, email, rating, reviews, monateSeitLetzterBewertung, auditOverride]
  ['Holzbau Brunner GmbH', 'schreiner', 'Uster', '8610', '+41445550101', '', 'info@holzbau-brunner.example', 4.8, 34, 5, 'none'],
  ['Schreinerei Aebischer', 'schreiner', 'Winterthur', '8400', '+41525550112', 'http://schreinerei-aebischer.example', '', 4.6, 21, 14, 'outdated'],
  ['Zimmerei Roth & Söhne', 'schreiner', 'Wetzikon', '8620', '+41445550133', '', '', 4.9, 52, 2, 'none'],
  ['Malergeschäft Kilic', 'maler', 'Dietikon', '8953', '+41445550144', 'http://maler-kilic.example', 'kontakt@maler-kilic.example', 4.4, 18, 9, 'nomobile'],
  ['Gipserei Da Silva', 'maler', 'Zürich', '8005', '+41445550155', '', '', 4.7, 41, 3, 'none'],
  ['Maler Meier AG', 'maler', 'Dübendorf', '8600', '+41445550166', 'https://maler-meier.example', 'info@maler-meier.example', 4.2, 63, 1, 'ok'],
  ['Sanitär Hofmann', 'sanitaer', 'Zürich', '8048', '+41445550177', 'http://sanitaer-hofmann.example', '', 4.5, 27, 22, 'dead'],
  ['Heizungsbau Zellweger', 'sanitaer', 'Bülach', '8180', '+41445550188', '', 'zellweger@heizung.example', 4.9, 15, 7, 'none'],
  ['Spenglerei Cavelti', 'dachdecker', 'Kloten', '8302', '+41445550199', 'http://cavelti-spengler.example', '', 4.3, 12, 31, 'outdated'],
  ['Elektro Vogt GmbH', 'elektriker', 'Horgen', '8810', '+41445550210', '', '', 4.6, 38, 4, 'none'],
  ['Elektrotechnik Bühler', 'elektriker', 'Wädenswil', '8820', '+41445550221', 'http://buehler-elektro.example', 'mail@buehler-elektro.example', 4.1, 9, 18, 'nossl'],
  ['Baugeschäft Marchetti AG', 'bau', 'Zürich', '8055', '+41445550232', 'http://marchetti-bau.example', '', 4.5, 44, 11, 'outdated'],
  ['Maurerbetrieb Kunz', 'bau', 'Uster', '8610', '+41445550243', '', '', 4.8, 19, 6, 'none'],
  ['Gartenbau Steiner', 'gartenbau', 'Wetzikon', '8620', '+41445550254', 'http://steiner-garten.example', 'info@steiner-garten.example', 4.7, 56, 2, 'social'],
  ['Gärtnerei Petrovic', 'gartenbau', 'Dietikon', '8953', '+41445550265', '', '', 4.4, 23, 8, 'none'],
  ['Plattenleger Bertoli', 'bodenleger', 'Winterthur', '8400', '+41525550276', 'http://bertoli-platten.example', '', 4.6, 31, 26, 'outdated'],
  ['Parkett Wüthrich', 'bodenleger', 'Zürich', '8003', '+41445550287', '', 'kontakt@parkett-wuethrich.example', 4.9, 47, 3, 'none'],
  ['Metallbau Schindler & Co.', 'metallbau', 'Bülach', '8180', '+41445550298', 'http://schindler-metallbau.example', '', 4.2, 14, 40, 'dead'],
  ['Schlosserei Trüb', 'metallbau', 'Dübendorf', '8600', '+41445550309', '', '', 4.5, 8, 15, 'none'],
  ['Storen Fankhauser', 'fenster', 'Horgen', '8810', '+41445550320', 'http://storen-fankhauser.example', 'info@storen-fankhauser.example', 4.8, 29, 5, 'nomobile'],
  ['Glaserei Hodzic', 'fenster', 'Zürich', '8004', '+41445550331', '', '', 4.3, 11, 20, 'none'],
  ['Küchenwerkstatt Lang', 'kuechenbau', 'Uster', '8610', '+41445550342', 'https://kuechen-lang.example', 'info@kuechen-lang.example', 4.9, 72, 1, 'ok'],
  ['Umzüge Krasniqi', 'umzug', 'Zürich', '8050', '+41445550353', 'http://umzuege-krasniqi.example', '', 4.0, 26, 12, 'nossl'],
  ['Gebäudereinigung Sutter', 'umzug', 'Winterthur', '8400', '+41525550364', '', 'sutter@reinigung.example', 4.6, 17, 9, 'none'],
];

const CITY_COORDS = {
  'Zürich': [47.3769, 8.5417],
  'Winterthur': [47.5, 8.7241],
  'Uster': [47.3474, 8.7204],
  'Dübendorf': [47.3971, 8.6187],
  'Dietikon': [47.4017, 8.4004],
  'Wetzikon': [47.3264, 8.7981],
  'Horgen': [47.2597, 8.5983],
  'Bülach': [47.5211, 8.5397],
  'Wädenswil': [47.2296, 8.6739],
  'Kloten': [47.4517, 8.585],
};

/** Vorgefertigte Audit-Ergebnisse, damit die Demo realistisch aussieht. */
function demoAudit(kind, website) {
  const now = Date.now();
  const base = {
    checkedAt: new Date(now).toISOString(),
    finalUrl: website,
    demo: true,
  };
  switch (kind) {
    case 'none':
      return { ...base, status: 'none', finalUrl: '' };
    case 'dead':
      return { ...base, status: 'dead', reason: 'dns', httpStatus: null };
    case 'outdated':
      return {
        ...base, status: 'ok', httpStatus: 200, https: false, hasViewport: false,
        copyrightYear: 2014, responseMs: 2400, pageBytes: 1_800_000,
        hasImpressum: false, hasContactForm: false, techFlags: ['tabellen-layout', 'jquery-1.x'],
      };
    case 'nomobile':
      return {
        ...base, status: 'ok', httpStatus: 200, https: true, hasViewport: false,
        copyrightYear: 2020, responseMs: 1600, pageBytes: 900_000,
        hasImpressum: true, hasContactForm: false, techFlags: [],
      };
    case 'nossl':
      return {
        ...base, status: 'ok', httpStatus: 200, https: false, hasViewport: true,
        copyrightYear: 2021, responseMs: 1100, pageBytes: 700_000,
        hasImpressum: true, hasContactForm: true, techFlags: [],
      };
    case 'social':
      return { ...base, status: 'social_only', httpStatus: 200, https: true };
    case 'ok':
    default:
      return {
        ...base, status: 'ok', httpStatus: 200, https: true, hasViewport: true,
        copyrightYear: new Date().getFullYear(), responseMs: 420, pageBytes: 480_000,
        hasImpressum: true, hasContactForm: true, techFlags: [],
      };
  }
}

export function searchDemo({ trades, limit = 200 }) {
  const wanted = new Set(trades && trades.length ? trades : DEMO.map((r) => r[1]));
  const out = [];
  const monthMs = 30 * 24 * 3600 * 1000;

  DEMO.forEach((row, i) => {
    const [name, trade, city, zip, phone, website, email, rating, reviews, monthsAgo, kind] = row;
    if (!wanted.has(trade)) return;
    const [lat, lng] = CITY_COORDS[city] || [47.3769, 8.5417];

    out.push({
      id: `demo:${i}`,
      source: 'demo',
      sourceUrl: '',
      name,
      trade,
      address: { street: `Musterweg ${i + 1}`, zip, city, canton: 'ZH', country: 'CH' },
      lat: lat + (i % 7) * 0.004,
      lng: lng + (i % 5) * 0.005,
      phone,
      email,
      website,
      socials: kind === 'social' ? { facebook: 'https://facebook.com/beispielbetrieb' } : {},
      openingHours: 'Mo-Fr 07:00-17:00',
      googleRating: rating,
      googleReviews: reviews,
      googleMapsUrl: '',
      lastActivityAt: new Date(Date.now() - monthsAgo * monthMs).toISOString(),
      audit: demoAudit(kind, website),
      isDemo: true,
    });
  });

  return out.slice(0, limit);
}
