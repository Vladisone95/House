"""V12 Wabi-Sabi - V1 layout restyled: limewash / tadelakt / microcement, aged oak, raw clay, linen, soot iron."""


OAK = "#8a735c"        # weathered, grey-brown aged oak
OAK_D = "#5e4c3c"      # darker aged oak (bath furniture, sofa base)
OAK_B = "#7d6853"      # aged oak (bed, wardrobe columns)
OAK_L = "#b9a184"      # pale aged oak (kids)
SOOT = "#3b3632"       # soot / blackened iron handles, lamps, tracks
BRONZE = "#4a4038"     # aged dark bronze fittings
CLAY = "#a07a5e"       # raw unglazed clay
RUST = "#9a6248"       # fired-clay rust linen
CLAY_L = "#b59a80"     # pale stoneware clay (basins, lamps)
MUSH = "#a89580"       # mushroom limewashed fronts
LINEN = "#cbbca4"      # oatmeal slub linen
CHARL = "#5f5952"      # charcoal-ash linen
BONE = "#e6dfd2"       # bone-glaze sanitary

SPEC = dict(
    name="Wabi-Sabi",
    description=("Wabi-Sabi restyle of V1 (same furniture, same places): bone + mushroom limewash walls, ash "
                 "microcement floors, weathered aged oak, clay tadelakt bath, raw-clay basins and vases, "
                 "ivory slipcovered linen sofa with rust-clay armchairs on a charcoal wool rug, oatmeal linen "
                 "drapes, moss + dusty-rose kids room, master with a raw clay plaster bed wall and charcoal "
                 "linen bedding, bone sanitary, soot iron lamps and aged bronze"),
    wall_color="#cfbb9f",
    rooms={
        "living": dict(floor="wabi_aged_oak", walls="wabi_limewash_mushroom", paint="#b39b80", skirting="#c2b6a5"),
        "hall": dict(floor="wabi_microcement", walls="wabi_limewash_bone", paint="#cfbb9f", skirting="#c2b6a5"),
        "kitchen": dict(floor="wabi_microcement", walls="wabi_limewash_bone", paint="#cfbb9f"),
        "bath_1": dict(floor="wabi_microcement", walls="wabi_tadelakt_clay"),
        "bath_2": dict(floor="wabi_microcement", walls="wabi_tadelakt_ash"),
        "bedroom_1": dict(floor="wabi_bleached_oak", walls="wabi_limewash_sand", paint="#dcc4a6", skirting="#dcc4a6"),
        "bedroom_2": dict(floor="wabi_aged_oak", walls="wabi_limewash_mushroom", paint="#b39b80", skirting="#c2b6a5"),
        "balcony": dict(floor="wabi_weathered_stone"),
    },
    aprons={"ripple": {"living": "wabi_ripple_ash", "bedroom_2": "wabi_clay_plaster"},
            "delicate_blues": "wabi_meadow_wash", "cream_marble": "wabi_raw_plaster",
            "greige_stone": "wabi_tadelakt_clay"},
    colors={
        "*": {"#b08d57": BRONZE,                  # brass fittings -> aged dark bronze
              "#151515": SOOT,                    # track lights soot iron
              "#fbfaf7": "#e9e1d3",               # sheers: unbleached linen gauze
              "#8e9196": "#c9bba6",               # AC units toned to the limewash
              "#f6f6f6": BONE},                   # WC / tub in bone glaze
        "living": {"#86694b": LINEN,              # sofa: ivory slipcovered linen (armchairs: items, rust clay)
                   "#6f6152": "#5a4434",          # rug: dark umber hand-knotted wool (sheen lifts it)
                   "#313233": "#6e5d4c",          # coffee table: aged wood
                   "#3a3b3d": CLAY,               # side table: raw clay
                   "#6b4a33": OAK,                # slat TV wall
                   "#6f5646": "#c4b39a",          # drapes: oatmeal linen
                   "#a08b78": MUSH,               # wardrobe doors limewashed mushroom
                   "#8a5f3e": OAK,                # wood column + interior
                   "#b88a5a": SOOT,               # handles
                   "#c9a46a": "#8f7c5e",          # pendant: patinated brass
                   "#1e1e1e": SOOT,               # floor lamp soot iron
                   "#cfcfcd": "#a89580",          # desk top weathered oak
                   "#6e6e70": "#6b6158",          # gaming chair charcoal taupe
                   "#ece6dc": "#cdbba4"},         # wallpaper panel base
        "hall": {"#6b4a33": OAK, "#8a5a3c": OAK_B, "#8a5f3e": OAK, "#a08b78": MUSH,
                 "#b88a5a": SOOT, "#3a3633": "#a08b6c",   # jute doormat
                 "#3b3b3d": CLAY, "#d9cfc0": "#cbbfac",   # raw clay + chalk vases
                 "#5a3e2b": "#6b5442", "#e9e6df": "#d8cfc0"},
        "kitchen": {"#cfc2ad": "#8a7a6a",         # base + tall units, oven: limewashed mushroom-grey
                    "#7a5236": OAK,               # worktop, wood wall units, dining table: aged oak
                    "#b9a88c": SOOT, "#3a3a3a": SOOT,
                    "#b8a990": CHARL,              # chairs charcoal-ash linen
                    "#efe6d6": "#bba68a",         # backsplash panel = raw plaster
                    "#e6e4df": "#d8cfc0",         # blind: natural linen
                    "#1e1e1e": SOOT,              # linear pendant soot iron
                    "#1c1c1c": "#4a4440",         # sink: dark soapstone
                    "#f4f3f0": "#d9cdb9"},        # stoneware place settings + bowl
        "bath_1": {"#3f2a1c": OAK_D, "#6b4428": OAK_B, "#3a3a3a": SOOT,
                   "#d9cbb5": "#c9b49a",          # towels oat waffle linen
                   "#e6ddd0": CLAY_L,             # raw clay vessel sink
                   "#c4b6a4": "#a8846a"},
        "bath_2": {"#3f2a1c": OAK_D, "#3a3a3a": SOOT,
                   "#d9cbb5": "#9a6a52",          # towels rust-clay linen
                   "#e6ddd0": CLAY_L, "#c4b6a4": "#c2ae98"},
        "bedroom_1": {"#7f9fb0": "#8f936f",       # wardrobe doors + desk chair: moss
                      "#efe6d6": "#ece4d6",       # bone carcass, bed, storage, interiors
                      "#8ea8b6": "#b98f7f",       # drapes dusty rose linen
                      "#5a7f96": "#c7ab8e",       # rug warm sand wool
                      "#c9a77c": OAK_L,           # desk, slats, handles pale aged oak
                      "#2f6fb3": "#a8644a",       # "Baby Turi" tag clay rust
                      "#ede6dc": "#efe7da", "#ecebe8": OAK_L,
                      "#d8cfc2": CLAY_L,          # clay table lamp
                      "#3d6fa8": "#7f8a6a", "#5e8fbf": "#c08a5a"},
        "bedroom_2": {"#a08b78": MUSH,            # wardrobes / console limewashed mushroom
                      "#8a5f3e": OAK_B,           # wood column, interiors + bed aged oak
                      "#b88a5a": SOOT,
                      "#6b4a33": OAK,
                      "#6f5646": "#8a8478",       # drapes ash-grey linen
                      "#8a7764": "#6f7880",       # rug faded indigo wool
                      "#ece6dc": "#9c7b62",       # wallpaper base raw clay
                      "#ecebe8": OAK_B,           # nightstands
                      "#d8cfc2": CLAY_L},         # clay table lamps
        "balcony": {"#9a6b43": "#8c8274", "#2f2f31": CLAY, "#f2efe9": "#d9cdb9"},  # grey teak, clay mugs
    },
    accent={"*": OAK_D,                  # sofa / armchair base + feet dark aged oak
            "bath_1": "#958676",         # shower curb microcement
            "bedroom_1": "#ddd0bd",      # kids duvet oatmeal linen
            "bedroom_2": CHARL},         # master duvet charcoal-ash linen
    metal={"*": BRONZE, "kitchen": SOOT},
    items={
        "plush-armchair-living-1": {"color": RUST},
        "plush-armchair-living-2": {"color": RUST},
    },
    finishes={
        "wabi_limewash_bone": dict(kind="stone", size=[3.0, 2.7], color="#cfbb9f", color2="#b9a385",
                                   joint_color="#cfbb9f", joint=0.0, roughness=0.9,
                                   note="V12: bone-white limewash, soft clouding, seamless"),
        "wabi_limewash_mushroom": dict(kind="stone", size=[3.0, 2.7], color="#b39b80", color2="#9a826a",
                                       joint_color="#b39b80", joint=0.0, roughness=0.9,
                                       note="V12: mushroom limewash, clouded brush marks, seamless"),
        "wabi_limewash_sand": dict(kind="stone", size=[3.0, 2.7], color="#dcc4a6", color2="#c8ac8a",
                                   joint_color="#dcc4a6", joint=0.0, roughness=0.9,
                                   note="V12: warm sand limewash (kids room)"),
        "wabi_tadelakt_clay": dict(kind="stone", size=[1.8, 2.7], color="#a8846a", color2="#8f6e56",
                                   joint_color="#a8846a", joint=0.0, roughness=0.3,
                                   note="V12: clay tadelakt, burnished lime plaster (bath 1, tub front)"),
        "wabi_tadelakt_ash": dict(kind="stone", size=[1.8, 2.7], color="#c2ae98", color2="#a8937c",
                                  joint_color="#c2ae98", joint=0.0, roughness=0.3,
                                  note="V12: ash-greige tadelakt (bath 2)"),
        "wabi_microcement": dict(kind="stone", size=[2.4, 2.4], color="#958676", color2="#7d6f60",
                                 joint_color="#958676", joint=0.0, roughness=0.5,
                                 note="V12: warm ash microcement, trowel clouding, jointless"),
        "wabi_aged_oak": dict(kind="parquet", size=[1.8, 0.24], direction="x", color="#9c876e", color2="#87725b",
                              joint_color="#4f4134", joint=0.0015, roughness=0.6,
                              note="V12: weathered grey-brown oak, wide 24 cm boards, oiled matte"),
        "wabi_bleached_oak": dict(kind="parquet", size=[1.8, 0.24], direction="x", color="#c9b79c",
                                  color2="#b8a588", joint_color="#7d6a54", joint=0.0015, roughness=0.6,
                                  note="V12: bleached / soaped oak wide boards (kids room)"),
        "wabi_weathered_stone": dict(kind="stone", size=[0.6, 0.6], color="#b0a696", color2="#968c7d",
                                     joint_color="#8f8679", joint=0.003, roughness=0.7,
                                     note="V12: weathered limestone-look outdoor slabs (balcony)"),
        "wabi_ripple_ash": dict(kind="ripple", size=[3.04, 2.7], color="#cdbba4", color2="#a48e75",
                                joint_color="#cdbba4", joint=0.0, roughness=0.9,
                                note="V12: Ripple wallpaper in ash-mushroom (living)"),
        "wabi_clay_plaster": dict(kind="stone", size=[3.04, 2.7], color="#9c7b62", color2="#86664f",
                                  joint_color="#9c7b62", joint=0.0, roughness=0.9,
                                  note="V12: raw clay plaster feature wall behind the master bed"),
        "wabi_meadow_wash": dict(kind="watercolor", size=[3.1, 2.7], color="#efe7da", color2="#c29484",
                                 joint_color="#efe7da", joint=0.0, roughness=0.9,
                                 note="V12: hand-painted dusty-rose / sand wash mural (kids bed wall)"),
        "wabi_raw_plaster": dict(kind="stone", size=[1.8, 0.6], color="#bba68a", color2="#a08b70",
                                 joint_color="#bba68a", joint=0.0, roughness=0.4,
                                 note="V12: sealed raw plaster backsplash, kitchen"),
    },
)
