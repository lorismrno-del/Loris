<?php get_header(); ?>
<section style="padding: 100px 0; text-align:center;">
  <div class="container">
    <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
      <h1><?php the_title(); ?></h1>
      <div><?php the_content(); ?></div>
    <?php endwhile; else: ?>
      <h1>Seite nicht gefunden</h1>
      <p><a href="<?php echo home_url('/'); ?>">Zurück zur Startseite</a></p>
    <?php endif; ?>
  </div>
</section>
<?php get_footer(); ?>
