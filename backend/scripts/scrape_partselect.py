"""
Generate 100 Realistic PartSelect Parts
50 Refrigerator + 50 Dishwasher Parts
Run: python generate_100_parts.py
"""

import json
import random


def generate_part_number():
    """Generate realistic part number (PS + 8 digits)"""
    return f"PS{random.randint(10000000, 99999999)}"


def select_models(count=4):
    """Select random compatible models"""
    models = [
        "WRF555SDFZ",
        "WRS325SDHZ",
        "WRS588FIHZ",
        "MFI2570FEZ",
        "GSS25GSHSS",
        "KSF26C6XYY",
        "WDT780SAEM1",
        "LFXS26973S",
        "RF28R7351SR",
        "FFHS2622MS",
        "GNE27JSMSS",
        "WRX735SDHZ",
        "KRFF507HPS",
        "KRMF706ESS",
        "PFE28KSKSS",
        "FGHB2868TF",
    ]
    return random.sample(models, min(count, len(models)))


def create_refrigerator_parts():
    """Generate 50 refrigerator parts"""
    parts = []
    brands = ["Whirlpool", "GE", "KitchenAid", "Samsung", "LG", "Frigidaire", "Maytag"]

    # Ice Maker Parts (8 parts)
    ice_maker_parts = [
        (
            "Ice Maker Assembly",
            124.99,
            "Complete ice maker assembly with motor, mold, and heating element",
            "Easy",
        ),
        (
            "Ice Maker Mold and Heater",
            59.99,
            "Ice mold tray with integrated heating element for releasing ice cubes",
            "Moderate",
        ),
        (
            "Ice Dispenser Auger Motor",
            79.99,
            "Motor that turns auger to dispense ice from bin",
            "Moderate",
        ),
        (
            "Ice Level Control Board",
            98.99,
            "Electronic control board that monitors ice level and controls production",
            "Moderate",
        ),
        (
            "Ice Maker Fill Tube",
            22.99,
            "Water fill tube that delivers water to ice maker mold",
            "Easy",
        ),
        (
            "Ice Bin Assembly",
            44.99,
            "Complete ice storage bin with auger and housing",
            "Easy",
        ),
        (
            "Ice Crusher Blade",
            32.99,
            "Blade assembly that crushes ice cubes for crushed ice dispensing",
            "Moderate",
        ),
        (
            "Ice Maker Water Valve",
            52.99,
            "Dedicated valve controlling water flow to ice maker",
            "Moderate",
        ),
    ]

    for name, price, desc, diff in ice_maker_parts:
        parts.append(
            {
                "part_number": generate_part_number(),
                "name": f"Refrigerator {name}",
                "category": "Refrigerator",
                "subcategory": "Ice Maker",
                "price": price,
                "description": desc,
                "compatible_models": select_models(),
                "brand": random.choice(brands),
                "image_url": f"https://www.partselect.com/images/{name.lower().replace(' ', '-')}.jpg",
                "installation_difficulty": diff,
                "installation_steps": [
                    "Disconnect power to refrigerator",
                    "Turn off water supply if applicable",
                    "Remove necessary panels or components",
                    "Disconnect wire harnesses and water lines",
                    "Remove old part using appropriate tools",
                    "Install new part ensuring proper alignment",
                    "Reconnect all electrical connections",
                    "Reconnect water lines if applicable",
                    "Reassemble any panels removed",
                    "Restore power and test operation",
                ],
                "common_symptoms": [
                    f"{name.split()[-1]} not working properly",
                    f"Ice maker malfunction",
                    f"Unusual noises from ice maker",
                    f"Ice production issues",
                ],
            }
        )

    # Water System Parts (8 parts)
    water_parts = [
        (
            "Water Inlet Valve",
            48.99,
            "Main water inlet valve controlling water flow to ice maker and dispenser",
            "Moderate",
        ),
        (
            "Water Filter Housing",
            39.99,
            "Housing unit that holds water filter cartridge",
            "Easy",
        ),
        (
            "Water Filter Cartridge",
            54.99,
            "Replacement water filter removing contaminants. Replace every 6 months",
            "Easy",
        ),
        (
            "Water Dispenser Actuator",
            27.99,
            "Push paddle activating water dispenser when pressed",
            "Easy",
        ),
        (
            "Water Reservoir Tank",
            64.99,
            "Internal water storage tank keeping chilled water ready",
            "Moderate",
        ),
        (
            "Water Line Assembly Kit",
            34.99,
            "Complete water line kit with tubing, fittings, and connectors",
            "Moderate",
        ),
        (
            "Water Dispenser Nozzle",
            19.99,
            "Dispenser outlet nozzle where water flows out",
            "Easy",
        ),
        (
            "Water Pressure Regulator",
            44.99,
            "Regulates water pressure to prevent component damage",
            "Moderate",
        ),
    ]

    for name, price, desc, diff in water_parts:
        parts.append(
            {
                "part_number": generate_part_number(),
                "name": f"Refrigerator {name}",
                "category": "Refrigerator",
                "subcategory": "Water System",
                "price": price,
                "description": desc,
                "compatible_models": select_models(),
                "brand": random.choice(brands),
                "image_url": f"https://www.partselect.com/images/{name.lower().replace(' ', '-')}.jpg",
                "installation_difficulty": diff,
                "installation_steps": [
                    "Turn off water supply to refrigerator",
                    "Unplug refrigerator from power outlet",
                    "Access component location",
                    "Disconnect water lines carefully",
                    "Disconnect electrical connections if present",
                    "Remove mounting hardware",
                    "Install new component",
                    "Reconnect water lines securely",
                    "Reconnect electrical connections",
                    "Test for leaks before final assembly",
                ],
                "common_symptoms": [
                    "Water dispenser not working",
                    "Water leaking",
                    "Low water pressure",
                    "Water quality issues",
                ],
            }
        )

    # Cooling System Parts (10 parts)
    cooling_parts = [
        (
            "Evaporator Fan Motor",
            72.99,
            "Fan motor circulating cold air throughout refrigerator and freezer",
            "Moderate",
        ),
        (
            "Condenser Fan Motor",
            68.99,
            "Fan motor cooling condenser coils located at bottom rear",
            "Moderate",
        ),
        (
            "Defrost Heater",
            36.99,
            "Heater melting frost off evaporator coils during defrost cycle",
            "Difficult",
        ),
        ("Defrost Timer", 52.99, "Controls automatic defrost cycle timing", "Moderate"),
        (
            "Defrost Thermostat",
            28.99,
            "Thermostat monitoring temperature during defrost cycle",
            "Moderate",
        ),
        (
            "Compressor Start Relay",
            31.99,
            "Relay helping compressor motor start",
            "Moderate",
        ),
        (
            "Overload Protector",
            24.99,
            "Protects compressor from overheating and electrical overload",
            "Easy",
        ),
        (
            "Evaporator Coils",
            189.99,
            "Coils where refrigerant absorbs heat to cool interior",
            "Difficult",
        ),
        (
            "Condenser Coils",
            124.99,
            "Coils releasing heat absorbed from refrigerator interior",
            "Moderate",
        ),
        ("Fan Blade", 18.99, "Blade attached to fan motor for air circulation", "Easy"),
    ]

    for name, price, desc, diff in cooling_parts:
        parts.append(
            {
                "part_number": generate_part_number(),
                "name": f"Refrigerator {name}",
                "category": "Refrigerator",
                "subcategory": "Cooling System",
                "price": price,
                "description": desc,
                "compatible_models": select_models(),
                "brand": random.choice(brands),
                "image_url": f"https://www.partselect.com/images/{name.lower().replace(' ', '-')}.jpg",
                "installation_difficulty": diff,
                "installation_steps": [
                    "Unplug refrigerator completely",
                    "Remove food and shelves as needed",
                    "Access component location",
                    "Take photos of wire connections",
                    "Disconnect electrical connections",
                    "Remove mounting hardware",
                    "Remove old component carefully",
                    "Install new component in correct position",
                    "Secure with mounting hardware",
                    "Reconnect electrical connections per photos",
                    "Reassemble and restore power",
                    "Allow 24 hours for proper cooling",
                ],
                "common_symptoms": [
                    "Refrigerator not cooling",
                    "Freezer too warm",
                    "Frost buildup",
                    "Unusual noises from compressor area",
                ],
            }
        )

    # Door Parts (8 parts)
    door_parts = [
        (
            "Door Gasket (Seal)",
            89.99,
            "Rubber seal keeping cold air inside refrigerator",
            "Easy",
        ),
        ("Door Handle", 76.99, "External handle for opening refrigerator door", "Easy"),
        (
            "Door Hinge",
            42.99,
            "Hinge allowing door to open and close smoothly",
            "Moderate",
        ),
        ("Door Shelf Bin", 28.99, "Plastic bin on door for storing items", "Easy"),
        ("Door Cam", 15.99, "Plastic cam helping door close automatically", "Easy"),
        ("Door Closer", 34.99, "Mechanism ensuring door closes completely", "Moderate"),
        (
            "Door Switch",
            22.99,
            "Switch turning off interior light when door closes",
            "Easy",
        ),
        (
            "Mullion",
            58.99,
            "Divider between fresh food and freezer compartments",
            "Moderate",
        ),
    ]

    for name, price, desc, diff in door_parts:
        parts.append(
            {
                "part_number": generate_part_number(),
                "name": f"Refrigerator {name}",
                "category": "Refrigerator",
                "subcategory": "Door Parts",
                "price": price,
                "description": desc,
                "compatible_models": select_models(),
                "brand": random.choice(brands),
                "image_url": f"https://www.partselect.com/images/{name.lower().replace(' ', '-')}.jpg",
                "installation_difficulty": diff,
                "installation_steps": [
                    "Open refrigerator door fully",
                    "Remove any covers or caps as needed",
                    "Access mounting hardware",
                    "Remove screws or clips holding part",
                    "Remove old part carefully",
                    "Position new part correctly",
                    "Secure with mounting hardware",
                    "Replace any covers or caps",
                    "Test door operation and seal",
                ],
                "common_symptoms": [
                    "Door not closing properly",
                    "Door sagging",
                    "Cold air leaking",
                    "Door component broken or loose",
                ],
            }
        )

    # Storage Parts (6 parts)
    storage_parts = [
        ("Glass Shelf", 94.99, "Tempered glass shelf for storing food items", "Easy"),
        ("Crisper Drawer", 58.99, "Drawer keeping fruits and vegetables fresh", "Easy"),
        (
            "Meat Drawer",
            64.99,
            "Drawer for storing meat at optimal temperature",
            "Easy",
        ),
        ("Drawer Slide Rail", 29.99, "Rail allowing drawer to slide smoothly", "Easy"),
        ("Shelf Support", 16.99, "Bracket supporting glass shelves", "Easy"),
        ("Deli Drawer", 52.99, "Drawer for storing deli meats and cheeses", "Easy"),
    ]

    for name, price, desc, diff in storage_parts:
        parts.append(
            {
                "part_number": generate_part_number(),
                "name": f"Refrigerator {name}",
                "category": "Refrigerator",
                "subcategory": "Storage",
                "price": price,
                "description": desc,
                "compatible_models": select_models(),
                "brand": random.choice(brands),
                "image_url": f"https://www.partselect.com/images/{name.lower().replace(' ', '-')}.jpg",
                "installation_difficulty": diff,
                "installation_steps": [
                    "Remove contents from drawer or shelf",
                    "Fully extend or remove drawer if applicable",
                    "Lift front edge slightly",
                    "Pull toward you to remove",
                    "For new part, align with tracks or supports",
                    "Slide into position",
                    "Lower into place",
                    "Test smooth operation",
                ],
                "common_symptoms": [
                    f"{name} broken or cracked",
                    "Drawer not sliding properly",
                    "Shelf support damaged",
                    "Storage component needs replacement",
                ],
            }
        )

    # Lighting Parts (4 parts)
    lighting_parts = [
        (
            "LED Light Bulb",
            24.99,
            "Energy-efficient LED bulb illuminating refrigerator interior",
            "Easy",
        ),
        ("Light Socket", 18.99, "Socket holding light bulb in place", "Easy"),
        (
            "Light Housing",
            32.99,
            "Complete housing assembly for interior lighting",
            "Moderate",
        ),
        (
            "Light Switch",
            16.99,
            "Door-activated switch controlling interior lights",
            "Easy",
        ),
    ]

    for name, price, desc, diff in lighting_parts:
        parts.append(
            {
                "part_number": generate_part_number(),
                "name": f"Refrigerator {name}",
                "category": "Refrigerator",
                "subcategory": "Lighting",
                "price": price,
                "description": desc,
                "compatible_models": select_models(),
                "brand": random.choice(brands),
                "image_url": f"https://www.partselect.com/images/{name.lower().replace(' ', '-')}.jpg",
                "installation_difficulty": diff,
                "installation_steps": [
                    "Unplug refrigerator or turn off circuit breaker",
                    "Locate light assembly",
                    "Remove light cover if present",
                    "For bulbs: twist counterclockwise to remove",
                    "For fixtures: disconnect wires and remove screws",
                    "Install new component",
                    "Reconnect electrical connections",
                    "Replace light cover",
                    "Restore power and test",
                ],
                "common_symptoms": [
                    "Interior light not working",
                    "Light flickering",
                    "Dim lighting",
                    "Light stays on when door closed",
                ],
            }
        )

    # Controls Parts (6 parts)
    controls_parts = [
        (
            "Temperature Control Thermostat",
            46.99,
            "Thermostat controlling refrigerator temperature",
            "Moderate",
        ),
        (
            "Electronic Control Board",
            164.99,
            "Main circuit board controlling all refrigerator functions",
            "Difficult",
        ),
        (
            "Dispenser Control Board",
            128.99,
            "Control board managing dispenser functions",
            "Moderate",
        ),
        (
            "Display Control Board",
            142.99,
            "User interface display and control panel",
            "Moderate",
        ),
        (
            "Damper Control",
            54.99,
            "Controls airflow between freezer and refrigerator",
            "Moderate",
        ),
        (
            "Adaptive Defrost Control Board",
            118.99,
            "Advanced control monitoring defrost cycles",
            "Difficult",
        ),
    ]

    for name, price, desc, diff in controls_parts:
        parts.append(
            {
                "part_number": generate_part_number(),
                "name": f"Refrigerator {name}",
                "category": "Refrigerator",
                "subcategory": "Controls",
                "price": price,
                "description": desc,
                "compatible_models": select_models(),
                "brand": random.choice(brands),
                "image_url": f"https://www.partselect.com/images/{name.lower().replace(' ', '-')}.jpg",
                "installation_difficulty": diff,
                "installation_steps": [
                    "Disconnect power to refrigerator",
                    "Remove control panel cover",
                    "Take clear photos of all wire connections",
                    "Label wires if needed",
                    "Disconnect wire harnesses from control",
                    "Remove control board mounting screws",
                    "Remove old control carefully",
                    "Install new control in same position",
                    "Reconnect all wire harnesses per photos",
                    "Secure with mounting screws",
                    "Replace control panel cover",
                    "Restore power and test all functions",
                ],
                "common_symptoms": [
                    "Temperature control not working",
                    "Display not functioning",
                    "Refrigerator not responding to settings",
                    "Error codes displayed",
                ],
            }
        )

    return parts


