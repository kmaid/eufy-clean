"""Constants for the Eufy Clean Vacuum integration."""

DOMAIN = "eufy_clean_vacuum"

# Configuration
CONF_OPENUDID = "openudid"

# Legacy DPS keys
LEGACY_DPS_MAP = {
    "PLAY_PAUSE": "2",
    "DIRECTION": "3",
    "WORK_MODE": "5",
    "WORK_STATUS": "15",
    "CLEANING_PARAMETERS": "154",
    "CLEANING_STATISTICS": "167",
    "ACCESSORIES_STATUS": "168",
    "GO_HOME": "101",
    "CLEAN_SPEED": "102",
    "FIND_ROBOT": "103",
    "BATTERY_LEVEL": "104",
    "ERROR_CODE": "106",
}

# Novel DPS keys (X10 Pro Omni and newer models)
NOVEL_DPS_MAP = {
    "PLAY_PAUSE": "152",
    "DIRECTION": "155",
    "WORK_MODE": "153",
    "WORK_STATUS": "153",
    "CLEANING_PARAMETERS": "154",
    "CLEANING_STATISTICS": "167",
    "ACCESSORIES_STATUS": "168",
    "GO_HOME": "173",
    "CLEAN_SPEED": "158",
    "FIND_ROBOT": "160",
    "BATTERY_LEVEL": "163",
    "ERROR_CODE": "177",
}

# Work status mapping
WORK_STATUS_MAP = {
    "sleeping": "stopped",
    "standby": "docked",
    "recharge": "docked",
    "running": "cleaning",
    "cleaning": "cleaning",
    "spot": "spot_cleaning",
    "completed": "docked",
    "charging": "charging",
    "sleep": "stopped",
    "go_home": "docked",
    "fault": "stopped",
}

# Vacuum states
VACUUM_STATE = {
    "STOPPED": "stopped",
    "CLEANING": "cleaning",
    "SPOT_CLEANING": "spot_cleaning",
    "DOCKED": "docked",
    "CHARGING": "charging",
}

# Clean speed modes
CLEAN_SPEED = {
    "NO_SUCTION": "No_suction",
    "STANDARD": "Standard",
    "QUIET": "Quiet",
    "TURBO": "Turbo",
    "BOOST_IQ": "Boost_IQ",
    "MAX": "Max",
}

# Novel clean speed modes
NOVEL_CLEAN_SPEED = [
    CLEAN_SPEED["QUIET"],
    CLEAN_SPEED["STANDARD"],
    CLEAN_SPEED["TURBO"],
    CLEAN_SPEED["MAX"],
]

# Legacy clean speed modes
LEGACY_CLEAN_SPEED = [
    CLEAN_SPEED["NO_SUCTION"],
    CLEAN_SPEED["BOOST_IQ"],
]

# Work modes
WORK_MODE = {
    "AUTO": "auto",
    "NO_SWEEP": "Nosweep",
    "SMALL_ROOM": "SmallRoom",
    "ROOM": "room",
    "ZONE": "zone",
    "EDGE": "Edge",
    "SPOT": "Spot",
}

# Control commands
CONTROL = {
    "START_AUTO_CLEAN": 0,
    "START_SELECT_ROOMS_CLEAN": 1,
    "START_SELECT_ZONES_CLEAN": 2,
    "START_SPOT_CLEAN": 3,
    "START_GOTO_CLEAN": 4,
    "START_RC_CLEAN": 5,
    "START_GOHOME": 6,
    "START_SCHEDULE_AUTO_CLEAN": 7,
    "START_SCHEDULE_ROOMS_CLEAN": 8,
    "START_FAST_MAPPING": 9,
    "START_GOWASH": 10,
    "STOP_TASK": 12,
    "PAUSE_TASK": 13,
    "RESUME_TASK": 14,
    "STOP_GOHOME": 15,
    "STOP_RC_CLEAN": 16,
    "STOP_GOWASH": 17,
    "STOP_SMART_FOLLOW": 18,
    "START_GLOBAL_CRUISE": 20,
    "START_POINT_CRUISE": 21,
    "START_ZONES_CRUISE": 22,
    "START_SCHEDULE_CRUISE": 23,
    "START_SCENE_CLEAN": 24,
    "START_MAPPING_THEN_CLEAN": 25,
}

