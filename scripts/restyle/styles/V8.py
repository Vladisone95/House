"""V8 Organic Modern - V1 layout (same ids, sizes, places), new colours / finishes only.

Palette: mushroom limewash walls, natural white oak + walnut, honed limestone, travertine slab,
moss-olive accents (kitchen base, bath 1 tiles, armchairs, drapes), camel boucle sofa + cognac leather,
putty plaster joinery, oatmeal wool / linen textiles, raw clay accents, aged bronze metal (one metal).
"""


OAK = "#b8936a"        # natural oiled white oak
OAK_L = "#c4a27a"      # lighter white oak (desks, nightstands, slats)
WALNUT = "#5c4130"     # walnut
BRONZE = "#7a6347"     # aged / brushed bronze
MOSS = "#6f6d47"       # moss olive
PUTTY = "#d8c9b1"      # putty plaster-lacquer joinery fronts
CAMEL = "#b5885b"      # camel boucle
COGNAC = "#8a5634"     # cognac leather
CLAY = "#a5704c"       # unglazed clay
TRAV = "#c9b18e"       # travertine (sinks, curb, side table)
OATMEAL = "#d3c2a5"    # oatmeal wool / linen
SHEER = "#ebe1cf"      # oat linen sheers

SPEC = dict(
    name="Organic Modern",
    description=("Organic Modern restyle of V1 (same furniture, same places): mushroom limewash walls, natural "
                 "white oak + walnut, honed limestone + travertine, moss-olive accents, camel boucle + cognac "
                 "leather, putty plaster joinery, oatmeal wool / linen, raw clay, aged bronze"),
    wall_color="#cdbca4",
    rooms={
        "living": dict(floor="organic_white_oak", paint="#c2a886", skirting="#a88f70"),
        "hall": dict(floor="organic_limestone", paint="#c4aa8a"),
        "kitchen": dict(floor="organic_limestone", paint="#d3c3ac"),
        "bath_1": dict(floor="organic_limestone", walls="organic_moss_tile"),
        "bath_2": dict(floor="organic_limestone", walls="organic_plaster_stone"),
        "bedroom_1": dict(floor="organic_white_oak", paint="#e2cca9", skirting="#efe5d5"),
        "bedroom_2": dict(floor="organic_white_oak", paint="#bea78a", skirting=WALNUT),
        "balcony": dict(floor="organic_limestone"),
    },
    aprons={"ripple": {"living": "organic_ripple_clay", "bedroom_2": "organic_oak_chevron"},
            "delicate_blues": "organic_meadow_watercolor",
            "cream_marble": "organic_travertine_slab",
            "greige_stone": "organic_travertine_slab"},
    metal={"*": BRONZE},
    accent={"*": WALNUT,                                # sofa / armchair base + feet: walnut
            "bedroom_1": "#b9a06a",                     # kids' duvet: ochre-moss linen
            "bedroom_2": "#cfb48f",                     # master duvet: camel-oat linen
            "bath_1": TRAV, "bath_2": TRAV},            # shower curb: travertine
    colors={
        "*": {"#b08d57": BRONZE,                        # brass fittings -> aged bronze
              "#151515": BRONZE,                        # track lights
              "#fbfaf7": SHEER},                        # sheers: oat linen
        "living": {"#86694b": CAMEL,                    # sofa (+ armchairs, overridden below): camel boucle
                   "#6f6152": "#9a8263",                # shag rug: oatmeal-camel wool (pile renders lighter)
                   "#313233": WALNUT,                   # coffee table: walnut (live-edge look)
                   "#3a3b3d": TRAV,                     # side table: travertine
                   "#6b4a33": WALNUT,                   # slat TV wall: walnut
                   "#6f5646": "#6b6a45",                # drapes: moss linen
                   "#a08b78": PUTTY,                    # wardrobe doors: putty plaster lacquer
                   "#8a5f3e": WALNUT,                   # wardrobe wood column + interior: walnut
                   "#b88a5a": BRONZE,                   # handles
                   "#c9a46a": BRONZE,                   # infinity pendant: bronze
                   "#1e1e1e": BRONZE,                   # floor lamp: bronze
                   "#cfcfcd": OAK_L,                    # desk top: white oak
                   "#6e6e70": COGNAC,                   # gaming chair: cognac leather
                   "#8e9196": "#c9b394",                # AC: wall-matched
                   "#ece6dc": "#b98f6c"},               # wallpaper panel base: clay
        "hall": {"#6b4a33": WALNUT, "#8a5a3c": WALNUT, "#8a5f3e": WALNUT,
                 "#a08b78": PUTTY, "#b88a5a": BRONZE,
                 "#3a3633": "#8d7a5c",                  # jute doormat
                 "#3b3b3d": CLAY,                       # clay vase
                 "#d9cfc0": "#e6dccb"},
        "kitchen": {"#cfc2ad": MOSS,                    # base + tall units, oven: moss olive
                    "#7a5236": OAK,                     # worktop, wall units: white oak (table: walnut, below)
                    "#b9a88c": BRONZE, "#3a3a3a": BRONZE,
                    "#b8a990": COGNAC,                  # dining chairs: cognac leather
                    "#efe6d6": "#d6c3a4",               # backsplash = travertine slab
                    "#e6e4df": "#e1d3bd",               # linen blind
                    "#1e1e1e": BRONZE,                  # linear pendant: bronze
                    "#1c1c1c": "#5a5045",               # sink: taupe stone composite
                    "#f4f3f0": "#dccdb4"},              # stoneware place settings
        "bath_1": {"#3f2a1c": WALNUT, "#6b4428": OAK_L, "#3a3a3a": BRONZE,
                   "#d9cbb5": CAMEL,                    # camel towels
                   "#e6ddd0": TRAV,                     # travertine vessel sink
                   "#c4b6a4": "#6f7048"},               # niche = moss tile
        "bath_2": {"#3f2a1c": WALNUT, "#3a3a3a": BRONZE,
                   "#d9cbb5": "#77744f",                # moss towels
                   "#e6ddd0": TRAV,
                   "#c4b6a4": "#b89f80"},               # niche = plaster stone
        "bedroom_1": {"#7f9fb0": "#8f9163",             # wardrobe doors: sage moss (chair: ochre, below)
                      "#efe6d6": "#f0e7d8",             # ivory carcass, bed, storage
                      "#8ea8b6": "#b8875a",             # drapes: caramel
                      "#5a7f96": "#9c9868",             # rug: moss wool
                      "#c9a77c": OAK_L,                 # desk, slats, handles: white oak
                      "#2f6fb3": "#9a5b34",             # "Baby Turi" tag: cognac
                      "#ede6dc": "#f0e4d0", "#ecebe8": OAK_L,
                      "#d8cfc2": "#c48a62",             # clay table lamp
                      "#8e9196": "#e2cca9",             # AC: wall-matched
                      "#3d6fa8": MOSS, "#5e8fbf": "#c08550"},
        "bedroom_2": {"#a08b78": OAK,                   # wardrobes / console fronts: white oak
                      "#8a5f3e": WALNUT,                # wood column, interiors + bed: walnut
                      "#b88a5a": BRONZE,
                      "#6b4a33": WALNUT,                # slat panel
                      "#6f5646": "#8f5a38",             # drapes: rust-cognac linen
                      "#8a7764": "#8d7860",             # rug: mushroom wool
                      "#ece6dc": "#bf9b70",
                      "#ecebe8": OAK_L,                 # nightstands white oak
                      "#8e9196": "#bea78a",             # AC: wall-matched
                      "#d8cfc2": CLAY},                 # clay ceramic lamps
        "balcony": {"#9a6b43": "#b89468",               # teak chairs + table
                    "#2f2f31": CLAY, "#f2efe9": "#dccdb4"},
    },
    items={
        "plush-armchair-living-1": {"color": MOSS},     # moss boucle armchairs
        "plush-armchair-living-2": {"color": MOSS},
        "dining-table-kitchen-1": {"color": WALNUT},    # walnut dining table
        "chair-bedroom-1-1": {"color": "#c08550"},      # ochre desk chair
        "serving-bowl-kitchen-1": {"color": CLAY},
    },
    finishes={
        "organic_white_oak": dict(kind="parquet", size=[1.20, 0.19], direction="x", color=OAK, color2="#a37f57",
                                  joint_color="#5e4630", joint=0.0015, roughness=0.5,
                                  note="V8 Organic Modern: natural oiled white oak planks (living, bedrooms)"),
        "organic_limestone": dict(kind="stone", size=[0.60, 0.60], color="#ab9475", color2="#927b5e",
                                  joint_color="#9c8769", joint=0.002, roughness=0.5,
                                  note="V8 Organic Modern: honed warm limestone 60 x 60 (hall, kitchen, baths, balcony)"),
        "organic_moss_tile": dict(kind="stone", size=[0.075, 0.30], color="#6f7048", color2="#5c5d3a",
                                  joint_color="#d8cfbf", joint=0.002, roughness=0.15,
                                  note="V8 Organic Modern: glossy moss-olive handmade tile 7.5 x 30, vertical stack (bath 1 walls)"),
        "organic_plaster_stone": dict(kind="stone", size=[1.20, 1.20], color="#b89f80", color2="#9c8467",
                                      joint_color="#b2a28b", joint=0.001, roughness=0.55,
                                      note="V8 Organic Modern: mushroom microcement / plaster-look large slabs (bath 2 walls)"),
        "organic_travertine_slab": dict(kind="marble", size=[1.80, 0.60], color="#d6c3a4", color2="#ae9370",
                                        joint_color="#cdb999", joint=0.001, roughness=0.35,
                                        note="V8 Organic Modern: vein-cut honed travertine slab (kitchen backsplash, tub front)"),
        "organic_ripple_clay": dict(kind="ripple", size=[3.04, 2.70], color="#b98f6c", color2="#946a4c",
                                    joint_color="#b98f6c", joint=0.0, roughness=0.85,
                                    note="V8 Organic Modern: 'Ripple' wallpaper in raw clay / terracotta-mushroom (living)"),
        "organic_oak_chevron": dict(kind="chevron", size=[3.04, 2.70], color="#bf9b70", color2="#a8845b",
                                    joint_color="#6b4f35", joint=0.0, roughness=0.6,
                                    note="V8 Organic Modern: white-oak chevron panels behind the master bed"),
        "organic_meadow_watercolor": dict(kind="watercolor", size=[3.10, 2.70], color="#f0e4d0",
                                          color2="#8f9163", joint_color="#f0e4d0", joint=0.0, roughness=0.9,
                                          note="V8 Organic Modern: cream + moss / ochre watercolour hills (kids' bed wall)"),
    },
)
