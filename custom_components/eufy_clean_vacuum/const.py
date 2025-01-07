"""Constants for the Eufy Clean Vacuum integration."""

from homeassistant.components.vacuum import VacuumActivity

# Basic state mapping
EUFY_CLEAN_GET_STATE = {
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
    "fault": "stopped"
}

EUFY_CLEAN_VACUUMCLEANER_STATE = {
    "STOPPED": "stopped",
    "CLEANING": "cleaning",
    "SPOT_CLEANING": "spot_cleaning",
    "DOCKED": "docked",
    "CHARGING": "charging"
}

# Clean speed settings
EUFY_CLEAN_CLEAN_SPEED = {
    "NO_SUCTION": "No_suction",
    "STANDARD": "Standard",
    "QUIET": "Quiet",
    "TURBO": "Turbo",
    "BOOST_IQ": "Boost_IQ",
    "MAX": "Max"
}

EUFY_CLEAN_NOVEL_CLEAN_SPEED = [
    EUFY_CLEAN_CLEAN_SPEED["QUIET"],
    EUFY_CLEAN_CLEAN_SPEED["STANDARD"],
    EUFY_CLEAN_CLEAN_SPEED["TURBO"],
    EUFY_CLEAN_CLEAN_SPEED["MAX"]
]

EUFY_CLEAN_LEGACY_CLEAN_SPEED = [
    EUFY_CLEAN_CLEAN_SPEED["NO_SUCTION"],
    EUFY_CLEAN_CLEAN_SPEED["BOOST_IQ"]
]

EUFY_CLEAN_GET_CLEAN_SPEED = {
    "no_suction": "No Suction",
    "standard": "Standard",
    "quiet": "Quiet",
    "turbo": "Turbo",
    "boost_iq": "Boost IQ",
    "max": "Max"
}

# Work status states with detailed comments
EUFY_CLEAN_WORK_STATUS = {
    # Cleaning
    "RUNNING": "Running",
    # In the dock, charging
    "CHARGING": "Charging",
    # Not in the dock, paused
    "STAND_BY": "standby",
    # Not in the dock - goes into this state after being paused for a while
    "SLEEPING": "Sleeping",
    # Going home because battery is depleted
    "RECHARGE_NEEDED": "Recharge",
    "RECHARGE": "Recharge",
    # In the dock, full charged
    "COMPLETED": "Completed",
    "STANDBY": "Standby",
    "SLEEP": "Sleep",
    "FAULT": "Fault",
    "FAST_MAPPING": "Fast Mapping",
    "CLEANING": "Cleaning",
    "REMOTE_CTRL": "Remote Ctrl",
    "GO_HOME": "Go Home",
    "CRUISIING": "Cruising",
}

# Work modes
EUFY_CLEAN_WORK_MODE = {
    "AUTO": "auto",
    "NO_SWEEP": "Nosweep",
    "SMALL_ROOM": "SmallRoom",
    "ROOM": "room",
    "ZONE": "zone",
    "EDGE": "Edge",
    "SPOT": "Spot"
}

# Control commands
EUFY_CLEAN_CONTROL = {
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
    "START_MAPPING_THEN_CLEAN": 25
}

# Error codes
EUFY_CLEAN_ERROR_CODES = {
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
    119: "WIFI BLUETOOTH ABNORMAL"
}

# Device models from devices.constants.ts
EUFY_CLEAN_DEVICES = {
    "T1250": "RoboVac 35C",
    "T2103": "RoboVac 11C",
    "T2117": "RoboVac 35C",
    "T2118": "RoboVac 30C",
    "T2119": "RoboVac 11S",
    "T2120": "RoboVac 15C MAX",
    "T2123": "RoboVac 25C",
    "T2128": "RoboVac 15C MAX",
    "T2130": "RoboVac 30C MAX",
    "T2132": "RoboVac 25C",
    "T2150": "RoboVac G10 Hybrid",
    "T2181": "RoboVac LR30 Hybrid+",
    "T2182": "RoboVac LR35 Hybrid+",
    "T2190": "RoboVac L70 Hybrid",
    "T2192": "RoboVac LR20",
    "T2193": "RoboVac LR30 Hybrid",
    "T2194": "RoboVac LR35 Hybrid",
    "T2210": "Robovac G50",
    "T2250": "Robovac G30",
    "T2251": "RoboVac G30",
    "T2252": "RoboVac G30 Verge",
    "T2253": "RoboVac G30 Hybrid",
    "T2254": "RoboVac G35",
    "T2255": "Robovac G40",
    "T2256": "RoboVac G40 Hybrid",
    "T2257": "RoboVac G20",
    "T2258": "RoboVac G20 Hybrid",
    "T2259": "RoboVac G32",
    "T2261": "RoboVac X8 Hybrid",
    "T2262": "RoboVac X8",
    "T2266": "Robovac X8 Pro",
    "T2267": "RoboVac L60",
    "T2268": "Robovac L60 Hybrid",
    "T2270": "RoboVac G35+",
    "T2272": "Robovac G30+ SES",
    "T2273": "RoboVac G40 Hybrid+",
    "T2276": "Robovac X8 Pro SES",
    "T2277": "Robovac L60 SES",
    "T2278": "Robovac L60 Hybrid SES",
    "T2320": "Robovac X9 Pro",
    "T2351": "Robovac X10 Pro Omni",
    "T2080": "Robovac S1"
}

