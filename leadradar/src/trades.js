/**
 * Branchen-Katalog: Bau & Handwerk Schweiz.
 *
 * Jede Branche kennt:
 *  - `google`: Suchbegriffe für die Google Places Textsuche
 *  - `osm`:    OpenStreetMap-Tag-Filter (Overpass)
 * So liefern beide Datenquellen vergleichbare Ergebnisse.
 */

export const GRUPPEN = [
  { id: 'bau', label: 'Bau & Handwerk' },
  { id: 'kmu', label: 'KMU & Gewerbe' },
  { id: 'dienstleistung', label: 'Dienstleistung & Beratung' },
  { id: 'gesundheit', label: 'Gesundheit & Wellness' },
];

export const TRADES = [
  {
    id: 'schreiner',
    label: 'Schreiner / Zimmerei',
    gruppe: 'bau',
    emoji: '🪵',
    google: ['Schreinerei', 'Schreiner', 'Zimmerei', 'Holzbau'],
    osm: [['craft', ['carpenter', 'joiner', 'cabinet_maker']]],
  },
  {
    id: 'maler',
    label: 'Maler & Gipser',
    gruppe: 'bau',
    emoji: '🎨',
    google: ['Malergeschäft', 'Maler', 'Gipser', 'Gipsergeschäft'],
    osm: [['craft', ['painter', 'plasterer']]],
  },
  {
    id: 'sanitaer',
    label: 'Sanitär & Heizung',
    gruppe: 'bau',
    emoji: '🚿',
    google: ['Sanitär', 'Sanitärinstallateur', 'Heizung', 'Spengler'],
    osm: [['craft', ['plumber', 'hvac']]],
  },
  {
    id: 'elektriker',
    label: 'Elektriker',
    gruppe: 'bau',
    emoji: '⚡',
    google: ['Elektriker', 'Elektroinstallateur', 'Elektrogeschäft'],
    osm: [['craft', ['electrician']]],
  },
  {
    id: 'bau',
    label: 'Baugeschäft / Bauunternehmen',
    gruppe: 'bau',
    emoji: '🏗️',
    google: ['Bauunternehmen', 'Baugeschäft', 'Hochbau', 'Tiefbau', 'Maurer'],
    osm: [
      ['craft', ['builder', 'stonemason', 'bricklayer']],
      ['office', ['construction_company']],
    ],
  },
  {
    id: 'dachdecker',
    label: 'Dachdecker & Spengler',
    gruppe: 'bau',
    emoji: '🏠',
    google: ['Dachdecker', 'Bedachungen', 'Spenglerei'],
    osm: [['craft', ['roofer', 'tinsmith']]],
  },
  {
    id: 'gartenbau',
    label: 'Garten- & Landschaftsbau',
    gruppe: 'bau',
    emoji: '🌳',
    google: ['Gartenbau', 'Gärtnerei', 'Landschaftsgärtner', 'Gartenpflege'],
    osm: [
      ['craft', ['gardener']],
      ['landuse', ['plant_nursery']],
    ],
  },
  {
    id: 'bodenleger',
    label: 'Bodenleger & Plattenleger',
    gruppe: 'bau',
    emoji: '🧱',
    google: ['Bodenleger', 'Plattenleger', 'Parkett', 'Fliesenleger'],
    osm: [['craft', ['floorer', 'tiler']]],
  },
  {
    id: 'metallbau',
    label: 'Metallbau & Schlosserei',
    gruppe: 'bau',
    emoji: '🔩',
    google: ['Metallbau', 'Schlosserei', 'Stahlbau'],
    osm: [['craft', ['metal_construction', 'blacksmith', 'locksmith', 'welder']]],
  },
  {
    id: 'fenster',
    label: 'Fenster, Storen & Glaserei',
    gruppe: 'bau',
    emoji: '🪟',
    google: ['Fensterbau', 'Storen', 'Rollladen', 'Glaserei'],
    osm: [['craft', ['window_construction', 'glaziery', 'sun_protection']]],
  },
  {
    id: 'kuechenbau',
    label: 'Küchen- & Innenausbau',
    gruppe: 'bau',
    emoji: '🍳',
    google: ['Küchenbau', 'Küchen Studio', 'Innenausbau'],
    osm: [
      ['shop', ['kitchen', 'interior_decoration']],
      ['craft', ['furniture']],
    ],
  },
  {
    id: 'umzug',
    label: 'Umzug & Reinigung',
    gruppe: 'kmu',
    emoji: '📦',
    google: ['Umzugsfirma', 'Reinigungsfirma', 'Gebäudereinigung'],
    osm: [
      ['shop', ['moving_company']],
      ['office', ['moving_company']],
      ['craft', ['cleaning']],
    ],
  },
  {
    id: 'architekt',
    label: 'Architektur & Planung',
    gruppe: 'dienstleistung',
    emoji: '📐',
    google: ['Architekturbüro', 'Architekt', 'Bauplanung'],
    osm: [['office', ['architect', 'engineer']]],
  },
  {
    id: 'autogewerbe',
    label: 'Garage & Autogewerbe',
    gruppe: 'kmu',
    emoji: '🚗',
    google: ['Autogarage', 'Autowerkstatt', 'Carrosserie'],
    osm: [['shop', ['car_repair', 'car', 'tyres']]],
  },
  {
    id: 'gastro',
    label: 'Restaurant & Gastro',
    gruppe: 'kmu',
    emoji: '🍽️',
    google: ['Restaurant', 'Pizzeria', 'Café', 'Bar'],
    osm: [['amenity', ['restaurant', 'cafe', 'bar', 'pub']]],
  },
  {
    id: 'beauty',
    label: 'Coiffeur, Kosmetik & Studio',
    gruppe: 'kmu',
    emoji: '💇',
    google: ['Coiffeur', 'Kosmetikstudio', 'Nagelstudio', 'Fitnessstudio'],
    osm: [
      ['shop', ['hairdresser', 'beauty', 'massage']],
      ['leisure', ['fitness_centre']],
    ],
  },
  {
    id: 'gesundheit',
    label: 'Praxis & Gesundheit',
    gruppe: 'gesundheit',
    emoji: '🩺',
    google: ['Physiotherapie', 'Zahnarzt', 'Arztpraxis', 'Podologie'],
    osm: [
      ['amenity', ['dentist', 'doctors', 'clinic']],
      ['healthcare', ['physiotherapist', 'podiatrist', 'psychotherapist']],
    ],
  },

  // ---------------------------------------------------- KMU & Gewerbe
  {
    id: 'lebensmittel',
    label: 'Bäckerei, Metzgerei & Hofladen',
    gruppe: 'kmu',
    emoji: '🥖',
    google: ['Bäckerei', 'Metzgerei', 'Hofladen', 'Käserei', 'Konditorei'],
    osm: [
      ['shop', ['bakery', 'butcher', 'cheese', 'farm', 'confectionery', 'greengrocer', 'deli']],
      ['craft', ['bakery', 'winery', 'brewery', 'distillery']],
    ],
  },
  {
    id: 'detailhandel',
    label: 'Laden & Detailhandel',
    gruppe: 'kmu',
    emoji: '🛍️',
    google: ['Blumen', 'Optiker', 'Papeterie', 'Boutique', 'Möbelgeschäft', 'Sportgeschäft'],
    osm: [
      ['shop', ['florist', 'optician', 'stationery', 'clothes', 'furniture', 'sports',
        'jewelry', 'books', 'toys', 'bicycle', 'electronics', 'shoes', 'gift', 'pet']],
    ],
  },
  {
    id: 'hotel',
    label: 'Hotel & Beherbergung',
    gruppe: 'kmu',
    emoji: '🏨',
    google: ['Hotel', 'Gasthof', 'Pension', 'Ferienwohnung', 'Camping'],
    osm: [
      ['tourism', ['hotel', 'guest_house', 'hostel', 'apartment', 'chalet', 'camp_site']],
    ],
  },
  {
    id: 'transport',
    label: 'Transport & Logistik',
    gruppe: 'kmu',
    emoji: '🚚',
    google: ['Transportunternehmen', 'Taxi', 'Kurierdienst', 'Fahrschule'],
    osm: [
      ['office', ['logistics', 'transport']],
      ['amenity', ['taxi', 'driving_school']],
      ['shop', ['driving_school']],
    ],
  },
  {
    id: 'landwirtschaft',
    label: 'Landwirtschaft & Forst',
    gruppe: 'kmu',
    emoji: '🚜',
    google: ['Landwirtschaftsbetrieb', 'Bauernhof', 'Forstunternehmen', 'Imkerei'],
    osm: [
      ['craft', ['agricultural_engines', 'sawmill', 'beekeeper']],
      ['shop', ['agrarian']],
      ['landuse', ['farmyard']],
    ],
  },

  // -------------------------------------- Dienstleistung & Beratung
  {
    id: 'treuhand',
    label: 'Treuhand & Buchhaltung',
    gruppe: 'dienstleistung',
    emoji: '📊',
    google: ['Treuhandbüro', 'Treuhand', 'Buchhaltung', 'Steuerberatung'],
    osm: [
      ['office', ['accountant', 'tax_advisor', 'financial', 'financial_advisor']],
    ],
  },
  {
    id: 'recht',
    label: 'Anwalt & Notariat',
    gruppe: 'dienstleistung',
    emoji: '⚖️',
    google: ['Anwaltskanzlei', 'Rechtsanwalt', 'Notariat'],
    osm: [['office', ['lawyer', 'notary']]],
  },
  {
    id: 'immobilien',
    label: 'Immobilien & Verwaltung',
    gruppe: 'dienstleistung',
    emoji: '🏘️',
    google: ['Immobilien', 'Liegenschaftsverwaltung', 'Makler'],
    osm: [['office', ['estate_agent', 'property_management']]],
  },
  {
    id: 'versicherung',
    label: 'Versicherung & Finanzen',
    gruppe: 'dienstleistung',
    emoji: '🛡️',
    google: ['Versicherungsbroker', 'Versicherungsagentur', 'Finanzberatung'],
    osm: [['office', ['insurance']]],
  },
  {
    id: 'agentur',
    label: 'Werbung, Foto & Events',
    gruppe: 'dienstleistung',
    emoji: '📸',
    google: ['Fotograf', 'Werbeagentur', 'Druckerei', 'Eventagentur'],
    osm: [
      ['craft', ['photographer', 'printer', 'signmaker']],
      ['office', ['advertising_agency', 'graphic_design', 'it']],
      ['shop', ['photo', 'copyshop']],
    ],
  },
  {
    id: 'bildung',
    label: 'Schule & Kinderbetreuung',
    gruppe: 'dienstleistung',
    emoji: '🎓',
    google: ['Kita', 'Kindertagesstätte', 'Musikschule', 'Nachhilfe', 'Sprachschule'],
    osm: [
      ['amenity', ['kindergarten', 'childcare', 'music_school', 'language_school', 'college']],
    ],
  },

  // ---------------------------------------- Gesundheit & Wellness
  {
    id: 'therapie',
    label: 'Therapie & Alternativmedizin',
    gruppe: 'gesundheit',
    emoji: '🌿',
    google: ['Massagepraxis', 'Naturheilpraxis', 'Osteopathie', 'Ergotherapie', 'Logopädie'],
    osm: [
      ['healthcare', ['alternative', 'occupational_therapist', 'speech_therapist', 'osteopath']],
      ['shop', ['herbalist']],
    ],
  },
  {
    id: 'tierarzt',
    label: 'Tierarzt & Tierpflege',
    gruppe: 'gesundheit',
    emoji: '🐾',
    google: ['Tierarzt', 'Tierarztpraxis', 'Hundesalon', 'Tierpension'],
    osm: [
      ['amenity', ['veterinary']],
      ['shop', ['pet_grooming']],
    ],
  },
];

export const TRADE_BY_ID = new Map(TRADES.map((t) => [t.id, t]));

export function tradeLabel(id) {
  return TRADE_BY_ID.get(id)?.label || id || 'Unbekannt';
}
