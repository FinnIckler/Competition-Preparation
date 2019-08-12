import apis
from modules import *
from lib.utils import user_input
import information_analysis as analysis
import grouping_scrambling_functions as grouping_scrambling
import pdf_file_generation as pdf_files
from helpers import helpers as helper
from constants import EVENT_DICT, EVENT_IDS
from lib.api.wca import persons

def blanks():
    scrambler_signature = True  # Will be mandatory soon(tm) anyways
    competition_name = input("Competition name or ID: (leave empty if not wanted) ")
    blank_sheets_round_name = input("Round name: (leave empty if not needed) ")
    print("Creating blank sheets...")
    pdf_files.create_blank_sheets(
        competition_name, scrambler_signature, blank_sheets_round_name
    )

'''
T: reading_grouping_from_file_bool, two_sided_nametags, valid_cubecomps_link, get_registration_information = True
F: create_only_nametags, new_creation, reading_scrambling_list_from_file, create_scoresheets_second_rounds_bool, only_one_competitor, create_registration_file_bool, create_only_registration_file, read_only_registration_file, create_schedule, create_only_schedule, scrambler_signature, use_cubecomps_ids = False
'''
def fromGroupingFileAll(parser_args):
    print("hey there")
    competitors_local = ''
    competitors_api_local = [] 
    scoresheet_competitor_name_local = ''
    EVENT_IDS_local = EVENT_IDS

    if parser_args.wca_registration:
        wca_info = parser_args.wca_registration
    else:
        wca_info = user_input.get_confirmation(
            "Used WCA registration for this competition? (y/n) "
        )
    if wca_info:
        print("Using WCA website information.")
    wca_password, wca_mail, competition_name, competition_name_stripped = apis.wca_registration(
        bool, parser_args
    )
    if parser_args.scrambler_signature:
        scrambler_signature = parser_args.scrambler_signature
    else:
        scrambler_signature = user_input.get_confirmation(
            "Add scrambler signature field to scorecards? (y/n)"
        )
    
    file_name, grouping_file_name = apis.competition_information_fetch(
        wca_info, True, False, False, parser_args
    )
    if not parser_args.use_access_token:
        competition_wcif_file = apis.get_wca_info(
            competition_name, competition_name_stripped, wca_password, wca_mail
        )
    else:
        competition_wcif_file = apis.get_wca_info(
            competition_name, competition_name_stripped, access_token
        )

    competitors_api, cubecomps_id, use_cubecomps_ids = apis.get_cubecomps_competition(
        False, competition_name, competition_name_stripped
    )

    ### always part 
    # Extract data from WCIF file
    wca_json = json.loads(competition_wcif_file)

    # Registration
    competitor_information_wca = analysis.get_registrations_from_wcif(
        wca_json,
        False,
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
        continue_script = user_input.get_confirmation(
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

    if wca_info:
        registration_list = registration_list_wca
    ### end of always

    result_string, EVENT_IDS_local = analysis.get_grouping_from_file(
            grouping_file_name,
            EVENT_DICT,
            EVENT_IDS_local,
            False,
            scoresheet_competitor_name_local,
        )

    print("Creating scoresheets...")
    pdf_files.create_scoresheets(
        competition_name,
        competition_name_stripped,
        result_string,
        EVENT_IDS_local,
        event_info,
        EVENT_DICT,
        False,
        round_counter,
        competitor_information,
        scoresheet_competitor_name_local,
        scrambler_signature,
    )

    ### Throw error messages for entire script if errors were thrown
    if ErrorMessages.messages:
        print("")
        print("Notable errors while creating grouping and scrambling:")
        for errors in ErrorMessages.messages:
            print(ErrorMessages.messages[errors])
    else:
        print("")
        print("No errors while creating files.")

    print("Please see folder {} for files.".format(competition_name_stripped))
    print("")

'''
T: only_one_competitor, reading_grouping_from_file_bool, two_sided_nametags, valid_cubecomps_link, get_registration_information = True
F: create_only_nametags, new_creation, reading_scrambling_list_from_file, create_scoresheets_second_rounds_bool, create_registration_file_bool, create_only_registration_file, read_only_registration_file, create_schedule, create_only_schedule, scrambler_signature, use_cubecomps_ids = False
'''
def fromGroupingFileOne(parser_args):
    print("hey there2")
    competitors_local = ''
    competitors_api_local = [] 
    scoresheet_competitor_name_local = ''
    EVENT_IDS_local = EVENT_IDS

    if parser_args.wca_registration:
        wca_info = parser_args.wca_registration
    else:
        wca_info = user_input.get_confirmation(
            "Used WCA registration for this competition? (y/n) "
        )
    if wca_info:
        print("Using WCA website information.")
    wca_password, wca_mail, competition_name, competition_name_stripped = apis.wca_registration(
        bool, parser_args
    )
    if parser_args.scrambler_signature:
        scrambler_signature = parser_args.scrambler_signature
    else:
        scrambler_signature = user_input.get_confirmation(
            "Add scrambler signature field to scorecards? (y/n)"
        )
    
    scoresheet_competitor_name_local = input("Competitor name or WCA ID: ")
    try:
        scoresheet_competitor_api = persons.get_wca_competitor(
            scoresheet_competitor_name_local
        )
        if scoresheet_competitor_api:
            scoresheet_competitor_name_local = scoresheet_competitor_api["person"]["name"]
    except KeyError:
        pass

    file_name, grouping_file_name = apis.competition_information_fetch(
        wca_info, True, False, False, parser_args
    )
    if not parser_args.use_access_token:
        competition_wcif_file = apis.get_wca_info(
            competition_name, competition_name_stripped, wca_password, wca_mail
        )
    else:
        competition_wcif_file = apis.get_wca_info(
            competition_name, competition_name_stripped, access_token
        )

    competitors_api, cubecomps_id, use_cubecomps_ids = apis.get_cubecomps_competition(
        False, competition_name, competition_name_stripped
    )

    ### always part 
    # Extract data from WCIF file
    wca_json = json.loads(competition_wcif_file)

    # Registration
    competitor_information_wca = analysis.get_registrations_from_wcif(
        wca_json,
        False,
        use_cubecomps_ids,
        competitors_local,
        competitors_api_local,
        True,
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
        continue_script = user_input.get_confirmation(
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

    if wca_info:
        registration_list = registration_list_wca
    ### end of always

    result_string, EVENT_IDS_local = analysis.get_grouping_from_file(
            grouping_file_name,
            EVENT_DICT,
            EVENT_IDS_local,
            True,
            scoresheet_competitor_name_local,
        )

    print("Creating scoresheets...")
    pdf_files.create_scoresheets(
        competition_name,
        competition_name_stripped,
        result_string,
        EVENT_IDS_local,
        event_info,
        EVENT_DICT,
        True,
        round_counter,
        competitor_information,
        scoresheet_competitor_name_local,
        scrambler_signature,
    )

    ### Throw error messages for entire script if errors were thrown
    if ErrorMessages.messages:
        print("")
        print("Notable errors while creating grouping and scrambling:")
        for errors in ErrorMessages.messages:
            print(ErrorMessages.messages[errors])
    else:
        print("")
        print("No errors while creating files.")

    print("Please see folder {} for files.".format(competition_name_stripped))
    print("")