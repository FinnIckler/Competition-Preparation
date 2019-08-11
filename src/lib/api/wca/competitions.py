### Error handling for WCA website login errors
def error_handling_wcif(competition_name, competition_page):
    competition_name_stripped = competition_name.replace(' ', '')
    if 'Not logged in' in competition_page:
        print('ERROR!!')
        print('While logging into WCA website, either WCA ID or password was wrong. Aborted script, please retry.')
    elif 'Competition with id' in competition_page:
        print('ERROR!!')
        print('Competition with name {} not found on WCA website.'.format(competition_name))
    elif 'Not authorized to manage' in competition_page:
        print('ERROR!!')
        print('You are not authorized to manage this competition. Please only select your competitions.')
    elif "The page you were looking for doesn't exist." in competition_page:
        print('ERROR!!')
        print('Misstiped competition link, please enter correct link.')
    else:
        if not os.path.exists(competition_name_stripped):
            os.makedirs(competition_name_stripped)
        return None
    sys.exit()

# Get upcoming competitions of user
def get_upcoming_wca_competitions(password="",email="",access_token=""):
    start_date = str(datetime.datetime.today()).split()[0]
    url = 'https://www.worldcubeassociation.org/api/v0/competitions?managed_by_me=true&start={}'.format(start_date)
    
    if password != "":
        competition_wcif_info = wca_api(url, email, password)
    else:
        competition_wcif_info = wca_api(url, access_token)
    
    return competition_wcif_info.text

def get_wca_info(competition_name, competition_name_stripped, *args):
    print('Fetching information from WCA competition website...')
    url = 'https://www.worldcubeassociation.org/api/v0/competitions/{}/wcif'.format(competition_name_stripped)
    
    if len(args) == 2:
        wca_password = args[0]
        wca_mail = args[1]
    
        competition_wcif_info = wca_api(url, wca_mail, wca_password)
    else:
        access_token = args[0]
        competition_wcif_info = wca_api(url, access_token)
        
    # Error handling for wrong WCA website information and file-save if successful information fetch
    error_handling_wcif(competition_name, competition_wcif_info.text)
    
    return competition_wcif_info.text

# Simple request to get information about input competition name
def get_wca_competition(competition_name):
    url = 'https://www.worldcubeassociation.org/api/v0/competitions/{}'.format(competition_name.replace(' ', ''))

    competition_info = ''
    api_info = requests.get(url)
    try:
        competition_info = json.loads(api_info.text)
    except KeyError:
        return ''
    return competition_info

# Function to actually talk to WCA API and collect response information
def wca_api(request_url, *args):
    grant_url = 'https://www.worldcubeassociation.org/oauth/token'
    
    if len(args) == 2:
        wca_password = args[1]
        wca_mail = args[0]
        wca_headers = {'grant_type':'password', 'username':wca_mail, 'password':wca_password, 'scope':'public manage_competitions'}
        wca_request_token = requests.post(grant_url, data=wca_headers)
        try:
            wca_access_token = json.loads(wca_request_token.text)['access_token']
            wca_refresh_token = json.loads(wca_request_token.text)['refresh_token']
            with open('.secret', 'w') as secret:
                print(str(datetime.datetime.now()) + ' token:' + wca_access_token + ' refresh_token:' + wca_refresh_token, file=secret)
        except KeyError:
            print('ERROR!! Failed to get competition information.\n\n Given error message: {}\n Message:{}\n\nScript aborted.'.format(json.loads(wca_request_token.text)['error'],  json.loads(wca_request_token.text)['error_description']))
            sys.exit()
    else:
        wca_access_token = args[0]
    
    wca_authorization = 'Bearer ' + wca_access_token
    wca_headers2 = {'Authorization': wca_authorization}
    competition_wcif_info = requests.get(request_url, headers=wca_headers2)

    return competition_wcif_info