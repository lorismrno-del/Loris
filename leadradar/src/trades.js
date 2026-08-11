/**
 * Branchen-Katalog: Bau & Handwerk Schweiz.
 *
 * Jede Branche kennt:
 *  - `google`: Suchbegriffe für die Google Places Textsuche
 *  - `osm`:    OpenStreetMap-Tag-Filter (Overpass)
 * So liefern beide Datenquellen vergleichbare Ergebnisse.
 */

export const TRADES = [
  {
    id: 'schreiner',
    label: 'Schreiner / Zimmerei',
    emoji: '🪵',
    google: ['Schreinerei', 'Schreiner', 'Zimmerei', 'Holzbau'],
    osm: [['craft', ['carpenter', 'joiner', 'cabinet_maker']]],
  },
  {
    id: 'maler',
    label: 'Maler & Gipser',
    emoji: '🎨',
    google: ['Malergeschäft', 'Maler', 'Gipser', 'Gipsergeschäft'],
    osm: [['craft', ['painter', 'plasterer']]],
  },
  {
    id: 'sanitaer',
    label: 'Sanitär & Heizung',
    emoji: '🚿',
    google: ['Sanitär', 'Sanitärinstallateur', 'Heizung', 'Spengler'],
    osm: [['craft', ['plumber', 'hvac']]],
  },
  {
    id: 'elektriker',
    label: 'Elektriker',
    emoji: '⚡',
    google: ['Elektriker', 'Elektroinstallateur', 'Elektrogeschäft'],
    osm: [['craft', ['electrician']]],
  },
  {
    id: 'bau',
    label: 'Baugeschäft / Bauunternehmen',
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
    emoji: '🏠',
    google: ['Dachdecker', 'Bedachungen', 'Spenglerei'],
    osm: [['craft', ['roofer', 'tinsmith']]],
  },
  {
    id: 'gartenbau',
    label: 'Garten- & Landschaftsbau',
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
    emoji: '🧱',
    google: ['Bodenleger', 'Plattenleger', 'Parkett', 'Fliesenleger'],
    osm: [['craft', ['floorer', 'tiler']]],
  },
  {
    id: 'metallbau',
    label: 'Metallbau & Schlosserei',
    emoji: '🔩',
    google: ['Metallbau', 'Schlosserei', 'Stahlbau'],
    osm: [['craft', ['metal_construction', 'blacksmith', 'locksmith', 'welder']]],
  },
  {
    id: 'fenster',
    label: 'Fenster, Storen & Glaserei',
    emoji: '🪟',
    google: ['Fensterbau', 'Storen', 'Rollladen', 'Glaserei'],
    osm: [['craft', ['window_construction', 'glaziery', 'sun_protection']]],
  },
  {
    id: 'kuechenbau',
    label: 'Küchen- & Innenausbau',
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
    emoji: '📐',
    google: ['Architekturbüro', 'Architekt', 'Bauplanung'],
    osm: [['office', ['architect', 'engineer']]],
  },
  {
    id: 'autogewerbe',
    label: 'Garage & Autogewerbe',
    emoji: '🚗',
    google: ['Autogarage', 'Autowerkstatt', 'Carrosserie'],
    osm: [['shop', ['car_repair', 'car', 'tyres']]],
  },
  {
    id: 'gastro',
    label: 'Restaurant & Gastro',
    emoji: '🍽️',
    google: ['Restaurant', 'Pizzeria', 'Café', 'Bar'],
    osm: [['amenity', ['restaurant', 'cafe', 'bar', 'pub']]],
  },
  {
    id: 'beauty',
    label: 'Coiffeur, Kosmetik & Studio',
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
    emoji: '🩺',
    google: ['Physiotherapie', 'Zahnarzt', 'Arztpraxis', 'Podologie'],
    osm: [
      ['amenity', ['dentist', 'doctors', 'clinic']],
      ['healthcare', ['physiotherapist', 'podiatrist', 'psychotherapist']],
    ],
  },
];

export const TRADE_BY_ID = new Map(TRADES.map((t) => [t.id, t]));

export function tradeLabel(id) {
  return TRADE_BY_ID.get(id)?.label || id || 'Unbekannt';
}
