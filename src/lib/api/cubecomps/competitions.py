### Cubecomps API
# API to collect competitor information
# Mostly used to update registration id for all competitors
def get_competitor_information_from_cubecomps(cubecomps_id, competition_name):
    cubecomps_id = 'http://cubecomps.com/live.php?cid={}'.format(cubecomps_id)
    competitors_api = []
    try:
        cubecomps_id.split('?')[1].split('&')[0].split('=')[1]
    except IndexError:
        print('ERROR! Not a valid cubecomps link, script continues without cubecomps.com information.')
        return ([], False)

    comp_id = split_cubecomps_id(cubecomps_id, 1, 0, 1)
    cubecomps_api_url = 'https://m.cubecomps.com/api/v1/competitions/{}'.format(comp_id)
    cubecomps_api = requests.get(cubecomps_api_url).json()

    if cubecomps_api['name'].replace('-', ' ') != competition_name and cubecomps_api['name'].replace('-', '') != competition_name.replace(' ', '').replace('-', ' '):
        print('Cubecomps link does not match given competition name/ID. Script uses fallback to registration ids from WCA website!')
        use_cubecomps_ids = False
    else:
        for competitor in cubecomps_api['competitors']:
            competitors_api.append({'name': competitor['name'], 'competitor_id': int(competitor['id'])})
        use_cubecomps_ids = True
    return (competitors_api, use_cubecomps_ids)

# API to collect information for one round to determine next rounds' competitors
def get_round_information_from_cubecomps(cubecomps_id):
    advancing_competitors_next_round = 0
    competitors_api = []
    try:
        print('Get round information from cubecomps.com...')
        print('')
        comp_id = split_cubecomps_id(cubecomps_id, 1, 0, 1)
        event_id = split_cubecomps_id(cubecomps_id, 1, 1, 1)
        round_id = split_cubecomps_id(cubecomps_id, 1, 2, 1)
    except IndexError:
        print('ERROR! Not a valid cubecomps link, script aborted.')
        sys.exit()
    
    cubecomps_api_url = 'https://m.cubecomps.com/api/v1/competitions/{}/events/{}/rounds/{}'.format(comp_id, event_id, round_id)
    cubecomps_api = requests.get(cubecomps_api_url).json()
    competition_name = cubecomps_api['competition_name']
    competition_name_stripped = competition_name.replace(' ', '')
    create_competition_folder(competition_name)
    event_round_name = '{} - {}'.format(cubecomps_api['event_name'], cubecomps_api['round_name']) 
    
    for competitor in cubecomps_api['results']:
        if competitor['top_position']:
            advancing_competitors_next_round += 1
            competitors_api.append({'name': competitor['name'], 'competitor_id': int(competitor['competitor_id']), 'ranking': int(competitor['position'])})
            
    return(cubecomps_api, competitors_api, event_round_name, advancing_competitors_next_round, competition_name, competition_name_stripped)

def split_cubecomps_id(cubecomps_id, ind1, ind2, ind3):
    return cubecomps_id.split('?')[ind1].split('&')[ind2].split('=')[ind3]
    
# Get all competitions from cubecomps
def get_cubecomps_competitions():
    url = 'https://m.cubecomps.com/api/v1/competitions'
    url_past = 'https://m.cubecomps.com/api/v1/competitions/past'
    current_competitions = requests.get(url).json()
    past_competitions = requests.get(url_past).json()
    compbined_competitions = current_competitions.copy()
    compbined_competitions.update(past_competitions)
    return compbined_competitions

# Find cubecomps competition
def get_cubecomps_competition(create_only_nametags, competition_name, competition_name_stripped):
    cubecomps_id = ''
    competitors_api = []
    use_cubecomps_ids = False
    
    if not create_only_nametags:    
        competitions_cubecomps = get_cubecomps_competitions()
        for dates in competitions_cubecomps: 
            for competition in competitions_cubecomps[dates]:
                if competition_name_stripped[:-4] == competition['name'].replace(' ', '').replace('-', '') and competition_name_stripped[-4:] in competition['date']:
                    cubecomps_id = competition['id'].replace('-', '')
                    break
    if cubecomps_id:
        competitors_api, use_cubecomps_ids = get_competitor_information_from_cubecomps(cubecomps_id, competition_name)
        if not competitors_api:
            use_cubecomps_ids = False
            print('')
            print('INFO! The competition was found on cubecomps. However, no registration information was uploaded. Uploading them before using this script ensures to have matching ids on all scoresheets and in cubecomps (which eases scoretaking a lot!).')
            print('')
        else:
            use_cubecomps_ids = True
            print('')
            print('INFO! Script found registration information on cubecomps.com. These registration ids will be used for scoresheets.')
            print('')
    else:
        print('')
        print('INFO! Competition was not found on cubecomps. Using this script and upload registration information afterwards might cause faulty registration ids on scoresheets. Use on own risk.')
        print('')
    return (competitors_api, cubecomps_id, use_cubecomps_ids) 