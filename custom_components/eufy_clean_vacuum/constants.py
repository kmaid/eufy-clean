"""Constants for Eufy Clean."""
from typing import Dict

EUFY_CLEAN_WORK_MODE: Dict[str, str] = {
    "AUTO": "AUTO",
    "SPOT": "SPOT",
    "EDGE": "EDGE",
    "SMALL_ROOM": "SMALL_ROOM",
    "ROOM": "ROOM",
}

EUFY_CLEAN_NOVEL_CLEAN_SPEED: Dict[str, str] = {
    "QUIET": "QUIET",
    "STANDARD": "STANDARD",
    "TURBO": "TURBO",
    "MAX": "MAX",
}

EUFY_CLEAN_CONTROL: Dict[str, int] = {
    "START_GOHOME": 1,
    "START_SPOT_CLEAN": 2,
    "START_SCENE_CLEAN": 3,
    "START_SELECT_ROOMS_CLEAN": 4,
    "PAUSE_TASK": 5,
    "RESUME_TASK": 6,
    "STOP_TASK": 7,
}

EUFY_CLEAN_X_SERIES: list[str] = ["X8", "X8PRO"]
