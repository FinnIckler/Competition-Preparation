'''
T: reading_grouping_from_file_bool, create_only_nametags, get_registration_information, two_sided_nametags, valid_cubecomps_link, get_registration_information = True
F: new_creation, reading_scrambling_list_from_file, create_scoresheets_second_rounds_bool, only_one_competitor, create_registration_file_bool, create_only_registration_file, read_only_registration_file, create_schedule, create_only_schedule, scrambler_signature, use_cubecomps_ids = False
'''
import apis
from modules import *
from lib.utils import user_input
import information_analysis as analysis
import grouping_scrambling_functions as grouping_scrambling
import pdf_file_generation as pdf_files
from helpers import helpers as helper
from constants import EVENT_DICT, EVENT_IDS

def printOnlyNametags(parser_args):
    reading_scrambling_list_from_file = False
    read_only_registration_file = False
    cubecomps_id_local = ''
    competitors_local = ''
    competitors_api_local = [] 
    scrambler_list_local = []
    scoresheet_competitor_name_local = ''
    EVENT_IDS_local = EVENT_IDS

    if parser_args.wca_registration:
        wca_info = parser_args.wca_registration
    else:
        wca_info = user_input.get_confirmation(
            "Used WCA registration for this competition? (y/n) "
        )
    if wca_info:
        print("Using WCA registration information.")
    
    """
    if not parser_args.use_access_token:
        wca_password, wca_mail, competition_name, competition_name_stripped = apis.wca_registration(
            True, parser_args
        )
    else:
        competition_name, competition_name_stripped = apis.wca_registration(
            True, parser_args
        )
    """

    wca_password, wca_mail, competition_name, competition_name_stripped = apis.wca_registration(
        True, parser_args
    )

    if parser_args.two_sided:
        two_sided_nametags = parser_args.two_sided
    else:
        two_sided_nametags = user_input.get_confirmation(
            "Create two-sided nametags? (grouping (and scrambling) information on the back) (y/n)"
        )
    if two_sided_nametags:
        print(
            "Using WCA registration and event information for competition {}.".format(
                competition_name
            )
        )

    competitors_api_local, cubecomps_id_local, use_cubecomps_ids = apis.get_cubecomps_competition(
        True, competition_name, competition_name_stripped
    )


    if not two_sided_nametags and not wca_info:
        get_registration_information = False
        read_only_registration_file = True

    if two_sided_nametags:
        while True:
            print("Use scrambling-list for nametags? (y/n)")
            nametag_scrambling = input("")
            if nametag_scrambling.upper() in ("N", "Y"):
                break
            else:
                print("Wrong input, please enter 'y' or 'n'.")
                print("")

        if nametag_scrambling.upper() == "Y":
            reading_scrambling_list_from_file = True
            scrambling_file_name = apis.get_file_name(
                "scrambling", parser_args.scrambling_file
            )

    file_name, grouping_file_name = apis.competition_information_fetch(
        wca_info,
        False,
        two_sided_nametags,
        False,
        parser_args,
    )

    if not two_sided_nametags and not wca_info:
        pass
    else:
        """
        if not parser_args.use_access_token:
            competition_wcif_file = apis.get_wca_info(
                competition_name, competition_name_stripped, wca_password, wca_mail
            )
        else:
            competition_wcif_file = apis.get_wca_info(
                competition_name, competition_name_stripped, access_token
            )
        """
        competition_wcif_file = apis.get_wca_info(
            competition_name, competition_name_stripped, wca_password, wca_mail
        )

    print(
        "Saved registration information from WCA website, extracting data now and collect relevant information..."
    )

    ### always part ###
    
    # Extract data from WCIF file
    wca_json = json.loads(competition_wcif_file)

    # Registration
    competitor_information_wca = analysis.get_registrations_from_wcif(
        wca_json,
        False,
        False,
        competitors_local,
        competitors_api_local,
        False,
        scoresheet_competitor_name_local,
    )

    # Events
    event_ids_wca, group_list, event_info, event_counter_wca, minimal_scramble_set_count, round_counter, event_list_wca = analysis.get_events_from_wcif(
        wca_json, EVENT_DICT
    )

    # Schedule
    full_schedule, competition_days, competition_start_day, timezone_utc_offset, events_per_day = analysis.get_schedule_from_wcif(
        wca_json
    )

    # Evaluate collected information
    if wca_info:
        competitor_information = competitor_information_wca

        wca_ids, registration_list_wca = analysis.prepare_registration_for_competitors(
            competitor_information, event_list_wca, len(event_list_wca)
        )

        if not registration_list_wca:
            print("")
            print(
                "ERROR!! WCA registration not used for this competition. Please select registration file for import. Script aborted."
            )
            return
        registration_list_wca = sorted(
            sorted(registration_list_wca, key=lambda x: x[1]),
            key=lambda x: x[1].split()[-1],
        )

        analysis.column_ids, event_list = grouping_scrambling.update_column_ids(
            event_list_wca, analysis.column_ids
        )
    if group_list:
        print("WCA information sucessfully imported.")
    else:
        print(
            "An error occured while importing the rounds and groups information from the WCIF file, script aborted."
        )
        print(
            'Please make sure to enter all necessary information in the "Manage events" tab on the WCA competition page.'
        )
        return
    if minimal_scramble_set_count == 1:
        continue_script = user_input.get_confirmation(
            "It looks like all your events only have one set of scrambles. Do you still want to continue running this script? (y/n)"
        )
        if not continue_script:
            print("")
            print(
                "Please edit the group information in the competition event tab  before running this script again."
            )
            print("Script aborted.")
            return
        else:
            print(
                "Continue script. Please be reminded, that there is a high possibility of not finding any scramblers!"
            )

    ### Get data from csv-export
    # same as for the WCA registration, get competitor information from registration file (if used): name, WCA ID, date of birth, gender, country and events registered for
    if not wca_info:
        print("Open registration file...")
        use_csv_registration_file = True
        if not competitors_api_local:
            competitors_api_local = competitors_local
        analysis.column_ids, event_list, event_counter, competitor_information, all_data, wca_ids = analysis.get_registration_from_file(
            wca_json,
            file_name,
            True,
            True,
            use_csv_registration_file,
            analysis.column_ids,
            competitor_information_wca,
            competitors_local,
            False,
            competitors_api_local,
        )

        registration_list = sorted(
            sorted(all_data, key=lambda x: x[1]), key=lambda x: x[1].split()[-1]
        )

        if event_counter != event_counter_wca:
            print(
                "ERROR!! Number of events from WCA Website does not match number of events in registration data. Please use correct registration file. Abort script."
            )
            return

    if wca_info:
        registration_list = registration_list_wca

    ### always part over ###

    if read_only_registration_file:
        use_csv_registration_file = False
        analysis.column_ids, event_list, event_counter, competitor_information, all_data, wca_ids = analysis.get_registration_from_file(
            wca_json,
            file_name,
            False,
            True,
            use_csv_registration_file,
            analysis.column_ids,
            event_counter,
            competitor_information_wca,
            competitors_local,
            False,
            competitors_api_local,
        )

    if registration_list:
        result_string = helper.initiate_result_string(registration_list)

    if two_sided_nametags:
        result_string, EVENT_IDS_local = analysis.get_grouping_from_file(
            grouping_file_name,
            EVENT_DICT,
            EVENT_IDS,
            False,
            scoresheet_competitor_name_local,
        )
        new_result_string, new_competitor_information = [], []
        if len(competitor_information) != len(result_string):
            print("")
            print(
                "ERROR! Count of registrations in grouping file and WCA website does not match."
            )
            for registered_competitor in competitor_information:
                for competitor_grouping in result_string:
                    if ftfy.fix_text(registered_competitor["name"]) == ftfy.fix_text(
                        competitor_grouping[0]
                    ):
                        new_result_string.append(competitor_grouping)
                        new_competitor_information.append(registered_competitor)
                        break

        if (
            len(new_competitor_information) <= len(competitor_information)
            and len(new_competitor_information) != 0
        ):
            print("Using only information that were found on both platforms.")
            print("")
            competitor_information = new_competitor_information
            result_string = new_result_string

    if wca_ids and event_list:
        print("Get necessary results from WCA website, this may take a few seconds...")
        competitor_information, ranking_single, competition_count = grouping_scrambling.get_competitor_results_from_wcif(
            event_list, wca_ids, competitor_information, True, wca_info
        )
    
    if reading_scrambling_list_from_file:
        with open(scrambling_file_name, "r", encoding="utf8") as f:
            reader = csv.reader(f)
            scrambler_list_local = list(reader)
        del scrambler_list_local[0:2]
        scrambler_list_local = helper.update_scrambler_list(scrambler_list_local)

    print("")
    print("Create nametags...")
    output_scrambling = "{}/{}Scrambling.csv".format(
        competition_name_stripped, competition_name_stripped
    )
    output_grouping = "{}/{}Grouping.csv".format(
        competition_name_stripped, competition_name_stripped
    )

    # Nametag file
    sheet = pdf_files.create_nametag_file(
        competitor_information,
        competition_name,
        competition_name_stripped,
        two_sided_nametags,
        True,
        result_string,
        EVENT_IDS_local,
        scrambler_list_local,
        EVENT_DICT,
        round_counter,
        group_list,
    ) # exits if 5th arg (creat_only_nametags) is True
            