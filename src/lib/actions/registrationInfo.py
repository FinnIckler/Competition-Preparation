'''
T: new_creation, create_registration_file_bool, create_only_registration_file = True
F: create_only_nametags, reading_scrambling_list_from_file, create_scoresheets_second_rounds_bool, reading_grouping_from_file_bool, only_one_competitor, read_only_registration_file, create_schedule, create_only_schedule, scrambler_signature, use_cubecomps_ids = False 
'''
import apis
import information_analysis as analysis
import grouping_scrambling_functions as grouping_scrambling
import pdf_file_generation as pdf_files
from modules import *
from constants import EVENT_DICT
from lib.utils import *

competitors_local = ''
competitors_api_local = [] 
scoresheet_competitor_name_local = ''

def printRegistration(parser_args):
    wca_info = get_confirmation(
        "Used WCA registration for this competition? (y/n) "
    )
    if wca_info:
        print("Using WCA registration information.")
    if not parser_args.use_access_token:
        wca_password, wca_mail, competition_name, competition_name_stripped = apis.wca_registration(
            True, parser_args
        )
    else:
        competition_name, competition_name_stripped = apis.wca_registration(
            True, parser_args
        )

    file_name, grouping_file_name = apis.competition_information_fetch(
        wca_info,
        False,
        False,
        True,
        parser_args,
    )

    if not parser_args.use_access_token:
        competition_wcif_file = apis.get_wca_info(
            competition_name, competition_name_stripped, wca_password, wca_mail
        )
    else:
        competition_wcif_file = apis.get_wca_info(
            competition_name, competition_name_stripped, access_token
        )

    print(
        "Saved registration information from WCA website, extracting data now and collect relevant information..."
    )

    ### the next part is always there ###

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
            sys.exit()
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
        sys.exit()

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
            sys.exit()
        else:
            print(
                "Continue script. Please be reminded, that there is a high possibility of not finding any scramblers!"
            )

    if wca_info:
        registration_list = registration_list_wca
    
    ### end of always part ###

    print("")
    print("Create registration file...")
    output_registration = "{}/{}Registration.csv".format(
        competition_name_stripped, competition_name_stripped
    )
    pdf_files.create_registration_file(
        output_registration, registration_list, analysis.column_ids
    )

    print("Registration file successfully created.")
    print("")

# TODO: maybe later at some point check if registration.csv exists in directory, but dont ask user...
"""
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
            new_creation,
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
            sys.exit()
""" 