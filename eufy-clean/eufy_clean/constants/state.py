from enum import Enum, auto

EUFY_CLEAN_GET_STATE = {
    'sleeping': 'stopped',
    'standby': 'docked',
    'recharge': 'docked',
    'running': 'cleaning',
    'cleaning': 'cleaning',
    'spot': 'spot_cleaning',
    'completed': 'docked',
    'charging': 'charging',
    'sleep': 'stopped',
    'go_home': 'docked',
    'fault': 'stopped'
}

class VacuumState(str, Enum):
    STOPPED = 'stopped'
    CLEANING = 'cleaning'
    SPOT_CLEANING = 'spot_cleaning'
    DOCKED = 'docked'
    CHARGING = 'charging'

class CleanSpeed(str, Enum):
    NO_SUCTION = 'No_suction'
    STANDARD = 'Standard'
    QUIET = 'Quiet'
    TURBO = 'Turbo'
    BOOST_IQ = 'Boost_IQ'
    MAX = 'Max'

EUFY_CLEAN_NOVEL_CLEAN_SPEED = [
    CleanSpeed.QUIET,
    CleanSpeed.STANDARD,
    CleanSpeed.TURBO,
    CleanSpeed.MAX
]

EUFY_CLEAN_LEGACY_CLEAN_SPEED = [
    CleanSpeed.NO_SUCTION,
    CleanSpeed.BOOST_IQ
]

EUFY_CLEAN_GET_CLEAN_SPEED = {
    'no_suction': 'No Suction',
    'standard': 'Standard',
    'quiet': 'Quiet',
    'turbo': 'Turbo',
    'boost_iq': 'Boost IQ',
    'max': 'Max'
}

class WorkStatus(str, Enum):
    # Cleaning
    RUNNING = 'Running'
    # In the dock, charging
    CHARGING = 'Charging'
    # Not in the dock, paused
    STAND_BY = 'standby'
    # Not in the dock - goes into this state after being paused for a while
    SLEEPING = 'Sleeping'
    # Going home because battery is depleted
    RECHARGE_NEEDED = 'Recharge'
    RECHARGE = 'Recharge'
    # In the dock, full charged
    COMPLETED = 'Completed'
    STANDBY = 'Standby'
    SLEEP = 'Sleep'
    FAULT = 'Fault'
    FAST_MAPPING = 'Fast Mapping'
    CLEANING = 'Cleaning'
    REMOTE_CTRL = 'Remote Ctrl'
    GO_HOME = 'Go Home'
    CRUISING = 'Cruising'

class WorkMode(str, Enum):
    AUTO = 'auto'
    NO_SWEEP = 'Nosweep'
    SMALL_ROOM = 'SmallRoom'
    ROOM = 'room'
    ZONE = 'zone'
    EDGE = 'Edge'
    SPOT = 'Spot'

class Control(int, Enum):
    START_AUTO_CLEAN = 0
    START_SELECT_ROOMS_CLEAN = 1
    START_SELECT_ZONES_CLEAN = 2
    START_SPOT_CLEAN = 3
    START_GOTO_CLEAN = 4
    START_RC_CLEAN = 5
    START_GOHOME = 6
    START_SCHEDULE_AUTO_CLEAN = 7
    START_SCHEDULE_ROOMS_CLEAN = 8
    START_FAST_MAPPING = 9
    START_GOWASH = 10
    STOP_TASK = 12
    PAUSE_TASK = 13
    RESUME_TASK = 14
    STOP_GOHOME = 15
    STOP_RC_CLEAN = 16
    STOP_GOWASH = 17
    STOP_SMART_FOLLOW = 18
    START_GLOBAL_CRUISE = 20
    START_POINT_CRUISE = 21
    START_ZONES_CRUISE = 22
    START_SCHEDULE_CRUISE = 23
    START_SCENE_CLEAN = 24
    START_MAPPING_THEN_CLEAN = 25

# Error codes from error_code_list_t2265.proto and error_code_list_standard.proto
EUFY_CLEAN_ERROR_CODES = {
    0: 'NONE',
    1: 'CRASH BUFFER STUCK',
    2: 'WHEEL STUCK',
    3: 'SIDE BRUSH STUCK',
    4: 'ROLLING BRUSH STUCK',
    5: 'HOST TRAPPED CLEAR OBST',
    6: 'MACHINE TRAPPED MOVE',
    7: 'WHEEL OVERHANGING',
    8: 'POWER LOW SHUTDOWN',
    13: 'HOST TILTED',
    14: 'NO DUST BOX',
    17: 'FORBIDDEN AREA DETECTED',
    18: 'LASER COVER STUCK',
    19: 'LASER SENSOR STUCK',
    2112: 'ROLLER BRUSH STUCK',
    2210: 'SIDE BRUSH OPEN CIRCUIT',
    2211: 'SIDE BRUSH SHORT CIRCUIT',
    2212: 'SIDE BRUSH ERROR',
    2213: 'SIDE BRUSH STUCK',
    2310: 'DUSTBIN NOT INSTALLED',
    2311: 'DUSTBIN NOT CLEANED FOR TOO LONG',
    3010: 'ROBOT WATER PUMP OPEN CIRCUIT',
    3013: 'ROBOT WATER INSUFFICIENT',
    4010: 'LASER ERROR',
    4011: 'LASER BLOCKED',
    4012: 'LASER STUCK',
    4111: 'LEFT BUMPER STUCK',
    4112: 'RIGHT BUMPER STUCK',
    4130: 'LASER COVER STUCK',
    5010: 'BATTERY OPEN CIRCUIT',
    5011: 'BATTERY SHORT CIRCUIT',
    5012: 'BATTERY CHARGING CURRENT TOO SMALL',
    5013: 'BATTERY DISCHARGE CURRENT TOO LARGE',
    5014: 'LOW BATTERY SHUTDOWN',
    5015: 'LOW BATTERY SCHEDULES FAILED',
    5016: 'CHARGING CURRENT TOO LARGE',
    5017: 'CHARGING VOLTAGE ABNORMAL',
    5018: 'BATTERY TEMPERATURE ABNORMAL',
    5021: 'DISCHARGE HIGH TEMPERATURE',
    5022: 'DISCHARGE LOW TEMPERATURE',
    5023: 'CHARGING HIGH TEMPERATURE',
    5024: 'CHARGING LOW TEMPERATURE',
    5110: 'WIFI OR BLUETOOTH ERROR',
    5111: 'BT ABNORMAL',
    5112: 'INFRARED COMMUNICATION ABNORMAL',
    6010: 'CLEAN WATER TANK NOT INSTALLED',
    6020: 'DIRTY WATER TANK NOT INSTALLED'
}
