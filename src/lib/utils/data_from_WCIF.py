import json, pycountry
from lib.api.wca.persons import get_wca_competitors
from constants import EVENT_DICT

# Input: Entire WCIF File for a competition
# Output: List of one dict per person, containing the attributes
# Name, Nationality, DEL?. ORG?, WCA_ID, NumComps, { 3x3A, 3x3S }, { BestEventName, BestEventWorldRank, BestEventType, BestEventResult }
def get_nametag_data(competition_wcif_file):
    wcif_json = json.loads(competition_wcif_file)
    persons_wcif = wcif_json['persons']
    ret = []

    WCA_IDs = []
    for person in persons_wcif:
        if person['wcaId']:
            WCA_IDs.append(person['wcaId'])
    
    persons_wca_api = get_wca_competitors(WCA_IDs)

    for person in persons_wcif:
        if person['registration']['status'] != 'accepted':
            continue
        
        curr = {
            'name' : person['name'],
            'nation' : pycountry.countries.get(alpha_2=person['countryIso2']).name,
            'delegate' : 'delegate' in person['roles'],
            'organizer' : 'organizer' in person['roles'] ,
            'wcaId' : person['wcaId'], # None if newcomer
            'gender' : person['gender']
        }
        
        # not a newcomer
        if person['wcaId'] != None:
            person_api_data = None
            for p in persons_wca_api:
                if person['wcaId'] == p['person']['wca_id']:
                    person_api_data = p
                    break
            
            curr['numComps'] = person_api_data['competition_count']

            _3x3 = {
                'single' : -1, 
                'average' : -1
            }
            best = {
                'ranking' : 10000000,
                'eventName' : '',
                'type' : '', # single | average
                'result' : -1
            }

            for pb in person['personalBests']:
                if pb['eventId'] == '333':
                    if pb['type'] == 'single':
                        _3x3['single'] = pb['best']
                    elif pb['type'] == 'average':
                        _3x3['average'] = pb['best']
                
                if pb['worldRanking'] < best['ranking']:
                    best['ranking'] = pb['worldRanking']
                    best['eventName'] = EVENT_DICT[pb['eventId']]
                    best['type'] = pb['type']
                    best['result'] = pb['best']
        
            curr['best'] = best
            curr['_3x3'] = _3x3

        ret.append(curr)
    
    return ret