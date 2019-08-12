from constants import Modes


class Executor:
    def __init__(self, parser):
        self.parser = parser

    def execute_action(self, action_id):
        """
            Executes the Action based on its action ID (integer value)
            List of available actions can be find in the Modes enum
        """
        mode = Modes(action_id)
        if mode == Modes.SCORESHEETS_BLANK:
            from .scoreSheets import blanks
            blanks()
        
        if mode == Modes.REGISTRATION_INFO:
            from .registrationInfo import printRegistration
            printRegistration(self.parser.parse_args())

        if mode == Modes.SCORESHEETS_CONSECUTIVE:
            from .consecRound import printConsecSheets
            printConsecSheets(self.parser.parse_args())
        
        if mode == Modes.SCHEDULE:
            from .onlySchedule import printSchedule
            printSchedule(self.parser.parse_args())
            
        if mode == Modes.NAMETAGS:
            from .nametags import printOnlyNametags
            printOnlyNametags(self.parser.parse_args())

        if mode == Modes.SCORESHEETS_GROUPING_ALL:
            from .scoreSheets import fromGroupingFileAll
            fromGroupingFileAll(self.parser.parse_args())

        if mode == Modes.SCORESHEETS_GROUPING_ONE:
            from .scoreSheets import fromGroupingFileOne
            fromGroupingFileOne(self.parser.parse_args())

        if mode == Modes.PREPERATION:
            from .doEverything import operation1
            operation1(self.parser.parse_args())