# Device series groupings
EUFY_CLEAN_X_SERIES = [
    "T2262",
    "T2261",
    "T2266",
    "T2276",
    "T2320",
    "T2351"
]

EUFY_CLEAN_G_SERIES = [
    "T2210",
    "T2250",
    "T2251",
    "T2252",
    "T2253",
    "T2254",
    "T2255",
    "T2256",
    "T2257",
    "T2258",
    "T2259",
    "T2270",
    "T2272",
    "T2273",
    "T2277"
]

EUFY_CLEAN_L_SERIES = [
    "T2190",
    "T2267",
    "T2268",
    "T2278"
]

EUFY_CLEAN_C_SERIES = [
    "T1250",
    "T2117",
    "T2118",
    "T2128",
    "T2130",
    "T2132",
    "T2120"
]

EUFY_CLEAN_S_SERIES = [
    "T2119",
    "T2080"
]

# Home Assistant state mappings
PROTO_STATE_MAP = {
    "standby": VacuumActivity.IDLE,
    "sleep": VacuumActivity.IDLE,
    "fault": VacuumActivity.ERROR,
    "charging": VacuumActivity.DOCKED,
    "fast_mapping": VacuumActivity.CLEANING,
    "cleaning": VacuumActivity.CLEANING,
    "remote_ctrl": VacuumActivity.CLEANING,
    "go_home": VacuumActivity.RETURNING,
    "cruisiing": VacuumActivity.CLEANING,
}

# Legacy API state mapping
EUFY_TO_HA_STATE = {
    # Running/Cleaning states
    "running": VacuumActivity.CLEANING,
    "cleaning": VacuumActivity.CLEANING,
    "spot": VacuumActivity.CLEANING,
    "cruising": VacuumActivity.CLEANING,
    "fast_mapping": VacuumActivity.CLEANING,
    "remote_ctrl": VacuumActivity.CLEANING,
    "auto": VacuumActivity.CLEANING,
    "room": VacuumActivity.CLEANING,
    "zone": VacuumActivity.CLEANING,
    "edge": VacuumActivity.CLEANING,
    "small_room": VacuumActivity.CLEANING,
    "global_cruise": VacuumActivity.CLEANING,
    "point_cruise": VacuumActivity.CLEANING,
    "zones_cruise": VacuumActivity.CLEANING,
    "scene_clean": VacuumActivity.CLEANING,
    "1": VacuumActivity.CLEANING,  # Novel API cleaning

    # Docked/Charging states
    "charging": VacuumActivity.DOCKED,
    "recharge": VacuumActivity.DOCKED,
    "completed": VacuumActivity.DOCKED,
    "standby": VacuumActivity.DOCKED,
    "stand_by": VacuumActivity.DOCKED,
    "2": VacuumActivity.DOCKED,  # Novel API charging
    "4": VacuumActivity.DOCKED,  # Novel API standby

    # Idle/Sleeping states
    "sleeping": VacuumActivity.IDLE,
    "sleep": VacuumActivity.IDLE,
    "stopped": VacuumActivity.IDLE,
    "no_sweep": VacuumActivity.IDLE,

    # Error states
    "fault": VacuumActivity.ERROR,
    "error": VacuumActivity.ERROR,

    # Returning states
    "go_home": VacuumActivity.RETURNING,
    "recharge_needed": VacuumActivity.RETURNING,
    "exploring_station": VacuumActivity.RETURNING,

    # Paused states
    "pause": VacuumActivity.PAUSED,
    "paused": VacuumActivity.PAUSED,
    "3": VacuumActivity.PAUSED,  # Novel API paused
}

# Additional constants for vacuum features
EUFY_CLEAN_TYPE = {
    "sweep_and_mop": "Sweep and Mop",
    "sweep_only": "Sweep Only",
    "mop_only": "Mop Only"
}

EUFY_MOP_MODE = {
    "high": "High",
    "medium": "Medium",
    "low": "Low"
}
