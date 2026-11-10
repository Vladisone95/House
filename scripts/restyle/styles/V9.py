"""V9 Quiet Luxury = V1 layout (same ids/sizes/places), tonal greige-mink-cashmere palette only.

Palette: greige / mushroom / mink walls, greige-washed oak + smoked walnut (two woods), honed limestone,
taupe-veined marble, ivory cashmere boucle sofa, camel suede + leather, mink velvet, ivory lacquer
joinery, smoked bronze (one metal); one dusty-blue note in the kids' room.
"""


BRONZE = "#5f4a35"      # smoked / brushed bronze (replaces brass + black hardware)
BRONZE_LT = "#8a7055"   # lighter bronze for lamps / pendant
WALNUT = "#4f3b2d"      # smoked walnut (wood accents, vanities, master wardrobes)
GOAK = "#a8896a"        # greige-washed oak
MINK = "#7e6857"        # mink (kitchen base, velvet)
IVORY = "#ddd0bd"       # ivory cashmere lacquer / boucle
CAMEL = "#a47b55"       # camel suede / leather
MARBLE = "#cfc0a8"      # honed taupe-veined marble / limestone tops
SHEER = "#e9e0d2"       # ivory wool-linen sheers

SPEC = dict(
    name="Quiet Luxury",
    description=("Colour scheme of V1 (same furniture, same places): Quiet Luxury - tonal greige / mushroom / mink "
                 "walls, greige-washed oak and honed limestone floors, taupe-veined marble, smoked walnut, "
                 "ivory cashmere boucle, camel suede, mink velvet, ivory lacquer joinery, smoked bronze hardware"),
    wall_color="#d2bea4",
    rooms={
        "living": dict(floor="quietlux_greige_oak", paint="#b49a7c", skirting="#a38d76"),
        "hall": dict(floor="quietlux_limestone", paint="#c2aa8c", skirting="#a38d76"),
        "kitchen": dict(floor="quietlux_limestone", paint="#c9b298"),
        "bath_1": dict(floor="quietlux_limestone", walls="quietlux_mink_stone"),
        "bath_2": dict(floor="quietlux_mink_stone", walls="quietlux_taupe_marble"),
        "bedroom_1": dict(floor="quietlux_greige_oak", paint="#e3cdb2", skirting="#e3cdb2"),
        "bedroom_2": dict(floor="quietlux_greige_oak", paint="#ad9478", skirting="#a38d76"),
        "balcony": dict(floor="quietlux_limestone"),
    },
    aprons={"ripple": {"living": "quietlux_ripple_cashmere", "bedroom_2": "quietlux_ripple_mink"},
            "delicate_blues": "quietlux_camel_watercolor",
            "cream_marble": "quietlux_taupe_marble",
            "greige_stone": "quietlux_taupe_marble"},
    metal={"*": BRONZE},
    accent={"*": WALNUT,                                 # sofa / armchair plinth + feet: smoked walnut
            "bedroom_1": "#c9a882",                      # kids' duvet: camel
            "bedroom_2": "#e6ddcf",                      # master duvet: ivory cashmere
            "bath_1": MARBLE, "bath_2": MARBLE},         # shower curb: marble
    colors={
        "*": {"#b08d57": BRONZE,                         # brass fittings -> smoked bronze
              "#151515": BRONZE,                         # track lights
              "#fbfaf7": SHEER},                         # sheers ivory
        "living": {"#86694b": "#c8b79e",                     # sofa (armchairs: camel, below): oatmeal-ivory cashmere boucle
                   "#6f6152": "#7d6b59",                 # rug: taupe wool (pile renders lighter)
                   "#313233": MARBLE,                    # coffee table: honed marble
                   "#3a3b3d": BRONZE,                    # side table bronze
                   "#6b4a33": WALNUT,                    # slat TV wall
                   "#6f5646": "#7a5f4b",                 # drapes mink velvet
                   "#a08b78": IVORY,                     # wardrobe doors: ivory cashmere lacquer
                   "#8a5f3e": WALNUT,                    # wardrobe wood column + interior: smoked walnut
                   "#b88a5a": BRONZE,                    # handles
                   "#c9a46a": BRONZE_LT,                 # infinity pendant bronze
                   "#1e1e1e": BRONZE,                    # floor lamp bronze
                   "#cfcfcd": WALNUT,                    # desk top walnut
                   "#6e6e70": "#8f6a4a",                 # gaming chair camel leather
                   "#8e9196": "#b49a7c",                 # AC: wall-matched
                   "#ece6dc": "#a88c6e"},                # wallpaper panel base
        "hall": {"#6b4a33": WALNUT, "#8a5a3c": WALNUT, "#8a5f3e": WALNUT,
                 "#a08b78": IVORY, "#b88a5a": BRONZE, "#3a3633": "#5d544b",
                 "#3b3b3d": BRONZE_LT, "#d9cfc0": "#ece5da"},
        "kitchen": {"#cfc2ad": MINK,                     # base + tall units, oven: mink matte lacquer
                    "#7a5236": WALNUT,                   # wall units, dining table: smoked walnut (tops: marble, below)
                    "#b9a88c": BRONZE, "#3a3a3a": BRONZE,
                    "#b8a990": CAMEL,                    # dining chairs: camel suede
                    "#efe6d6": "#cbb79b",                # backsplash panel = taupe marble
                    "#e6e4df": "#d9cfc1",                # venetian blind greige
                    "#1e1e1e": BRONZE,                   # linear pendant
                    "#1c1c1c": "#3e352d",                # sink: smoked-bronze composite
                    "#f4f3f0": "#ece5da"},               # ivory porcelain
        "bath_1": {"#3f2a1c": WALNUT, "#6b4428": GOAK, "#3a3a3a": BRONZE,
                   "#d9cbb5": CAMEL,                     # camel towels
                   "#e6ddd0": "#d6c8b4",                 # marble vessel sink
                   "#c4b6a4": "#9e8570"},                # niche = mink stone
        "bath_2": {"#3f2a1c": WALNUT, "#3a3a3a": BRONZE,
                   "#d9cbb5": MINK,                      # mink towels
                   "#e6ddd0": "#e2d8c8",                 # ivory stone sink
                   "#c4b6a4": "#cbb79b"},                # niche = taupe marble
        "bedroom_1": {"#7f9fb0": "#b79473",              # wardrobe doors + chair: camel
                      "#efe6d6": "#efe8dd",              # ivory carcass, bed, storage
                      "#8ea8b6": "#a8968a",              # drapes oat-mink
                      "#5a7f96": "#b3a28c",              # rug oatmeal wool
                      "#c9a77c": GOAK,                   # desk, slat wall, handles greige oak
                      "#2f6fb3": "#7d8ea2",              # Baby Turi tag dusty blue
                      "#ede6dc": "#efe8dd", "#ecebe8": "#d9cbbb",
                      "#d8cfc2": BRONZE_LT,              # table lamp bronze
                      "#8e9196": "#e3cdb2",              # AC: wall-matched
                      "#3d6fa8": "#b88a6a", "#5e8fbf": "#8fa0b2"},   # notebooks caramel, pencil case dusty blue
        "bedroom_2": {"#a08b78": WALNUT,                 # wardrobes / console fronts: smoked walnut
                      "#8a5f3e": GOAK,                   # wood columns + interiors: greige oak (bed: mink, below)
                      "#b88a5a": BRONZE,
                      "#6b4a33": WALNUT,
                      "#6f5646": "#6e5646",              # drapes deep mink velvet
                      "#8a7764": "#8a7967",              # rug cashmere greige
                      "#ece6dc": "#846c58",              # wallpaper panel base mink
                      "#ecebe8": MARBLE,                 # nightstands marble
                      "#8e9196": "#ad9478",              # AC: wall-matched
                      "#d8cfc2": BRONZE_LT},             # table lamps bronze
        "balcony": {"#9a6b43": "#9c8b77", "#2f2f31": BRONZE, "#f2efe9": "#ece5da"},
    },
    items={
        "plush-armchair-living-1": {"color": CAMEL},     # camel suede armchairs
        "plush-armchair-living-2": {"color": CAMEL},
        "countertop-kitchen-1": {"color": MARBLE},       # honed marble worktops
        "countertop-kitchen-2": {"color": MARBLE},
        "countertop-kitchen-3": {"color": MARBLE},
        "countertop-kitchen-4": {"color": MARBLE},
        "floating-bed-master-suite-1": {"color": MINK},  # mink upholstered bed
        "chair-bedroom-1-1": {"color": "#8fa0b2"},       # dusty-blue desk chair
    },
    finishes={
        "quietlux_greige_oak": dict(kind="parquet", size=[1.20, 0.19], direction="x",
                                    color="#a8896a", color2="#967759", joint_color="#5a4430",
                                    joint=0.0015, roughness=0.5,
                                    note="greige-washed (mushroom) wide French oak, matte oil"),
        "quietlux_limestone": dict(kind="stone", size=[1.20, 0.60],
                                   color="#cab394", color2="#b39c7e", joint_color="#b8a284",
                                   joint=0.002, roughness=0.45,
                                   note="honed warm-grey limestone, large format 60 x 120"),
        "quietlux_mink_stone": dict(kind="stone", size=[0.60, 1.20],
                                    color="#9e8570", color2="#856d59", joint_color="#8a725e",
                                    joint=0.002, roughness=0.35,
                                    note="mink / taupe honed stone-look porcelain 60 x 120"),
        "quietlux_taupe_marble": dict(kind="marble", size=[1.20, 0.60],
                                      color="#cbb79b", color2="#7d6249", joint_color="#bfaa8c",
                                      joint=0.0015, roughness=0.2,
                                      note="warm ivory marble with soft taupe veins, satin polish"),
        "quietlux_ripple_cashmere": dict(kind="ripple", size=[3.04, 2.70],
                                         color="#a88c6e", color2="#7f6650", joint_color="#a88c6e",
                                         joint=0.0, roughness=0.85,
                                         note="cashmere-camel fluted ripple wall panel"),
        "quietlux_ripple_mink": dict(kind="ripple", size=[3.04, 2.70],
                                     color="#846c58", color2="#6a5444", joint_color="#846c58",
                                     joint=0.0, roughness=0.85,
                                     note="mink upholstered-look ripple bed wall"),
        "quietlux_camel_watercolor": dict(kind="watercolor", size=[3.10, 2.70],
                                          color="#efe8dd", color2="#c49a72", joint_color="#efe8dd",
                                          joint=0.0, roughness=0.9,
                                          note="ivory clouds with soft camel washes, kids room"),
    },
)
