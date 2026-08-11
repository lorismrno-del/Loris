/**
 * Gesprächsleitfaden, E-Mail- und WhatsApp-Vorlagen - automatisch auf das
 * konkrete Problem des Betriebs zugeschnitten und mit den echten
 * Verkaufsargumenten von Lorino Co. bestückt.
 *
 * Ziel: Loris klickt auf einen Lead und weiss in 3 Sekunden, was er sagen soll.
 */
import { getSettings } from './settings.js';
import { tradeLabel } from './trades.js';

/**
 * Der Aufhänger - der eine Satz, der das Gespräch eröffnet.
 * Wird aus dem Ergebnis der Website-Analyse abgeleitet.
 */
function hook(lead) {
  const a = lead.audit || {};
  const ort = lead.address?.city || 'Ihrer Region';
  const branche = tradeLabel(lead.trade).split(/[ &/]/)[0];

  switch (a.status) {
    case 'none':
      return {
        opener: 'ich habe gesehen, dass Sie auf Google gut gefunden werden – aber noch keine eigene Webseite haben.',
        problem: `Wer Sie googelt, sieht aktuell nur den Kartenausschnitt. Keine Bilder Ihrer Arbeiten, keine Referenzen, kein Kontaktformular.`,
        value: `Über 80 % der Leute schauen online nach, bevor sie einen ${branche} anrufen. Ihre Konkurrenz in ${ort} hat eine Seite – genau dort gehen Ihnen Anfragen verloren.`,
        subject: `${lead.name} – Sie haben noch keine Webseite?`,
      };
    case 'dead':
      return {
        opener: `ich wollte Ihre Webseite ${cleanHost(lead.website)} anschauen – die ist gerade nicht erreichbar. Wussten Sie das?`,
        problem: `${a.summary || 'Die Seite lädt nicht.'} Für jeden, der Sie googelt, sieht das aus, als gäbe es Ihren Betrieb nicht mehr.`,
        value: 'Das ist der teuerste Fehler überhaupt: Sie zahlen vermutlich noch fürs Hosting, bekommen aber null Anfragen darüber.',
        subject: `Ihre Webseite ${cleanHost(lead.website)} ist offline`,
      };
    case 'parked':
      return {
        opener: `ich habe Ihre Domain ${cleanHost(lead.website)} aufgerufen – da steht nur eine Platzhalterseite.`,
        problem: 'Die Domain ist reserviert, aber es gibt keinen Inhalt dahinter. Interessenten springen sofort wieder ab.',
        value: 'Die Domain haben Sie ja schon – es fehlt nur die Webseite dazu. Das ist schneller gemacht, als Sie denken.',
        subject: `${cleanHost(lead.website)} zeigt nur eine Platzhalterseite`,
      };
    case 'social_only':
      return {
        opener: 'ich sehe, Sie sind auf Social Media aktiv – haben aber keine eigene Webseite.',
        problem: 'Wer Sie über Google sucht – und das sind die Kunden mit konkretem Auftrag – landet im Leeren. Facebook und Instagram ranken bei Google praktisch nicht.',
        value: 'Ihre Fotos und Referenzen haben Sie ja bereits. Die gehören nur noch auf eine Seite, die Ihnen selbst gehört.',
        subject: `${lead.name} – auf Instagram gefunden, auf Google nicht`,
      };
    case 'directory_only':
      return {
        opener: 'ich habe gesehen, dass man Sie online eigentlich nur über local.ch findet.',
        problem: 'Dort stehen Sie zwischen zwanzig Mitbewerbern in derselben Liste – ohne Bilder, ohne Ihre Handschrift, ohne Referenzen.',
        value: 'Eine eigene Seite hebt Sie da sofort heraus – und die Anfragen kommen direkt zu Ihnen statt über ein Portal.',
        subject: `${lead.name} – nur auf local.ch gefunden`,
      };
    case 'ok': {
      if (a.hasViewport === false) {
        return {
          opener: 'ich habe Ihre Webseite auf dem Handy geöffnet – und musste ziemlich zoomen, um überhaupt etwas zu lesen.',
          problem: 'Über 60 % Ihrer Besucher kommen vom Smartphone. Die Seite ist dafür schlicht nicht gebaut.',
          value: 'Google stuft mobil unbrauchbare Seiten zusätzlich ab – Sie verlieren also doppelt: bei den Besuchern und beim Ranking.',
          subject: 'Ihre Webseite auf dem Handy – kurz angeschaut',
        };
      }
      if (a.sslBroken || a.https === false) {
        return {
          opener: 'bei Ihrer Webseite zeigt der Browser aktuell die Warnung "Nicht sicher" an.',
          problem: 'Chrome blendet das bei jedem Besucher gross ein. Ein grosser Teil klickt sofort wieder weg – gerade ältere Kunden.',
          value: 'Das lässt sich beheben. Meistens lohnt es sich, gleich die ganze Seite mitzunehmen, statt nur das Zertifikat zu flicken.',
          subject: 'Ihre Webseite zeigt "Nicht sicher" an',
        };
      }
      if (lead.websiteAgeYears >= 3) {
        return {
          opener: `ich habe Ihre Webseite angeschaut – im Footer steht noch ${a.copyrightYear}.`,
          problem: 'Eine Seite, die jahrelang nicht angefasst wurde, wirkt schnell so, als wäre der Betrieb gar nicht mehr aktiv.',
          value: `Dabei sind Sie mit ${lead.googleReviews ? lead.googleReviews + ' Bewertungen' : 'Ihren Bewertungen'} offensichtlich sehr gefragt – das sollte man Ihrer Seite auch ansehen.`,
          subject: 'Kurzes Feedback zu Ihrer Webseite',
        };
      }
      if (a.hasContactForm === false) {
        return {
          opener: 'ich habe Ihre Webseite angeschaut – mir ist aufgefallen, dass es kein Kontaktformular gibt.',
          problem: 'Wer abends um 21 Uhr auf Ihrer Seite landet, will nicht anrufen. Ohne Formular ist der Interessent weg.',
          value: 'Ein Formular mit WhatsApp-Anbindung fängt genau diese Anfragen ab – rund um die Uhr.',
          subject: 'Ihre Webseite – eine Sache ist mir aufgefallen',
        };
      }
      return {
        opener: 'ich habe Ihre Webseite angeschaut – die macht grundsätzlich einen soliden Eindruck.',
        problem: 'Mir ist trotzdem aufgefallen, dass beim Thema Anfragen noch Luft nach oben ist.',
        value: `Für ${branche}betriebe in ${ort} hole ich da normalerweise noch einiges heraus.`,
        subject: 'Kurzes Feedback zu Ihrer Webseite',
      };
    }
    default:
      return {
        opener: `ich bin bei der Suche nach ${branche}betrieben in ${ort} auf Sie gestossen.`,
        problem: 'Mir ist aufgefallen, dass Ihr Online-Auftritt noch Potenzial hat.',
        value: 'Da kann ich Ihnen sehr wahrscheinlich helfen.',
        subject: `Kurze Frage zu ${lead.name}`,
      };
  }
}

