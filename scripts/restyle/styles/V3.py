"""V3 - style of V1 (ADR 0011). Regenerate: uv run python scripts/restyle/run.py V3

Espresso & Terracotta (moody warm): Universal-Khaki walls, espresso + smoked oak + honey oak, terracotta floors
and zellige, deep teal, rust, merlot in the master suite, terracotta + mustard kids' room. Metals: antique brass
+ black (track lights).
"""

BRASS = "#9a7442"      # antique brass
ESPRESSO = "#3b2c24"   # espresso wood (slats, portal, sofa base)
ESPRESSO2 = "#4a382d"  # espresso oak joinery
KHAKI = "#b8a992"      # Universal Khaki lacquer
TERRA = "#b0643f"      # terracotta velvet
RUST = "#8e4a2e"       # rust
COGNAC = "#7a4a2a"     # cognac leather
TEAL = "#2f5f62"       # deep teal
SAND = "#d6c2a0"       # sand wool / linen
HONEY = "#b48552"      # honey oak
INTERIOR = "#cbb595"   # khaki-oak cabinet interiors

SPEC = dict(
    name="Espresso & Terracotta",
    description=("Colour scheme of V1 (same furniture, same places): moody warm - Universal-Khaki walls, "
                 "espresso + smoked oak wood, terracotta velvet sofa + cognac leather armchairs against a deep-teal "
                 "ripple wall, rust drapes, terracotta floors and zellige, deep-teal bath and hall wardrobe, merlot "
                 "master suite, terracotta + mustard kids' room, antique brass"),
    wall_color="#ddd2bf",
    rooms={
        "living": dict(floor="smoked_oak", paint="#d2c3aa", skirting=ESPRESSO),
        "hall": dict(floor="terracotta_tiles", paint="#ddd2bf"),
        "kitchen": dict(floor="terracotta_tiles", paint="#e6dccb"),
        "bath_1": dict(floor="travertine", walls="teal_zellige"),
        "bath_2": dict(floor="terracotta_tiles", walls="travertine"),
        "bedroom_1": dict(floor="honey_oak", paint="#efdcc4", skirting="#efe2cf"),
        "bedroom_2": dict(floor="smoked_oak", paint="#c9b7a3", skirting=ESPRESSO),
        "balcony": dict(floor="terracotta_tiles"),
    },
    aprons={"ripple": {"living": "espresso_ripple_teal", "bedroom_2": "espresso_chevron"},
            "delicate_blues": "espresso_apricot_mural", "cream_marble": "clay_zellige",
            "greige_stone": "travertine"},
    metal={"*": BRASS},
    accent={"*": ESPRESSO,              # sofa / armchair espresso base + feet
            "bedroom_1": "#e8b48a",     # duvet apricot linen
            "bedroom_2": "#e6d5bc",     # duvet oat linen against the espresso chevron
            "bath_1": "#dacab0", "bath_2": "#dacab0"},  # shower curb travertine
    colors={
        "*": {"#b08d57": BRASS,                 # brass -> darker antique brass
              "#fbfaf7": "#efe2cf",             # sheers warm sand linen
              "#8e9196": "#d8ccb6"},            # AC units blend with the khaki walls
        "living": {"#86694b": TERRA,            # plush sofa: terracotta velvet (armchairs: items)
                   "#6f6152": SAND,             # shag rug sand wool
                   "#313233": "#cdbb9c",        # coffee table travertine
                   "#3a3b3d": BRASS,            # side table antique brass
                   "#6b4a33": ESPRESSO,         # slat TV wall espresso
                   "#6f5646": RUST,             # drapes rust
                   "#a08b78": KHAKI,            # wardrobe doors Universal Khaki
                   "#8a5f3e": ESPRESSO2,        # wood column espresso (interior: items)
                   "#b88a5a": BRASS,
                   "#c9a46a": BRASS,            # infinity pendant antique brass
                   "#1e1e1e": BRASS,            # floor lamp brass
                   "#cfcfcd": ESPRESSO2,        # desk top espresso
                   "#6e6e70": "#5a3b2e",        # gaming chair brown
                   "#ece6dc": "#4c7472"},       # wallpaper panel base teal
        "hall": {"#6b4a33": ESPRESSO, "#8a5a3c": ESPRESSO, "#8a5f3e": INTERIOR,
                 "#a08b78": TEAL,               # hall wardrobe deep teal
                 "#b88a5a": BRASS, "#3a3633": "#5a3b2e",
                 "#3b3b3d": "#b8693f", "#d9cfc0": "#e9dcc8", "#5a3e2b": COGNAC},
        "kitchen": {"#cfc2ad": "#2f4f53",       # base + tall units, oven: deep ink-teal
                    "#7a5236": ESPRESSO2,       # worktop, wood wall units, table: espresso oak
                    "#b9a88c": BRASS, "#3a3a3a": BRASS,
                    "#b8a990": COGNAC,          # upholstered chairs cognac leather
                    "#efe6d6": "#c47b57",       # backsplash terracotta zellige
                    "#1c1c1c": "#cdbb9c",       # sink: sand composite
                    "#1e1e1e": BRASS,           # linear pendant antique brass
                    "#f4f3f0": "#c98a68",       # place settings + bowl: clay stoneware
                    "#e6e4df": "#e6dccb"},
        "bath_1": {"#3f2a1c": ESPRESSO2, "#6b4428": ESPRESSO2, "#3a3a3a": BRASS,
                   "#d9cbb5": "#a5583a",        # towels rust
                   "#e6ddd0": "#cdbb9c",        # vessel sink travertine
                   "#c4b6a4": TEAL},
        "bath_2": {"#3f2a1c": ESPRESSO2, "#3a3a3a": BRASS,
                   "#d9cbb5": TEAL,             # towels deep teal
                   "#e6ddd0": "#b8693f",        # vessel sink terracotta clay
                   "#c4b6a4": "#dacab0"},
        "bedroom_1": {"#7f9fb0": "#b8714f",     # wardrobe doors + chair terracotta
                      "#efe6d6": "#f1e6d4",
                      "#8ea8b6": "#c49a3c",     # drapes mustard
                      "#5a7f96": "#7a9e98",     # rug sea-teal wool
                      "#c9a77c": HONEY,         # honey oak desk, slats, handles
                      "#2f6fb3": "#a5512f",     # tag terracotta
                      "#d8cfc2": "#c49a3c",     # table lamp mustard
                      "#ede6dc": "#f1e4d2", "#ecebe8": HONEY,
                      "#3d6fa8": "#b8693f", "#5e8fbf": "#c49a3c"},
        "bedroom_2": {"#a08b78": KHAKI,         # wardrobes khaki
                      "#8a5f3e": ESPRESSO2,     # wood column + bed espresso (interiors: items)
                      "#b88a5a": BRASS,
                      "#6b4a33": ESPRESSO,
                      "#6f5646": "#6b2f33",     # drapes merlot
                      "#8a7764": "#a87a78",     # rug dusty plum-rose
                      "#ece6dc": "#6a5240",
                      "#ecebe8": ESPRESSO2,     # nightstands espresso
                      "#d8cfc2": BRASS},        # table lamps antique brass
        "balcony": {"#9a6b43": "#2b2b2b", "#2f2f31": "#b8693f", "#f2efe9": "#c98a68"},
    },
    items={
        "plush-armchair-living-1": {"color": COGNAC},    # cognac leather armchairs
        "plush-armchair-living-2": {"color": COGNAC},
        "wardrobe-living-1": {"interior_color": INTERIOR},
        "wardrobe-master-suite-1": {"interior_color": INTERIOR},
        "wardrobe-master-suite-2": {"interior_color": INTERIOR},
        "tv-console-master-suite-1": {"interior_color": INTERIOR},
        "wardrobe-bedroom-1-1": {"interior_color": "#f1e6d4"},
        "tall-cabinet-bathroom-1-1": {"interior_color": INTERIOR},
        "tall-cabinet-master-bathroom-1": {"interior_color": INTERIOR},
    },
    finishes={
        "espresso_ripple_teal": dict(kind="ripple", size=[3.04, 2.70], color="#4c7472", color2="#2f5355",
                                     joint_color="#4c7472", joint=0.0, roughness=0.85,
                                     note="V3: deep-teal 'Ripple' wallpaper behind the terracotta sofa (living)"),
        "espresso_apricot_mural": dict(kind="watercolor", size=[3.10, 2.70], color="#f1e0c8", color2="#c9794f",
                                       joint_color="#f1e0c8", joint=0.0, roughness=0.9,
                                       note="V3: cream mural with apricot / terracotta sunset washes (kids' bed wall)"),
    },
)
