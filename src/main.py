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

# TODO: weird bug where it never executes the action on the frist run, i.e. always user input twice. 
# Am I stupid or something? See shitty attempt at debuging commented out
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
            print("  {}. {}".format(mode.value, MODE_HELP[mode.value]))
        program_type = input("")

        print("")
        # TODO: isdigit() didnt fix the bug
        if program_type.isdigit():
            program_type = int(program_type)
            #print("we 2")
            if program_type in range(1, 9):
                #print("we 3")
                executor = Executor(parser)
                #print("we 4")
                executor.execute_action(program_type)
                #print("we 5")
            else:
                print("Quitting programm.")
                sys.exit()


# if access_token_found and not parser_args.use_access_token:
#    use_access_token = get_confirmation(
#        "An access token from a previous run of this script was found. Would you like to use this one to proceed? (No password input will be necessary)"
#    )