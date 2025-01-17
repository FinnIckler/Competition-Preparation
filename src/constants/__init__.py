from enum import Enum

EVENT_DICT = {
    "333": "3x3x3",
    "222": "2x2x2",
    "444": "4x4x4",
    "555": "5x5x5",
    "666": "6x6x6",
    "777": "7x7x7",
    "333bf": "3x3x3 Blindfolded",
    "333fm": "3x3x3 Fewest Moves",
    "333oh": "3x3x3 One-Handed",
    "333ft": "3x3x3 With Feet",
    "clock": "Clock",
    "minx": "Megaminx",
    "pyram": "Pyraminx",
    "skewb": "Skewb",
    "sq1": "Square-1",
    "444bf": "4x4x4 Blindfolded",
    "555bf": "5x5x5 Blindfolded",
    "333mbf": "3x3x3 Multi-Blindfolded",
}
EVENT_IDS = {
    "333": 999,
    "222": 999,
    "444": 999,
    "555": 999,
    "666": 999,
    "777": 999,
    "333bf": 999,
    "333fm": 999,
    "333oh": 999,
    "333ft": 999,
    "minx": 999,
    "pyram": 999,
    "clock": 999,
    "skewb": 999,
    "sq1": 999,
    "444bf": 999,
    "555bf": 999,
    "333mbf": 999,
}


class Modes(Enum):
    PREPERATION = 1
    SCORESHEETS_CONSECUTIVE = 2
    SCORESHEETS_BLANK = 3
    REGISTRATION_INFO = 4
    NAMETAGS = 5
    SCHEDULE = 6
    SCORESHEETS_GROUPING_ALL = 7
    SCORESHEETS_GROUPING_ONE = 8


MODE_HELP = [
    "",
    "Competition preparation (grouping, scrambling, scoresheets, nametags, schedule, registration file)",
    "Scoresheets for consecutive rounds",
    "Blank scoresheets",
    "Registration information",
    "Nametags",
    "Schedule",
    "Scoresheets from grouping-file (all)",
    "Scoresheets from grouping-file (for one person)",
    "Quit",
]
