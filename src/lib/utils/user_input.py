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