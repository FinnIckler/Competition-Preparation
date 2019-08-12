'''
T: create_scoresheets_second_rounds_bool = True
F: new_creation, create_registration_file_bool, create_only_registration_file, create_only_nametags, reading_scrambling_list_from_file, reading_grouping_from_file_bool, only_one_competitor, read_only_registration_file, create_schedule, create_only_schedule, scrambler_signature, use_cubecomps_ids = False 
'''
import apis
from lib.api import *
import information_analysis as analysis
import grouping_scrambling_functions as grouping_scrambling
import pdf_file_generation as pdf_files
from modules import *
from constants import EVENT_DICT
from lib.utils import *

def printConsecSheets(parser_args):
    competitors_local = ''
    competitors_api_local = [] 
    scoresheet_competitor_name_local = ''

    use_cubecomps_ids = True
    if parser_args.cubecomps:
        cubecomps_id = parser_args.cubecomps
    else:
        cubecomps_id = input("Link to previous round: ")
    cubecomps_api, competitors_local, event_round_name, advancing_competitors_next_round, competition_name, competition_name_stripped = apis.get_round_information_from_cubecomps(
        cubecomps_id
    )

    event_2 = event_round_name.split(" - ")[0].replace(" Cube", "")
    event_2 = list(EVENT_DICT.keys())[list(EVENT_DICT.values()).index(event_2)]

    current_round_number = (
        event_round_name.split(" - ")[1]
        .replace("Round", "")
        .replace("Combined", "Round")
        .replace("Final", "")
        .replace("First", "-r1")
        .replace("Second", "-r2")
        .replace("Semi", "-r3")
        .replace(" ", "")[-1:]
    )
    if current_round_number.isdigit():
        round_number = int(current_round_number) + 1
    else:
        print("Please open next round before using script. Script aborted.")
        return

    next_round_name = "{} -{} {}".format(
        event_round_name.split(" - ")[0].replace(" Cube", ""),
        event_round_name.split(" - ")[1]
        .replace("First", "")
        .replace("Second", "")
        .replace("Semi", "")
        .replace("Combined ", " Round"),
        str(round_number),
    )
    event_round_name = next_round_name.replace(" 4", "")

    if not parser_args.use_access_token:
        wca_password, wca_mail = apis.wca_registration(False, parser_args)

    if parser_args.wca_registration:
        wca_info = parser_args.wca_registration
    else:
        wca_info = get_confirmation(
            "Used WCA registration for this competition? (y/n) "
        )
    if wca_info:
        print("Using WCA website information.")
    if parser_args.scrambler_signature:
        scrambler_signature = parser_args.scrambler_signature
    else:
        scrambler_signature = get_confirmation(
            "Add scrambler signature field to scorecards? (y/n)"
        )
    file_name, grouping_file_name = apis.competition_information_fetch(
        wca_info, False, False, False, parser_args
    )

    if not parser_args.use_access_token:
        competition_wcif_file = apis.get_wca_info(
            competition_name, competition_name_stripped, wca_password, wca_mail
        )
    else:
        competition_wcif_file = apis.get_wca_info(
            competition_name, competition_name_stripped, access_token
        )
    
    ### always part ###

    # Extract data from WCIF file
    wca_json = json.loads(competition_wcif_file)

    # Registration
    competitor_information_wca = analysis.get_registrations_from_wcif(
        wca_json,
        True,
        use_cubecomps_ids,
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
        continue_script = get_confirmation(
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
        if not competitors_api:
            competitors_api_local = competitors_local
        analysis.column_ids, event_list, event_counter, competitor_information, all_data, wca_ids = analysis.get_registration_from_file(
            wca_json,
            file_name,
            False,
            reading_grouping_from_file_bool,
            use_csv_registration_file,
            analysis.column_ids,
            competitor_information_wca,
            competitors_local,
            use_cubecomps_ids,
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
    
    ### always part over

    print("Creating scoresheets for {} ...".format(event_round_name))
    pdf_files.create_scoresheets_second_rounds(
        competition_name,
        competitor_information,
        advancing_competitors_next_round,
        event_round_name,
        event_info,
        event_2,
        next_round_name,
        scrambler_signature,
    )

    if registration_list:
        result_string = helper.initiate_result_string(registration_list)
