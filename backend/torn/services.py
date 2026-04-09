import requests
import os
import json
import redis
from django.conf import settings
from datetime import datetime, timedelta

try:
    redis_client = redis.StrictRedis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
except Exception:
    redis_client = None

class TornAPIService:
    BASE_URL = 'https://api.torn.com'
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('TORN_API_KEY')
    def _get_cache_key(self, endpoint, selections, id=None):
        return f"torn_api:{endpoint}:{id}:{selections}"
    def _fetch(self, endpoint, selections, id='', cache_ttl=60):
        if not self.api_key:
            return {}
        cache_key = self._get_cache_key(endpoint, selections, id)
        if redis_client:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        url = f"{self.BASE_URL}/{endpoint}/{id}?selections={selections}&key={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'error' not in data and redis_client:
                redis_client.setex(cache_key, cache_ttl, json.dumps(data))
            return data
        return {}
    def get_faction_members(self, faction_id=''):
        return self._fetch('faction', 'basic,positions', id=faction_id, cache_ttl=60)
    def get_chain_data(self, faction_id=''):
        return self._fetch('faction', 'chain', id=faction_id, cache_ttl=30)
    def get_war_data(self, faction_id=''):
        return self._fetch('faction', 'crimes,upgrades', id=faction_id, cache_ttl=30)
    def get_member_stats(self, player_id):
        return self._fetch('user', 'profile,personalstats', id=player_id, cache_ttl=60)
