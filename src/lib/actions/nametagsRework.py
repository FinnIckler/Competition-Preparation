from lib.api.wca import get_upcoming_wca_competitions, get_wcif_for_comp
from lib.utils.user_input import get_password_mail, select_upcoming_competition, get_confirmation
from lib.utils.directory_handling import check_for_local_csv_files
from lib.utils.data_from_WCIF import get_nametag_data
from lib.pdf_generation.genNametags import gen_nametags
import os

def print_only_nametags():
    # TODO: Check if access token already here, only ask for mail etc if not

    (password, email) = get_password_mail()
    upcomingJson = get_upcoming_wca_competitions(email=email, password=password)
    upcomingComps = sorted(upcomingJson, key = lambda x : x['start_date'])
    (competition_name, competition_name_stripped) = select_upcoming_competition(upcomingComps)

    two_sided_nametags = False
    if not os.path.exists(competition_name_stripped):
        os.makedirs(competition_name_stripped)
    else:
        (reg_file, grp_file, scr_file) = check_for_local_csv_files(competition_name_stripped)
        if grp_file != None and scr_file != None:
            two_sided_nametags = get_confirmation(
                "Create two-sided nametags? (grouping and scrambling information on the back) (y/n)"
            )


    competition_wcif_file = get_wcif_for_comp(
        competition_name, competition_name_stripped, email=email, password=password
    )

    print(
        "Saved registration information from WCA website, extracting data now and collect relevant information..."
    )

    people = get_nametag_data(competition_wcif_file)

    if two_sided_nametags: # extend people with their assignments according to .csv s
        # TODO
        pass
    
    gen_nametags(competition_name, people)
    