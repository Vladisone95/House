"""V6 Warm Minimalism = V1 layout (same ids, sizes, positions, rotations), new colours + finishes only."""


OAK = "#b08660"        # natural white oak, matte oiled
OAK_LT = "#d2b48c"     # light oiled oak (cabinet interiors)
BRONZE = "#7a5f44"     # brushed / aged bronze
LIME = "#c2a67e"       # limewash-sand lacquer fronts
STONE = "#bda57f"      # honed limestone
ECRU = "#ddcdb2"       # ecru boucle / linen
CAMEL = "#a0724a"      # camel / cognac leather + wool

SPEC = dict(
    name="Warm Minimalism",
    description=("Colour scheme of V1 (same furniture, same places): warm minimalism - tonal limewash sand walls "
                 "with matching skirting, wide natural-oak floors, honed limestone + tadelakt baths, "
                 "oak + limewash fronts, ecru boucle sofa with camel-leather armchairs and oak plinth, "
                 "oat linen drapes, apricot-oat kids room, camel master suite, brushed bronze"),
    wall_color="#d8c3a2",
    rooms={
        "living": dict(floor="warmmin_natural_oak", paint="#d4b994", skirting="#d4b994"),
        "hall": dict(floor="warmmin_limestone", paint="#cfb48f", skirting="#cfb48f"),
        "kitchen": dict(floor="warmmin_limestone", paint="#d8bf9a", skirting="#d8bf9a"),
        "bath_1": dict(floor="warmmin_limestone", walls="warmmin_tadelakt"),
        "bath_2": dict(floor="warmmin_limestone", walls="warmmin_limestone_slab"),
        "bedroom_1": dict(floor="warmmin_natural_oak", paint="#ecd0b0", skirting="#ecd0b0"),
        "bedroom_2": dict(floor="warmmin_natural_oak", paint="#cbb08e", skirting="#cbb08e"),
        "balcony": dict(floor="warmmin_limestone"),
    },
    aprons={"ripple": {"living": "warmmin_ripple_oat", "bedroom_2": "warmmin_ripple_camel"},
            "delicate_blues": "warmmin_dune_watercolor", "cream_marble": "warmmin_limestone_slab",
            "greige_stone": "warmmin_tadelakt"},
    accent={"living": OAK,                        # sofa / armchair plinth + feet natural oak
            "bedroom_1": "#efd9bf",               # kids' duvet soft apricot linen
            "bedroom_2": "#ece2d0",               # master duvet ecru linen
            "bath_1": STONE,                      # shower curb limestone
            "*": OAK},
    metal={"*": BRONZE},
    colors={
        "*": {"#b08d57": BRONZE,                  # brass fittings -> brushed bronze
              "#151515": BRONZE,                  # track lights bronze
              "#fbfaf7": "#f3ece0",               # sheers warm ecru voile
              "#d8cfc2": "#e9dcc6",               # table lamps linen shades
              "#f6f6f6": "#f1ece3"},              # sanitary in warm bisque white
        "living": {"#86694b": ECRU,               # corner sofa ecru boucle (armchairs overridden: camel leather)
                   "#6f6152": "#a9835a",          # shag rug camel wool
                   "#313233": STONE,              # coffee table honed limestone
                   "#3a3b3d": BRONZE,             # side table bronze
                   "#6b4a33": OAK,                # slat TV wall oak
                   "#6f5646": "#d6c1a0",          # drapes oat linen
                   "#a08b78": LIME,               # wardrobe doors limewash sand
                   "#8a5f3e": OAK,                # wood column oak
                   "#b88a5a": BRONZE,
                   "#c9a46a": "#8f7352",          # infinity pendant bronze
                   "#1e1e1e": BRONZE,             # floor lamp bronze
                   "#cfcfcd": OAK,                # desk top oak
                   "#6e6e70": "#8a6e55",          # gaming chair camel
                   "#ece6dc": "#d4bb96",
                   "#8e9196": "#d4b994"},         # AC = wall
        "hall": {"#6b4a33": OAK, "#8a5a3c": OAK, "#8a5f3e": OAK, "#a08b78": LIME, "#b88a5a": BRONZE,
                 "#3a3633": "#8c7458",            # jute doormat
                 "#3b3b3d": "#a8714e",            # clay vase
                 "#d9cfc0": "#eee6d8",
                 "#5a3e2b": "#9a6a42", "#e9e6df": "#ece2d2"},   # shoes tan leather + ecru
        "kitchen": {"#cfc2ad": OAK,               # base + tall units, oven, plinth: oak fronts
                    "#7a5236": "#c8ad85",         # worktop, wall units, dining table: limestone / bleached oak
                    "#b9a88c": BRONZE, "#3a3a3a": BRONZE,
                    "#b8a990": CAMEL,             # dining chairs camel leather
                    "#1e1e1e": BRONZE,            # linear pendant bronze
                    "#f4f3f0": "#efe6d6",         # place settings ecru stoneware
                    "#1c1c1c": "#a8916f",         # sink sand granite composite
                    "#efe6d6": "#d6c3a4",         # backsplash = limestone slab
                    "#e6e4df": "#d6c3a4"},        # blind
        "bath_1": {"#3f2a1c": OAK, "#6b4428": OAK, "#3a3a3a": BRONZE,
                   "#d9cbb5": "#b48a62",          # camel towels
                   "#e6ddd0": "#d9c9ad",          # limestone vessel sink
                   "#c4b6a4": "#c9ae8f"},         # niche = tadelakt
        "bath_2": {"#3f2a1c": OAK, "#3a3a3a": BRONZE,
                   "#d9cbb5": "#e3d3b8",          # oat towels
                   "#e6ddd0": "#c8a985",          # travertine vessel sink
                   "#c4b6a4": "#d6c3a4"},         # niche = limestone slab
        "bedroom_1": {"#7f9fb0": "#d9a98a",       # wardrobe doors + chair: soft apricot clay
                      "#efe6d6": "#f1e8da",       # cream carcass, bed, storage
                      "#8ea8b6": "#e2c3a0",       # drapes peach-camel
                      "#5a7f96": "#e0c6a4",       # rug oat-apricot wool
                      "#c9a77c": OAK,             # desk, slats, handles oak
                      "#2f6fb3": "#b8683f",       # Baby Turi tag caramel-rust
                      "#ede6dc": "#f2e8da",
                      "#ecebe8": OAK,             # nightstand
                      "#3d6fa8": "#c98a5e", "#5e8fbf": "#d4a24c",
                      "#8e9196": "#ecd0b0"},
        "bedroom_2": {"#a08b78": "#d2bb98",       # wardrobe / console doors limewash
                      "#8a5f3e": OAK,             # wood fronts + bed oak
                      "#b88a5a": BRONZE,
                      "#6b4a33": OAK,
                      "#6f5646": "#a9875f",       # drapes camel linen
                      "#8a7764": "#b89a74",       # rug toffee-oat wool
                      "#ece6dc": "#c9ad8c",
                      "#ecebe8": STONE,           # nightstands limestone
                      "#8e9196": "#cbb08e"},
        "balcony": {"#9a6b43": OAK, "#2f2f31": "#b9825e", "#f2efe9": "#efe6d6"},
    },
    items={
        "plush-armchair-living-1": {"color": CAMEL},        # camel leather lounge chairs
        "plush-armchair-living-2": {"color": CAMEL},
        "wardrobe-living-1": {"interior_color": OAK_LT},
        "wardrobe-hall-1": {"interior_color": OAK_LT},
        "wardrobe-master-suite-1": {"interior_color": OAK_LT},
        "wardrobe-master-suite-2": {"interior_color": OAK_LT},
        "tv-console-master-suite-1": {"interior_color": OAK_LT},
        "serving-bowl-kitchen-1": {"color": OAK},           # oak serving bowl
        "chair-bedroom-1-1": {"color": OAK},                # kids' desk chair oak
        "tall-cabinet-bathroom-1-1": {"interior_color": OAK_LT},
        "tall-cabinet-master-bathroom-1": {"interior_color": OAK_LT},
    },
    finishes={
        "warmmin_natural_oak": dict(kind="parquet", size=[1.80, 0.22], direction="x", color="#c4a07a",
                                    color2="#b28d66", joint_color="#6e5238", joint=0.0015, roughness=0.5,
                                    note="V6: wide-plank natural white oak, matte oiled (living, bedrooms)"),
        "warmmin_limestone": dict(kind="stone", size=[0.60, 0.60], color="#c4ab82", color2="#ad9470",
                                  joint_color="#b09874", joint=0.002, roughness=0.45,
                                  note="V6: honed warm limestone 60 x 60 (hall, kitchen, baths, balcony)"),
        "warmmin_limestone_slab": dict(kind="stone", size=[0.60, 1.20], color="#d6c3a4", color2="#bca684",
                                       joint_color="#c4b090", joint=0.0015, roughness=0.4,
                                       note="V6: honed limestone 60 x 120 vertical (bath 2 walls, kitchen backsplash)"),
        "warmmin_tadelakt": dict(kind="stone", size=[1.20, 1.20], color="#c9ae8f", color2="#b39472",
                                 joint_color="#c1a687", joint=0.0005, roughness=0.3,
                                 note="V6: sand-clay tadelakt / microcement-look plaster (bath 1 walls, tub front)"),
        "warmmin_ripple_oat": dict(kind="ripple", size=[3.04, 2.70], color="#dcc6a2", color2="#a8845a",
                                   joint_color="#d4bb96", joint=0.0, roughness=0.85,
                                   note="V6: Ripple wallpaper in oat / sand (living sofa wall)"),
        "warmmin_ripple_camel": dict(kind="ripple", size=[3.04, 2.70], color="#c4a07a", color2="#94704c",
                                     joint_color="#c4a07a", joint=0.0, roughness=0.85,
                                     note="V6: Ripple wallpaper in camel behind the master bed"),
        "warmmin_dune_watercolor": dict(kind="watercolor", size=[3.10, 2.70], color="#f2e8da", color2="#d4a47c",
                                        joint_color="#f2e8da", joint=0.0, roughness=0.9,
                                        note="V6: soft apricot-sand dune watercolour mural (kids bed wall)"),
    },
)