/** Vollständiger Gesprächsleitfaden fürs Telefon. */
export function callScript(lead) {
  const h = hook(lead);
  const s = getSettings();
  const agentur = s.agencyName.replace(/[.\s]+$/, "");
  const preview = s.freePreview ? s.freePreviewLine : '';

  const steps = [
    {
      title: '1 · Einstieg',
      hint: '10 Sekunden. Ruhig sprechen, dann kurz warten.',
      text: `Grüezi, ${s.ownerName} von ${agentur}. Störe ich gerade mitten in der Arbeit?\n\n— Antwort abwarten —\n\nIch mache Webseiten für Handwerks- und Baubetriebe hier in der Region, und ${h.opener}`,
    },
    {
      title: '2 · Problem benennen',
      hint: 'Nicht verkaufen. Nur zeigen, was Sie gesehen haben.',
      text: h.problem,
    },
    {
      title: '3 · Konsequenz aufzeigen',
      hint: 'Was kostet ihn das? Kurz halten.',
      text: h.value,
    },
    {
      title: '4 · Die Frage',
      hint: 'Ziel ist der Termin, nicht der Verkauf.',
      text: `Ich habe da ein paar konkrete Ideen für Sie. ${
        s.freePreview
          ? 'Und das Beste: ' + preview + ' '
          : ''
      }Passt es Ihnen, wenn wir das in 15 Minuten unverbindlich anschauen? Geht diese Woche noch – oder ist nächste Woche besser?`,
    },
    {
      title: '5 · Einwände',
      hint: 'Nicht auswendig lernen – nur überfliegen.',
      text: [
        `"Keine Zeit."\n→ Verstehe ich, Sie sind auf der Baustelle. Genau darum mache ich das komplett für Sie – Sie liefern mir am Ende nur ein paar Fotos. Das Gespräch selbst dauert 15 Minuten.`,
        `"Zu teuer."\n→ Darf ich fragen, mit welchem Betrag Sie rechnen? ${
          s.freePreview
            ? 'Und ganz ehrlich: Sie sehen die fertige Seite, bevor Sie einen Franken zahlen. Wenn sie Ihnen nicht gefällt, kostet es Sie nichts.'
            : 'Ein einziger zusätzlicher Auftrag zahlt das meistens schon.'
        }`,
        `"Hab schon eine Webseite."\n→ Ja, die habe ich mir angeschaut – genau darüber wollte ich mit Ihnen reden. Darf ich Ihnen kurz sagen, was mir aufgefallen ist?`,
        `"Schicken Sie mir Unterlagen."\n→ Mache ich gerne. Damit ich nichts Unpassendes schicke: Was wäre Ihnen wichtiger – mehr Kundenanfragen oder mehr Bewerbungen von Mitarbeitern?`,
        `"Mein Neffe/Sohn macht das."\n→ Perfekt, dann haben Sie ja jemanden. Wie lange läuft das Projekt schon? … Falls es doch stockt: Ich zeige Ihnen unverbindlich eine Vorschau, dann haben Sie einen Vergleich.`,
        `"Kein Interesse."\n→ Alles klar, dann will ich Sie nicht aufhalten. Darf ich Ihnen kurz per WhatsApp schicken, was mir aufgefallen ist? Dann haben Sie es schriftlich, falls es später doch ein Thema wird.`,
      ].join('\n\n'),
    },
    {
      title: '6 · Abschluss',
      hint: 'Termin bestätigen, Kanal nennen.',
      text: `Super, dann halte ich {Termin} fest. Ich schicke Ihnen gleich eine kurze Bestätigung per ${
        lead.email || lead.customEmail ? 'E-Mail' : 'WhatsApp'
      }. Merci und bis dann!`,
    },
  ];

  return { steps, facts: buildFacts(lead), usps: s.usps, process: s.processSteps };
}

