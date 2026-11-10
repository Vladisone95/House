"""V5 Modern Minimalism: V1 layout, colours/finishes only. Chalk white + concrete grey + graphite, brushed steel
+ matte black; one signal-yellow accent in the kids' room."""


W = "#ececea"      # matte white lacquer (handleless: handles = front colour)
G = "#3a3b3d"      # graphite / soft black
INK = "#222224"    # matte black (lamps, track lights, sofa plinth)
STEEL = "#a8aaac"  # brushed stainless
GREY = "#d9d8d4"   # pale warm-grey interiors / boucle
ACC = "#e2b93b"    # the one accent (kids' room only): signal yellow

SPEC = dict(
    name="Modern Minimalism",
    description=("V1's furniture and places restyled as Modern Minimalism - monochrome chalk whites, "
                 "pale concrete large-format floors, grey-washed oak in bedrooms, handleless matte-white "
                 "fronts, graphite wood, a charcoal wool sofa with chalk boucle armchairs, brushed steel + "
                 "matte black, a single yellow accent in the kids' room"),
    wall_color="#ebeae6",
    rooms={
        "living": dict(floor="minimal_concrete", paint="#e3e2de", skirting="#e3e2de"),
        "hall": dict(floor="minimal_concrete", paint="#e0dfdb"),
        "kitchen": dict(floor="minimal_concrete", paint="#ecebe7"),
        "bath_1": dict(floor="minimal_graphite", walls="minimal_white_stone"),
        "bath_2": dict(floor="minimal_graphite", walls="minimal_concrete"),
        "bedroom_1": dict(floor="minimal_grey_oak", paint="#e6e8ea", skirting="#e6e8ea"),
        "bedroom_2": dict(floor="minimal_grey_oak", paint="#c9c7c2", skirting="#c9c7c2"),
        "balcony": dict(floor="minimal_concrete"),
    },
    aprons={"ripple": {"living": "minimal_ripple_grey", "bedroom_2": "minimal_ripple_graphite"},
            "delicate_blues": "minimal_cloud_watercolor", "cream_marble": "minimal_white_quartz",
            "greige_stone": "minimal_graphite"},
    accent={"living": INK,                       # sofa / armchair plinth + feet matte black
            "bedroom_1": "#dcdddf",              # kids' duvet pale cool grey
            "bedroom_2": "#f0f0ee",              # master duvet chalk white against the graphite wall
            "bath_1": "#4a4a4c",                 # shower curb = graphite floor
            "*": G},
    metal={"*": STEEL},
    colors={
        "*": {"#b08d57": STEEL,                  # brass fittings -> brushed steel
              "#151515": INK,                    # track lights matte black
              "#fbfaf7": "#f4f4f2",              # sheers cool white
              "#d8cfc2": "#f2f2f0",              # table lamps white
              "#e6ddd0": "#f4f4f2",              # vessel sinks white (bath 2 overridden below)
              "#f6f6f6": "#f4f4f2"},             # sanitary white
        "living": {"#86694b": "#47484a",         # corner sofa charcoal wool (armchairs overridden: chalk boucle)
                   "#6f6152": "#cfcdc8",         # shag rug pale grey
                   "#313233": "#262628",         # coffee table soft black
                   "#3a3b3d": STEEL,             # side table steel
                   "#6b4a33": G,                 # slat TV wall graphite
                   "#6f5646": "#d6d6d3",         # drapes light grey
                   "#a08b78": W, "#8a5f3e": G, "#b88a5a": W,
                   "#c9a46a": INK,               # infinity pendant black
                   "#1e1e1e": INK,               # floor lamp black
                   "#cfcfcd": "#f0f0ee",         # desk white
                   "#6e6e70": "#2b2b2d",         # gaming chair black
                   "#ece6dc": "#e9e9e7",
                   "#8e9196": "#e3e2de"},        # AC = wall
        "hall": {"#6b4a33": G, "#8a5a3c": G, "#8a5f3e": G, "#a08b78": G, "#b88a5a": G,
                 "#3a3633": "#4a4a4c", "#3b3b3d": "#1f1f20", "#d9cfc0": "#f2f2f0",
                 "#5a3e2b": INK, "#e9e6df": "#f2f2f0"},   # shoes black + white
        "kitchen": {"#cfc2ad": W,                # base + tall units white handleless
                    "#7a5236": G,                # worktops, wall units, dining table graphite
                    "#b9a88c": W, "#3a3a3a": G,
                    "#b8a990": "#8a8b8d",        # chairs mid-grey wool felt
                    "#1e1e1e": INK,              # linear pendant black
                    "#f4f3f0": "#f6f6f4",        # place settings white porcelain
                    "#1c1c1c": "#2b2b2d",        # sink graphite composite
                    "#efe6d6": "#f3f3f1", "#e6e4df": "#ededeb"},
        "bath_1": {"#3f2a1c": "#333335", "#6b4428": "#333335", "#3a3a3a": STEEL,
                   "#d9cbb5": "#4c4c4e",         # towels graphite
                   "#c4b6a4": "#efefed"},
        "bath_2": {"#3f2a1c": W, "#3a3a3a": STEEL,
                   "#d9cbb5": "#efefed",         # towels white
                   "#e6ddd0": "#a3a09a",         # concrete vessel sink
                   "#c4b6a4": "#9d9a94"},
        "bedroom_1": {"#7f9fb0": "#d6d7d8",      # wardrobe doors pale grey (chair overridden: yellow)
                      "#efe6d6": "#f2f2f0",
                      "#8ea8b6": "#e0e1e2",      # drapes white-grey
                      "#5a7f96": "#bfc1c3",      # rug light grey
                      "#c9a77c": "#c4c6c8",      # desk, slats, handles light grey
                      "#2f6fb3": ACC,            # Baby Turi tag yellow
                      "#ede6dc": "#f3f3f1", "#ecebe8": "#d6d7d8",
                      "#3d6fa8": "#2b2b2d", "#5e8fbf": ACC,
                      "#8e9196": "#e6e8ea"},
        "bedroom_2": {"#a08b78": "#e4e4e2", "#8a5f3e": G, "#b88a5a": "#e4e4e2",
                      "#6b4a33": "#2e2e30",
                      "#6f5646": "#6e6f71",      # drapes charcoal
                      "#8a7764": "#b5b3ae",      # rug greige wool
                      "#ece6dc": "#4c4c4e", "#ecebe8": "#2e2e30",
                      "#8e9196": "#c9c7c2"},
        "balcony": {"#9a6b43": G, "#2f2f31": G, "#f2efe9": "#f4f4f2"},
    },
    items={
        "plush-armchair-living-1": {"color": "#e2e0db"},     # chalk boucle
        "plush-armchair-living-2": {"color": "#e2e0db"},
        "wardrobe-living-1": {"interior_color": GREY},
        "wardrobe-hall-1": {"interior_color": GREY},
        "wardrobe-master-suite-1": {"interior_color": GREY},
        "wardrobe-master-suite-2": {"interior_color": GREY},
        "tv-console-master-suite-1": {"interior_color": GREY},
        "wardrobe-bedroom-1-1": {"interior_color": "#f2f2f0", "front_color:1": "#f2f2f0"},
        "chair-bedroom-1-1": {"color": ACC},                 # kids' desk chair = the accent
        "serving-bowl-kitchen-1": {"color": G},
        "tall-cabinet-bathroom-1-1": {"interior_color": "#d9d8d4"},
        "tall-cabinet-master-bathroom-1": {"interior_color": "#d9d8d4"},
    },
    finishes={
        "minimal_concrete": dict(kind="stone", size=[1.20, 0.60], color="#9d9a94", color2="#8c8983",
                                 joint_color="#85827c", joint=0.0015, roughness=0.4,
                                 note="V5: pale concrete / microcement-look porcelain 120 x 60"),
        "minimal_grey_oak": dict(kind="parquet", size=[1.50, 0.22], direction="x", color="#bdb5aa",
                                 color2="#aaa296", joint_color="#6e675e", joint=0.0012, roughness=0.5,
                                 note="V5: grey-washed matt oak wide planks (bedrooms)"),
        "minimal_graphite": dict(kind="stone", size=[0.60, 1.20], color="#4a4a4c", color2="#3c3c3e",
                                 joint_color="#3a3a3c", joint=0.0015, roughness=0.35,
                                 note="V5: graphite stone-look 60 x 120 (bath floors, tub front)"),
        "minimal_white_stone": dict(kind="stone", size=[0.60, 1.20], color="#efefed", color2="#e0e0de",
                                    joint_color="#dcdcda", joint=0.0015, roughness=0.3,
                                    note="V5: matte chalk-white large-format 60 x 120 vertical (bath 1 walls)"),
        "minimal_white_quartz": dict(kind="marble", size=[1.80, 0.60], color="#f3f3f1", color2="#d4d4d4",
                                     joint_color="#e6e6e4", joint=0.001, roughness=0.2,
                                     note="V5: white quartz slab backsplash with faint grey veining"),
        "minimal_ripple_grey": dict(kind="ripple", size=[3.04, 2.70], color="#dddcd8", color2="#a9a8a4",
                                    joint_color="#e9e9e7", joint=0.0, roughness=0.85,
                                    note="V5: 'Ripple' in cool pale grey (living)"),
        "minimal_ripple_graphite": dict(kind="ripple", size=[3.04, 2.70], color="#4c4c4e", color2="#323234",
                                        joint_color="#4c4c4e", joint=0.0, roughness=0.85,
                                        note="V5: graphite ripple behind the master bed"),
        "minimal_cloud_watercolor": dict(kind="watercolor", size=[3.10, 2.70], color="#f3f3f1",
                                         color2="#a9b4bd", joint_color="#f3f3f1", joint=0.0, roughness=0.9,
                                         note="V5: soft grey-blue cloud mural (kids' bed wall)"),
    },
)
