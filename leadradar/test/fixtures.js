/**
 * Testseiten: bilden die Fälle nach, die in der Praxis vorkommen.
 * Wird von analyzer.test.js gestartet.
 */
import http from 'node:http';

export const PAGES = {
  // Klassische Handwerker-Seite von 2013: Tabellen-Layout, kein Viewport
  '/alt': {
    type: 'text/html; charset=iso-8859-1',
    body: `<html><head><title>Schreinerei Muster - Ihr Partner</title>
<meta name="generator" content="Microsoft FrontPage 6.0"></head>
<body bgcolor="#ffffff">
<table width="800" border="0"><tr><td>
<font face="Arial" size="2" color="#000000">Willkommen bei der Schreinerei Muster</font>
<table width="600" border="1"><tr><td>Wir fertigen Möbel nach Mass seit 1978.
Unsere Werkstatt befindet sich in Musterwil. Rufen Sie uns an unter 044 555 00 00
oder schreiben Sie an <a href="mailto:info@schreinerei-muster.example">info@schreinerei-muster.example</a>.
Wir freuen uns auf Ihre Anfrage. Diese Seite ist optimiert für Internet Explorer 6.</td></tr></table>
<script src="js/jquery-1.4.2.min.js"></script>
<p>&copy; 2013 Schreinerei Muster</p>
</td></tr></table></body></html>`,
  },

  // Moderne, gepflegte Seite - hier soll KEIN Bedarf erkannt werden
  '/modern': {
    type: 'text/html; charset=utf-8',
    body: `<html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Muster Gartenbau AG – Gartenpflege und Neuanlagen in Winterthur</title>
<meta name="description" content="Ihr Gartenbaubetrieb in Winterthur. Neuanlagen, Unterhalt und Baumpflege.">
</head><body>
<header><nav><a href="/leistungen">Leistungen</a><a href="/kontakt">Kontakt</a>
<a href="/impressum">Impressum</a></nav></header>
<main><h1>Ihr Garten in besten Händen</h1>
<p>Seit 2004 gestalten und pflegen wir Gärten in der Region Winterthur. Von der Neuanlage
über den regelmässigen Unterhalt bis zur fachgerechten Baumpflege übernehmen wir alles
aus einer Hand. Unser Team besteht aus zwölf ausgebildeten Landschaftsgärtnern.</p>
<form action="/anfrage" method="post">
<input type="text" name="name"><input type="email" name="email">
<textarea name="nachricht"></textarea><button>Senden</button></form>
<a href="https://www.instagram.com/muster_gartenbau">Instagram</a>
</main>
<footer><p>© ${new Date().getFullYear()} Muster Gartenbau AG · <a href="mailto:info@muster-gartenbau.example">info@muster-gartenbau.example</a></p></footer>
</body></html>`,
  },

  // Geparkte Domain
  '/parkiert': {
    type: 'text/html',
    body: `<html><head><title>Domain</title></head><body>
<h1>Diese Domain wurde registriert</h1><p>Website coming soon.</p></body></html>`,
  },

  // Seite mit verschleierter E-Mail + Kontaktseite
  '/versteckt': {
    type: 'text/html; charset=utf-8',
    body: `<html><head><meta name="viewport" content="width=device-width">
<title>Malerei Beispiel GmbH</title></head><body>
<h1>Malerei Beispiel</h1>
<p>Wir sind Ihr Malergeschäft in der Region. Innen- und Aussenanstriche, Tapezierarbeiten
und Fassadensanierungen gehören zu unserem Angebot. Unser Betrieb existiert seit 1995 und
beschäftigt heute acht Mitarbeitende.</p>
<a href="/kontaktseite">Kontakt</a>
<p>© 2019 Malerei Beispiel GmbH</p></body></html>`,
  },
  '/kontaktseite': {
    type: 'text/html; charset=utf-8',
    body: `<html><head><title>Kontakt</title></head><body><h1>Impressum &amp; Kontakt</h1>
<p>Schreiben Sie uns: buero (at) malerei-beispiel (dot) example</p>
<p>Telefon 044 555 12 34</p></body></html>`,
  },

  // Nur Weiterleitung auf Facebook
  '/nurfacebook': { redirect: 'https://www.facebook.com/beispielbetrieb' },

  // Fehlerseite
  '/tot': { status: 404, type: 'text/html', body: '<h1>404 Not Found</h1>' },
};

export function startFixtureServer(port = 3199) {
  const server = http.createServer((req, res) => {
    const page = PAGES[req.url.split('?')[0]];
    if (!page) {
      res.writeHead(404, { 'content-type': 'text/html' });
      return res.end('<h1>404</h1>');
    }
    if (page.redirect) {
      res.writeHead(302, { location: page.redirect });
      return res.end();
    }
    res.writeHead(page.status || 200, {
      'content-type': page.type || 'text/html',
      'last-modified': 'Tue, 14 May 2013 09:00:00 GMT',
    });
    res.end(page.body);
  });
  return new Promise((resolve) => server.listen(port, '127.0.0.1', () => resolve(server)));
}
