"""V13 Modern Industrial = V1 layout, colours/finishes only."""

STEEL = "#2c2d30"      # blackened steel
SMOKED = "#5a4636"     # smoked / reclaimed oak
RECLAIM = "#6b5340"    # reclaimed wood, a shade lighter
CHAR = "#43464a"       # charcoal lacquer
RUST = "#a0522d"
BRICK = "#9a4a32"
COPPER = "#9c5f3a"     # second metal: copper pendant / lamps
COGNAC = "#93542f"     # real cognac leather
CHARW = "#4d4741"      # warm charcoal wool
CONCRETE = "#8a847b"   # cast concrete

SPEC = dict(
    name="Modern Industrial",
    description=("Colour scheme of V1 (same furniture, same places): modern industrial loft - warm microcement "
                 "and concrete-grey slabs, exposed-brick feature walls, blackened steel + copper, smoked reclaimed "
                 "oak, charcoal fronts, cognac leather sofa and dining chairs, charcoal wool armchairs, concrete "
                 "basins, matte-black WCs, rust accents; steel-blue + mustard kids' room"),
    wall_color="#cfc8bd",
    rooms={
        "living": dict(floor="industrial_reclaimed_oak", paint="#c6bfb4", skirting=STEEL),
        "hall": dict(floor="industrial_microcement", paint="#c4bdb2", skirting=STEEL),
        "kitchen": dict(floor="industrial_microcement", paint="#cdc6bb"),
        "bath_1": dict(floor="industrial_microcement", walls="industrial_concrete_wall"),
        "bath_2": dict(floor="industrial_microcement", walls="industrial_graphite_slab"),
        "bedroom_1": dict(floor="industrial_weathered_oak", paint="#ddd5c8", skirting="#e6e3dd"),
        "bedroom_2": dict(floor="industrial_reclaimed_oak", paint="#b3aa9e", skirting=STEEL),
        "balcony": dict(floor="industrial_microcement"),
    },
    aprons={"ripple": {"living": "industrial_brick", "bedroom_2": "industrial_graphite_slab"},
            "delicate_blues": "industrial_blueprint_watercolor",
            "cream_marble": "industrial_brick",
            "greige_stone": "industrial_graphite_slab"},
    colors={
        "*": {"#b08d57": STEEL,                        # brass fittings -> blackened steel
              "#151515": "#1f2022",                    # track lights black steel
              "#fbfaf7": "#e2ded6",                    # sheers warm-grey linen
              "#8e9196": "#bdb6ab"},                   # AC units toned to the walls
        "living": {"#86694b": COGNAC,                  # sofa cognac leather (armchairs: items, charcoal)
                   "#6f6152": "#3e3b38",               # rug charcoal wool (fibre sheen lifts it to mid-grey)
                   "#313233": RECLAIM,                 # coffee table reclaimed wood
                   "#3a3b3d": STEEL,                   # side table steel
                   "#6b4a33": "#3a2e26",               # slat TV wall dark smoked oak
                   "#6f5646": "#45474a",               # drapes charcoal
                   "#a08b78": CHAR,                    # wardrobe doors charcoal
                   "#8a5f3e": SMOKED,                  # wood column + interior
                   "#b88a5a": STEEL,
                   "#c9a46a": COPPER,                  # pendant copper
                   "#cfcfcd": RECLAIM,                 # desk top reclaimed wood
                   "#6e6e70": "#36373a",               # gaming chair
                   "#ece6dc": BRICK},                  # wallpaper panel = brick
        "hall": {"#6b4a33": STEEL, "#8a5a3c": SMOKED, "#8a5f3e": SMOKED,
                 "#a08b78": CHAR, "#b88a5a": STEEL, "#3a3633": "#2a2b2d",
                 "#3b3b3d": RUST, "#d9cfc0": "#8f8c87",
                 "#5a3e2b": "#6b3f22", "#e9e6df": "#3a3b3d"},   # cognac boots + black sneakers
        "kitchen": {"#cfc2ad": "#3a3c3f",              # base + tall units graphite
                    "#7a5236": SMOKED,                 # worktop, wall units, table smoked oak
                    "#b9a88c": STEEL, "#3a3a3a": STEEL,
                    "#b8a990": COGNAC,                 # chairs cognac leather
                    "#efe6d6": BRICK,                  # backsplash brick
                    "#e6e4df": "#6e7073",              # venetian blind steel grey
                    "#f4f3f0": "#c4bfb7"},             # grey stoneware place settings + bowl
        "bath_1": {"#3f2a1c": "#4a3a2e", "#6b4428": SMOKED, "#3a3a3a": "#202022",
                   "#d9cbb5": RUST,                    # towels rust
                   "#e6ddd0": CONCRETE,                # concrete vessel sink
                   "#c4b6a4": "#9a948a",
                   "#f6f6f6": "#2b2b2d"},              # matte-black WC
        "bath_2": {"#3f2a1c": "#4a3a2e", "#3a3a3a": "#202022",
                   "#d9cbb5": "#8f8b85",               # towels concrete grey
                   "#e6ddd0": CONCRETE, "#c4b6a4": "#6a645c"},
        "bedroom_1": {"#7f9fb0": "#4f6577",            # wardrobe doors + chair steel blue
                      "#efe6d6": "#e6e3dd",
                      "#8ea8b6": "#b98a3a",            # drapes mustard
                      "#5a7f96": "#8f8b84",            # rug warm grey
                      "#c9a77c": "#8a6e52",            # desk, slats, handles weathered oak
                      "#2f6fb3": "#b0532e",            # Baby Turi tag rust
                      "#ede6dc": "#ebe6dc", "#ecebe8": "#8a6e52",
                      "#d8cfc2": "#4f6577",            # steel-blue enamel table lamp
                      "#3d6fa8": "#b0532e", "#5e8fbf": "#c39a3e"},
        "bedroom_2": {"#a08b78": CHAR,                 # wardrobes / console charcoal
                      "#8a5f3e": SMOKED,               # wood column, interiors + bed smoked oak
                      "#b88a5a": STEEL,
                      "#6b4a33": "#3a2e26",
                      "#6f5646": "#8a3f24",            # drapes rust
                      "#8a7764": "#7d7873",            # rug concrete grey
                      "#ece6dc": "#5c5d5f",
                      "#ecebe8": SMOKED, "#d8cfc2": COPPER},  # copper table lamps
        "balcony": {"#9a6b43": STEEL, "#2f2f31": RUST, "#f2efe9": "#3a3b3d"},
    },
    accent={"*": STEEL,                  # sofa / armchair base + feet blackened steel
            "bath_1": "#6a645c",         # shower curb graphite concrete
            "bedroom_1": "#a9b8c4",      # kids duvet pale steel-blue
            "bedroom_2": "#9e978d"},     # master duvet warm-grey washed linen
    metal={"*": STEEL},
    items={
        "plush-armchair-living-1": {"color": CHARW},
        "plush-armchair-living-2": {"color": CHARW},
    },
    finishes={
        "industrial_microcement": dict(
            kind="stone", size=[1.20, 1.20], color="#7c766e", color2="#69635b", joint_color="#5e5850",
            joint=0.001, roughness=0.5,
            note="V13: warm-grey microcement-look large slabs 120 x 120 (hall, kitchen, baths, balcony)"),
        "industrial_concrete_wall": dict(
            kind="stone", size=[1.20, 0.60], color="#9a948a", color2="#827c72", joint_color="#76706a",
            joint=0.0015, roughness=0.55,
            note="V13: light raw-concrete-look slabs 120 x 60 (bath 1 walls)"),
        "industrial_graphite_slab": dict(
            kind="stone", size=[0.60, 1.20], color="#6a645c", color2="#55504a", joint_color="#47423d",
            joint=0.0015, roughness=0.45,
            note="V13: graphite concrete-look 60 x 120 vertical (bath 2 walls + tub front, master bed wall)"),
        "industrial_brick": dict(
            kind="tiles", size=[0.25, 0.065], color="#9a4a32", color2="#743523", joint_color="#a69c8e",
            joint=0.005, roughness=0.85,
            note="V13: exposed-brick-look slips 25 x 6.5 with pale mortar (living sofa wall, kitchen backsplash)"),
        "industrial_reclaimed_oak": dict(
            kind="parquet", size=[1.50, 0.22], direction="x", color="#6f5a47", color2="#5b4838",
            joint_color="#241b14", joint=0.002, roughness=0.55,
            note="V13: smoked reclaimed oak wide planks (living, master suite)"),
        "industrial_weathered_oak": dict(
            kind="parquet", size=[1.50, 0.22], direction="x", color="#a8927a", color2="#968069",
            joint_color="#5a4a3b", joint=0.0015, roughness=0.5,
            note="V13: lighter weathered grey oak (kids' room)"),
        "industrial_blueprint_watercolor": dict(
            kind="watercolor", size=[3.10, 2.70], color="#ebe6dc", color2="#4f6f88",
            joint_color="#ebe6dc", joint=0.0, roughness=0.85,
            note="V13: steel-blue watercolour sky mural on the kids' bed wall"),
    },
)