def create_dishwasher_parts():
    """Generate 50 dishwasher parts"""
    parts = []
    brands = [
        "Whirlpool",
        "GE",
        "KitchenAid",
        "Bosch",
        "Samsung",
        "LG",
        "Frigidaire",
        "Maytag",
    ]
    dw_models = [
        "WDT780SAEM1",
        "KDFE104HPS",
        "WDF520PADM",
        "KDTM354ESS",
        "SHX3AR75UC",
        "LDT5665ST",
        "FFCD2418US",
        "MDB4949SKZ",
        "DW80R9950US",
        "WDT750SAKZ",
        "KDPM354GPS",
        "GDT695SSJSS",
    ]

    def select_dw_models(count=4):
        return random.sample(dw_models, min(count, len(dw_models)))

    # Wash System Parts (10 parts)
    wash_parts = [
        (
            "Lower Spray Arm",
            28.99,
            "Spray arm distributing water to lower rack dishes",
            "Easy",
        ),
        (
            "Upper Spray Arm",
            34.99,
            "Spray arm distributing water to upper rack dishes",
            "Easy",
        ),
        (
            "Middle Spray Arm",
            38.99,
            "Third spray arm for enhanced cleaning in middle zone",
            "Easy",
        ),
        (
            "Spray Arm Bearing",
            14.99,
            "Bearing allowing spray arm to rotate freely",
            "Easy",
        ),
        (
            "Spray Arm Hub",
            18.99,
            "Central hub connecting spray arm to water supply",
            "Easy",
        ),
        (
            "Wash Impeller",
            32.99,
            "Impeller forcing water through spray arms",
            "Moderate",
        ),
        (
            "Wash Pump Housing",
            56.99,
            "Housing containing wash pump components",
            "Moderate",
        ),
        (
            "Spray Arm Seal",
            12.99,
            "Seal preventing water leaks at spray arm connection",
            "Easy",
        ),
        (
            "Water Distribution Tube",
            42.99,
            "Tube distributing water to upper spray arm",
            "Moderate",
        ),
        ("Spray Arm Nut", 8.99, "Nut securing spray arm to mounting post", "Easy"),
    ]

    for name, price, desc, diff in wash_parts:
        parts.append(
            {
                "part_number": generate_part_number(),
                "name": f"Dishwasher {name}",
                "category": "Dishwasher",
                "subcategory": "Wash System",
                "price": price,
                "description": desc,
                "compatible_models": select_dw_models(),
                "brand": random.choice(brands),
                "image_url": f"https://www.partselect.com/images/dw-{name.lower().replace(' ', '-')}.jpg",
                "installation_difficulty": diff,
                "installation_steps": [
                    "Open dishwasher door fully",
                    "Remove dish racks as needed",
                    "Access component location",
                    "Remove old part (twist, lift, or unscrew)",
                    "Clean mounting area",
                    "Install new part ensuring proper fit",
                    "Secure according to type (twist, clip, or screw)",
                    "Test rotation or operation if applicable",
                    "Replace dish racks",
                ],
                "common_symptoms": [
                    "Dishes not getting clean",
                    "Poor water spray",
                    "Spray arm not rotating",
                    "Incomplete wash cycle",
                ],
            }
        )

    # Pump Parts (8 parts)
    pump_parts = [
        (
            "Pump and Motor Assembly",
            189.99,
            "Complete pump assembly circulating and draining water",
            "Difficult",
        ),
        ("Drain Pump", 78.99, "Pump removing waste water from dishwasher", "Moderate"),
        (
            "Circulation Pump",
            142.99,
            "Pump circulating water during wash cycle",
            "Difficult",
        ),
        ("Pump Impeller", 24.99, "Rotating blade inside pump moving water", "Moderate"),
        ("Pump Seal Kit", 18.99, "Seals preventing water leaks from pump", "Moderate"),
        ("Drain Impeller", 16.99, "Impeller in drain pump removing water", "Moderate"),
        (
            "Pump Housing",
            64.99,
            "Housing containing pump motor and impeller",
            "Difficult",
        ),
        (
            "Chopper Blade",
            19.99,
            "Blade grinding food particles before draining",
            "Easy",
        ),
    ]

    for name, price, desc, diff in pump_parts:
        parts.append(
            {
                "part_number": generate_part_number(),
                "name": f"Dishwasher {name}",
                "category": "Dishwasher",
                "subcategory": "Pump",
                "price": price,
                "description": desc,
                "compatible_models": select_dw_models(),
                "brand": random.choice(brands),
                "image_url": f"https://www.partselect.com/images/dw-{name.lower().replace(' ', '-')}.jpg",
                "installation_difficulty": diff,
                "installation_steps": [
                    "Turn off power to dishwasher",
                    "Turn off water supply",
                    "Remove lower access panel",
                    "Place towels to catch water",
                    "Disconnect hoses and electrical connections",
                    "Remove pump mounting hardware",
                    "Remove old pump or component",
                    "Install new component",
                    "Reconnect all connections securely",
                    "Test for leaks before final assembly",
                ],
                "common_symptoms": [
                    "Dishwasher won't drain",
                    "Dishwasher won't fill",
                    "Grinding or humming noise",
                    "Water standing in bottom",
                ],
            }
        )

    # Door Parts (8 parts)
    door_parts = [
        (
            "Door Latch Assembly",
            54.99,
            "Latch keeping door closed and activating door switch",
            "Moderate",
        ),
        ("Door Gasket", 41.99, "Seal preventing water leaks from door", "Easy"),
        (
            "Door Handle",
            38.99,
            "Handle for opening and closing dishwasher door",
            "Easy",
        ),
        ("Door Hinge", 32.99, "Hinge allowing door to open and close", "Moderate"),
        ("Door Spring", 22.99, "Spring assisting door opening and closing", "Moderate"),
        ("Door Strike", 15.99, "Strike plate door latch engages with", "Easy"),
        ("Door Cable", 28.99, "Cable connecting door to spring mechanism", "Moderate"),
        (
            "Door Balance Link Kit",
            34.99,
            "Kit balancing door weight for smooth operation",
            "Moderate",
        ),
    ]

    for name, price, desc, diff in door_parts:
        parts.append(
            {
                "part_number": generate_part_number(),
                "name": f"Dishwasher {name}",
                "category": "Dishwasher",
                "subcategory": "Door Parts",
                "price": price,
                "description": desc,
                "compatible_models": select_dw_models(),
                "brand": random.choice(brands),
                "image_url": f"https://www.partselect.com/images/dw-{name.lower().replace(' ', '-')}.jpg",
                "installation_difficulty": diff,
                "installation_steps": [
                    "Turn off power to dishwasher",
                    "Open door carefully",
                    "Remove inner door panel screws",
                    "Separate inner panel from outer door",
                    "Disconnect wire harness if present",
                    "Remove old component",
                    "Install new component",
                    "Reconnect electrical connections",
                    "Reassemble door panel",
                    "Test door operation",
                ],
                "common_symptoms": [
                    "Door won't stay closed",
                    "Door won't latch",
                    "Water leaking from door",
                    "Door difficult to open or close",
                ],
            }
        )

    # Heating Parts (6 parts)
    heating_parts = [
        (
            "Heating Element",
            42.99,
            "Element heating water during wash and drying dishes",
            "Moderate",
        ),
        (
            "High Limit Thermostat",
            24.99,
            "Safety thermostat preventing overheating",
            "Moderate",
        ),
        (
            "Thermal Fuse",
            16.99,
            "Fuse protecting heating element from overheating",
            "Easy",
        ),
        (
            "Heating Element Bracket",
            12.99,
            "Bracket securing heating element in place",
            "Easy",
        ),
        (
            "Rinse Aid Heater",
            38.99,
            "Small heater warming rinse aid dispenser",
            "Moderate",
        ),
        (
            "Drying Fan Assembly",
            68.99,
            "Fan circulating hot air for faster drying",
            "Moderate",
        ),
    ]

    for name, price, desc, diff in heating_parts:
        parts.append(
            {
                "part_number": generate_part_number(),
                "name": f"Dishwasher {name}",
                "category": "Dishwasher",
                "subcategory": "Heating",
                "price": price,
                "description": desc,
                "compatible_models": select_dw_models(),
                "brand": random.choice(brands),
                "image_url": f"https://www.partselect.com/images/dw-{name.lower().replace(' ', '-')}.jpg",
                "installation_difficulty": diff,
                "installation_steps": [
                    "Turn off power completely",
                    "Remove lower dish rack",
                    "Remove spray arm if blocking access",
                    "Locate component at bottom of tub",
                    "Disconnect wire terminals",
                    "Remove mounting hardware",
                    "Remove old component",
                    "Install new component",
                    "Reconnect electrical connections",
                    "Test with multimeter if applicable",
                    "Reassemble and test",
                ],
                "common_symptoms": [
                    "Dishes not drying",
                    "Water not heating",
                    "Dishes still wet after cycle",
                    "Dishwasher not heating water",
                ],
            }
        )

    # Accessories Parts (8 parts)
    accessories_parts = [
        ("Silverware Basket", 18.99, "Basket holding utensils during wash", "Easy"),
        ("Upper Dishrack", 89.99, "Complete upper rack assembly for dishes", "Easy"),
        ("Lower Dishrack", 124.99, "Complete lower rack assembly for dishes", "Easy"),
        ("Dishrack Roller", 12.99, "Wheel allowing rack to slide smoothly", "Easy"),
        ("Rack Adjuster", 16.99, "Mechanism adjusting rack height", "Easy"),
        ("Tine Row", 24.99, "Row of tines for holding dishes in place", "Easy"),
        ("Cup Shelf", 28.99, "Flip-down shelf for cups and small items", "Easy"),
        ("Cutlery Basket", 22.99, "Alternative basket design for utensils", "Easy"),
    ]

    for name, price, desc, diff in accessories_parts:
        parts.append(
            {
                "part_number": generate_part_number(),
                "name": f"Dishwasher {name}",
                "category": "Dishwasher",
                "subcategory": "Accessories",
                "price": price,
                "description": desc,
                "compatible_models": select_dw_models(),
                "brand": random.choice(brands),
                "image_url": f"https://www.partselect.com/images/dw-{name.lower().replace(' ', '-')}.jpg",
                "installation_difficulty": diff,
                "installation_steps": [
                    "Open dishwasher door",
                    "Remove old component by lifting or sliding",
                    "For racks: note position and remove from rails",
                    "For accessories: detach from existing rack",
                    "Install new component in same position",
                    "For racks: slide onto rails ensuring smooth glide",
                    "Test movement and stability",
                    "Adjust as needed for proper fit",
                ],
                "common_symptoms": [
                    f"{name} broken or damaged",
                    "Component missing",
                    "Dishes falling through rack",
                    "Rack not sliding properly",
                ],
            }
        )

    # Controls Parts (6 parts)
    controls_parts = [
        (
            "Control Board",
            164.99,
            "Main electronic control board managing all functions",
            "Difficult",
        ),
        (
            "User Interface Control",
            128.99,
            "Control panel with buttons and display",
            "Moderate",
        ),
        ("Touchpad", 89.99, "Touch-sensitive control panel", "Moderate"),
        ("Door Switch", 26.99, "Switch detecting if door is closed", "Easy"),
        (
            "Float Switch",
            32.99,
            "Switch preventing dishwasher from overfilling",
            "Moderate",
        ),
        (
            "Pressure Switch",
            38.99,
            "Switch detecting water level during cycle",
            "Moderate",
        ),
    ]

    for name, price, desc, diff in controls_parts:
        parts.append(
            {
                "part_number": generate_part_number(),
                "name": f"Dishwasher {name}",
                "category": "Dishwasher",
                "subcategory": "Controls",
                "price": price,
                "description": desc,
                "compatible_models": select_dw_models(),
                "brand": random.choice(brands),
                "image_url": f"https://www.partselect.com/images/dw-{name.lower().replace(' ', '-')}.jpg",
                "installation_difficulty": diff,
                "installation_steps": [
                    "Turn off power to dishwasher",
                    "Remove control panel screws",
                    "Carefully pull panel forward",
                    "Take photos of all wire connections",
                    "Label wires before disconnecting",
                    "Disconnect wire harnesses from control",
                    "Remove control mounting screws",
                    "Install new control",
                    "Reconnect all wires per photos",
                    "Secure control with mounting screws",
                    "Reassemble control panel",
                    "Restore power and test functions",
                ],
                "common_symptoms": [
                    "Buttons not responding",
                    "Display not working",
                    "Dishwasher won't start",
                    "Cycle not advancing",
                    "Error codes displayed",
                ],
            }
        )

    # Water System Parts (4 parts)
    water_system_parts = [
        (
            "Water Inlet Valve",
            56.99,
            "Valve controlling water flow into dishwasher",
            "Moderate",
        ),
        ("Drain Hose", 22.99, "Hose carrying waste water to drain", "Moderate"),
        ("Fill Hose", 18.99, "Hose carrying fresh water to tub", "Moderate"),
        (
            "Rinse Aid Dispenser",
            28.99,
            "Dispenser releasing rinse agent during cycle",
            "Easy",
        ),
    ]

    for name, price, desc, diff in water_system_parts:
        parts.append(
            {
                "part_number": generate_part_number(),
                "name": f"Dishwasher {name}",
                "category": "Dishwasher",
                "subcategory": "Water System",
                "price": price,
                "description": desc,
                "compatible_models": select_dw_models(),
                "brand": random.choice(brands),
                "image_url": f"https://www.partselect.com/images/dw-{name.lower().replace(' ', '-')}.jpg",
                "installation_difficulty": diff,
                "installation_steps": [
                    "Turn off power and water supply",
                    "Remove lower access panel or pull dishwasher out",
                    "Place towels to catch water",
                    "Disconnect water line or hose",
                    "Disconnect electrical connection if present",
                    "Remove mounting brackets or clamps",
                    "Remove old component",
                    "Install new component with new clamps",
                    "Reconnect water lines securely",
                    "Reconnect electrical connections",
                    "Turn on water slowly and check for leaks",
                    "Restore power and test",
                ],
                "common_symptoms": [
                    "Dishwasher won't fill with water",
                    "Water leaking",
                    "Spots on dishes",
                    "Rinse aid not dispensing",
                ],
            }
        )

    return parts


