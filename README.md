# vlr-data

A Python library for scraping and caching player and match statistics from [vlr.gg](https://vlr.gg), a popular Valorant esports statistics website.

## Features

- Fetch player agent statistics by player ID
- Fetch player match statistics by player ID
- Caching support (in-memory or Redis)
- Type enforcement and error handling

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/vlr-data.git
cd vlr-data
pip install -r requirements.txt
```

## Usage

```python
import cache
from scraper import helper, .player

cache = cache.Cache()
data = .player.fetch_player_agent_stats_by_id(12345)
print(data)
```

## Configuration

- To use Redis for caching, set the `REDIS_URL` environment variable in a `.env` file at the project root.

## Development

- All scraping logic is in the `scraper` directory.
- Caching logic is in `cache.py`.
- Type enforcement and custom exceptions are in `scraper/helper.py`.

## License

MIT License
