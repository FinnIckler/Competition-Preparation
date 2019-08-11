'''
T: create_schedule, create_only_schedule = True
F: create_scoresheets_second_rounds_bool, new_creation, create_registration_file_bool, create_only_registration_file, create_only_nametags, reading_scrambling_list_from_file, reading_grouping_from_file_bool, only_one_competitor, read_only_registration_file, scrambler_signature, use_cubecomps_ids = False 
'''
import apis
import json
from lib.utils import user_input
#from lib.api import *
import information_analysis as analysis
import grouping_scrambling_functions as grouping_scrambling
import pdf_file_generation as pdf_files
#from modules import *
from constants import EVENT_DICT
#from lib.utils import *

def printSchedule(parser_args):
    print("Yo welcome to schedule")
    competitors_local = ''
    competitors_api_local = [] 
    scoresheet_competitor_name_local = ''

    if parser_args.wca_registration:
        wca_info = parser_args.wca_registration
    else:
        wca_info = user_input.get_confirmation(
            "Used WCA registration for this competition? (y/n) "
        )
    if wca_info:
        print("Using WCA website information.")

    if not parser_args.use_access_token:
        wca_password, wca_mail, competition_name, competition_name_stripped = apis.wca_registration(
            True, parser_args
        )
    else:
        competition_name, competition_name_stripped = apis.wca_registration(
            True, parser_args
        )
    two_sided_nametags = False

    file_name, grouping_file_name = apis.competition_information_fetch(
        wca_info, False, two_sided_nametags, False, parser_args
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
        False,
        False,
        competitors_local,
        competitors_api_local,
        False,
        scoresheet_competitor_name_local
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
            False,
            False,
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
    
    if full_schedule:
        full_schedule = sorted(
            sorted(full_schedule, key=lambda x: x["event_name"]),
            key=lambda x: x["startTime"],
        )
    
        # Use schedule to determine the days each competitor registered for
        for schedule_event in full_schedule:
            events_per_day = analysis.get_events_per_day(schedule_event, events_per_day)
    
        registration_list = analysis.get_competitor_events_per_day(
            registration_list, analysis.column_ids, events_per_day
        )
    
        # Create schedule PDF
        pdf_files.create_schedule_file(
            competition_name,
            competition_name_stripped,
            full_schedule,
            event_info,
            competition_days,
            competition_start_day,
            timezone_utc_offset,
            analysis.formats,
            analysis.format_names,
            round_counter,
        )
        
        return
    else:
        print("")
        print(
            "ERROR!! No schedule found on WCA website. Script continues without creating schedule."
        )
    
    