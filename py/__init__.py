retrofit_order = [
    { "year": 2030, "type": "envelope",    "component": "roof",     "description": "Dachdämmung und Austausch der Dachflächenfenster"},
    { "year": 2032, "type": "envelope",    "component": "windows",  "description": 'Fenstertausch'},
    { "year": 2032, "type": "envelope",    "component": "extWalls", "description": "Dämmung der Außenwände" },
    { "year": 2025, "type": "envelope",    "component": "basement", "description": "Dämmung der Kellerdecke" },
    { "year": 2025, "type": "heating",     "component": "gas-55",   "description": "Einbau eines effizienten Heizkessels"},
    { "year": 2035, "type": "heating",     "component": "hp-35",    "description": "Einbau einer Wärmepumpe"}
]

color_codes = [
    {"qp": 30, "class": "A+", "rgb": [0, 166, 80], "description": "Fortschrittlicher Standard"},
    {"qp": 50, "class": "A", "rgb": [53, 178, 75], "description": "Gesetzliche Anforderung an Neubauten"},
    {"qp": 75, "class": "B", "rgb": [134, 199, 59], "description": "Gesetzliche Anforderung an Neubauten (Stand 2002)"},
    {"qp": 100, "class": "C", "rgb": [207, 222, 35], "description": "Teilsaniertes Gebäude"},
    {"qp": 130, "class": "D", "rgb": [255, 241, 0], "description": "Teilsaniertes oder unsaniertes Gebäude"},
    {"qp": 160, "class": "E", "rgb": [254, 207, 11], "description": "Teilsaniertes oder unsaniertes Gebäude"},
    {"qp": 200, "class": "F", "rgb": [246, 117, 26], "description": "Teilsaniertes oder unsaniertes Gebäude"},
    {"qp": 250, "class": "G", "rgb": [177, 16, 22], "description": "Teilsaniertes oder unsaniertes Gebäude"},
    {"qp": 999, "class": "H", "rgb": [177, 16, 22], "description": "Teilsaniertes oder unsaniertes Gebäude"}
]

description_initial_condition = [
    {"qp": 30, "text": ["Ihr Gebäude erfüllt die fortschrittlichsten energetischen Standards.  Glückwunsch!"]},
    {"qp": 60, "text": ["Ihr Gebäude erfüllt die aktuell geltenden Anforderungen an Neubauten. Glückwunsch!"]},
    {"qp": 90, "text": ["Ihr Gebäude erfüllt die Anforderungen an Neubauten aus dem Jahr 2002."]},
    {"qp": 130, "text": ["Die energetische Eigenschaften ihres Gebäudes sind überdurchschnittlich gut, bieten aber dennoch ein großes Einsparpotential."]},
    {"qp": 180, "text": ["Der Energieverbrauch Ihres Gebäudes ist überdurchschnittlich groß.",
                         "Eine energetische Sanierung lohnt sich in Ihrem Fall besonders, da Sie Ihre Energiekosten erheblich senken können."]},
    {"qp": 230, "text": ["Der Energieverbrauch Ihres Gebäudes ist überdurchschnittlich groß.",
                         "Eine energetische Sanierung lohnt sich in Ihrem Fall besonders, da Sie Ihre Energiekosten erheblich senken können."]},
    {"qp": 999, "text": ["Der Energieverbrauch Ihres Gebäudes ist außerordentlich groß.",
                         "Eine energetische Sanierung lohnt sich in Ihrem Fall besonders, da Sie Ihre Energiekosten erheblich senken können."]}
]
