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
            from .blanks import blanks
            blanks()
        
        if mode == Modes.REGISTRATION_INFO:
            from .registrationInfo import printRegistration
            printRegistration(self.parser.parse_args())

        if mode == Modes.SCORESHEETS_CONSECUTIVE:
            from .consecRound import printConsecSheets
            printConsecSheets(self.parser.parse_args())
        