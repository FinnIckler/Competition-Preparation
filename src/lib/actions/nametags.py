from lib.api.wca import get_upcoming_wca_competitions, get_wcif_for_comp
from lib.utils.user_input import get_password_mail, select_upcoming_competition, get_confirmation
import json, os

#import apis
#Changed to make comments about the code

def printOnlyNametags():
    # TODO: Add parser_arg for local directory, and search in it for *registration.csv to use instead

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

    competition_wcif_file = get_wcif_for_comp(
        competition_name, competition_name_stripped, email=email, password=password
    )

    print(
        "Saved registration information from WCA website, extracting data now and collect relevant information..."
    )

    people = getRegistrationDataFromWCIF(competition_wcif_file)

    print(people)

def getRegistrationDataFromWCIF(competition_wcif_file):
    wca_json = json.loads(competition_wcif_file)

    people_json = wca_json['persons']

    ret = []

    for person in people_json:
        if person['registration']['status'] != 'accepted':
            continue
    
        curr = {}
        curr['name'] = person['name']
        curr['wcaId'] = person['wcaId']
        curr['nation'] = person['countryIso2']
        curr['gender'] = person['gender']
        curr['birthdate'] = person['birthdate']
        curr['eventIds'] = person['registration']['eventIds'] 
        curr['guests'] = person['registration']['guests']

        ret.append(curr)
    
    return ret