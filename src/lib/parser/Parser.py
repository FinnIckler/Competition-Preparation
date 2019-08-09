from argparse import ArgumentParser

class PreperationParser(ArgumentParser):
    def __init__(self):
        super().__init__(description="Give input to script to skip steps during run time.")
        self.add_argument(
        "-m", "--mail", help="WCA account mail address which is used for login."
        )
        self.add_argument("-o", "--option", help="Input any of the given options of script.")
        self.add_argument(
            "-wreg",
            "--wca_registration",
            action="store_true",
            help="Boolean. Did competition use WCA registration?",
        )
        self.add_argument("-c", "--competition", help="Competition name")
        self.add_argument(
            "-t",
            "--two_sided",
            action="store_true",
            help="Boolean. Specify, if back of nametags should be created (with grouping and scrambling information).",
        )
        self.add_argument(
            "-ssig",
            "--scrambler_signature",
            action="store_true",
            help="Boolean. Specify, if scrambler signature field should be put on scoresheets.",
        )
        self.add_argument(
            "-r",
            "--registration_file",
            help="Name of registration file if WCA registration was not used.",
        )
        self.add_argument(
            "-g", "--grouping_file", help="Name of grouping file. For options 5, 7 and 8."
        )
        self.add_argument(
            "-s", "--scrambling_file", help="Name of scrambling file. For option 5."
        )
        self.add_argument(
            "-cu",
            "--cubecomps",
            help="Cubecomps link to create scoresheets of consecutive rounds.",
        )
        self.add_argument(
            "-a",
            "--use_access_token",
            action="store_true",
            help="If script has been used before, an access token to the WCA API will be saved. This token can be reused.",
        )

    def isValid(self):
        pass
