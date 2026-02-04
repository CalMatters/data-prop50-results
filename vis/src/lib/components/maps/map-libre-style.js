const style = {
  "version": 8,
  "glyphs": 'https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf',
  "sources": {
    "protomaps": {
      "type": "vector",
      "attribution": `<a href=\"https://github.com/protomaps/basemaps">Protomaps</a> © <a href="https://openstreetmap.org\">OpenStreetMap</a>`,
      "url": "pmtiles://https://data-map-bucket-2.s3.us-west-1.amazonaws.com/v4-osm-us-west.pmtiles"
    }
  },
  "layers": [
    // background
    {
      id: 'background',
      type: 'background',
      paint: {
        'background-color': '#ffffff'
      }
    },
    // earth
    {
      id: 'earth',
      type: 'fill',
      filter: ['==', '$type', 'Polygon'
      ],
      source: 'protomaps',
      'source-layer': 'earth',
      paint: {
        'fill-color': '#dddddd'
      }
    },
    // landuse_park
    {
      id: 'landuse_park',
      type: 'fill',
      source: 'protomaps',
      'source-layer': 'landuse',
      filter: [ 'in', 'kind', 'national_park', 'park', 'cemetery', 'protected_area', 'nature_reserve', 'forest', 'golf_course', 'wood', 'nature_reserve', 'forest', 'scrub', 'grassland', 'grass', 'military', 'naval_base', 'airfield'
      ],
      paint: {
        'fill-opacity': ['interpolate',
          ['linear'
          ],
          ['zoom'
          ],
          6,
          0,
          11,
          1
        ],
        'fill-color': [ 
          'case',
          [ 'in',
            ['get', 'kind'
            ],
            [ 'literal',
              [ 'national_park', 'park', 'cemetery', 'protected_area', 'nature_reserve', 'forest', 'golf_course'
              ]
            ]
          ],
          '#fcfcfc',
          ['in',
            ['get', 'kind'
            ],
            ['literal',
              ['wood', 'nature_reserve', 'forest'
              ]
            ]
          ],
          '#fafafa',
          ['in',
            ['get', 'kind'
            ],
            ['literal',
              ['scrub', 'grassland', 'grass'
              ]
            ]
          ],
          '#fafafa',
          ['in',
            ['get', 'kind'
            ],
            ['literal',
              ['glacier'
              ]
            ]
          ],
          '#fcfcfc',
          ['in',
            ['get', 'kind'
            ],
            ['literal',
              ['sand'
              ]
            ]
          ],
          '#fafafa',
          ['in',
            ['get', 'kind'
            ],
            ['literal',
              ['military', 'naval_base', 'airfield'
              ]
            ]
          ],
          '#f7f7f7',
          '#ffffff'
        ]
      }
    },
    // landuse_urban_green
    {
      id: 'landuse_urban_green',
      type: 'fill',
      source: 'protomaps',
      'source-layer': 'landuse',
      filter: ['in', 'kind', 'allotments', 'village_green', 'playground'
      ],
      paint: {
        'fill-color': '#fcfcfc',
        'fill-opacity': 0.7
      }
    },
    // landuse_hospital
    {
      id: 'landuse_hospital',
      type: 'fill',
      source: 'protomaps',
      'source-layer': 'landuse',
      filter: ['==', 'kind', 'hospital'
      ],
      paint: {
        'fill-color': '#f8f8f8'
      }
    },
    // landuse_industrial
    {
      id: 'landuse_industrial',
      type: 'fill',
      source: 'protomaps',
      'source-layer': 'landuse',
      filter: ['==', 'kind', 'industrial'
      ],
      paint: {
        'fill-color': '#fcfcfc'
      }
    },
    // landuse_school
    {
      id: 'landuse_school',
      type: 'fill',
      source: 'protomaps',
      'source-layer': 'landuse',
      filter: ['in', 'kind', 'school', 'university', 'college'
      ],
      paint: {
        'fill-color': '#f8f8f8'
      }
    },
    // landuse_beach
    {
      id: 'landuse_beach',
      type: 'fill',
      source: 'protomaps',
      'source-layer': 'landuse',
      filter: ['in', 'kind', 'beach'
      ],
      paint: {
        'fill-color': '#f6f6f6'
      }
    },
    // landuse_zoo
    {
      id: 'landuse_zoo',
      type: 'fill',
      source: 'protomaps',
      'source-layer': 'landuse',
      filter: ['in', 'kind', 'zoo'
      ],
      paint: {
        'fill-color': '#f7f7f7'
      }
    },
    // landuse_aerodrome
    {
      id: 'landuse_aerodrome',
      type: 'fill',
      source: 'protomaps',
      'source-layer': 'landuse',
      filter: ['in', 'kind', 'aerodrome'
      ],
      paint: {
        'fill-color': '#fdfdfd'
      }
    },
    // roads_runway
    {
      id: 'roads_runway',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: ['==', 'kind_detail', 'runway'
      ],
      paint: {
        'line-color': '#efefef',
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          10,
          0,
          12,
          4,
          18,
          30
        ]
      }
    },
    // roads_taxiway
    {
      id: 'roads_taxiway',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      minzoom: 13,
      filter: ['==', 'kind_detail', 'taxiway'
      ],
      paint: {
        'line-color': '#efefef',
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          13,
          0,
          13.5,
          1,
          15,
          6
        ]
      }
    },
    // landuse_runway
    {
      id: 'landuse_runway',
      type: 'fill',
      source: 'protomaps',
      'source-layer': 'landuse',
      filter: ['any',
        ['in', 'kind', 'runway', 'taxiway'
        ]
      ],
      paint: {
        'fill-color': '#efefef'
      }
    },
    // landuse_pedestrian
    {
      id: 'landuse_pedestrian',
      type: 'fill',
      source: 'protomaps',
      'source-layer': 'landuse',
      filter: ['in', 'kind', 'pedestrian', 'dam'
      ],
      paint: {
        'fill-color': '#fdfdfd'
      }
    },
    // landuse_pier
    {
      id: 'landuse_pier',
      type: 'fill',
      source: 'protomaps',
      'source-layer': 'landuse',
      filter: ['==', 'kind', 'pier'
      ],
      paint: {
        'fill-color': '#efefef'
      }
    },
    // roads_tunnels_other_casing
    {
      id: 'roads_tunnels_other_casing',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: ['all',
        ['has', 'is_tunnel'
        ],
        ['in', 'kind', 'other', 'path'
        ]
      ],
      paint: {
        'line-color': '#d6d6d6',
        'line-gap-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          14,
          0,
          20,
          7
        ]
      }
    },
    // roads_tunnels_minor_casing
    {
      id: 'roads_tunnels_minor_casing',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: ['all',
        ['has', 'is_tunnel'
        ],
        ['==', 'kind', 'minor_road'
        ]
      ],
      paint: {
        'line-color': '#fcfcfc',
        'line-dasharray': [
          3,
          2
        ],
        'line-gap-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          11,
          0,
          12.5,
          0.5,
          15,
          2,
          18,
          11
        ],
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          12,
          0,
          12.5,
          1
        ]
      }
    },
    // roads_tunnels_link_casing
    {
      id: 'roads_tunnels_link_casing',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: ['all',
        ['has', 'is_tunnel'
        ],
        ['has', 'is_link'
        ]
      ],
      paint: {
        'line-color': '#fcfcfc',
        'line-dasharray': [
          3,
          2
        ],
        'line-gap-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          13,
          0,
          13.5,
          1,
          18,
          11
        ],
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          12,
          0,
          12.5,
          1
        ]
      }
    },
    // roads_tunnels_major_casing
    {
      id: 'roads_tunnels_major_casing',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: [
        'all',
        ['!has', 'is_tunnel'
        ],
        ['!has', 'is_bridge'
        ],
        ['==', 'kind', 'major_road'
        ]
      ],
      paint: {
        'line-color': '#fcfcfc',
        'line-dasharray': [
          3,
          2
        ],
        'line-gap-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          7,
          0,
          7.5,
          0.5,
          18,
          13
        ],
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          9,
          0,
          9.5,
          1
        ]
      }
    },
    // roads_tunnels_highway_casing
    {
      id: 'roads_tunnels_highway_casing',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: [
        'all',
        ['!has', 'is_tunnel'
        ],
        ['!has', 'is_bridge'
        ],
        ['==', 'kind', 'highway'
        ],
        ['!has', 'is_link'
        ]
      ],
      paint: {
        'line-color': '#fcfcfc',
        'line-dasharray': [
          6,
          0.5
        ],
        'line-gap-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          3,
          0,
          3.5,
          0.5,
          18,
          15
        ],
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          7,
          0,
          7.5,
          1,
          20,
          15
        ]
      }
    },
    // roads_tunnels_other
    {
      id: 'roads_tunnels_other',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: ['all',
        ['has', 'is_tunnel'
        ],
        ['in', 'kind', 'other', 'path'
        ]
      ],
      paint: {
        'line-color': '#d6d6d6',
        'line-dasharray': [
          4.5,
          0.5
        ],
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          14,
          0,
          20,
          7
        ]
      }
    },
    // roads_tunnels_minor
    {
      id: 'roads_tunnels_minor',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: ['all',
        ['has', 'is_tunnel'
        ],
        ['==', 'kind', 'minor_road'
        ]
      ],
      paint: {
        'line-color': '#d6d6d6',
        'line-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          11,
          0,
          12.5,
          0.5,
          15,
          2,
          18,
          11
        ]
      }
    },
    // roads_tunnels_link
    {
      id: 'roads_tunnels_link',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: ['all',
        ['has', 'is_tunnel'
        ],
        ['has', 'is_link'
        ]
      ],
      paint: {
        'line-color': '#d6d6d6',
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          13,
          0,
          13.5,
          1,
          18,
          11
        ]
      }
    },
    // roads_tunnels_major
    {
      id: 'roads_tunnels_major',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: ['all',
        ['has', 'is_tunnel'
        ],
        ['==', 'kind', 'major_road'
        ]
      ],
      paint: {
        'line-color': '#d6d6d6',
        'line-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          6,
          0,
          12,
          1.6,
          15,
          3,
          18,
          13
        ]
      }
    },
    // roads_tunnels_highway
    {
      id: 'roads_tunnels_highway',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: [
        'all',
        ['has', 'is_tunnel'
        ],
        ['==',
          ['get', 'kind'
          ], 'highway'
        ],
        ['!',
          ['has', 'is_link'
          ]
        ]
      ],
      paint: {
        'line-color': '#d6d6d6',
        'line-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          3,
          0,
          6,
          1.1,
          12,
          1.6,
          15,
          5,
          18,
          15
        ]
      }
    },
    // roads_pier
    {
      id: 'roads_pier',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: ['==', 'kind_detail', 'pier'
      ],
      paint: {
        'line-color': '#efefef',
        'line-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          12,
          0,
          12.5,
          0.5,
          20,
          16
        ]
      }
    },
    // roads_minor_service_casing
    {
      id: 'roads_minor_service_casing',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      minzoom: 13,
      filter: [
        'all',
        ['!has', 'is_tunnel'
        ],
        ['!has', 'is_bridge'
        ],
        ['==', 'kind', 'minor_road'
        ],
        ['==', 'kind_detail', 'service'
        ]
      ],
      paint: {
        'line-color': '#ffffff',
        'line-gap-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          13,
          0,
          18,
          8
        ],
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          13,
          0,
          13.5,
          0.8
        ]
      }
    },
    // roads_minor_casing
    {
      id: 'roads_minor_casing',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: [
        'all',
        ['!has', 'is_tunnel'
        ],
        ['!has', 'is_bridge'
        ],
        ['==', 'kind', 'minor_road'
        ],
        ['!=', 'kind_detail', 'service'
        ]
      ],
      paint: {
        'line-color': '#ffffff',
        'line-gap-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          11,
          0,
          12.5,
          0.5,
          15,
          2,
          18,
          11
        ],
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          12,
          0,
          12.5,
          1
        ]
      }
    },
    // roads_link_casing
    {
      id: 'roads_link_casing',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      minzoom: 13,
      filter: ['has', 'is_link'
      ],
      paint: {
        'line-color': '#ffffff',
        'line-gap-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          13,
          0,
          13.5,
          1,
          18,
          11
        ],
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          13,
          0,
          13.5,
          1.5
        ]
      }
    },
    // roads_major_casing_late
    {
      id: 'roads_major_casing_late',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      minzoom: 12,
      filter: [
        'all',
        ['!has', 'is_tunnel'
        ],
        ['!has', 'is_bridge'
        ],
        ['==', 'kind', 'major_road'
        ]
      ],
      paint: {
        'line-color': '#ffffff',
        'line-gap-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          6,
          0,
          12,
          1.6,
          15,
          3,
          18,
          13
        ],
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          9,
          0,
          9.5,
          1
        ]
      }
    },
    // roads_highway_casing_late
    {
      id: 'roads_highway_casing_late',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      minzoom: 12,
      filter: [
        'all',
        ['!has', 'is_tunnel'
        ],
        ['!has', 'is_bridge'
        ],
        ['==', 'kind', 'highway'
        ],
        ['!has', 'is_link'
        ]
      ],
      paint: {
        'line-color': '#ffffff',
        'line-gap-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          3,
          0,
          3.5,
          0.5,
          18,
          15
        ],
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          7,
          0,
          7.5,
          1,
          20,
          15
        ]
      }
    },
    // roads_other
    {
      id: 'roads_other',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: [
        'all',
        ['!has', 'is_tunnel'
        ],
        ['!has', 'is_bridge'
        ],
        ['in', 'kind', 'other', 'path'
        ],
        ['!=', 'kind_detail', 'pier'
        ]
      ],
      paint: {
        'line-color': '#f5f5f5',
        'line-dasharray': [
          3,
          1
        ],
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          14,
          0,
          20,
          7
        ]
      }
    },
    // roads_link
    {
      id: 'roads_link',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: ['has', 'is_link'
      ],
      paint: {
        'line-color': '#ebebeb',
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          13,
          0,
          13.5,
          1,
          18,
          11
        ]
      }
    },
    // roads_minor_service
    {
      id: 'roads_minor_service',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: [
        'all',
        ['!has', 'is_tunnel'
        ],
        ['!has', 'is_bridge'
        ],
        ['==', 'kind', 'minor_road'
        ],
        ['==', 'kind_detail', 'service'
        ]
      ],
      paint: {
        'line-color': '#f5f5f5',
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          13,
          0,
          18,
          8
        ]
      }
    },
    // roads_minor
    {
      id: 'roads_minor',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: [
        'all',
        ['!has', 'is_tunnel'
        ],
        ['!has', 'is_bridge'
        ],
        ['==', 'kind', 'minor_road'
        ],
        ['!=', 'kind_detail', 'service'
        ]
      ],
      paint: {
        'line-color': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          11,
          '#ebebeb',
          16,
          '#f5f5f5'
        ],
        'line-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          11,
          0,
          12.5,
          0.5,
          15,
          2,
          18,
          11
        ]
      }
    },
    // roads_major_casing_early
    {
      id: 'roads_major_casing_early',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      maxzoom: 12,
      filter: [
        'all',
        ['!has', 'is_tunnel'
        ],
        ['!has', 'is_bridge'
        ],
        ['==', 'kind', 'major_road'
        ]
      ],
      paint: {
        'line-color': '#ffffff',
        'line-gap-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          7,
          0,
          7.5,
          0.5,
          18,
          13
        ],
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          9,
          0,
          9.5,
          1
        ]
      }
    },
    // roads_major
    {
      id: 'roads_major',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: [
        'all',
        ['!has', 'is_tunnel'
        ],
        ['!has', 'is_bridge'
        ],
        ['==', 'kind', 'major_road'
        ]
      ],
      paint: {
        'line-color': '#ebebeb',
        'line-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          6,
          0,
          12,
          1.6,
          15,
          3,
          18,
          13
        ]
      }
    },
    // roads_highway_casing_early
    {
      id: 'roads_highway_casing_early',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      maxzoom: 12,
      filter: [
        'all',
        ['!has', 'is_tunnel'
        ],
        ['!has', 'is_bridge'
        ],
        ['==', 'kind', 'highway'
        ],
        ['!has', 'is_link'
        ]
      ],
      paint: {
        'line-color': '#ffffff',
        'line-gap-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          3,
          0,
          3.5,
          0.5,
          18,
          15
        ],
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          7,
          0,
          7.5,
          1
        ]
      }
    },
    // roads_highway
    {
      id: 'roads_highway',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: [
        'all',
        ['!has', 'is_tunnel'
        ],
        ['!has', 'is_bridge'
        ],
        ['==', 'kind', 'highway'
        ],
        ['!has', 'is_link'
        ]
      ],
      paint: {
        'line-color': '#ebebeb',
        'line-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          3,
          0,
          6,
          1.1,
          12,
          1.6,
          15,
          5,
          18,
          15
        ]
      }
    },
    // roads_rail
    {
      id: 'roads_rail',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: ['==', 'kind', 'rail'
      ],
      paint: {
        'line-dasharray': [
          0.3,
          0.75
        ],
        'line-opacity': 0.5,
        'line-color': '#d6d6d6',
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          3,
          0,
          6,
          0.15,
          18,
          9
        ]
      }
    },
    // roads_bridges_other_casing
    {
      id: 'roads_bridges_other_casing',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      minzoom: 12,
      filter: ['all',
        ['has', 'is_bridge'
        ],
        ['in', 'kind', 'other', 'path'
        ]
      ],
      paint: {
        'line-color': '#ffffff',
        'line-gap-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          14,
          0,
          20,
          7
        ]
      }
    },
    // roads_bridges_link_casing
    {
      id: 'roads_bridges_link_casing',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      minzoom: 12,
      filter: ['all',
        ['has', 'is_bridge'
        ],
        ['has', 'is_link'
        ]
      ],
      paint: {
        'line-color': '#ffffff',
        'line-gap-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          13,
          0,
          13.5,
          1,
          18,
          11
        ],
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          12,
          0,
          12.5,
          1.5
        ]
      }
    },
    // roads_bridges_minor_casing
    {
      id: 'roads_bridges_minor_casing',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      minzoom: 12,
      filter: ['all',
        ['has', 'is_bridge'
        ],
        ['==', 'kind', 'minor_road'
        ]
      ],
      paint: {
        'line-color': '#ffffff',
        'line-gap-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          11,
          0,
          12.5,
          0.5,
          15,
          2,
          18,
          11
        ],
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          13,
          0,
          13.5,
          0.8
        ]
      }
    },
    // roads_bridges_major_casing
    {
      id: 'roads_bridges_major_casing',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      minzoom: 12,
      filter: ['all',
        ['has', 'is_bridge'
        ],
        ['==', 'kind', 'major_road'
        ]
      ],
      paint: {
        'line-color': '#ffffff',
        'line-gap-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          7,
          0,
          7.5,
          0.5,
          18,
          10
        ],
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          9,
          0,
          9.5,
          1.5
        ]
      }
    },
    // roads_bridges_other
    {
      id: 'roads_bridges_other',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      minzoom: 12,
      filter: ['all',
        ['has', 'is_bridge'
        ],
        ['in', 'kind', 'other', 'path'
        ]
      ],
      paint: {
        'line-color': '#f5f5f5',
        'line-dasharray': [
          2,
          1
        ],
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          14,
          0,
          20,
          7
        ]
      }
    },
    // roads_bridges_minor
    {
      id: 'roads_bridges_minor',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      minzoom: 12,
      filter: ['all',
        ['has', 'is_bridge'
        ],
        ['==', 'kind', 'minor_road'
        ]
      ],
      paint: {
        'line-color': '#f5f5f5',
        'line-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          11,
          0,
          12.5,
          0.5,
          15,
          2,
          18,
          11
        ]
      }
    },
    // roads_bridges_link
    {
      id: 'roads_bridges_link',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      minzoom: 12,
      filter: ['all',
        ['has', 'is_bridge'
        ],
        ['has', 'is_link'
        ]
      ],
      paint: {
        'line-color': '#f5f5f5',
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          13,
          0,
          13.5,
          1,
          18,
          11
        ]
      }
    },
    // roads_bridges_major
    {
      id: 'roads_bridges_major',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      minzoom: 12,
      filter: ['all',
        ['has', 'is_bridge'
        ],
        ['==', 'kind', 'major_road'
        ]
      ],
      paint: {
        'line-color': '#ebebeb',
        'line-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          6,
          0,
          12,
          1.6,
          15,
          3,
          18,
          13
        ]
      }
    },
    // roads_bridges_highway_casing
    {
      id: 'roads_bridges_highway_casing',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      minzoom: 12,
      filter: ['all',
        ['has', 'is_bridge'
        ],
        ['==', 'kind', 'highway'
        ],
        ['!has', 'is_link'
        ]
      ],
      paint: {
        'line-color': '#ffffff',
        'line-gap-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          3,
          0,
          3.5,
          0.5,
          18,
          15
        ],
        'line-width': ['interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          7,
          0,
          7.5,
          1,
          20,
          15
        ]
      }
    },
    // roads_bridges_highway
    {
      id: 'roads_bridges_highway',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'roads',
      filter: ['all',
        ['has', 'is_bridge'
        ],
        ['==', 'kind', 'highway'
        ],
        ['!has', 'is_link'
        ]
      ],
      paint: {
        'line-color': '#ebebeb',
        'line-width': [
          'interpolate',
          ['exponential',
            1.6
          ],
          ['zoom'
          ],
          3,
          0,
          6,
          1.1,
          12,
          1.6,
          15,
          5,
          18,
          15
        ]
      }
    },
    // buildings
    {
      id: 'buildings',
      type: 'fill',
      source: 'protomaps',
      'source-layer': 'buildings',
      filter: ['in', 'kind', 'building', 'building_part'
      ],
      paint: {
        'fill-color': '#efefef',
        'fill-opacity': 0.5
      }
    },
    // water
    {
      id: 'water',
      type: 'fill',
      filter: ['==', '$type', 'Polygon'
      ],
      source: 'protomaps',
      'source-layer': 'water',
      paint: {
        'fill-color': '#0a819f',
        'fill-opacity': 0.95,
      }
    },
    // water_stream
    {
      id: 'water_stream',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'water',
      minzoom: 10,
      filter: ['in', 'kind', 'stream'
      ],
      paint: {
        'line-color': '#0a819f',
        'line-width': 0.5,
        'line-opacity': 0.95,
      }
    },
    // water_river
    {
      id: 'water_river',
      type: 'line',
      source: 'protomaps',
      'source-layer': 'water',
      minzoom: 10,
      filter: ['in', 'kind', 'river'
      ],
      paint: {
        'line-color': '#0a819f',
        'line-opacity': 0.95,
        'line-width': [
          'interpolate',
          ['linear'
          ],
          // ['exponential', 1.6], 
          ['zoom'
          ],
          10,
          0.5,
          11,
          1,
          18,
          12
        ]
      }
    },


    // LABELS
    // address_label
    {
      id: 'address_label',
      type: 'symbol',
      source: 'protomaps',
      'source-layer': 'buildings',
      minzoom: 18,
      filter: ['==', 'kind', 'address'],
      layout: {
        'symbol-placement': 'point',
        'text-font': ['Noto Sans Italic'],
        'text-field': ['get', 'addr_housenumber'],
        'text-size': 12
      },
      paint: {
        'text-color': '#adadad',
        'text-halo-color': '#ffffff',
        'text-halo-width': 1
      }
    },
    // water_waterway_label
    {
      id: 'water_waterway_label',
      type: 'symbol',
      source: 'protomaps',
      'source-layer': 'water',
      minzoom: 13,
      filter: ['in', 'kind', 'river', 'stream'],
      layout: {
        'symbol-placement': 'line',
        'text-font': ['Noto Sans Italic'],
        'text-field': [
          'case',
          [
            'all',
            ['any', ['has', 'name'], ['has', 'pgf:name']],
            ['!', ['any', ['has', 'name2'], ['has', 'pgf:name2']]],
            ['!', ['any', ['has', 'name3'], ['has', 'pgf:name3']]]
          ],
          [
            'case',
            ['has', 'script'],
            [
              'case',
              ['any', ['is-supported-script', ['get', 'name']], ['has', 'pgf:name']],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'name:en']],
                {},
                '\n',
                {},
                [
                  'case',
                  [
                    'all',
                    ['!', ['has', 'name:en']],
                    ['has', 'name:en'],
                    ['!', ['has', 'script']]
                  ],
                  '',
                  ['coalesce', ['get', 'pgf:name'], ['get', 'name']]
                ],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ],
              ['get', 'name:en']
            ],
            [
              'format',
              ['coalesce', ['get', 'name:en'], ['get', 'pgf:name'], ['get', 'name']],
              {}
            ]
          ],
          [
            'all',
            ['any', ['has', 'name'], ['has', 'pgf:name']],
            ['any', ['has', 'name2'], ['has', 'pgf:name2']],
            ['!', ['any', ['has', 'name3'], ['has', 'pgf:name3']]]
          ],
          [
            'case',
            ['all', ['has', 'script'], ['has', 'script2']],
            [
              'format',
              ['get', 'name:en'],
              {},
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              },
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script2'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              }
            ],
            [
              'case',
              ['has', 'script2'],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name'], ['get', 'name']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script2'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name2'], ['get', 'name2']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ]
            ]
          ],
          [
            'case',
            ['all', ['has', 'script'], ['has', 'script2'], ['has', 'script3']],
            [
              'format',
              ['get', 'name:en'],
              {},
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              },
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script2'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              },
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name3'], ['get', 'name3']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script3'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              }
            ],
            [
              'case',
              ['!', ['has', 'script']],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name'], ['get', 'name']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script2'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                },
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name3'], ['get', 'name3']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script3'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ],
              ['!', ['has', 'script2']],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name2'], ['get', 'name2']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                },
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name3'], ['get', 'name3']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script3'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name3'], ['get', 'name3']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                },
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script2'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ]
            ]
          ]
        ],
        'text-size': 12,
        'text-letter-spacing': 0.2
      },
      paint: {
        'text-color': '#adadad',
        'text-halo-color': '#dcdcdc',
        'text-halo-width': 1
      }
    },
    // roads_labels_minor
    {
      id: 'roads_labels_minor',
      type: 'symbol',
      source: 'protomaps',
      'source-layer': 'roads',
      minzoom: 15,
      filter: ['in', 'kind', 'minor_road', 'other', 'path'],
      layout: {
        'symbol-sort-key': ['get', 'min_zoom'],
        'symbol-placement': 'line',
        'text-font': ['Noto Sans Regular'],
        'text-field': [
          'case',
          [
            'all',
            ['any', ['has', 'name'], ['has', 'pgf:name']],
            ['!', ['any', ['has', 'name2'], ['has', 'pgf:name2']]],
            ['!', ['any', ['has', 'name3'], ['has', 'pgf:name3']]]
          ],
          [
            'case',
            ['has', 'script'],
            [
              'case',
              ['any', ['is-supported-script', ['get', 'name']], ['has', 'pgf:name']],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'name:en']],
                {},
                '\n',
                {},
                [
                  'case',
                  [
                    'all',
                    ['!', ['has', 'name:en']],
                    ['has', 'name:en'],
                    ['!', ['has', 'script']]
                  ],
                  '',
                  ['coalesce', ['get', 'pgf:name'], ['get', 'name']]
                ],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ],
              ['get', 'name:en']
            ],
            [
              'format',
              ['coalesce', ['get', 'name:en'], ['get', 'pgf:name'], ['get', 'name']],
              {}
            ]
          ],
          [
            'all',
            ['any', ['has', 'name'], ['has', 'pgf:name']],
            ['any', ['has', 'name2'], ['has', 'pgf:name2']],
            ['!', ['any', ['has', 'name3'], ['has', 'pgf:name3']]]
          ],
          [
            'case',
            ['all', ['has', 'script'], ['has', 'script2']],
            [
              'format',
              ['get', 'name:en'],
              {},
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              },
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script2'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              }
            ],
            [
              'case',
              ['has', 'script2'],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name'], ['get', 'name']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script2'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name2'], ['get', 'name2']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ]
            ]
          ],
          [
            'case',
            ['all', ['has', 'script'], ['has', 'script2'], ['has', 'script3']],
            [
              'format',
              ['get', 'name:en'],
              {},
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              },
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script2'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              },
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name3'], ['get', 'name3']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script3'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              }
            ],
            [
              'case',
              ['!', ['has', 'script']],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name'], ['get', 'name']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script2'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                },
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name3'], ['get', 'name3']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script3'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ],
              ['!', ['has', 'script2']],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name2'], ['get', 'name2']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                },
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name3'], ['get', 'name3']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script3'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name3'], ['get', 'name3']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                },
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script2'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ]
            ]
          ]
        ],
        'text-size': 12
      },
      paint: {
        'text-color': '#adadad',
        'text-halo-color': '#ffffff',
        'text-halo-width': 1
      }
    },
    // water_label_lakes
    {
      id: 'water_label_lakes',
      type: 'symbol',
      source: 'protomaps',
      'source-layer': 'water',
      filter: ['in', 'kind', 'lake', 'water'],
        layout: {
          "text-font": ["Noto Sans Italic"],
          "text-field": ["coalesce", ["get", "name:en"], ["get", "name"]],
          "text-size": [
            "interpolate",
            ["linear"],
            ["zoom"],
            8, 16,
            14, 20
          ],
          "text-letter-spacing": 0.1,
          "text-max-width": 9
      },

      paint: {
        'text-color': '#ffffff',
        'text-halo-color': 'rgba(0, 0, 0, 0.25)',
        'text-halo-width': 2
      }
    },
    // roads_labels_major
    {
      id: 'roads_labels_major',
      type: 'symbol',
      source: 'protomaps',
      'source-layer': 'roads',
      minzoom: 11,
      filter: ['in', 'kind', 'highway', 'major_road'],
      layout: {
        'symbol-sort-key': ['get', 'min_zoom'],
        'symbol-placement': 'line',
        'text-font': ['Noto Sans Regular'],
        'text-field': [
          'case',
          [
            'all',
            ['any', ['has', 'name'], ['has', 'pgf:name']],
            ['!', ['any', ['has', 'name2'], ['has', 'pgf:name2']]],
            ['!', ['any', ['has', 'name3'], ['has', 'pgf:name3']]]
          ],
          [
            'case',
            ['has', 'script'],
            [
              'case',
              ['any', ['is-supported-script', ['get', 'name']], ['has', 'pgf:name']],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'name:en']],
                {},
                '\n',
                {},
                [
                  'case',
                  [
                    'all',
                    ['!', ['has', 'name:en']],
                    ['has', 'name:en'],
                    ['!', ['has', 'script']]
                  ],
                  '',
                  ['coalesce', ['get', 'pgf:name'], ['get', 'name']]
                ],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ],
              ['get', 'name:en']
            ],
            [
              'format',
              ['coalesce', ['get', 'name:en'], ['get', 'pgf:name'], ['get', 'name']],
              {}
            ]
          ],
          [
            'all',
            ['any', ['has', 'name'], ['has', 'pgf:name']],
            ['any', ['has', 'name2'], ['has', 'pgf:name2']],
            ['!', ['any', ['has', 'name3'], ['has', 'pgf:name3']]]
          ],
          [
            'case',
            ['all', ['has', 'script'], ['has', 'script2']],
            [
              'format',
              ['get', 'name:en'],
              {},
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              },
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script2'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              }
            ],
            [
              'case',
              ['has', 'script2'],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name'], ['get', 'name']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script2'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name2'], ['get', 'name2']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ]
            ]
          ],
          [
            'case',
            ['all', ['has', 'script'], ['has', 'script2'], ['has', 'script3']],
            [
              'format',
              ['get', 'name:en'],
              {},
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              },
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script2'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              },
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name3'], ['get', 'name3']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script3'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              }
            ],
            [
              'case',
              ['!', ['has', 'script']],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name'], ['get', 'name']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script2'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                },
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name3'], ['get', 'name3']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script3'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ],
              ['!', ['has', 'script2']],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name2'], ['get', 'name2']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                },
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name3'], ['get', 'name3']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script3'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name3'], ['get', 'name3']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                },
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script2'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ]
            ]
          ]
        ],
        'text-size': 12
      },
      paint: {
        'text-color': '#999999',
        'text-halo-color': '#ffffff',
        'text-halo-width': 1
      }
    },
    // places_subplace
    {
      id: 'places_subplace',
      type: 'symbol',
      source: 'protomaps',
      'source-layer': 'places',
      filter: ['==', 'kind', 'neighbourhood'],
      layout: {
        'symbol-sort-key': ['get', 'min_zoom'],
        'text-field': [
          'case',
          [
            'all',
            ['any', ['has', 'name'], ['has', 'pgf:name']],
            ['!', ['any', ['has', 'name2'], ['has', 'pgf:name2']]],
            ['!', ['any', ['has', 'name3'], ['has', 'pgf:name3']]]
          ],
          [
            'case',
            ['has', 'script'],
            [
              'case',
              ['any', ['is-supported-script', ['get', 'name']], ['has', 'pgf:name']],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'name:en']],
                {},
                '\n',
                {},
                [
                  'case',
                  [
                    'all',
                    ['!', ['has', 'name:en']],
                    ['has', 'name:en'],
                    ['!', ['has', 'script']]
                  ],
                  '',
                  ['coalesce', ['get', 'pgf:name'], ['get', 'name']]
                ],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ],
              ['get', 'name:en']
            ],
            [
              'format',
              ['coalesce', ['get', 'name:en'], ['get', 'pgf:name'], ['get', 'name']],
              {}
            ]
          ],
          [
            'all',
            ['any', ['has', 'name'], ['has', 'pgf:name']],
            ['any', ['has', 'name2'], ['has', 'pgf:name2']],
            ['!', ['any', ['has', 'name3'], ['has', 'pgf:name3']]]
          ],
          [
            'case',
            ['all', ['has', 'script'], ['has', 'script2']],
            [
              'format',
              ['get', 'name:en'],
              {},
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              },
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script2'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              }
            ],
            [
              'case',
              ['has', 'script2'],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name'], ['get', 'name']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script2'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name2'], ['get', 'name2']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ]
            ]
          ],
          [
            'case',
            ['all', ['has', 'script'], ['has', 'script2'], ['has', 'script3']],
            [
              'format',
              ['get', 'name:en'],
              {},
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              },
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script2'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              },
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name3'], ['get', 'name3']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script3'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              }
            ],
            [
              'case',
              ['!', ['has', 'script']],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name'], ['get', 'name']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script2'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                },
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name3'], ['get', 'name3']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script3'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ],
              ['!', ['has', 'script2']],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name2'], ['get', 'name2']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                },
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name3'], ['get', 'name3']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script3'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name3'], ['get', 'name3']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                },
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script2'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ]
            ]
          ]
        ],
        'text-font': ['Noto Sans Regular'],
        'text-max-width': 7,
        'text-letter-spacing': 0.1,
        'text-padding': ['interpolate', ['linear'], ['zoom'], 5, 2, 8, 4, 12, 18, 15, 20],
        'text-size': ['interpolate', ['exponential', 1.2], ['zoom'], 11, 8, 14, 14, 18, 24],
        'text-transform': 'uppercase'
      },
      paint: {
        'text-color': '#8f8f8f',
        'text-halo-color': '#ffffff',
        'text-halo-width': 1
      }
    },
    // places_locality
    {
      id: 'places_locality',
      type: 'symbol',
      source: 'protomaps',
      'source-layer': 'places',
      filter: ['==', 'kind', 'locality'],
      layout: {
        'icon-image': ['step', ['zoom'], 'townspot', 8, ''],
        'icon-size': 0.7,
        'text-field': [
          'case',
          [
            'all',
            ['any', ['has', 'name'], ['has', 'pgf:name']],
            ['!', ['any', ['has', 'name2'], ['has', 'pgf:name2']]],
            ['!', ['any', ['has', 'name3'], ['has', 'pgf:name3']]]
          ],
          [
            'case',
            ['has', 'script'],
            [
              'case',
              ['any', ['is-supported-script', ['get', 'name']], ['has', 'pgf:name']],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'name:en']],
                {},
                '\n',
                {},
                [
                  'case',
                  [
                    'all',
                    ['!', ['has', 'name:en']],
                    ['has', 'name:en'],
                    ['!', ['has', 'script']]
                  ],
                  '',
                  ['coalesce', ['get', 'pgf:name'], ['get', 'name']]
                ],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ],
              ['get', 'name:en']
            ],
            [
              'format',
              ['coalesce', ['get', 'name:en'], ['get', 'pgf:name'], ['get', 'name']],
              {}
            ]
          ],
          [
            'all',
            ['any', ['has', 'name'], ['has', 'pgf:name']],
            ['any', ['has', 'name2'], ['has', 'pgf:name2']],
            ['!', ['any', ['has', 'name3'], ['has', 'pgf:name3']]]
          ],
          [
            'case',
            ['all', ['has', 'script'], ['has', 'script2']],
            [
              'format',
              ['get', 'name:en'],
              {},
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              },
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script2'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              }
            ],
            [
              'case',
              ['has', 'script2'],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name'], ['get', 'name']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script2'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name2'], ['get', 'name2']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ]
            ]
          ],
          [
            'case',
            ['all', ['has', 'script'], ['has', 'script2'], ['has', 'script3']],
            [
              'format',
              ['get', 'name:en'],
              {},
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              },
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script2'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              },
              '\n',
              {},
              ['coalesce', ['get', 'pgf:name3'], ['get', 'name3']],
              {
                'text-font': [
                  'case',
                  ['==', ['get', 'script3'], 'Devanagari'],
                  ['literal', ['Noto Sans Devanagari Regular v1']],
                  ['literal', ['Noto Sans Regular']]
                ]
              }
            ],
            [
              'case',
              ['!', ['has', 'script']],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name'], ['get', 'name']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script2'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                },
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name3'], ['get', 'name3']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script3'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ],
              ['!', ['has', 'script2']],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name2'], ['get', 'name2']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                },
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name3'], ['get', 'name3']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script3'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ],
              [
                'format',
                ['coalesce', ['get', 'name:en'], ['get', 'pgf:name3'], ['get', 'name3']],
                {},
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name'], ['get', 'name']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                },
                '\n',
                {},
                ['coalesce', ['get', 'pgf:name2'], ['get', 'name2']],
                {
                  'text-font': [
                    'case',
                    ['==', ['get', 'script2'], 'Devanagari'],
                    ['literal', ['Noto Sans Devanagari Regular v1']],
                    ['literal', ['Noto Sans Regular']]
                  ]
                }
              ]
            ]
          ]
        ],
        'text-font': ['Noto Sans Regular'],
        'text-padding': ['interpolate', ['linear'], ['zoom'], 5, 3, 8, 7, 12, 11],
        'text-size': [
          'interpolate',
          ['linear'],
          ['zoom'],
          2, [
            'case', ['<', ['get', 'population_rank'], 13], 8,
            ['>=', ['get', 'population_rank'], 13], 13,
            0
          ],
          4, [
            'case', ['<', ['get', 'population_rank'], 13], 10,
            ['>=', ['get', 'population_rank'], 13], 15,
            0
          ],
          6,
          [
            'case', ['<', ['get', 'population_rank'], 12], 11,
            ['>=', ['get', 'population_rank'], 12], 17,
            0
          ],
          8,
          [
            'case', ['<', ['get', 'population_rank'], 11], 11,
            ['>=', ['get', 'population_rank'], 11], 18,
            0
          ],
          10,
          [
            'case', ['<', ['get', 'population_rank'], 9], 12,
            ['>=', ['get', 'population_rank'], 9], 20,
            0
          ],
          15,
          [
            'case', ['<', ['get', 'population_rank'], 8], 12,
            ['>=', ['get', 'population_rank'], 8], 22,
            0
          ]
        ],
        'icon-padding': [
          'interpolate',
          ['linear'],
          ['zoom'],
          0, 0,
          8, 4,
          10, 8,
          12, 6,
          22, 2
        ],
        'text-justify': 'auto',
        'text-anchor': ['step', ['zoom'], 'left', 8, 'center'],
        'text-radial-offset': 0.4,
      },
      paint: {
        'text-color': '#5c5c5c',
        'text-halo-color': '#ffffff',
        'text-halo-width': 1
      }
    }
  ]
}
export default style