def main():
    """Generate and save 100 parts"""
    print("Generating 100 PartSelect Parts...")
    print("=" * 50)

    # Generate parts
    refrigerator_parts = create_refrigerator_parts()
    dishwasher_parts = create_dishwasher_parts()

    # Combine
    all_parts = refrigerator_parts + dishwasher_parts

    print(f"\n✅ Generated {len(all_parts)} parts:")
    print(f"   - Refrigerator: {len(refrigerator_parts)} parts")
    print(f"   - Dishwasher: {len(dishwasher_parts)} parts")

    # Count by subcategory
    print("\n📊 Breakdown by subcategory:")
    from collections import Counter

    ref_subcats = Counter(p["subcategory"] for p in refrigerator_parts)
    print("\n   Refrigerator:")
    for subcat, count in sorted(ref_subcats.items()):
        print(f"      - {subcat}: {count} parts")

    dw_subcats = Counter(p["subcategory"] for p in dishwasher_parts)
    print("\n   Dishwasher:")
    for subcat, count in sorted(dw_subcats.items()):
        print(f"      - {subcat}: {count} parts")

    # Save to JSON
    output_file = "parts_data.json"
    with open(output_file, "w") as f:
        json.dump(all_parts, f, indent=2)

    print(f"\n💾 Saved to: {output_file}")
    print(f"📦 File size: {len(json.dumps(all_parts)) / 1024:.1f} KB")
    print("\n✨ Done! Ready to import into your database.")
    print(f"\nNext steps:")
    print(f"1. Replace backend/parts_data.json with {output_file}")
    print(f"2. Run: python database/initialize_db.py")
    print(f"3. Restart backend")


if __name__ == "__main__":
    main()
