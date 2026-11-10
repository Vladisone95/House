"""V10 Modern Mediterranean: V1 layout, limewash whites, Aegean blue, olive, sun-bleached oak, zellige, aged brass.

Palette: limewash creams, white linen sofa, Aegean-blue armchairs / kitchen / zellige, olive (wall, vanity,
drapes), sun-bleached oak + rattan, limestone, aged brass (one metal); terracotta only as small accents
(side table, vases, bath-1 towels, master duvet, serving bowl).
"""


OAK = "#c09a68"        # sun-bleached oak furniture
OAK_L = "#ceb085"      # paler bleached oak (desk, kids)
LIME = "#e6dbc5"       # limewash-white lacquer fronts
AEGEAN = "#34607c"     # Aegean blue
AEGEAN_L = "#4f7088"   # Aegean linen (armchairs, towels)
OLIVE = "#686a40"      # olive green
BRASS = "#a3824a"      # aged brass
TERRA = "#b8714f"      # terracotta - minor accent only
LINEN = "#e6dcc8"      # natural white linen
SAND = "#c9ad80"       # jute / sand
RATTAN = "#c2a06a"     # rattan
SHEER = "#f3eee4"      # white linen sheers

SPEC = dict(
    name="Modern Mediterranean",
    description=("Colour scheme of V1 (same furniture, same places): Modern Mediterranean - limewash whites, "
                 "white linen sofa, Aegean blue armchairs + kitchen + zellige, olive, sun-bleached oak + rattan, "
                 "limestone floors, cream + olive zellige, aged brass, terracotta only as small accents"),
    wall_color="#ebe1cd",
    rooms={
        "living": dict(floor="medit_bleached_oak", paint="#dfcca8", skirting="#e6dbc5"),
        "hall": dict(floor="medit_limestone", paint="#e4d4b4", skirting="#e6dbc5"),
        "kitchen": dict(floor="medit_limestone", paint="#ede3cf"),
        "bath_1": dict(floor="medit_limestone", walls="medit_aegean_zellige"),
        "bath_2": dict(floor="medit_limestone", walls="medit_lime_plaster"),
        "bedroom_1": dict(floor="medit_bleached_oak", paint="#bcd3df", skirting="#f2ede3"),
        "bedroom_2": dict(floor="medit_bleached_oak", paint="#dfcfae", skirting="#e6dbc5"),
        "balcony": dict(floor="medit_limestone"),
    },
    aprons={"ripple": {"living": "medit_ripple_olive", "bedroom_2": "medit_ripple_aegean"},
            "delicate_blues": "medit_lemon_watercolor", "cream_marble": "medit_cream_zellige",
            "greige_stone": "medit_olive_zellige"},
    metal={"*": BRASS},
    accent={"*": OAK,                                  # sofa / armchair base + feet: bleached oak
            "bedroom_1": "#7fa4bb",                    # kids' duvet: sea-blue linen
            "bedroom_2": "#a8664a",                    # master duvet: terracotta linen (accent)
            "bath_1": "#dccdb0", "bath_2": "#dccdb0"},  # shower curb: limestone
    colors={
        "*": {"#b08d57": BRASS,                        # brass fittings -> aged brass
              "#151515": BRASS,                        # track lights
              "#fbfaf7": SHEER},                       # sheers white linen
        "living": {"#86694b": LINEN,                   # sofa: natural white linen (armchairs: Aegean, below)
                   "#6f6152": "#a88a5c",               # rug: jute (pile renders lighter)
                   "#313233": "#cdb894",               # coffee table limestone
                   "#3a3b3d": TERRA,                   # side table terracotta accent
                   "#6b4a33": OAK,                     # slat TV wall bleached oak
                   "#6f5646": "#cdb58f",               # drapes natural flax
                   "#a08b78": LIME,                    # wardrobe doors limewash white
                   "#8a5f3e": OAK,                     # wardrobe wood column + interior
                   "#b88a5a": BRASS,
                   "#c9a46a": RATTAN,                  # pendant rattan-brass
                   "#1e1e1e": BRASS,                   # floor lamp brass
                   "#cfcfcd": OAK_L,                   # desk top
                   "#6e6e70": OLIVE,                   # gaming chair olive
                   "#8e9196": "#dfcca8",               # AC: wall-matched
                   "#ece6dc": "#a8a472"},              # wallpaper panel olive ridges
        "hall": {"#6b4a33": OAK, "#8a5a3c": OAK, "#8a5f3e": OAK, "#a08b78": LIME, "#b88a5a": BRASS,
                 "#3a3633": "#a58e66",                 # jute doormat
                 "#3b3b3d": TERRA,                     # terracotta vase
                 "#d9cfc0": "#f1ece2"},                # white ceramic vase
        "kitchen": {"#cfc2ad": AEGEAN,                 # base + tall units, oven front: Aegean blue
                    "#7a5236": OAK,                    # worktop, wall units, dining table: bleached oak
                    "#b9a88c": BRASS, "#3a3a3a": BRASS,
                    "#b8a990": "#86874f",              # dining chairs: olive linen
                    "#efe6d6": "#ece2cc",              # backsplash = cream zellige
                    "#e6e4df": "#efe8da",              # blind linen
                    "#1e1e1e": BRASS,                  # linear pendant
                    "#1c1c1c": "#ebe4d6",              # white fireclay sink
                    "#f4f3f0": "#efe6d2"},             # cream ceramics
        "bath_1": {"#3f2a1c": OAK, "#6b4428": OAK, "#3a3a3a": BRASS,
                   "#d9cbb5": TERRA,                   # terracotta towels on Aegean zellige
                   "#e6ddd0": "#cdb894",               # limestone vessel basin
                   "#c4b6a4": "#3d6680"},              # niche = Aegean zellige
        "bath_2": {"#3f2a1c": OLIVE, "#3a3a3a": BRASS,  # olive-painted vanity + tall cabinet
                   "#d9cbb5": AEGEAN_L,                # Aegean towels
                   "#e6ddd0": "#f4f0e8",               # handmade white basin
                   "#c4b6a4": "#ddcba9"},              # niche = lime plaster
        "bedroom_1": {"#7f9fb0": "#d9bb52",            # wardrobe doors + chair: lemon yellow
                      "#efe6d6": "#f3eee2",            # carcass, bed, storage white
                      "#8ea8b6": "#4a7896",            # drapes Aegean
                      "#5a7f96": "#c4ad78",            # rug sand
                      "#c9a77c": OAK_L,                # desk, slats, handles bleached oak
                      "#2f6fb3": "#2f5f8a",            # Baby Turi tag deep Aegean
                      "#ede6dc": "#f4ecd6",            # mural base
                      "#ecebe8": OAK_L,
                      "#d8cfc2": "#c47f5a",            # terracotta lamp
                      "#8e9196": "#bcd3df",            # AC: wall-matched
                      "#3d6fa8": TERRA, "#5e8fbf": OLIVE},
        "bedroom_2": {"#a08b78": LIME,                 # wardrobes / console limewash white
                      "#8a5f3e": OAK,                  # wood column + bed
                      "#b88a5a": BRASS,
                      "#6b4a33": OAK,
                      "#6f5646": "#6f7350",            # drapes olive linen
                      "#8a7764": "#a99470",            # rug jute-sand
                      "#ece6dc": "#44708d",            # headboard wallpaper Aegean
                      "#ecebe8": RATTAN,               # nightstands rattan
                      "#8e9196": "#dfcfae",            # AC: wall-matched
                      "#d8cfc2": "#ece5d6"},           # ceramic lamps
        "balcony": {"#9a6b43": AEGEAN, "#2f2f31": TERRA, "#f2efe9": "#f1ece2"},
    },
    items={
        "plush-armchair-living-1": {"color": AEGEAN_L},  # Aegean linen armchairs
        "plush-armchair-living-2": {"color": AEGEAN_L},
        "serving-bowl-kitchen-1": {"color": TERRA},
        "outdoor-dining-table-balcony-1": {"color": "#e6dbc5"},  # limewashed table
    },
    finishes={
        "medit_bleached_oak": dict(kind="parquet", size=[1.80, 0.22], direction="x", color="#cfb68e",
                                   color2="#bea178", joint_color="#8a7a62", joint=0.0015, roughness=0.5,
                                   note="V10: sun-bleached / whitewashed oak, wide 180 x 22 planks"),
        "medit_limestone": dict(kind="stone", size=[0.60, 0.60], color="#dccdb0", color2="#c8b593",
                                joint_color="#cbbd9f", joint=0.002, roughness=0.45,
                                note="V10: honed warm limestone-look 60 x 60 (hall, kitchen, baths, balcony)"),
        "medit_aegean_zellige": dict(kind="stone", size=[0.15, 0.15], color="#3d6680", color2="#2e536b",
                                     joint_color="#e8e1d3", joint=0.002, roughness=0.12,
                                     note="V10: Aegean-blue zellige-look 15 x 15 (bath 1 walls)"),
        "medit_cream_zellige": dict(kind="stone", size=[0.15, 0.15], color="#ece2cc", color2="#d9cba9",
                                    joint_color="#f2ece0", joint=0.002, roughness=0.12,
                                    note="V10: cream zellige-look 15 x 15 (kitchen backsplash)"),
        "medit_olive_zellige": dict(kind="stone", size=[0.15, 0.15], color="#6e7046", color2="#5a5c36",
                                    joint_color="#e6dfcf", joint=0.002, roughness=0.12,
                                    note="V10: olive zellige-look 15 x 15 (bath 2 tub front)"),
        "medit_lime_plaster": dict(kind="stone", size=[0.60, 1.20], color="#ddcba9", color2="#c8b28a",
                                   joint_color="#d3c09e", joint=0.001, roughness=0.55,
                                   note="V10: limewash / tadelakt-look warm white 60 x 120 (bath 2 walls)"),
        "medit_ripple_olive": dict(kind="ripple", size=[3.04, 2.70], color="#a8a472", color2="#82804c",
                                   joint_color="#a8a472", joint=0.0, roughness=0.85,
                                   note="V10: Ripple wallpaper in soft olive (living sofa wall)"),
        "medit_ripple_aegean": dict(kind="ripple", size=[3.04, 2.70], color="#44708d", color2="#335a74",
                                    joint_color="#44708d", joint=0.0, roughness=0.85,
                                    note="V10: Aegean-blue ripple wallpaper behind the master bed"),
        "medit_lemon_watercolor": dict(kind="watercolor", size=[3.10, 2.70], color="#f4ecd6",
                                       color2="#dcb94f", joint_color="#f4ecd6", joint=0.0, roughness=0.9,
                                       note="V10: painted lemon-grove mural on the kids' bed wall"),
    },
)
