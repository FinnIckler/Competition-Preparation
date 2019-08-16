"""
    Please read the README.md to get further information.
"""

### Module import
from lib.parser import PreperationParser
from constants import Modes, MODE_HELP
from lib.actions import Executor
import sys

parser = PreperationParser()
parser_args = parser.parse_args()

# TODO: rework access token shit, should be 'on' by default
# access_token_found = False
# if parser_args.use_access_token and key_exists():
#    access_token = get_key()
#    access_token_found = True
# else:
#    parser_args.use_access_token = False


### Selection of script functions
while True:
    if parser_args.option and int(parser_args.option) in range(1, 9):
        program_type = parser_args.option
    else:
        print(
            "Input for script options was missing/wrong, please select an option manually."
        )
        print("Please select: ")
        for mode in Modes:
            print("{}. {}".format(mode.value, MODE_HELP[mode.value]))
        program_type = input("")

    print("")
    if int(program_type):
        if int(program_type) in range(1, 9):
            executor = Executor(parser)
            executor.execute_action(int(program_type))
        if int(program_type) == 420:
            from lib.actions import nametagsRework
            nametagsRework.print_only_nametags()
        print("Quitting programm.")
        sys.exit()


# if access_token_found and not parser_args.use_access_token:
#    use_access_token = get_confirmation(
#        "An access token from a previous run of this script was found. Would you like to use this one to proceed? (No password input will be necessary)"
#    )