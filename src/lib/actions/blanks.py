import pdf_file_generation as pdf_files


def blanks():
    scrambler_signature = True  # Will be mandatory soon(tm) anyways
    competition_name = input("Competition name or ID: (leave empty if not wanted) ")
    blank_sheets_round_name = input("Round name: (leave empty if not needed) ")
    print("Creating blank sheets...")
    pdf_files.create_blank_sheets(
        competition_name, scrambler_signature, blank_sheets_round_name
    )