# Error codes
ERROR_CODES = {
    0: "NONE",
    1: "CRASH BUFFER STUCK",
    2: "WHEEL STUCK",
    3: "SIDE BRUSH STUCK",
    4: "ROLLING BRUSH STUCK",
    5: "HOST TRAPPED CLEAR OBST",
    6: "MACHINE TRAPPED MOVE",
    7: "WHEEL OVERHANGING",
    8: "POWER LOW SHUTDOWN",
    13: "HOST TILTED",
    14: "NO DUST BOX",
    17: "FORBIDDEN AREA DETECTED",
    18: "LASER COVER STUCK",
    19: "LASER SENSOR STUCK",
    20: "LASER BLOCKED",
    21: "DOCK FAILED",
    26: "POWER APPOINT START FAIL",
    31: "SUCTION PORT OBSTRUCTION",
    32: "WIPE HOLDER MOTOR STUCK",
    33: "WIPING BRACKET MOTOR STUCK",
    39: "POSITIONING FAIL CLEAN END",
    40: "MOP CLOTH DISLODGED",
    41: "AIRDRYER HEATER ABNORMAL",
    50: "MACHINE ON CARPET",
    51: "CAMERA BLOCK",
    52: "UNABLE LEAVE STATION",
    55: "EXPLORING STATION FAIL",
    70: "CLEAN DUST COLLECTOR",
    71: "WALL SENSOR FAIL",
    72: "ROBOVAC LOW WATER",
    73: "DIRTY TANK FULL",
    74: "CLEAN WATER LOW",
    75: "WATER TANK ABSENT",
    76: "CAMERA ABNORMAL",
    77: "3D TOF ABNORMAL",
    78: "ULTRASONIC ABNORMAL",
    79: "CLEAN TRAY NOT INSTALLED",
    80: "ROBOVAC COMM FAIL",
    81: "SEWAGE TANK LEAK",
    82: "CLEAN TRAY NEEDS CLEAN",
    83: "POOR CHARGING CONTACT",
    101: "BATTERY ABNORMAL",
    102: "WHEEL MODULE ABNORMAL",
    103: "SIDE BRUSH ABNORMAL",
    104: "FAN ABNORMAL",
    105: "ROLLER BRUSH MOTOR ABNORMAL",
    106: "HOST PUMP ABNORMAL",
    107: "LASER SENSOR ABNORMAL",
    111: "ROTATION MOTOR ABNORMAL",
    112: "LIFT MOTOR ABNORMAL",
    113: "WATER SPRAY ABNORMAL",
    114: "WATER PUMP ABNORMAL",
    117: "ULTRASONIC ABNORMAL",
    119: "WIFI BLUETOOTH ABNORMAL",
}

# Device models
X_SERIES = [
    "T2262",  # RoboVac X8
    "T2261",  # RoboVac X8 Hybrid
    "T2266",  # RoboVac X8 Pro
    "T2276",  # RoboVac X8 Pro SES
    "T2320",  # RoboVac X9 Pro
    "T2351",  # RoboVac X10 Pro Omni
]

G_SERIES = [
    "T2210",  # RoboVac G50
    "T2250",  # RoboVac G30
    "T2251",  # RoboVac G30
    "T2252",  # RoboVac G30 Verge
    "T2253",  # RoboVac G30 Hybrid
    "T2254",  # RoboVac G35
    "T2255",  # RoboVac G40
    "T2256",  # RoboVac G40 Hybrid
    "T2257",  # RoboVac G20
    "T2258",  # RoboVac G20 Hybrid
    "T2259",  # RoboVac G32
    "T2270",  # RoboVac G35+
    "T2272",  # RoboVac G30+ SES
    "T2273",  # RoboVac G40 Hybrid+
    "T2277",  # RoboVac G30+ SES
]
