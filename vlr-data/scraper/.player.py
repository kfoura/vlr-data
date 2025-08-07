import requests
import helper
from bs4 import BeautifulSoup
import sys
import os

# Nonsense to make import cache work
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

import cache

cache = cache.Cache()

# Cache key-value pairs expire after a day
cache_expiry = 86400

@helper.enforce_types
def fetch_player_agent_stats_by_id(id: int, agent_history_time: str="60d"):
    '''
    Fetches player's agent statistics by the id found in the URL.
    id: The id of the player, as assigned by vlr.gg
    agent_history_time: The amount of historical data needed, must be one of '30d', '60d', '90d', or 'all'
    
    Player info is returned in the following format:
    {
        
        "username": "{In Game Name}",
        "name": "{Full Name}",
        "agents": {
            "{Agent Name}": {
                "Use": "({Map count}) {Percentage used}%",
                "Rounds": "{Round Count}"
                "Rating": "{Rating}",
                "ACS": "{Average Combat Score}",
                "KD": "{Kill-death ratio}",
                "ADR": "{Average Damage per Round}",
                "KAST": "{Kill, Assist, Survived, Traded Percentage}%",
                "KPR": "{Kills Per Round}",
                "APR": "{Assists Per Round}",
                "FKPR": "{First Kills Per Round}",
                "FDPR": "{First Deaths Per Round}",
                "Kills": "{Total Kills}",
                "Assists": "{Total Assists}",
                "FK": "{Total First Kills}",
                "FD": "{Total First Deaths}"
            },
            ...
        }
        
    }
    
    '''
    # Checking to see whether or not cached information for this exists. If so, return that.
    cached_data = cache.get(f'player_agent {id}')
    create_cache = True
    if cached_data:
        create_cache = False
        data = cached_data.get(agent_history_time)
        if data:
            return data
    
    # Raise error incase the history time wanted isn't allowed
    if agent_history_time not in ["30d", "60d", "90d", "all"]:
        raise ValueError("agent_history_time must be 30d, 60d, 90d, or all.")
    
    res = requests.get(f"https://www.vlr.gg/player/{str(id)}/?timespan={agent_history_time}")
    # Raise errors if anything goes wrong with the request
    if "text/html" not in res.headers.get("Content-Type", ""):
        raise helper.InvalidContentTypeException(f"Expected text/html but got {res.headers.get("Content-Type", "")}")
    if res.status_code != 200 and res.status_code != 404:
        raise RuntimeError(f"Request failed with status code: {res.status_code}")
    if "Page not found" in res.text:
        raise helper.InvalidPlayerException(f"Player with id {str(id)} does not exist")
   
   # Setup scraper
    soup = BeautifulSoup(res.text, "html.parser")
    data = {}
    
    # Get the username of the player
    name_tag = soup.find('h1', class_="wf-title")
    if name_tag:
        data["username"] = name_tag.get_text(strip=True)
    else:
        raise helper.NoNameException(f"Player with id {str(id)} has no username associated with them")
    
    # Get the full name of the player
    name_tag = soup.find('h2', class_="player-real-name ge-text-light")
    if name_tag:
        data["name"] = name_tag.get_text(strip=True)
    else:
        raise helper.NoNameException(f"Player with id {str(id)} has no name associated with them")
    
    # Get information about their agents. If something goes wrong, we catch it and throw an error
    try:
        all_rows = soup.find_all('tr')[1:]
        data['agents'] = {}
        for row in all_rows:
            agent = row.find('img').get('alt', None)
            field_names = ['Use', 'Rounds', 'Rating', 'ACS', 'KD', 'ADR', 'KAST', 'KPR', 'APR', 'FKPR', 'FDPR', 'Kills', 'Deaths', 'Assists', 'FK', 'FD']
            tds = row.find_all('td')[1:]
            data['agents'][agent] = {field: td.get_text(strip=True) for field, td in zip(field_names, tds)}
                
    except:
        raise helper.DataNotFoundException("Data for one of more of the agent fields could not be found")
    
    # Create a key-value pair in the cache or update it if something doesn't exist
    if create_cache:
        cached_data = {f"{agent_history_time}": data}
    else: 
        cached_data[f"{agent_history_time}"] = data
    
    cache.set(f'player_agent {id}', cached_data, expires=cache_expiry)
    return data



@helper.enforce_types
def fetch_player_stats_by_match_by_id(id: int, by_map: bool=True):
    
    # Checking to see whether or not cached information for this exists. If so, return that.
    # cached_data = cache.get(f'player_matches_stats {id}')
    # if cached_data:
    #     return cached_data
    
    res = requests.get(f"https://vlr.gg/player/matches/{id}")
    
    if "text/html" not in res.headers.get("Content-Type", ""):
        raise helper.InvalidContentTypeException(f"Expected text/html but got {res.headers.get("Content-Type", "")}")
    if res.status_code != 200 and res.status_code != 404:
        raise RuntimeError(f"Request failed with status code: {res.status_code}")
    if "Page not found" in res.text:
        raise helper.InvalidPlayerException(f"Player with id {str(id)} does not exist")
    
    soup = BeautifulSoup(res.text, "html.parser")
    matches = []
    page_count = 1
    pages = soup.find('div', class_="action-container-pages").find_all('a')[-1].text
    if pages:
        page_count = int(pages)
    
    for i in range(page_count):
        all_matches = soup.find_all('a', class_="wf-card fc-flex m-item")
        for match in all_matches:
            matches.append(match['href'])
        res = requests.get(f"https://vlr.gg/player/matches/{id}/?page={i}")
        soup = BeautifulSoup(res.text, "html.parser")
    
    
    #def fetch_match_stats(player: str):
        
fetch_player_stats_by_match_by_id(15500)