/** Die Fakten, die während des Gesprächs sichtbar sein sollten. */
function buildFacts(lead) {
  const a = lead.audit || {};
  const facts = [];

  if (lead.googleReviews) {
    facts.push(`Google: ${lead.googleRating}★ aus ${lead.googleReviews} Bewertungen`);
  }
  if (lead.inactiveYears >= 2) {
    facts.push(`Letzte Google-Bewertung vor ${lead.inactiveYears} Jahren`);
  }
  if (a.status === 'ok') {
    if (a.copyrightYear) facts.push(`Footer der Webseite sagt: © ${a.copyrightYear}`);
    if (a.hasViewport === false) facts.push('Nicht mobiltauglich (kein Viewport-Tag)');
    if (a.https === false) facts.push('Läuft über http:// statt https://');
    if (a.responseMs) facts.push(`Ladezeit der Startseite: ${(a.responseMs / 1000).toFixed(1)} s`);
    if (a.hasContactForm === false) facts.push('Kein Kontaktformular gefunden');
    if (a.hasImpressum === false) facts.push('Kein Impressum gefunden');
    if (a.techFlags?.length) facts.push('Technik: ' + a.techFlags.join(', '));
    if (a.title) facts.push(`Seitentitel: "${a.title.slice(0, 80)}"`);
  }
  if (lead.openingHours) facts.push('Öffnungszeiten: ' + lead.openingHours);
  if (lead.distanceKm != null) facts.push(`${lead.distanceKm} km vom Suchmittelpunkt`);

  return facts;
}

