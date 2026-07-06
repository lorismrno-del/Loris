<?php
function lorino_setup() {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('custom-logo');
}
add_action('after_setup_theme', 'lorino_setup');

function lorino_scripts() {
    wp_enqueue_style('lorino-style', get_stylesheet_uri(), array(), '3.0');
}
add_action('wp_enqueue_scripts', 'lorino_scripts');

/**
 * Zeigt ein Bild an: entweder das Bild, das der Nutzer im Customizer
 * hochgeladen hat, oder – falls keines gesetzt ist – das eingebaute
 * Standard-Bild aus dem Theme-Ordner. Das Layout bleibt dabei unverändert,
 * es wird lediglich die Bildquelle ausgetauscht.
 */
function lorino_image($setting, $default_file, $alt = '', $style = '') {
    $custom = get_theme_mod($setting);
    $src = $custom ? $custom : get_template_directory_uri() . '/images/' . $default_file;
    return '<img src="' . esc_url($src) . '" alt="' . esc_attr($alt) . '"' . ($style ? ' style="' . esc_attr($style) . '"' : '') . '>';
}

/**
 * Customizer: Eigener Bereich "Bilder der Webseite" — hier kann jedes
 * Bild der Seite ausgetauscht werden, ohne dass sich am Layout etwas
 * ändert. Leer lassen = eingebaute Standard-Grafik wird angezeigt.
 */
function lorino_customize_register($wp_customize) {
    $wp_customize->add_section('lorino_images', array(
        'title'       => 'Bilder der Webseite',
        'priority'    => 30,
        'description' => 'Hier können Sie alle Bilder der Webseite austauschen. Leer lassen = eingebaute Standard-Grafik wird angezeigt. Das Layout/Design bleibt dabei unverändert.',
    ));

    $images = array(
        'lorino_logo_header'  => 'Logo im Header (helle Seite)',
        'lorino_logo_footer'  => 'Logo im Footer (dunkle Seite)',
        'lorino_img_about'    => 'Über mich: Ihr Portraitfoto',
        'lorino_img_reference'=> 'Leistungen: Referenzprojekt-Bild',
        'lorino_img_home_hero'=> 'Startseite: Illustration im Hero-Bereich',
        'lorino_img_home_diagram' => 'Startseite: Diagramm "Was eine Webseite bewirkt"',
        'lorino_img_services' => 'Leistungen: Bild oben',
        'lorino_img_process'  => 'Ablauf: Bild oben',
        'lorino_img_why'      => 'Warum wir: Bild oben',
        'lorino_img_faq'      => 'FAQ: Bild oben',
        'lorino_img_contact'  => 'Kontakt: Bild oben',
    );

    foreach ($images as $key => $label) {
        $wp_customize->add_setting($key, array('sanitize_callback' => 'esc_url_raw'));
        $wp_customize->add_control(new WP_Customize_Image_Control($wp_customize, $key, array(
            'label'    => $label,
            'section'  => 'lorino_images',
            'settings' => $key,
        )));
    }
}
add_action('customize_register', 'lorino_customize_register');

/**
 * Erstellt automatisch alle 7 Seiten mit den passenden Templates,
 * sobald das Theme aktiviert wird. Bereits vorhandene Seiten (gleicher
 * Slug) werden nicht doppelt angelegt.
 */
function lorino_create_pages() {
    $pages = array(
        array('title' => 'Startseite',   'slug' => 'startseite',  'template' => 'template-home.php'),
        array('title' => 'Über mich',    'slug' => 'ueber-mich',  'template' => 'template-about.php'),
        array('title' => 'Leistungen',   'slug' => 'leistungen',  'template' => 'template-services.php'),
        array('title' => 'Ablauf',       'slug' => 'ablauf',      'template' => 'template-process.php'),
        array('title' => 'Warum Lorino', 'slug' => 'warum-lorino','template' => 'template-why.php'),
        array('title' => 'FAQ',          'slug' => 'faq',         'template' => 'template-faq.php'),
        array('title' => 'Kontakt',      'slug' => 'kontakt',     'template' => 'template-contact.php'),
        array('title' => 'Impressum',    'slug' => 'impressum',   'template' => 'template-impressum.php'),
        array('title' => 'Datenschutz',  'slug' => 'datenschutz', 'template' => 'template-datenschutz.php'),
    );

    $home_id = null;

    foreach ($pages as $p) {
        $existing = get_page_by_path($p['slug']);

        if ($existing) {
            $page_id = $existing->ID;
        } else {
            $page_id = wp_insert_post(array(
                'post_title'   => $p['title'],
                'post_name'    => $p['slug'],
                'post_status'  => 'publish',
                'post_type'    => 'page',
                'post_content' => '',
            ));
        }

        if ($page_id && !is_wp_error($page_id)) {
            update_post_meta($page_id, '_wp_page_template', $p['template']);
        }

        if ($p['slug'] === 'startseite') {
            $home_id = $page_id;
        }
    }

    // Startseite als Frontpage festlegen
    if ($home_id) {
        update_option('show_on_front', 'page');
        update_option('page_on_front', $home_id);
    }

    flush_rewrite_rules();
}
add_action('after_switch_theme', 'lorino_create_pages');

// Zusätzlicher Sicherheitsnetz-Hook: falls das Theme nur überschrieben statt
// neu aktiviert wurde (after_switch_theme feuert dann nicht), wird die
// Seiten-Erstellung beim nächsten Seitenaufruf einmalig nachgeholt.
function lorino_ensure_pages() {
    if (!get_option('lorino_pages_created_v2')) {
        lorino_create_pages();
        update_option('lorino_pages_created_v2', 1);
    }
}
add_action('init', 'lorino_ensure_pages');
