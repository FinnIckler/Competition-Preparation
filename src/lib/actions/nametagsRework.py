from lib.api.wca import get_upcoming_wca_competitions, get_wca_info
from lib.utils.user_input import get_password_mail, select_upcoming_competition, get_confirmation
import json, os

#import apis

def printOnlyNametags():
    # TODO: Add parser_arg for local directory, and search in it for *registration.csv to use instead
    # TODO: Add cubecomps support back, use IDs from cubecomps over the ones from WCA if they differ, cause scoretaking

    (password, email) = get_password_mail()
    upcomingJson = get_upcoming_wca_competitions(password, email)
    upcomingComps = sorted(upcomingJson, key = lambda x : x['start_date'])
    (competition_name, competition_name_stripped) = select_upcoming_competition(upcomingComps)

    if not os.path.exists(competition_name_stripped):
        os.makedirs(competition_name_stripped)

    two_sided_nametags = get_confirmation(
        "Create two-sided nametags? (grouping (and scrambling) information on the back) (y/n)"
    )

    if two_sided_nametags:
        print(
            "Using WCA registration and event information for competition {}.".format(
                competition_name
            )
        )

    competition_wcif_file = get_wca_info(
        competition_name, competition_name_stripped, email=email, password=password
    )

    print(
        "Saved registration information from WCA website, extracting data now and collect relevant information..."
    )
