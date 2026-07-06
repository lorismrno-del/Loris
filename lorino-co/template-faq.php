<?php /* Template Name: FAQ */ get_header(); ?>

<section style="padding-top:60px;" class="blob-wrap">
  <div class="blob blob-green"></div>
  <div class="container">
    <div class="page-intro">
      <div>
        <h1 class="section-title">Häufige Fragen</h1>
        <p class="section-lead" style="max-width:70ch;">Hier finden Sie Antworten auf die Fragen, die mir am häufigsten gestellt werden. Ist Ihre Frage nicht dabei? Melden Sie sich einfach direkt bei mir.</p>
      </div>
      <div class="hero-illustration hero-illustration-sm" style="background:linear-gradient(135deg,#f0fdf4 0%,#dcfce7 100%);">
        <?php echo lorino_image('lorino_img_faq', 'faq_0_transparent.png', 'Illustration FAQ'); ?>
      </div>
    </div>
    <div class="grid-3" style="grid-template-columns: 1fr; margin-top:32px;">
      <div class="card">
        <h3>Wie läuft ein Projekt ab?</h3>
        <p>In klar strukturierten Schritten — von der Kontaktaufnahme bis zur laufenden Betreuung. Details finden Sie auf unserer <a href="<?php echo home_url('/ablauf'); ?>" style="color:#2563eb; font-weight:600;">Ablauf-Seite</a>.</p>
      </div>
      <div class="card">
        <h3>Erhalte ich zuerst eine Vorschau?</h3>
        <p>Ja. Sie sehen Ihre Website, bevor Sie sich entscheiden — kostenlos und unverbindlich. Erst wenn Sie überzeugt sind, geht es weiter.</p>
      </div>
      <div class="card">
        <h3>Sind die Webseiten mobil optimiert?</h3>
        <p>Selbstverständlich. Jede Website wird für alle Geräte optimiert — Mobile-First, da über 60% der Besucher vom Smartphone kommen.</p>
      </div>
      <div class="card">
        <h3>Was kostet eine Webseite?</h3>
        <p>Das hängt vom Umfang ab. Nach einem kurzen, kostenlosen Beratungsgespräch erhalten Sie ein individuelles, unverbindliches Angebot — ohne versteckte Kosten.</p>
      </div>
      <div class="card">
        <h3>Wie lange dauert die Umsetzung?</h3>
        <p>Je nach Umfang zwischen einer und drei Wochen. Kleinere Anpassungen sind oft schon innerhalb weniger Tage möglich.</p>
      </div>
      <div class="card">
        <h3>Muss ich mich um Hosting und Technik kümmern?</h3>
        <p>Nein. Ich übernehme Hosting, Sicherheit und Updates — Sie konzentrieren sich ganz auf Ihr Handwerk.</p>
      </div>
      <div class="card">
        <h3>Kann ich Inhalte später selbst ändern?</h3>
        <p>Ja, auf Wunsch richte ich Ihnen ein einfaches System ein, mit dem Sie Texte und Bilder selbst aktualisieren können. Alternativ übernehme ich Anpassungen für Sie.</p>
      </div>
      <div class="card">
        <h3>Arbeiten Sie auch mit Betrieben ausserhalb der Baubranche?</h3>
        <p>Mein Fokus liegt klar auf Bauunternehmen und Handwerksbetrieben, da ich mich hier am besten auskenne — aber sprechen Sie mich gerne an.</p>
      </div>
    </div>
    <div style="text-align:center; margin-top:48px;">
      <a href="<?php echo home_url('/kontakt'); ?>" class="btn-primary">Frage nicht dabei? Kontaktieren Sie uns →</a>
    </div>
  </div>
</section>

<?php get_footer(); ?>
