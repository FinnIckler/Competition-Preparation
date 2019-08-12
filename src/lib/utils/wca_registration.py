# Get user input for wca login (mail-address, password and competition name)
# All try-except cases were implemented for simple development and will not change the normal user input
def register(new_creation: bool, mail="", access_token="",competition=""):
    print('')
    print('To get the competition information (such as events and schedule), please enter your WCA login credentials.')
    if access_token == "":
        while True:
            if mail and "@" in mail:
                wca_mail = mail
            else:
                if mail and "@" not in mail:
                    print('')
                    print('Input for mail was wrong in parser options. Please enter correct mail address manually.')
                wca_mail = input('Your WCA mail address: ')
            # Validation if correct mail address was entered
            if '@' not in wca_mail:
                if wca_mail[:4].isdigit() and wca_mail[8:].isdigit():
                    print('Please enter your WCA account email address instead of WCA ID.')
                else:
                    print('Please enter valid email address.')
            else:
                break
        wca_password = getpass.getpass('Your WCA password: ')
    
    if new_creation:
        print('Getting upcoming competitions from WCA website...')
        if access_token != "":
            upcoming_competitions = sorted(json.loads(get_upcoming_wca_competitions(wca_password, wca_mail)), key=lambda x:x['start_date'])
        else:
            upcoming_competitions = sorted(json.loads(get_upcoming_wca_competitions(access_token)), key=lambda x:x['start_date'])
        counter = 1
        if upcoming_competitions:
            print('Please select competition (by number) or enter competition name:')
            for competition in upcoming_competitions:
                print('{}. {}'.format(counter, competition['name']))
                counter += 1
        not_valid_competition_name = True
        while not_valid_competition_name:
            if competition:
                competition_name = competition
            else:
                competition_name = input('Competition name or ID: ')
            if competition_name.isdigit():
                if int(competition_name) <= len(upcoming_competitions):
                    competition_name = upcoming_competitions[int(competition_name)-1]['name'].replace('-', ' ')
                    not_valid_competition_name = False
                else:
                    print('Wrong input, please select number or enter competition name/ID.')
            else:
                try:
                    get_wca_competition(competition_name)['name']
                    not_valid_competition_name = False
                except KeyError:
                    print('Competition {} not found on WCA website, please enter valid competition name.'.format(competition_name))
                    competition = ''

        create_competition_folder(competition_name)
        competition_name_stripped = competition_name.replace(' ', '')
        if access_token == "":
            return (wca_password, wca_mail, competition_name, competition_name_stripped)
        else:
            return (competition_name, competition_name_stripped)
    return (wca_password, wca_mail)