### Module import
from modules import *
import helpers.helpers as helper
import apis
import information_analysis as analysis
import grouping_scrambling_functions as grouping_scrambling
import pdf_file_generation as pdf_files
from lib.parser import PreperationParser
from constants import EVENT_DICT, EVENT_IDS, MODE_HELP
from lib.utils import *
from lib.actions import Executor
from lib.api.wca import *


def operation1(parser_args):
    create_only_nametags, reading_scrambling_list_from_file, create_scoresheets_second_rounds_bool, reading_grouping_from_file_bool, only_one_competitor, create_only_registration_file, read_only_registration_file, create_only_schedule, scrambler_signature, use_cubecomps_ids, = (False for i in range(10))

    new_creation, create_registration_file_bool, create_schedule, get_registration_information, two_sided_nametags, valid_cubecomps_link,  = (True for i in range(6))

    scoresheet_competitor_name, cubecomps_id, competitors = '', '', ''
    competitors_api, scrambler_list, result_string = [], [], []

    EVENT_IDS_local = EVENT_IDS
    
    ### Evaluation of script selection and initialization
    # Get necessary information for new competition

    # Ran if program_type is 1
    if new_creation or create_only_nametags:
        if parser_args.wca_registration:
            wca_info = parser_args.wca_registration
        else:
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
        if not create_only_registration_file:
            if parser_args.two_sided:
                two_sided_nametags = parser_args.two_sided
            else:
                two_sided_nametags = get_confirmation(
                    "Create two-sided nametags? (grouping (and scrambling) information on the back) (y/n)"
                )
            if two_sided_nametags:
                print(
                    "Using WCA registration and event information for competition {}.".format(
                        competition_name
                    )
                )

            competitors_api, cubecomps_id, use_cubecomps_ids = apis.get_cubecomps_competition(
                create_only_nametags, competition_name, competition_name_stripped
            )

            if not create_only_nametags:
                if (parser_args.scrambler_signature):
                    scrambler_signature = parser_args.scrambler_signature
                else:
                    scrambler_signature = get_confirmation(
                        "Add scrambler signature field to scorecards? (y/n)"
                    )

        if create_only_nametags and not two_sided_nametags and not wca_info:
            get_registration_information = False
            read_only_registration_file = True

        if create_only_nametags and two_sided_nametags:
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
            create_only_nametags and two_sided_nametags,
            new_creation,
            parser_args,
        )

        if create_only_nametags and not two_sided_nametags and not wca_info:
            pass
        else:
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

    # Select grouping file if only nametags should be generated
    # Ran if program_type is 7 or 8 
    elif reading_grouping_from_file_bool:
        if parser_args.wca_registration:
            wca_info = parser_args.wca_registration
        else:
            wca_info = get_confirmation(
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
            scrambler_signature = get_confirmation(
                "Add scrambler signature field to scorecards? (y/n)"
            )
        if only_one_competitor:
            scoresheet_competitor_name = input("Competitor name or WCA ID: ")
            try:
                scoresheet_competitor_api = get_wca_competitor(
                    scoresheet_competitor_name
                )
                if scoresheet_competitor_api:
                    scoresheet_competitor_name = scoresheet_competitor_api["person"]["name"]
            except KeyError:
                pass
        file_name, grouping_file_name = apis.competition_information_fetch(
            wca_info, True, False, new_creation, parser_args
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
            create_only_nametags, competition_name, competition_name_stripped
        )

    # Get all information from wca competition (using WCIF) and collection information from WCA database export
    # Ran if program_type is 1, 7 or 8 
    # Ran always now! cause 3 (blanks) already caught
    if get_registration_information:
        # Extract data from WCIF file
        wca_json = json.loads(competition_wcif_file)

        # Registration
        competitor_information_wca = analysis.get_registrations_from_wcif(
            wca_json,
            create_scoresheets_second_rounds_bool,
            use_cubecomps_ids,
            competitors,
            competitors_api,
            only_one_competitor,
            scoresheet_competitor_name,
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

        ### Get data from csv-export
        # same as for the WCA registration, get competitor information from registration file (if used): name, WCA ID, date of birth, gender, country and events registered for
        if not wca_info:
            print("Open registration file...")
            use_csv_registration_file = True
            if not competitors_api:
                competitors_api = competitors
            analysis.column_ids, event_list, event_counter, competitor_information, all_data, wca_ids = analysis.get_registration_from_file(
                wca_json,
                file_name,
                new_creation,
                reading_grouping_from_file_bool,
                use_csv_registration_file,
                analysis.column_ids,
                competitor_information_wca,
                competitors,
                use_cubecomps_ids,
                competitors_api,
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

    ### Parse registration file
    # When is this being run?? True if something in first 1 case...
    if read_only_registration_file:
        use_csv_registration_file = False
        analysis.column_ids, event_list, event_counter, competitor_information, all_data, wca_ids = analysis.get_registration_from_file(
            wca_json,
            file_name,
            new_creation,
            reading_grouping_from_file_bool,
            use_csv_registration_file,
            analysis.column_ids,
            event_counter,
            competitor_information_wca,
            competitors,
            use_cubecomps_ids,
            competitors_api,
        )

    ### Create schedule (if exists on WCA website)
    # Ran if 1 and something happens, full_schedule comes back from analysis.get_schedule_from_wcif(wca_json)
    if create_schedule and full_schedule:
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
        if create_schedule:
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
            if create_only_schedule:
                sys.exit()
    elif create_schedule:
        print("")
        print(
            "ERROR!! No schedule found on WCA website. Script continues without creating schedule."
        )

    ### Create registration file (.csv)
    # Ran if program_type is 1
    if create_registration_file_bool:
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

        if create_only_registration_file:
            sys.exit()

    ### Create new string for grouping and add name + DOB
    # Ran if I dont fucking know
    if registration_list:
        result_string = helper.initiate_result_string(registration_list)

    ### Selection of necessary information from WCA database export. Information include:
    # - rankings for all events at competition
    # - competition count per competitor
    # - single and average rankings for 3x3x3 for each competitior
    # Ran if program_type is 1
    if new_creation:
        if wca_ids and event_list:
            print("Get necessary results from WCA website, this may take a few seconds...")
            competitor_information, ranking_single, competition_count = grouping_scrambling.get_competitor_results_from_wcif(
                event_list, wca_ids, competitor_information, create_only_nametags, wca_info
            )

    # Run grouping and scrambling
    # Ran if program_type is 1
    if new_creation:
        print("")
        print("Running grouping and scrambling...")
        result_string, scrambler_list = grouping_scrambling.run_grouping_and_scrambling(
            group_list,
            result_string,
            registration_list,
            analysis.column_ids,
            ranking_single,
            competition_count,
            EVENT_IDS_local,
            event_ids_wca,
            competitor_information,
            round_counter,
        )

        # Add dummy columns for events with < 5 scramblers
        for scrambler_id in range(0, len(scrambler_list)):
            while len(scrambler_list[scrambler_id]) < 7:
                scrambler_list[scrambler_id].append("dummy name")

        scrambler_list_sorted_by_schedule = grouping_scrambling.sort_scrambler_by_schedule(
            full_schedule, scrambler_list, round_counter
        )
        if scrambler_list_sorted_by_schedule:
            scrambler_list = scrambler_list_sorted_by_schedule
        print("Grouping and scrambling done.")

    # Get scrambler list from file if needed for nametags
    # Ran if I dont fucking know
    if reading_scrambling_list_from_file:
        with open(scrambling_file_name, "r", encoding="utf8") as f:
            reader = csv.reader(f)
            scrambler_list = list(reader)
        del scrambler_list[0:2]
        scrambler_list = helper.update_scrambler_list(scrambler_list)

    ### Save all results to separate files
    # Ran if program_type is 1
    if new_creation:
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
            create_only_nametags,
            result_string,
            EVENT_IDS_local,
            scrambler_list,
            EVENT_DICT,
            round_counter,
            group_list,
        )
        print("")
        print("Create scrambling and grouping file...")

        # Grouping file
        pdf_files.create_grouping_file(
            output_grouping, EVENT_IDS_local, EVENT_DICT, result_string
        )

        # Scrambling file
        pdf_files.create_scrambling_file(
            output_scrambling, competition_name, scrambler_list
        )
        print(
            "Scrambling and grouping successfully saved. Nametags compiled into PDF: {0:d} label(s) output on {1:d} page(s).".format(
                sheet.label_count, sheet.page_count
            )
        )
        print("")

    # Scoresheet file
    # EXCEPTION: no scoresheets created for 3x3x3 Fewest Moves
    # Ran if program_type is 1, 7, or 8
    if new_creation or reading_grouping_from_file_bool:
        if reading_grouping_from_file_bool:
            result_string, _local = analysis.get_grouping_from_file(
                grouping_file_name,
                EVENT_DICT,
                EVENT_IDS_local,
                only_one_competitor,
                scoresheet_competitor_name,
            )

        print("Creating scoresheets...")
        pdf_files.create_scoresheets(
            competition_name,
            competition_name_stripped,
            result_string,
            EVENT_IDS_local,
            event_info,
            EVENT_DICT,
            only_one_competitor,
            round_counter,
            competitor_information,
            scoresheet_competitor_name,
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

