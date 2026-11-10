"""V4 Contemporary = V1 layout restyled: crisp soft whites + graphite, light grey-oak and concrete-look
large-format porcelain, walnut accents, ink-blue + cognac punctuation, brushed steel / chrome metal.
Woods: grey-washed oak, walnut, light oak (kids). Metals: brushed steel + graphite."""


STEEL = "#a7aaad"      # brushed steel / chrome hardware
GRAPHITE = "#3a3c40"   # matte graphite lacquer
WALNUT = "#5e4130"     # dark walnut accent wood
WHITE = "#eceae6"      # soft-white lacquer
INK = "#2f3f5a"        # ink blue accent
INKVELVET = "#33435f"  # ink-blue velvet (sofa)
COGNAC = "#9a5a32"     # cognac leather / accent
GREIGE = "#c9c4bc"     # greige wool / linen
INTERIOR = "#e1dfdb"   # pale grey cabinet interiors

SPEC = dict(
    name="Contemporary",
    description=("Contemporary restyle of V1 (same furniture, same places): crisp soft-white walls, ink-blue velvet "
                 "sofa + cognac leather armchairs on a greige rug, graphite + white two-tone joinery, light grey oak "
                 "and concrete-look large-format porcelain, white statuario slabs, walnut accents, charcoal master "
                 "suite with a cognac rug, coral kids' room, brushed steel / chrome"),
    wall_color="#e6e1d9",
    rooms={
        "living": dict(floor="contemporary_grey_oak", paint="#ddd5c9", skirting=GRAPHITE),
        "hall": dict(floor="contemporary_concrete", paint="#d9d2c7"),
        "kitchen": dict(floor="contemporary_concrete", paint="#ebe7e0"),
        "bath_1": dict(floor="contemporary_graphite_stone", walls="contemporary_concrete_wall"),
        "bath_2": dict(floor="contemporary_graphite_stone", walls="contemporary_statuario_wall"),
        "bedroom_1": dict(floor="contemporary_grey_oak", paint="#e3e6e9", skirting="#eceae6"),
        "bedroom_2": dict(floor="contemporary_grey_oak", paint="#cdc6bc", skirting=GRAPHITE),
        "balcony": dict(floor="contemporary_anthracite"),
    },
    aprons={"ripple": {"living": "contemporary_ripple_dove", "bedroom_2": "contemporary_ripple_charcoal"},
            "delicate_blues": "contemporary_coral_watercolor",
            "cream_marble": "contemporary_statuario",
            "greige_stone": "contemporary_statuario_wall"},
    metal={"*": STEEL},
    accent={"*": WALNUT,                # sofa / armchair walnut base + feet
            "bedroom_1": "#f0c4b4",     # duvet soft coral
            "bedroom_2": GREIGE,        # duvet greige linen
            "bath_1": "#4c4d50", "bath_2": "#4c4d50"},  # shower curb graphite stone
    colors={
        "*": {"#b08d57": STEEL,                      # brass fittings -> brushed steel / chrome
              "#151515": GRAPHITE,                   # track lights graphite
              "#fbfaf7": "#f2f1ee",                  # sheers crisp white voile
              "#8e9196": "#e2e0dc"},                 # AC units blend with the walls
        "living": {"#86694b": INKVELVET,             # sofa: ink-blue velvet (armchairs: items)
                   "#6f6152": GREIGE,                # rug: greige wool
                   "#313233": "#e6e4e0",             # coffee table white marble-look
                   "#3a3b3d": COGNAC,                # side table cognac lacquer accent
                   "#6b4a33": GRAPHITE,              # slat TV wall graphite
                   "#6f5646": "#5a5c61",             # drapes charcoal-grey
                   "#a08b78": WHITE,                 # wardrobe doors soft-white lacquer
                   "#8a5f3e": WALNUT,                # wardrobe wood column walnut (interior: items)
                   "#b88a5a": STEEL,                 # handles brushed steel
                   "#c9a46a": "#b9bcbf",             # infinity pendant polished chrome
                   "#1e1e1e": GRAPHITE,              # floor lamp graphite
                   "#cfcfcd": "#f0efec",             # desk top white
                   "#6e6e70": "#45474b",             # gaming chair charcoal
                   "#ece6dc": "#d9d7d3"},            # wallpaper panel base
        "hall": {"#6b4a33": GRAPHITE, "#8a5a3c": WALNUT, "#8a5f3e": INTERIOR,
                 "#a08b78": GRAPHITE,                # hall wardrobe graphite
                 "#b88a5a": STEEL, "#3a3633": "#45474b",
                 "#3b3b3d": COGNAC, "#d9cfc0": "#f0efec", "#5a3e2b": COGNAC},
        "kitchen": {"#cfc2ad": GRAPHITE,             # base + tall units, oven: matte graphite
                    "#7a5236": "#ecebe7",            # worktop, wall units: white quartz / lacquer (table: items)
                    "#b9a88c": STEEL, "#3a3a3a": STEEL,
                    "#b8a990": COGNAC,               # upholstered chairs cognac leather
                    "#efe6d6": "#ecebe7",            # backsplash panel = statuario
                    "#1c1c1c": STEEL,                # sink brushed stainless
                    "#1e1e1e": GRAPHITE,             # linear pendant graphite
                    "#e6e4df": "#eeede9"},
        "bath_1": {"#3f2a1c": WALNUT, "#6b4428": WALNUT, "#3a3a3a": STEEL,
                   "#d9cbb5": INKVELVET,             # towels ink blue
                   "#e6ddd0": GRAPHITE,              # vessel sink matte graphite
                   "#c4b6a4": "#a3a19c"},
        "bath_2": {"#3f2a1c": GRAPHITE, "#3a3a3a": STEEL,
                   "#d9cbb5": COGNAC,                # towels cognac
                   "#e6ddd0": "#f6f6f4",             # vessel sink gloss white
                   "#c4b6a4": "#e9e7e3"},
        "bedroom_1": {"#7f9fb0": "#e07a5f",          # wardrobe doors + desk chair: coral
                      "#efe6d6": "#eeeeec",          # carcass, bed, storage: soft white
                      "#8ea8b6": "#8e9aa6",          # drapes cool grey-blue
                      "#5a7f96": "#9aa6c4",          # rug periwinkle wool
                      "#c9a77c": "#c8a985",          # desk, slats, handles light oak
                      "#2f6fb3": INK,                # Baby Turi tag ink blue
                      "#d8cfc2": "#eeeeec",          # table lamp white
                      "#ede6dc": "#f1ece6", "#ecebe8": "#c8a985",
                      "#3d6fa8": "#e07a5f", "#5e8fbf": INK},
        "bedroom_2": {"#a08b78": "#bdb8b1",          # wardrobe / console doors warm grey lacquer
                      "#8a5f3e": WALNUT,             # wood column + bed walnut (interiors: items)
                      "#b88a5a": STEEL,
                      "#6b4a33": WALNUT,
                      "#6f5646": "#4b4d52",          # drapes charcoal
                      "#8a7764": "#b07a58",          # rug cognac wool
                      "#ece6dc": "#4b4d52",
                      "#ecebe8": GRAPHITE,           # nightstands graphite
                      "#d8cfc2": "#e8e6e2"},         # table lamps white
        "balcony": {"#9a6b43": GRAPHITE, "#2f2f31": COGNAC, "#f2efe9": "#eeede9"},
    },
    items={
        "plush-armchair-living-1": {"color": COGNAC},    # cognac leather armchairs
        "plush-armchair-living-2": {"color": COGNAC},
        "dining-table-kitchen-1": {"color": WALNUT},     # walnut table against white quartz + graphite
        "wardrobe-living-1": {"interior_color": INTERIOR},
        "wardrobe-master-suite-1": {"interior_color": INTERIOR},
        "wardrobe-master-suite-2": {"interior_color": INTERIOR},
        "tv-console-master-suite-1": {"interior_color": INTERIOR},
        "tall-cabinet-bathroom-1-1": {"interior_color": INTERIOR},
        "tall-cabinet-master-bathroom-1": {"interior_color": INTERIOR},
    },
    finishes={
        "contemporary_grey_oak": dict(kind="parquet", size=[1.80, 0.22], direction="x", color="#a8977f",
                                      color2="#95856f", joint_color="#5e5345", joint=0.0015, roughness=0.42,
                                      note="V4: wide grey-washed oak plank (living, bedrooms)"),
        "contemporary_concrete": dict(kind="stone", size=[1.20, 0.60], color="#9a958d", color2="#87837c",
                                      joint_color="#7e7a74", joint=0.002, roughness=0.35,
                                      note="V4: light concrete-look porcelain 120 x 60 (hall, kitchen)"),
        "contemporary_concrete_wall": dict(kind="stone", size=[0.60, 1.20], color="#a3a19c", color2="#8c8a85",
                                           joint_color="#8a8883", joint=0.002, roughness=0.35,
                                           note="V4: mid-grey concrete-look porcelain 60 x 120 vertical (bath 1 walls)"),
        "contemporary_graphite_stone": dict(kind="stone", size=[0.60, 0.60], color="#4c4d50", color2="#3c3d40",
                                            joint_color="#38393b", joint=0.002, roughness=0.35,
                                            note="V4: graphite stone-look porcelain 60 x 60 (bath floors)"),
        "contemporary_statuario": dict(kind="marble", size=[1.80, 0.60], color="#f2f1ee", color2="#8f9196",
                                       joint_color="#e6e5e1", joint=0.001, roughness=0.15,
                                       note="V4: white statuario-look slab with grey veins (kitchen backsplash)"),
        "contemporary_statuario_wall": dict(kind="marble", size=[0.60, 1.20], color="#eceae6", color2="#9a9ca0",
                                            joint_color="#dcdad6", joint=0.002, roughness=0.18,
                                            note="V4: statuario-look porcelain 60 x 120 vertical (bath 2 walls + tub front)"),
        "contemporary_anthracite": dict(kind="tiles", size=[0.60, 0.60], color="#5b5c5e", color2="#47484a",
                                        joint_color="#4a4b4d", joint=0.003, roughness=0.6,
                                        note="V4: anthracite outdoor porcelain 60 x 60 (balcony)"),
        "contemporary_ripple_dove": dict(kind="ripple", size=[3.04, 2.70], color="#d9d7d3", color2="#a9a6a1",
                                         joint_color="#d9d7d3", joint=0.0, roughness=0.85,
                                         note="V4: Ripple wallpaper in dove grey (living sofa wall)"),
        "contemporary_ripple_charcoal": dict(kind="ripple", size=[3.04, 2.70], color="#56585d", color2="#3e4044",
                                             joint_color="#56585d", joint=0.0, roughness=0.85,
                                             note="V4: charcoal ripple wallpaper behind the master bed"),
        "contemporary_coral_watercolor": dict(kind="watercolor", size=[3.10, 2.70], color="#f1ece6",
                                              color2="#e07a5f", joint_color="#f1ece6", joint=0.0, roughness=0.9,
                                              note="V4: soft-white mural with coral washes (kids bed wall)"),
    },
)
