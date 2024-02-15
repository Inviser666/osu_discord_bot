import requests
import json


def makeScoreImage(mapID,player,date,mods,score,maxcombo,rank,count50,count100,count300,countmiss,countkatu,countgeki,pp):
    
    if rank == 'F':
        rank = 'D'
    JSON = {
            'mode': '0', # 0 = osu!std, 1 = osu!taiko, 2 = osu!catch, 3 = osu!mania
            'beatmap_id': mapID, # Osu Beatmap ID 
            'score': {
                'username': player,
                'date': date,
                'enabled_mods': mods, # Bitmask of mods, look https://github.com/ppy/osu-api/wiki#mods
                'score': score,
                'maxcombo': maxcombo,
                'rank': rank, # accepted types are XH, X, SH, S, A, B, C or D 
                'count50': count50,
                'count100': count100,
                'count300': count300,
                'countmiss': countmiss,
                'countkatu': countkatu,
                'countgeki': countgeki,
                'pp': pp #floats are always rounded to 2 decimal places
            }
        }
    JSONex = {
            'mode': '0', # 0 = osu!std, 1 = osu!taiko, 2 = osu!catch, 3 = osu!mania
            'beatmap_id': '2469345', # Osu Beatmap ID 
            'score': {
                'username': 'justaspin',
                'date': '2020-06-28 18:39:24',
                'enabled_mods': '600', # Bitmask of mods, look https://github.com/ppy/osu-api/wiki#mods
                'score': '4930126',
                'maxcombo': '464',
                'rank': 'SH', # accepted types are XH, X, SH, S, A, B, C or D 
                'count50': '0',
                'count100': '7',
                'count300': '330',
                'countmiss': '0',
                'countkatu': '6',
                'countgeki': '95',
                'pp': '1089.33' #floats are always rounded to 2 decimal places
            }
        }
    r = requests.post("https://lookatmysco.re/api/submit",json=JSON)
    my_json = r._content.decode('utf8')
    obj = json.loads(my_json)
    print(obj['image']['url'])
    return str(obj['image']['url'])