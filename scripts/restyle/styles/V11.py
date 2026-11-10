"""V11 Scandinavian - V1 layout (same ids, sizes, places), new colours + finishes only."""


WHITE = "#f4f2ec"       # crisp warm-neutral white (walls, carcasses)
FRONT = "#f0efeb"       # matte white joinery fronts
BIRCH = "#d9bb8f"       # birch / birch plywood
STEEL = "#a8acb0"       # brushed steel / nickel
DBLUE = "#7f97aa"       # dusty Nordic blue
MUSTARD = "#d6a84a"     # hygge mustard
ROSE = "#d4a5a0"        # dusty pink
GREY = "#a6a7a3"        # light-grey wool upholstery
LAMP = "#e9e9e5"        # matte white lamps / tracks

SPEC = dict(
    name="Scandinavian",
    description=("Colour scheme of V1 (same furniture, same places): Scandinavian / hygge - crisp whites, "
                 "white-washed pine + birch, light-grey wool sofa with mustard armchairs, dusty Nordic blue "
                 "kitchen, drapes and headboard wall, white + dusty-blue subway tiles, mustard and dusty-pink "
                 "textiles, white lamps and tracks, brushed steel"),
    wall_color=WHITE,
    rooms={
        "living": dict(floor="scandi_whitewash_pine", paint="#f5f4f0", skirting="#f5f4f0"),
        "hall": dict(floor="scandi_grey_tiles", paint=WHITE, skirting="#f5f4f0"),
        "kitchen": dict(floor="scandi_grey_tiles", paint="#f5f4f0"),
        "bath_1": dict(floor="scandi_grey_mosaic", walls="scandi_subway_white"),
        "bath_2": dict(floor="scandi_grey_mosaic", walls="scandi_subway_blue"),
        "bedroom_1": dict(floor="scandi_whitewash_pine", paint="#f2e2dc", skirting="#f6f5f1"),
        "bedroom_2": dict(floor="scandi_whitewash_pine", paint="#dcdedb", skirting="#f5f4f0"),
        "balcony": dict(floor="scandi_grey_deck"),
    },
    aprons={"ripple": {"living": "scandi_ripple_grey", "bedroom_2": "scandi_ripple_blue"},
            "delicate_blues": "scandi_blush_watercolor", "cream_marble": "scandi_subway_white",
            "greige_stone": "scandi_subway_white"},
    colors={
        "*": {"#b08d57": STEEL,                     # brass fittings -> brushed steel
              "#151515": LAMP,                      # track lights matte white
              "#fbfaf7": "#f7f6f2",                 # sheers white linen
              "#8e9196": "#eeede9",                 # AC units blend into the white walls
              "#f6f6f6": "#f7f7f5"},                # white sanitary
        "living": {"#86694b": GREY,                 # sofa light-grey wool (armchairs: items, mustard)
                   "#6f6152": "#b8ae9e",            # shag rug: oatmeal wool (fibre sheen lifts it to off-white)
                   "#313233": BIRCH,                # coffee table birch
                   "#3a3b3d": "#eeeeea",            # side table white
                   "#6b4a33": BIRCH,                # slat TV wall birch
                   "#6f5646": DBLUE,                # drapes dusty blue
                   "#a08b78": FRONT,                # wardrobe doors white
                   "#8a5f3e": BIRCH,                # wardrobe wood column + interior birch
                   "#b88a5a": STEEL,
                   "#c9a46a": LAMP,                 # pendant matte white
                   "#1e1e1e": LAMP,                 # floor lamp matte white
                   "#cfcfcd": BIRCH,                # desk top birch
                   "#6e6e70": "#8e9297",            # gaming chair grey
                   "#ece6dc": "#efefed"},           # wallpaper panel base
        "hall": {"#6b4a33": BIRCH, "#8a5a3c": BIRCH, "#8a5f3e": BIRCH,
                 "#a08b78": FRONT, "#b88a5a": STEEL, "#3a3633": "#8b8e90",   # grey felt doormat
                 "#3b3b3d": DBLUE, "#d9cfc0": "#f2f1ed",
                 "#5a3e2b": "#9a9c9e", "#e9e6df": "#f2f1ed"},               # grey felt + white sneakers
        "kitchen": {"#cfc2ad": DBLUE,               # base + tall units, oven: dusty Nordic blue
                    "#7a5236": BIRCH,               # worktop, wall units, dining table: birch
                    "#b9a88c": STEEL, "#3a3a3a": STEEL,
                    "#b8a990": MUSTARD,             # upholstered chairs mustard wool
                    "#efe6d6": "#f5f5f2",           # backsplash = white subway
                    "#e6e4df": "#f2f1ee",           # blind white
                    "#1e1e1e": LAMP,                # linear pendant matte white
                    "#1c1c1c": "#d9d9d5",           # sink: light-grey composite
                    "#2a2a2c": "#e9e9e5",           # hood visor white
                    "#f4f3f0": "#e4e6e6"},          # grey-white stoneware
        "bath_1": {"#3f2a1c": BIRCH, "#6b4428": BIRCH, "#3a3a3a": STEEL,
                   "#d9cbb5": ROSE,                 # towels dusty pink
                   "#e6ddd0": "#f4f4f2", "#c4b6a4": "#f5f5f2"},
        "bath_2": {"#3f2a1c": BIRCH, "#3a3a3a": STEEL,
                   "#d9cbb5": MUSTARD,              # towels mustard
                   "#e6ddd0": "#f4f4f2", "#c4b6a4": "#9cb2c3"},
        "bedroom_1": {"#7f9fb0": MUSTARD,           # wardrobe doors + desk chair mustard
                      "#efe6d6": "#f6f5f1",         # white carcass, bed, storage
                      "#8ea8b6": ROSE,              # drapes dusty pink
                      "#5a7f96": "#a9b9c6",         # rug soft dusty blue
                      "#c9a77c": BIRCH,             # desk, slat wall, handles birch
                      "#2f6fb3": "#b8605c",         # Baby Turi tag deep rose
                      "#ede6dc": "#f6f1ec", "#ecebe8": BIRCH,
                      "#d8cfc2": LAMP,              # table lamp white
                      "#3d6fa8": DBLUE, "#5e8fbf": MUSTARD},
        "bedroom_2": {"#a08b78": FRONT,             # wardrobe / console doors white
                      "#8a5f3e": BIRCH,             # wood column, interiors + bed birch
                      "#b88a5a": STEEL,
                      "#6b4a33": BIRCH,
                      "#6f5646": "#9da3a6",         # drapes mid-grey linen
                      "#8a7764": "#d6b4ad",         # rug blush wool
                      "#ece6dc": "#7f95a6",         # headboard wallpaper base dusty blue
                      "#ecebe8": BIRCH,             # nightstands birch
                      "#d8cfc2": LAMP},             # ceramic table lamps white
        "balcony": {"#9a6b43": "#cdb38c", "#2f2f31": MUSTARD, "#f2efe9": DBLUE},
    },
    accent={"*": BIRCH,                  # sofa / armchair base + feet birch
            "bath_1": "#d3d4d1",         # shower curb light grey
            "bedroom_1": "#e6c6c0",      # kids duvet dusty-pink linen
            "bedroom_2": "#f1efe9"},     # master duvet crisp white linen
    metal={"*": STEEL, "kitchen": BIRCH},   # kitchen chairs on birch legs
    items={
        "plush-armchair-living-1": {"color": MUSTARD},
        "plush-armchair-living-2": {"color": MUSTARD},
    },
    finishes={
        "scandi_whitewash_pine": dict(kind="parquet", size=[1.80, 0.22], direction="x", color="#e6dac4",
                                      color2="#d6c7ab", joint_color="#a89a82", joint=0.0015, roughness=0.5,
                                      note="V11: white-washed pine / birch wide planks 180 x 22 (living, bedrooms)"),
        "scandi_grey_tiles": dict(kind="tiles", size=[0.60, 0.60], color="#d3d4d1", color2="#a3a5a4",
                                  joint_color="#bcbdba", joint=0.002, roughness=0.45,
                                  note="V11: soft-grey speckled porcelain 60 x 60 (hall, kitchen)"),
        "scandi_grey_mosaic": dict(kind="tiles", size=[0.10, 0.10], color="#a3a8ab", color2="#868b8f",
                                   joint_color="#d2d4d4", joint=0.002, roughness=0.4,
                                   note="V11: grey 10 x 10 mosaic with light grout (bath floors)"),
        "scandi_subway_white": dict(kind="stone", size=[0.15, 0.075], color="#f5f5f2", color2="#e6e7e4",
                                    joint_color="#b9bcbe", joint=0.002, roughness=0.15,
                                    note="V11: glossy white subway 15 x 7.5, grey grout (bath 1, backsplash, tub)"),
        "scandi_subway_blue": dict(kind="stone", size=[0.15, 0.075], color="#9cb2c3", color2="#889fb2",
                                   joint_color="#e6e8e8", joint=0.002, roughness=0.15,
                                   note="V11: dusty Nordic-blue glazed subway 15 x 7.5, white grout (bath 2 walls)"),
        "scandi_ripple_grey": dict(kind="ripple", size=[3.04, 2.70], color="#eeeeec", color2="#b9c0c6",
                                   joint_color="#eeeeec", joint=0.0, roughness=0.85,
                                   note="V11: Ripple wallpaper in white / cool blue-grey (living)"),
        "scandi_ripple_blue": dict(kind="ripple", size=[3.04, 2.70], color="#7f95a6", color2="#5f7689",
                                   joint_color="#7f95a6", joint=0.0, roughness=0.85,
                                   note="V11: dusty-blue ripple headboard wall (master suite)"),
        "scandi_blush_watercolor": dict(kind="watercolor", size=[3.10, 2.70], color="#f6f1ec", color2="#d39a93",
                                        joint_color="#f6f1ec", joint=0.0, roughness=0.9,
                                        note="V11: blush-pink watercolour clouds on the kids bed wall"),
        "scandi_grey_deck": dict(kind="parquet", size=[1.20, 0.14], direction="y", color="#a9a59d",
                                 color2="#97938b", joint_color="#4a4844", joint=0.006, roughness=0.65,
                                 note="V11: weathered silver-grey deck boards (balcony)"),
    },
)
