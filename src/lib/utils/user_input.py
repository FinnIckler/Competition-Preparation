# Return if certain information should be used or not (by using y/n choice)
def get_confirmation(message):
    print(message)

    while True:
        confirmation = input('')
        if confirmation.upper() in ('N', 'Y'):
            break
        else:
            print('Wrong input, please enter \'y\' or \'n\'.')
            print('')

    return confirmation.upper() == 'Y'

def get_password_mail(): # TODO: check if mail already in parser_args
    import getpass
    while True:
        email = input('Please enter WCA Mail: \n')
        # Validation if correct mail address was entered
        if '@' not in email:
            if email[:4].isdigit() and email[8:].isdigit():
                print('Please enter your WCA account email address instead of WCA ID.')
            else:
                print('Please enter valid email address.')
        else:
            break
    password = getpass.getpass('Your WCA password: \n')

    return (password, email)

def select_upcoming_competition(jsonResponse):
    if len(jsonResponse) < 1:
        print("No upcoming compeititons!")
        return
    
    print('Please select competition (by number) or enter competition name:')
    counter = 1
    for competition in jsonResponse:
        print('{}. {}'.format(counter, competition['name']))
        counter += 1
    
    valid_string_entered = False
    while not valid_string_entered:
        competition_name = input('Competition name or ID: ')
    
        if competition_name.isdigit():
            if int(competition_name) <= len(jsonResponse):
                competition_name = jsonResponse[int(competition_name)-1]['name'].replace('-', ' ')
                valid_string_entered = True
            else:
                print('Wrong input, please select number or enter competition name/ID.')
        else:
            try:
                from api.wca import get_wca_competition
                get_wca_competition(competition_name)['name']
                valid_string_entered = True
            except KeyError:
                print('Competition {} not found on WCA website, please enter valid competition name.'.format(competition_name))
    
    competition_name_stripped = competition_name.replace(' ', '')

    return (competition_name, competition_name_stripped)