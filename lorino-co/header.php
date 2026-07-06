<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo('charset'); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title><?php wp_title('|', true, 'right'); ?><?php bloginfo('name'); ?><?php $d = get_bloginfo('description'); if ($d) echo ' | ' . $d; ?></title>
<meta name="description" content="<?php echo esc_attr(get_bloginfo('description') ?: 'Lorino Co. — Premium-Websites für Bauunternehmen und Handwerksbetriebe in der deutschsprachigen Schweiz.'); ?>">
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>

<header class="site-header">
  <div class="container navbar">
    <a href="<?php echo home_url('/'); ?>" class="logo-badge">
      <?php echo lorino_image('lorino_logo_header', 'logo-final.png', 'Lorino Co. Logo', 'height:32px; width:auto; display:block;'); ?>
    </a>
    <nav class="nav-links">
      <a href="<?php echo home_url('/'); ?>">Start</a>
      <a href="<?php echo home_url('/ueber-mich'); ?>">Über mich</a>
      <a href="<?php echo home_url('/leistungen'); ?>">Leistungen</a>
      <a href="<?php echo home_url('/ablauf'); ?>">Ablauf</a>
      <a href="<?php echo home_url('/warum-lorino'); ?>">Warum wir</a>
      <a href="<?php echo home_url('/faq'); ?>">FAQ</a>
    </nav>
    <a href="<?php echo home_url('/kontakt'); ?>" class="nav-cta nav-cta-desktop">Kostenlose Beratung</a>

    <input type="checkbox" id="lorino-menu-toggle" class="lorino-menu-toggle">
    <label for="lorino-menu-toggle" class="lorino-hamburger" aria-label="Menü öffnen">
      <span></span><span></span><span></span>
    </label>
    <div class="lorino-mobile-menu">
      <a href="<?php echo home_url('/'); ?>">Start</a>
      <a href="<?php echo home_url('/ueber-mich'); ?>">Über mich</a>
      <a href="<?php echo home_url('/leistungen'); ?>">Leistungen</a>
      <a href="<?php echo home_url('/ablauf'); ?>">Ablauf</a>
      <a href="<?php echo home_url('/warum-lorino'); ?>">Warum wir</a>
      <a href="<?php echo home_url('/faq'); ?>">FAQ</a>
      <a href="<?php echo home_url('/kontakt'); ?>" class="nav-cta" style="margin-top:12px;">Kostenlose Beratung</a>
    </div>
  </div>
</header>
