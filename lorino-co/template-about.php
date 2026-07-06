<?php /* Template Name: Über mich */ get_header(); ?>

<section style="padding-top:60px;" class="blob-wrap">
  <div class="blob blob-blue"></div>
  <div class="container about-grid">
    <div class="about-image" style="position:relative;">
      <?php echo lorino_image('lorino_img_about', 'loris-portrait.jpg', 'Loris - Gründer von Lorino Co.'); ?>
      <div class="floating-badge" style="bottom:8px; right:8px;">
        <div class="badge-icon">🚀</div>
        <div>Gründer &amp;<br><span style="font-weight:400; color:#64748b;">Webdesigner</span></div>
      </div>
    </div>
    <div>
      <span class="eyebrow"><span class="dot"></span> Der Mensch hinter Lorino Co.</span>
      <h1 class="section-title">Über mich</h1>
      <p style="color:#475569; font-size:17px; margin-bottom:16px;">Mein Name ist Loris, Gründer von Lorino Co. Als Webagentur mit Fokus auf Bauunternehmen und Handwerksbetriebe in der Schweiz ist es meine Mission, kleinen und mittleren Betrieben zu einem professionellen, modernen Online-Auftritt zu verhelfen — ohne Baukasten, ohne Vorlage, sondern individuell auf jedes Unternehmen zugeschnitten.</p>
      <p style="color:#475569; font-size:17px; margin-bottom:16px;">Ich habe Lorino Co. gegründet, weil ich immer wieder gesehen habe, wie viele hervorragende Handwerksbetriebe online unsichtbar bleiben — nur weil ihre Webseite veraltet ist oder ganz fehlt. Mein Ziel ist es, das zu ändern: mit Webseiten, die nicht nur gut aussehen, sondern messbar mehr Kundenanfragen bringen.</p>
      <p style="color:#475569; font-size:17px; margin-bottom:24px;">Persönliche Betreuung, klare Kommunikation und langfristige Partnerschaften stehen dabei für mich an erster Stelle — von der ersten Beratung bis zur laufenden Betreuung Ihrer Webseite.</p>
      <a href="<?php echo home_url('/kontakt'); ?>" class="btn-primary">Lernen wir uns kennen →</a>
    </div>
  </div>
</section>

<!-- MEINE GESCHICHTE -->
<section>
  <div class="container" style="max-width:800px;">
    <h2 class="section-title">Meine Geschichte</h2>
    <p style="color:#475569; font-size:17px; margin-bottom:16px;">Alles begann mit einer einfachen Beobachtung: Ich sah Bauunternehmen und Handwerksbetriebe, die technisch und handwerklich Spitzenarbeit leisten — aber online praktisch unsichtbar waren. Veraltete Webseiten, fehlende Kontaktmöglichkeiten, kein Vertrauen auf den ersten Blick. Kunden wanderten ab, bevor sie überhaupt angerufen hatten.</p>
    <p style="color:#475569; font-size:17px; margin-bottom:16px;">Diese Lücke wollte ich schliessen. Nicht mit 08/15-Baukästen, sondern mit echten, durchdachten Webseiten, die verstehen, was Bauunternehmen wirklich brauchen: Vertrauen, Klarheit und eine einfache Möglichkeit für Kunden, Kontakt aufzunehmen.</p>
    <p style="color:#475569; font-size:17px;">Heute arbeite ich mit Leidenschaft an jedem einzelnen Projekt — weil ich weiss, dass hinter jeder Webseite ein echter Betrieb mit echten Menschen steht, die es verdienen, online genauso überzeugend aufzutreten wie auf der Baustelle.</p>
  </div>
</section>

<!-- WERTE -->
<section class="bg-slate blob-wrap">
  <div class="blob blob-gold"></div>
  <div class="container">
    <h2 class="section-title">Meine Werte</h2>
    <p class="section-lead">Das, wofür ich stehe — bei jedem Projekt, ohne Kompromisse.</p>
    <div class="grid-3">
      <div class="card">
        <div class="icon">❤️</div>
        <h3>Leidenschaft</h3>
        <p>Ich mache diesen Job nicht, weil ich muss, sondern weil ich brenne für gutes Design und echte Ergebnisse für meine Kunden.</p>
      </div>
      <div class="card">
        <div class="icon">🤝</div>
        <h3>Ehrlichkeit</h3>
        <p>Klare Kommunikation, ehrliche Preise, keine versteckten Kosten. Was ich verspreche, halte ich auch.</p>
      </div>
      <div class="card">
        <div class="icon">🎯</div>
        <h3>Ergebnisorientierung</h3>
        <p>Eine schöne Webseite allein reicht nicht — sie muss auch funktionieren und Ihnen echte Kunden bringen.</p>
      </div>
    </div>
  </div>
</section>

<!-- WARUM LORINO TEASER -->
<section>
  <div class="container">
    <h2 class="section-title">Warum Lorino Co.?</h2>
    <div class="advantages-list">
      <div class="advantage-item"><span class="check">✓</span> Spezialisiert auf Baubranche</div>
      <div class="advantage-item"><span class="check">✓</span> Keine Standardvorlagen</div>
      <div class="advantage-item"><span class="check">✓</span> Kostenlose Website-Vorschau</div>
      <div class="advantage-item"><span class="check">✓</span> Persönliche Betreuung</div>
      <div class="advantage-item"><span class="check">✓</span> Mobile Optimierung</div>
      <div class="advantage-item"><span class="check">✓</span> Langfristige Partnerschaft</div>
    </div>
    <div style="text-align:center; margin-top:32px;">
      <a href="<?php echo home_url('/warum-lorino'); ?>" class="btn-secondary">Alle Vorteile ansehen →</a>
    </div>
  </div>
</section>

<section style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); text-align:center;">
  <div class="container">
    <h2 class="section-title" style="color:#fff;">Lassen Sie uns Ihr Projekt besprechen</h2>
    <p class="section-lead" style="margin-left:auto; margin-right:auto; color:#cbd5e1;">Ich freue mich darauf, Sie und Ihren Betrieb kennenzulernen.</p>
    <a href="<?php echo home_url('/kontakt'); ?>" class="btn-primary" style="background:#f59e0b; color:#0f172a;">Jetzt Kontakt aufnehmen →</a>
  </div>
</section>

<?php get_footer(); ?>
