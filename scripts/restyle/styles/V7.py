"""V7 Japandi: V1 layout, classic Japandi contrast - light oak + charred (shou sugi ban) wood, washi whites,
stone greys, charcoal slate, muted clay accents, matte black metal."""


OAK = "#c4a57f"       # natural white oak furniture
OAK_LT = "#d8c3a2"    # pale oak (cabinet interiors)
CHAR = "#2b2623"      # shou sugi ban / charred-stained wood
BLACK = "#1f1f1f"     # blackened steel
CLAY = "#a3755a"      # muted clay accent
WASHI = "#ece5d8"     # rice-paper white
STONE = "#b8b1a6"     # stone grey
LINEN = "#cdbfa8"     # oat linen
CHARCOAL = "#4a4643"  # charcoal linen

SPEC = dict(
    name="Japandi",
    description=("Colour scheme of V1 (same furniture, same places): classic Japandi contrast - natural white oak "
                 "against charred shou-sugi-ban wood, washi-paper whites, stone greys, charcoal slate baths, "
                 "mushroom linen sofa on an oak plinth with clay armchairs, oat linen drapes, "
                 "blackened-steel metal"),
    wall_color="#d8c9b0",
    rooms={
        "living": dict(floor="japandi_oak", paint="#d4c3a6", skirting=CHAR),
        "hall": dict(floor="japandi_stone", paint="#d8c9b0"),
        "kitchen": dict(floor="japandi_stone", paint="#dccdb4"),
        "bath_1": dict(floor="japandi_slate", walls="japandi_washi_tile"),
        "bath_2": dict(floor="japandi_slate", walls="japandi_pietra"),
        "bedroom_1": dict(floor="japandi_oak", paint="#e0c6ac", skirting="#efe9de"),
        "bedroom_2": dict(floor="japandi_oak", paint="#c2ae92", skirting=CHAR),
        "balcony": dict(floor="japandi_slate"),
    },
    aprons={"ripple": {"living": "japandi_ripple_stone", "bedroom_2": "japandi_charred_chevron"},
            "delicate_blues": "japandi_ink_watercolor", "cream_marble": "japandi_pietra",
            "greige_stone": "japandi_slate"},
    accent={"living": OAK,                              # sofa / armchair plinth + feet light oak
            "bedroom_1": "#dcc3ad",                     # kids' duvet pale clay linen
            "bedroom_2": "#e6dccb",                     # master duvet washi oat linen
            "bath_1": "#4c4946",                        # shower curb = slate
            "*": OAK},
    metal={"*": BLACK},
    colors={
        "*": {"#b08d57": BLACK,                         # brass -> blackened steel
              "#151515": BLACK,                         # track lights black
              "#fbfaf7": "#f1ece2",                     # sheers washi voile
              "#d8cfc2": "#ece4d4"},                    # table lamps washi paper
        "living": {"#86694b": "#9a8b78",                # corner sofa mushroom-grey linen (armchairs: clay)
                   "#6f6152": "#a3937b",                # shag rug pebble wool
                   "#313233": CHAR,                     # coffee table charred wood
                   "#3a3b3d": OAK,                      # side table light oak
                   "#6b4a33": CHAR,                     # slat TV wall shou sugi ban
                   "#6f5646": LINEN,                    # drapes oat linen
                   "#a08b78": OAK,                      # wardrobe doors light oak
                   "#8a5f3e": CHAR,                     # wardrobe column charred
                   "#b88a5a": BLACK,
                   "#c9a46a": "#e9e2d3",                # pendant washi paper
                   "#1e1e1e": BLACK,                    # floor lamp black
                   "#cfcfcd": OAK,                      # desk top oak
                   "#6e6e70": "#3b3936",                # gaming chair charcoal
                   "#ece6dc": "#c4b296",
                   "#8e9196": "#d4c3a6"},               # AC = wall
        "hall": {"#6b4a33": CHAR, "#8a5a3c": CHAR, "#8a5f3e": OAK, "#a08b78": OAK, "#b88a5a": BLACK,
                 "#3a3633": "#4a4540", "#3b3b3d": CLAY, "#d9cfc0": "#e3dccd",
                 "#5a3e2b": CHARCOAL, "#e9e6df": WASHI},          # shoes charcoal + washi canvas
        "kitchen": {"#cfc2ad": CHAR,                    # base + tall units, oven front: charred oak
                    "#7a5236": OAK,                     # worktop, wall units, dining table: light oak
                    "#b9a88c": BLACK, "#3a3a3a": BLACK,
                    "#b8a990": CHARCOAL,                # dining chairs charcoal linen
                    "#1e1e1e": BLACK,
                    "#f4f3f0": "#e6dfd2",               # place settings speckled stoneware
                    "#efe6d6": "#ad9c80",               # backsplash = pietra stone
                    "#e6e4df": WASHI},                  # blind washi
        "bath_1": {"#3f2a1c": OAK, "#6b4428": CHAR, "#3a3a3a": BLACK,
                   "#d9cbb5": CHARCOAL,                 # charcoal waffle towels
                   "#e6ddd0": STONE,                    # stone vessel sink
                   "#c4b6a4": "#dcd2c0"},
        "bath_2": {"#3f2a1c": CHAR, "#3a3a3a": BLACK,
                   "#d9cbb5": "#b58f78",                # clay towels
                   "#e6ddd0": "#ece7de",                # washi-white vessel sink
                   "#c4b6a4": "#ad9c80"},
        "bedroom_1": {"#7f9fb0": "#c49a82",             # wardrobe doors: soft clay
                      "#efe6d6": "#efe9de",             # washi carcass, bed, storage
                      "#8ea8b6": LINEN,                 # drapes oat linen
                      "#5a7f96": "#cfa98e",             # rug pale clay
                      "#c9a77c": OAK,                   # desk, slats, handles oak
                      "#2f6fb3": "#a85d45",             # Baby Turi tag clay red
                      "#ede6dc": "#efe9de", "#ecebe8": OAK,
                      "#3d6fa8": "#6f7d84", "#5e8fbf": "#c49a82",
                      "#8e9196": "#e0c6ac"},
        "bedroom_2": {"#a08b78": OAK,                   # wardrobe / console doors light oak
                      "#8a5f3e": CHAR,                  # wood column + bed charred
                      "#b88a5a": BLACK, "#6b4a33": CHAR,
                      "#6f5646": CHARCOAL,              # drapes charcoal linen
                      "#8a7764": "#9a8b76",             # rug stone wool
                      "#ece6dc": CHAR, "#ecebe8": OAK,
                      "#8e9196": "#c2ae92"},
        "balcony": {"#9a6b43": "#b89a72", "#2f2f31": CLAY, "#f2efe9": WASHI},
    },
    items={
        "plush-armchair-living-1": {"color": CLAY},         # clay linen lounge chairs
        "plush-armchair-living-2": {"color": CLAY},
        "wardrobe-living-1": {"interior_color": OAK_LT},
        "wardrobe-hall-1": {"interior_color": OAK_LT},
        "wardrobe-master-suite-1": {"interior_color": OAK_LT},
        "wardrobe-master-suite-2": {"interior_color": OAK_LT},
        "tv-console-master-suite-1": {"interior_color": OAK_LT},
        "chair-bedroom-1-1": {"color": OAK},                # kids' desk chair oak
        "serving-bowl-kitchen-1": {"color": CHAR},          # charred-wood bowl
        "tall-cabinet-bathroom-1-1": {"interior_color": OAK_LT},
        "tall-cabinet-master-bathroom-1": {"interior_color": OAK_LT},
    },
    finishes={
        "japandi_oak": dict(kind="parquet", size=[1.20, 0.19], direction="x", color="#b8956a",
                            color2="#a6845c", joint_color="#6e5638", joint=0.0015, roughness=0.5,
                            note="V7: natural matte white oak planks (living, bedrooms)"),
        "japandi_stone": dict(kind="stone", size=[0.60, 0.60], color="#8f8370", color2="#786b58",
                              joint_color="#8a857c", joint=0.002, roughness=0.5,
                              note="V7: honed warm-grey limestone-look 60 x 60 (hall, kitchen)"),
        "japandi_slate": dict(kind="stone", size=[0.60, 0.60], color="#4c4946", color2="#3b3936",
                              joint_color="#2f2d2b", joint=0.003, roughness=0.55,
                              note="V7: charcoal slate-look 60 x 60 (bath floors, tub apron, balcony)"),
        "japandi_washi_tile": dict(kind="stone", size=[0.10, 0.30], color="#dcd2c0", color2="#c6b9a3",
                                   joint_color="#bfb8ab", joint=0.002, roughness=0.2,
                                   note="V7: handmade washi-white glazed 10 x 30, vertical stack (bath 1 walls)"),
        "japandi_pietra": dict(kind="stone", size=[0.60, 1.20], color="#ad9c80", color2="#937f63",
                               joint_color="#a49d91", joint=0.002, roughness=0.35,
                               note="V7: pietra-grey stone-look 60 x 120 (bath 2 walls, kitchen backsplash)"),
        "japandi_ripple_stone": dict(kind="ripple", size=[3.04, 2.70], color="#cdbca0", color2="#8a785e",
                                     joint_color="#c4b296", joint=0.0, roughness=0.85,
                                     note="V7: Ripple wallpaper in stone grey (living sofa wall)"),
        "japandi_charred_chevron": dict(kind="chevron", size=[3.04, 2.70], color="#2e2926", color2="#3d3632",
                                        joint_color="#141110", joint=0.0, roughness=0.8,
                                        note="V7: shou-sugi-ban charred timber panelling behind the master bed"),
        "japandi_ink_watercolor": dict(kind="watercolor", size=[3.10, 2.70], color="#ece3d3", color2="#6f7a80",
                                       joint_color="#efe9de", joint=0.0, roughness=0.9,
                                       note="V7: sumi-e ink-wash misty mountains mural (kids bed wall)"),
    },
)
