import requests
import helper
from bs4 import BeautifulSoup
@helper.enforce_types
def fetch_player_agent_stats_by_id(id: int, agent_history_time: str="60d"):
    '''
    Fetches player's agent statistics by the id found in the URL.
    id: The id of the player, as assigned by vlr.gg
    agent_history_time: The amount of historical data needed, must be one of '30d', '60d', '90d', or 'all'
    
    Player info is returned in the following format:
    {
        "username": "{In Game Name}",
        "name": "{Full Name},
        
    }
    
    '''
    if agent_history_time not in ["30d", "60d", "90d", "all"]:
        raise ValueError("agent_history_time must be 30d, 60d, 90d, or all.")
    res = requests.get(f"https://www.vlr.gg/player/{str(id)}/?timespan={agent_history_time}")
    print(res.status_code)
    if "text/html" not in res.headers.get("Content-Type", ""):
        raise helper.InvalidContentTypeException(f"Expected text/html but got {res.headers.get("Content-Type", "")}")
    if res.status_code != 200 and res.status_code != 404:
        raise RuntimeError(f"Request failed with status code: {res.status_code}")
    if "Page not found" in res.text:
        raise helper.InvalidPlayerException(f"Player with id {str(id)} does not exist")
   
    soup = BeautifulSoup(res.text, "html.parser")
   
    data = {}
    
    name_tag = soup.find('h1', class_="wf-title")
    
    if name_tag:
        data["username"] = name_tag.get_text(strip=True)
    else:
        raise helper.NoNameException(f"Player with id {str(id)} has no username associated with them")

    name_tag = soup.find('h2', class_="player-real-name ge-text-light")
    
    if name_tag:
        data["name"] = name_tag.get_text(strip=True)
    else:
        raise helper.NoNameException(f"Player with id {str(id)} has no name associated with them")
    
    print(data)

fetch_player_agent_stats_by_id(9)
