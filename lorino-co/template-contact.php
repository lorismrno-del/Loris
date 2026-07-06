<?php
/* Template Name: Kontakt */

// Kontaktformular verarbeiten und per E-Mail an die Geschäftsadresse senden
$lorino_form_message = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['lorino_contact_submit'])) {
    if (!wp_verify_nonce($_POST['lorino_contact_nonce'] ?? '', 'lorino_contact_form')) {
        $lorino_form_message = 'error';
    } elseif (!empty($_POST['website_url'])) {
        $lorino_form_message = ''; // Bot erkannt, stillschweigend ignorieren
    } else {
        $name    = sanitize_text_field($_POST['name'] ?? '');
        $email   = sanitize_email($_POST['email'] ?? '');
        $phone   = sanitize_text_field($_POST['phone'] ?? '');
        $message = sanitize_textarea_field($_POST['message'] ?? '');

        if ($name && $email && $message) {
            $to      = 'info@lorinoweb.ch';
            $subject = 'Neue Anfrage über die Webseite von ' . $name;
            $body    = "Name: $name\nE-Mail: $email\nTelefon: $phone\n\nNachricht:\n$message";
            $headers = array('Content-Type: text/plain; charset=UTF-8', 'Reply-To: ' . $email);

            if (wp_mail($to, $subject, $body, $headers)) {
                $lorino_form_message = 'success';
            } else {
                $lorino_form_message = 'error';
            }
        } else {
            $lorino_form_message = 'incomplete';
        }
    }
}

get_header();
?>

<section style="padding-top:60px;" class="blob-wrap">
  <div class="blob blob-blue"></div>
  <div class="container">
    <div class="page-intro">
      <div>
        <h1 class="section-title">Jetzt Kontakt aufnehmen</h1>
        <p class="section-lead">Kostenlose Beratung, unverbindlich und ohne Risiko.</p>
      </div>
      <div class="hero-illustration hero-illustration-sm" style="background:linear-gradient(135deg,#eff6ff 0%,#dbeafe 100%);">
        <?php echo lorino_image('lorino_img_contact', 'contact_0_transparent.png', 'Illustration Kontakt'); ?>
      </div>
    </div>
    <div class="contact-grid">
      <div>
        <?php if ($lorino_form_message === 'success'): ?>
          <div style="padding:16px 20px; background:#f0fdf4; border:1px solid #bbf7d0; color:#166534; border-radius:12px; margin-bottom:16px; font-weight:600;">
            ✓ Vielen Dank! Ihre Nachricht wurde erfolgreich gesendet.
          </div>
        <?php elseif ($lorino_form_message === 'error'): ?>
          <div style="padding:16px 20px; background:#fef2f2; border:1px solid #fecaca; color:#991b1b; border-radius:12px; margin-bottom:16px; font-weight:600;">
            Leider gab es ein technisches Problem. Bitte kontaktieren Sie uns direkt per WhatsApp oder Telefon.
          </div>
        <?php elseif ($lorino_form_message === 'incomplete'): ?>
          <div style="padding:16px 20px; background:#fffbeb; border:1px solid #fde68a; color:#92400e; border-radius:12px; margin-bottom:16px; font-weight:600;">
            Bitte füllen Sie alle Pflichtfelder aus (Name, E-Mail, Nachricht).
          </div>
        <?php endif; ?>
        <form class="contact-form" action="" method="post">
          <input type="text" name="name" placeholder="Ihr Name" required>
          <input type="email" name="email" placeholder="Ihre E-Mail" required>
          <input type="tel" name="phone" placeholder="Ihre Telefonnummer">
          <textarea name="message" rows="5" placeholder="Erzählen Sie uns von Ihrem Betrieb..." required></textarea>
          <input type="text" name="website_url" style="position:absolute; left:-9999px;" tabindex="-1" autocomplete="off">
          <?php wp_nonce_field('lorino_contact_form', 'lorino_contact_nonce'); ?>
          <button type="submit" name="lorino_contact_submit" value="1" class="btn-primary" style="border:none; cursor:pointer; justify-content:center;">Nachricht senden</button>
        </form>
      </div>
      <div>
        <a href="https://wa.me/41765201046" target="_blank" class="whatsapp-card" style="display:block;">
          <div style="font-size:28px;">💬</div>
          <h3>WhatsApp schreiben</h3>
          <p>Schnell und direkt — schreiben Sie uns per WhatsApp.</p>
          <span class="link">Jetzt schreiben →</span>
        </a>
        <div class="contact-details">
          <h3 style="font-size:18px; margin-bottom:16px;">Direkter Kontakt</h3>
          <a href="tel:+41765201046" class="contact-row">
            <span class="icon-sm">📞</span> +41 76 520 10 46
          </a>
          <a href="mailto:info@lorinoweb.ch" class="contact-row">
            <span class="icon-sm">✉️</span> info@lorinoweb.ch
          </a>
          <a href="https://instagram.com/lorino_co" target="_blank" class="contact-row">
            <span class="icon-sm">📷</span> @lorino_co
          </a>
        </div>
      </div>
    </div>
  </div>
</section>

<?php get_footer(); ?>
