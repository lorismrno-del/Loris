<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <div class="logo-badge" style="margin-bottom:16px; background:transparent; padding:0;">
          <?php echo lorino_image('lorino_logo_footer', 'logo-transparent-cropped.png', 'Lorino Co. Logo', 'height:44px; width:auto; display:block;'); ?>
        </div>
        <p>Webagentur für Bauunternehmen und Handwerksbetriebe in der Schweiz.</p>
      </div>
      <div>
        <h4>Navigation</h4>
        <ul class="footer-links">
          <li><a href="<?php echo home_url('/ueber-mich'); ?>">Über mich</a></li>
          <li><a href="<?php echo home_url('/leistungen'); ?>">Leistungen</a></li>
          <li><a href="<?php echo home_url('/ablauf'); ?>">Ablauf</a></li>
          <li><a href="<?php echo home_url('/faq'); ?>">FAQ</a></li>
          <li><a href="<?php echo home_url('/kontakt'); ?>">Kontakt</a></li>
        </ul>
      </div>
      <div>
        <h4>Kontakt</h4>
        <ul class="footer-links">
          <li><a href="tel:+41765201046">+41 76 520 10 46</a></li>
          <li><a href="mailto:info@lorinoweb.ch">info@lorinoweb.ch</a></li>
          <li><a href="https://instagram.com/lorino_co" target="_blank">@lorino_co</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© <?php echo date('Y'); ?> Lorino Co. Alle Rechte vorbehalten.</span>
      <span><a href="<?php echo home_url('/impressum'); ?>">Impressum</a> · <a href="<?php echo home_url('/datenschutz'); ?>">Datenschutz</a></span>
    </div>
  </div>
</footer>

<a href="https://wa.me/41765201046" target="_blank" class="lorino-whatsapp-float" aria-label="WhatsApp kontaktieren">
  <svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" width="30" height="30">
    <path fill="#fff" d="M16 3C9 3 3.3 8.6 3.3 15.5c0 2.4.7 4.7 1.9 6.7L3 29l7-2.1c1.9 1 4 1.6 6 1.6 7 0 12.7-5.6 12.7-12.5C28.7 8.6 23 3 16 3z"/>
    <path fill="#25D366" d="M16 4.3c-6.2 0-11.2 5-11.2 11.2 0 2.2.6 4.2 1.7 6l-1.1 4 4.2-1.1c1.7 1 3.6 1.5 5.6 1.5 6.2 0 11.2-5 11.2-11.2S22.2 4.3 16 4.3zm5.9 15.9c-.3.7-1.5 1.4-2.1 1.5-.5.1-1.2.1-1.9-.1-.4-.1-1-.3-1.7-.6-3-1.3-5-4.3-5.1-4.5-.2-.2-1.2-1.6-1.2-3s.7-2.2 1-2.5c.3-.3.6-.4.8-.4h.6c.2 0 .4 0 .6.5.2.5.7 1.8.8 2 .1.2.1.4 0 .6-.1.2-.2.4-.4.6-.2.2-.4.5-.5.6-.2.2-.4.4-.2.8.2.4.9 1.5 1.9 2.4 1.3 1.2 2.4 1.5 2.8 1.7.4.2.6.2.8-.1.2-.2.9-1 1.1-1.4.2-.4.5-.3.8-.2.3.1 2 .9 2.3 1.1.3.2.5.2.6.4.1.2.1.9-.2 1.6z"/>
  </svg>
</a>

<?php wp_footer(); ?>
</body>
</html>
