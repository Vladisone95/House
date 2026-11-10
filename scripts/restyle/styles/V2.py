"""V2 - style of V1 (ADR 0011). Regenerate: uv run python scripts/restyle/run.py V2

Sage & Oak (Japandi light): Cloud Dancer whites, pale ash floor + light oak, sage / eucalyptus / forest greens,
muted rose in the master suite, butter + sage kids' room, matte black metal. Woods: pale ash, light oak, pale
birch (interiors). Metal: matte black only.
"""

OAK = "#c09a6c"        # light oak joinery
BLACK = "#2b2b2b"      # matte black metal
OLIVE = "#6f7d5a"      # deep sage-olive velvet (living sofa)
OAT = "#d9ccb2"        # oatmeal boucle / linen
SAGE = "#a7b39b"       # sage zellige / sage paint
EUCA = "#7f9177"       # eucalyptus green lacquer
FOREST = "#4f5e48"     # forest green
ROSE = "#c49488"       # muted rose
BIRCH = "#e6dcc8"      # pale birch interiors
CLOUD = "#efede6"      # Cloud Dancer white

SPEC = dict(
    name="Sage & Oak",
    description=("Colour scheme of V1 (same furniture, same places): Japandi light - Cloud Dancer whites, "
                 "pale ash + light oak, sage-olive velvet sofa with oatmeal boucle armchairs, sage / eucalyptus / "
                 "forest greens, muted rose + forest green in the master suite, butter + sage kids' room, "
                 "cream terrazzo + sage zellige, matte black metal"),
    wall_color=CLOUD,
    rooms={
        "living": dict(floor="pale_ash", paint="#dfe3d4", skirting=OAK),
        "hall": dict(floor="cream_terrazzo", paint=CLOUD),
        "kitchen": dict(floor="cream_terrazzo", paint="#eeebe2"),
        "bath_1": dict(floor="cream_terrazzo", walls="sage_zellige"),
        "bath_2": dict(floor="cream_terrazzo", walls="cloud_stone"),
        "bedroom_1": dict(floor="pale_ash", paint="#f0e4c4", skirting=CLOUD),
        "bedroom_2": dict(floor="pale_ash", paint="#dcc3b8", skirting=OAK),
        "balcony": dict(floor="outdoor_tiles"),
    },
    aprons={"ripple": {"living": "sageoak_ripple_sage", "bedroom_2": "ripple_forest"},
            "delicate_blues": "sageoak_meadow", "cream_marble": "sage_zellige",
            "greige_stone": "cloud_stone"},
    metal={"*": BLACK},
    accent={"*": OAK,                  # sofa / armchair oak base + feet
            "bedroom_1": "#dfe5d3",    # duvet: sage-white linen
            "bedroom_2": "#b9c2a6",    # duvet: sage linen against the rose walls
            "bath_1": "#ece5d8", "bath_2": "#ece5d8"},  # shower curb cream terrazzo
    colors={
        "*": {"#b08d57": BLACK,                 # brass fittings -> matte black
              "#151515": BLACK,                 # track lights
              "#fbfaf7": "#f1eee4",             # sheers: natural linen
              "#8e9196": "#e6e6e0"},            # AC units blend with the walls
        "living": {"#86694b": OLIVE,            # plush sofa: deep sage-olive velvet (armchairs: items)
                   "#6f6152": "#c2c4a8",        # shag rug: sage-oat wool
                   "#313233": OAK,              # coffee table light oak
                   "#3a3b3d": BLACK,            # side table matte black
                   "#6b4a33": OAK,              # slat TV wall light oak
                   "#6f5646": "#5f7a6e",        # drapes smoky jade
                   "#a08b78": "#aab19d",        # wardrobe doors sage-grey
                   "#8a5f3e": OAK,              # wardrobe wood column light oak (interior: items)
                   "#b88a5a": BLACK,            # handles black
                   "#c9a46a": BLACK,            # infinity pendant matte black ring
                   "#1e1e1e": OAK,              # floor lamp oak
                   "#cfcfcd": "#e2d3b8",        # desk top white oak
                   "#6e6e70": "#8f9886",        # gaming chair sage-grey
                   "#ece6dc": "#b8c2a8"},       # wallpaper panel base
        "hall": {"#6b4a33": OAK, "#8a5a3c": OAK, "#8a5f3e": BIRCH,
                 "#a08b78": EUCA,               # hall wardrobe eucalyptus
                 "#b88a5a": BLACK, "#3a3633": "#6b7062",
                 "#3b3b3d": "#8a9a7c", "#d9cfc0": CLOUD, "#5a3e2b": "#9c7a52"},
        "kitchen": {"#cfc2ad": EUCA,            # base + tall units, oven: eucalyptus green
                    "#7a5236": OAK,             # worktop, wood wall units, dining table: light oak
                    "#b9a88c": BLACK,           # base-unit handles black
                    "#3a3a3a": BLACK,
                    "#b8a990": OAT,             # upholstered chairs oatmeal linen
                    "#efe6d6": SAGE,            # backsplash panel = sage zellige
                    "#1c1c1c": "#2e2e2c",       # sink matte black granite
                    "#1e1e1e": BLACK,           # linear pendant
                    "#f4f3f0": "#dfe2d5",       # place settings: sage-white stoneware
                    "#e6e4df": CLOUD},
        "bath_1": {"#3f2a1c": OAK, "#6b4428": OAK, "#3a3a3a": BLACK,
                   "#d9cbb5": OAT,              # towels oatmeal
                   "#e6ddd0": "#2e2e2c",        # vessel sink matte black stone
                   "#c4b6a4": SAGE, "#d9dde0": "#d9dde0"},
        "bath_2": {"#3f2a1c": OAK, "#3a3a3a": BLACK,
                   "#d9cbb5": "#93a385",        # towels sage
                   "#e6ddd0": SAGE,             # vessel sink sage ceramic
                   "#c4b6a4": "#ece8df"},
        "bedroom_1": {"#7f9fb0": "#d8c486",     # wardrobe doors: butter yellow (desk chair: items)
                      "#efe6d6": "#f3eee2",     # cream carcass, bed, storage
                      "#8ea8b6": "#8fa07c",     # drapes sage
                      "#5a7f96": "#a9b58f",     # rug sage wool
                      "#c9a77c": "#d6bb91",     # desk, slat wall, handles pale oak
                      "#2f6fb3": "#5d7f4f",     # "Baby Turi" tag sage green
                      "#d8cfc2": "#e8d9a8",     # table lamp butter
                      "#ede6dc": "#f2ecdc", "#ecebe8": "#d6bb91",
                      "#3d6fa8": "#7f9a6c", "#5e8fbf": "#d8b44f"},
        "bedroom_2": {"#a08b78": "#e9e3d8",     # wardrobe / console doors warm white
                      "#8a5f3e": OAK,           # wood column + bed light oak (interiors: items)
                      "#b88a5a": BLACK,
                      "#6b4a33": OAK,           # slat panel light oak
                      "#6f5646": FOREST,        # drapes forest green
                      "#8a7764": ROSE,          # rug muted rose wool
                      "#ece6dc": "#5d6c56",
                      "#ecebe8": OAK,           # nightstands light oak
                      "#d8cfc2": "#e6d3c8"},    # table lamps blush
        "balcony": {"#9a6b43": OAK, "#2f2f31": "#5d6c56", "#f2efe9": "#dfe2d5"},
    },
    items={
        "plush-armchair-living-1": {"color": OAT},       # oatmeal boucle armchairs vs the olive sofa
        "plush-armchair-living-2": {"color": OAT},
        "wardrobe-living-1": {"interior_color": BIRCH},
        "wardrobe-hall-1": {"interior_color": BIRCH},
        "wardrobe-master-suite-1": {"interior_color": BIRCH},
        "wardrobe-master-suite-2": {"interior_color": BIRCH},
        "tv-console-master-suite-1": {"interior_color": BIRCH},
        "wardrobe-bedroom-1-1": {"interior_color": BIRCH},
        "tall-cabinet-bathroom-1-1": {"interior_color": BIRCH},
        "tall-cabinet-master-bathroom-1": {"interior_color": BIRCH},
        "chair-bedroom-1-1": {"color": "#8fa07c"},      # kids' desk chair sage
    },
    finishes={
        "sageoak_ripple_sage": dict(kind="ripple", size=[3.04, 2.70], color="#b8c2a8", color2="#8e9c80",
                                    joint_color="#b8c2a8", joint=0.0, roughness=0.85,
                                    note="V2: 'Ripple' wallpaper in a true mid sage (living sofa wall)"),
        "sageoak_meadow": dict(kind="watercolor", size=[3.10, 2.70], color="#f3ead0", color2="#93a878",
                               joint_color="#f3ead0", joint=0.0, roughness=0.9,
                               note="V2: butter-cream meadow mural with sage washes (kids' bed wall)"),
    },
)
