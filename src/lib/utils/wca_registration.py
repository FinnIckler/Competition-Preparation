from validate_email import validate_email
from lib.logging import Logger
from lib.api.wca import get_upcoming_wca_competitions, get_wca_competition

# Get user input for wca login (mail-address, password and competition name)
# All try-except cases were implemented for simple development and will not change the normal user input
def register(new_creation: bool, mail="", access_token="", competition=""):
    if access_token == "":
        print("\nUsing Login Credentials")
        if not validate_email(mail):
            print("")
            print("Please enter correct mail address manually.")
            while not validate_email(mail):
                mail = input("Your WCA mail address: ")
        wca_password = getpass.getpass("Your WCA password: ")

    if new_creation:
        print("Getting upcoming competitions from WCA website...")
        if access_token != "":
            competitions = get_upcoming_wca_competitions(
                password=wca_password, mail=mail
            )
        else:
            competitions = get_upcoming_wca_competitions(access_token=access_token)
        upcoming_competitions = sorted(competitions, key=lambda x: x["start_date"])
        if len(upcoming_competitions) == 0:
            Logger.info("User doesn't have any upcoming competitions")
            return (wca_password, wca_mail)
        else:
            print("Please select competition (by number) or enter competition name:")
            for i, competition in enumerate(upcoming_competitions):
                print("{}. {}".format(i + 1, competition["name"]))
        not_valid_competition_name = True
        #TODO Remove this while loop with a more sensible thing
        while not_valid_competition_name:
            competition_name = input("Competition name or ID: ")
            if competition_name.isdigit():
                if int(competition_name) <= len(upcoming_competitions):
                    competition_name = upcoming_competitions[int(competition_name) - 1][
                        "name"
                    ].replace("-", " ")
                    not_valid_competition_name = False
                else:
                    print(
                        "Wrong input, please select number or enter competition name/ID."
                    )
            else:
                try:
                    get_wca_competition(competition_name)["name"]
                    not_valid_competition_name = False
                except KeyError:
                    print(
                        "Competition {} not found on WCA website, please enter valid competition name.".format(
                            competition_name
                        )
                    )
                    competition = ""

        create_competition_folder(competition_name)
        competition_name_stripped = competition_name.replace(" ", "")
        if access_token == "":
            return (wca_password, wca_mail, competition_name, competition_name_stripped)
        else:
            return (competition_name, competition_name_stripped)
    return (wca_password, wca_mail)
