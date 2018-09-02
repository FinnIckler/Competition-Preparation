'''
Multiple functions to log in on the WCA website and catch all necessary competition and competitor registration information
'''


from pdf_file_generation import *
from chromedriver_data import *
from db import WCA_Database

### Error handling for WCA website login errors
def error_handling_wcif(driver, competition_name, store_file, competition_page):
    if 'Not logged in' in competition_page:
        print('ERROR!!')
        print('While logging into WCA website, either WCA ID or password was wrong. Aborted script, please retry.')
        quit_program(wcif_file)
    elif 'Competition with id' in competition_page:
        print('ERROR!!')
        print('Competition with name ' + competition_name + ' not found on WCA website.')
        quit_program(wcif_file)
    elif 'Not authorized to manage' in competition_page:
        print('ERROR!!')
        print('You are not authorized to manage this competition. Please only select your competitions.')
        quit_program(wcif_file)
    elif "The page you were looking for doesn't exist." in competition_page:
        print('ERROR!!')
        print('Misstiped competition link, please enter correct link.')
        quit_program(wcif_file)
    else:
        if not os.path.exists(competition_name):
            os.makedirs(competition_name)
        with open(store_file, 'w', encoding='utf-8') as file_save:
            print(competition_page, file=file_save)


### 5 functions for login and saving necessary information from WCA website
def wca_registration_system():
    while True:
        registration_information_format = input('Use WCA website information? (y/n) ')
        print('')
        if registration_information_format.upper() in ('N', 'Y'):
            break
        else:   
            print("Wrong input, please enter 'y' or 'n'.")
            print('')

    if registration_information_format.upper() == 'Y':
        print('Using WCA website information.')
        return True
    else:
        return False

def get_file_name(id):
    while True:
        file_name = input('Enter ' + id + '-file name: ')
        file_name = file_name.replace('.csv', '').replace('.txt', '')
        file_name_csv = file_name + '.csv'
        file_name_txt = file_name + '.txt'
        if not os.path.isfile(file_name_csv) and not os.path.isfile(file_name_txt):
            print('File ' + file_name_txt + ' or ' + file_name_csv + ' not found. Please enter valid file name.')
        else:
            break
    if os.path.isfile(file_name_txt):
        return file_name_txt
    else:
        return file_name_csv
                
def competition_information_fetch(wca_info, only_scoresheets, two_sided_nametags, new_creation):
    file_name, grouping_file_name = '', ''
    if wca_info:
        if (two_sided_nametags and not new_creation) or only_scoresheets:
            grouping_file_name = get_file_name('grouping')
        print('Fechting events and registration information from WCA competition website...')
    
    if not wca_info:
        while True:
            file_name = input('Enter registration-file name: ')
            file_name = file_name.replace('.csv', '').replace('.txt', '')
            file_name_csv = file_name + '.csv'
            file_name_txt = file_name + '.txt'
            if not os.path.isfile(file_name_csv) and not os.path.isfile(file_name_txt):
                print('File ' + file_name_txt + ' or ' + file_name_csv + ' not found. Please enter valid file name.')
            else:
                break
        if os.path.isfile(file_name_txt):
            file_name = file_name_txt
        else:
            file_name = file_name_csv
        if only_scoresheets or (not new_creation and two_sided_nametags):
            grouping_file_name = "German Nationals 2018/GermanNationals2018Grouping.csv" #get_file_name('grouping')
    return (file_name, grouping_file_name)

def wca_registration(new_creation):
    wca_id = input('Your WCA ID: ')
    wca_password = getpass.getpass('Your WCA password: ')
    
    if new_creation:
        competition_name = input('Competition name: ')
        create_competition_folder(competition_name)
        competition_name_stripped = competition_name.replace(' ', '')
        wcif_file = competition_name + '/' + competition_name_stripped + '-grouping.txt'
        return (wca_id, wca_password, competition_name, competition_name_stripped, wcif_file)
    return (wca_id, wca_password)

def get_wca_info(wca_id, wca_password, competition_name, competition_name_stripped, file):
    print('Fetching rounds and group information from WCA competition website...')
    url = 'https://www.worldcubeassociation.org/users/sign_in'
    url2 = 'https://www.worldcubeassociation.org/api/v0/competitions/' + competition_name_stripped + '/wcif'
    
    driver = webdriver.Chrome(chromedriver_path, chrome_options=chrome_options)
    driver.get(url)
    
    u = driver.find_element_by_name('user[login]')
    u.send_keys(wca_id)
    p = driver.find_element_by_name('user[password]')
    p.send_keys(wca_password)
    p.send_keys(Keys.RETURN)
    driver.get(url2)
    wcif_file = competition_name + '/wcif_information.txt'
    
    competition_page = driver.find_element_by_xpath('html').text
    driver.close()
    driver.quit()    
    
    # error handling for wrong WCA website information and file-save if successful information fetch
    error_handling_wcif(driver, competition_name, wcif_file, competition_page)
    
    return wcif_file
    
def get_information(which_information):
    print(which_information)
    while True:
        input_information = input('')
        if input_information.upper() in ('N', 'Y'):
            break
        else:   
            print("Wrong input, please enter 'y' or 'n'.")
            print('')
                
    if input_information.upper() == 'Y':
        return True
    else:
        return False

def create_competition_folder(competition_name):
    if not os.path.exists(competition_name):
        os.makedirs(competition_name)
