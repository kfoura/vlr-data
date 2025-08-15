import requests
import helper
from bs4 import BeautifulSoup
import sys
import os
import time
import csv

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
        "team": "{Team Name}",
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
    
    name_tag = soup.find_all('div', class_="wf-card")[2]
    name_tag = name_tag.find('div', attrs={'style': 'font-weight: 500;'}).get_text(strip=True)
    if name_tag:
        data["team"] = name_tag
    else:
        data["team"] = None
        
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
def fetch_player_stats_by_match_by_id(id: int):
    
    # Checking to see whether or not cached information for this exists. If so, return that.
    cached_data = cache.get(f'player_matches_stats {id}')
    if cached_data:
        return cached_data
    player_username = fetch_player_agent_stats_by_id(id).get("username")
    team_name = fetch_player_agent_stats_by_id(id).get("team")
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
        divs = soup.find('div', class_="mod-dark")
        if divs:
            if divs.find_all('a', class_='wf-card fc-flex m-item'):
                for a in divs.find_all('a', class_='wf-card fc-flex m-item'):
                    matches.append(a['href'])
    matches = set(matches)
    result = []
    for match in matches:
        res = requests.get(f"https://vlr.gg{match}")
        if "text/html" not in res.headers.get("Content-Type", ""):
            raise helper.InvalidContentTypeException(f"Expected text/html but got {res.headers.get('Content-Type', '')}")
        if res.status_code != 200 and res.status_code != 404:
            raise RuntimeError(f"Request failed with status code: {res.status_code}")
        if "Page not found" in res.text:
            raise helper.InvalidMatchException(f"Match {match} does not exist")
        
        match_soup = BeautifulSoup(res.text, "html.parser")
        stat_div = match_soup.find('div', class_="vm-stats-container")
        maps = [div for div in stat_div.find_all('div') if div.get("data-game-id") and div.get("data-game-id") != "all"]
        maps = set(maps)
        for m in maps:
            data = {}
            map_stats = m.find("div", class_="vm-stats-game-header")
            team_stats = m.find_all("div", attrs={"style": "overflow-x: auto; margin-top: 15px; padding-bottom: 5px;"}) 
            agent = m.find_all("div", attrs={"style": "overflow-x: auto; margin-top: 15px; padding-bottom: 5px;"}) 
            
            team_stats_idx = [x for x in range(len(team_stats)) if player_username in team_stats[x].get_text()][0]
            try:
                agent = agent[team_stats_idx].find_all('td', class_="mod-player")
                agent = [x for x in agent if player_username.lower() in x.get_text().lower()][0]
                agent = agent.find_parent('tr')
                agent = agent.find('td', class_="mod-agents").find('img').get('title')
                data['agent'] = agent
            except AttributeError:
                continue
            team_stats = team_stats[team_stats_idx].get_text().split()
            idx = team_stats.index(player_username)
            try:
                stats = team_stats[idx:idx+40]
                data['username'] = stats[0]
                data['team'] = team_name
                data['all'] = {
                    "Rating": stats[2],
                    "ACS": stats[5],
                    "Kills": stats[8],
                    "Deaths": stats[12],
                    "Assists": stats[16],
                    "KAST": stats[22],
                    "ADR": stats[25],
                    "HS": stats[28],
                    "FK": stats[31],
                    "FD": stats[34]
                }
                data['attack'] = {
                    "Rating": stats[3],
                    "ACS": stats[6],
                    "Kills": stats[9],
                    "Deaths": stats[13],
                    "Assists": stats[17],
                    "KAST": stats[23],
                    "ADR": stats[26],
                    "HS": stats[29],
                    "FK": stats[32],
                    "FD": stats[35]
                }
                data['defend'] = {
                    "Rating": stats[4],
                    "ACS": stats[7],
                    "Kills": stats[10],
                    "Deaths": stats[14],
                    "Assists": stats[18],
                    "KAST": stats[24],
                    "ADR": stats[27],
                    "HS": stats[30],
                    "FK": stats[33],
                    "FD": stats[36]
                }
            except IndexError:
                continue
            #data['enemy_team']
            map_name = map_stats.find("div", class_="map").get_text().split()
            map_name = [x for x in map_name[:2] if x != "PICK"][0]
            team_names = map_stats.find_all("div", class_="team-name")
            team_names = [x.get_text(strip=True) for x in team_names]
            print(team_names)
            data['map'] = map_name
            data['enemy_team'] = team_names[0] if team_stats_idx == 1 else team_names[1]
            data['team'] = team_names[team_stats_idx]
            result.append(data)
    cache.set(f'player_matches_stats {id}', result, expires=cache_expiry)
        
# start = time.time()
# x = fetch_player_stats_by_match_by_id(15500)
# end = time.time()
# print(f"Time taken: {end - start} seconds")
# time_taken = end - start
# print(f"{100 * ((144.739 - time_taken) / 144.739)}%")

# def flatten_dict(d, parent_key='', sep='_'):
#     items = {}
#     for k, v in d.items():
#         new_key = f"{parent_key}{sep}{k}" if parent_key else k
#         if isinstance(v, dict):
#             items.update(flatten_dict(v, new_key, sep=sep))
#         else:
#             items[new_key] = v
#     return items

# print(x)
# flat_data = [flatten_dict(y) for y in x if x and y]

# fieldnames = flatten_dict(x[0]).keys()

# with open('player_stats.csv', 'w', encoding='utf-8') as f:
#     writer = csv.DictWriter(f, fieldnames=fieldnames)
#     writer.writeheader()
#     writer.writerows(flat_data)