/** E-Mail-Vorlage (Betreff + Text). */
export function emailTemplate(lead) {
  const h = hook(lead);
  const s = getSettings();
  const ort = lead.address?.city || '';
  const anrede = lead.contactName ? `Grüezi ${lead.contactName}` : 'Grüezi';

  const body = `${anrede}

mein Name ist ${s.ownerName}, ich baue Webseiten für Bau- und Handwerksbetriebe${ort ? ' in der Region ' + ort : ''}.

${capitalize(h.opener)}

${h.problem}

${h.value}

${
  s.freePreview
    ? s.freePreviewLine + '\n\nSie gehen also null Risiko ein.'
    : 'Gerne zeige ich Ihnen unverbindlich, was möglich wäre.'
}

Hätten Sie diese oder nächste Woche 15 Minuten Zeit für ein kurzes Gespräch?${
    s.bookingUrl ? `\n\nDirekt einen Termin auswählen: ${s.bookingUrl}` : ''
  }

Freundliche Grüsse
${s.ownerName}
${s.agencyName} · ${s.slogan}
${s.phone} · ${s.email}
${s.website}

---
Sie erhalten diese Nachricht, weil ich Ihren Betrieb online recherchiert habe. Wenn Sie keine weitere Nachricht wünschen, antworten Sie kurz mit "Stopp" – dann melde ich mich nicht mehr.`;

  return { subject: h.subject, body };
}

/** Kurze WhatsApp-Nachricht (Handwerker antworten darauf oft am schnellsten). */
export function whatsappTemplate(lead) {
  const h = hook(lead);
  const s = getSettings();
  return (
    `Grüezi, ${s.agencyName.replace(/[.\s]+$/, "")} hier – ${s.ownerName}. ${capitalize(h.opener)} ` +
    `${h.problem} ` +
    `${s.freePreview ? 'Ich mache Ihnen gerne eine kostenlose Vorschau – Sie sehen die Seite fertig, bevor Sie etwas zahlen. ' : ''}` +
    `Hätten Sie diese Woche 15 Minuten? Merci! – ${s.phone}`
  );
}

/** Kurze SMS-Variante (falls WhatsApp nicht vorhanden). */
export function smsTemplate(lead) {
  const h = hook(lead);
  const s = getSettings();
  return `${s.agencyName}: Grüezi, ${capitalize(h.opener)} Kostenlose Vorschau möglich – Sie zahlen erst, wenn sie Ihnen gefällt. Kurz Zeit? ${s.phone} (${s.ownerName})`;
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function cleanHost(url) {
  if (!url) return 'Ihre Webseite';
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return url;
  }
}

/**
 * Rechtliche Hinweise für die Schweiz - werden im UI angezeigt.
 * Orientierungshilfe, keine Rechtsberatung.
 */
export const LEGAL_NOTES = [
  {
    title: 'Telefon-Kaltakquise B2B',
    text: 'In der Schweiz grundsätzlich erlaubt – ABER: Wer im Telefonbuch einen Stern-Eintrag (*) hat, will keine Werbeanrufe. Solche Anrufe verstossen gegen Art. 3 Abs. 1 lit. u UWG. Vor dem Anruf kurz auf local.ch oder search.ch prüfen – dort ist der Stern sichtbar.',
  },
  {
    title: 'Kalte Werbe-E-Mails',
    text: 'Art. 3 Abs. 1 lit. o UWG verbietet Massenwerbung ohne Einwilligung. Einzelne, individuell geschriebene B2B-Mails mit klarem Bezug zum Betrieb sind die deutlich sicherere Variante – und funktionieren ohnehin besser. Absender, Adresse und Abmeldemöglichkeit gehören immer dazu (ist in der Vorlage enthalten).',
  },
  {
    title: 'Datenschutz (revDSG)',
    text: 'Daten juristischer Personen fallen nicht unter das DSG. Sobald Sie Namen von Ansprechpersonen erfassen, gilt es: nur speichern, was Sie brauchen, und auf Verlangen löschen. Diese App speichert alles lokal auf Ihrem Rechner – nichts geht an Dritte.',
  },
  {
    title: 'Datenquellen',
    text: 'OpenStreetMap steht unter ODbL (Namensnennung nötig, falls Sie die Daten veröffentlichen). Google-Places-Daten dürfen nur begrenzt zwischengespeichert werden – für die eigene Akquiseliste unproblematisch, ein Weiterverkauf wäre es nicht.',
  },
  {
    title: 'Nach dem "Nein"',
    text: 'Setzen Sie den Lead sofort auf "Nicht kontaktieren". Die App blendet ihn dann aus allen Anruflisten aus und markiert ihn dauerhaft rot – so rufen Sie niemanden versehentlich zweimal an.',
  },
];
