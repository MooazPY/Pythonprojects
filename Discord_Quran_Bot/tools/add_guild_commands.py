import os
import json
import sys
from pathlib import Path
from urllib import request, error

# Load .env
env_path = Path(__file__).resolve().parents[1] / '.env'
if not env_path.exists():
    print('No .env found at', env_path, file=sys.stderr)
    sys.exit(2)

token = None
guild = None
with open(env_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' not in line:
            continue
        k, v = line.split('=', 1)
        k = k.strip()
        v = v.strip().strip('"\'')
        if k == 'DIS_TOKEN':
            token = v
        if k == 'DISCORD_GUILD_ID':
            guild = v

if not token or not guild:
    print('DIS_TOKEN or DISCORD_GUILD_ID missing', file=sys.stderr)
    sys.exit(2)

API_BASE = 'https://discord.com/api/v10'
headers = {
    'Authorization': f'Bot {token}',
    'User-Agent': 'DiscordBot (add-commands-script, 1.0)'
}

from urllib.request import Request, urlopen

def get_json(url):
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except error.HTTPError as e:
        print('HTTP GET error', e.code, e.reason, file=sys.stderr)
        print(e.read().decode(), file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print('GET failed', e, file=sys.stderr)
        sys.exit(2)

def put_json(url, payload):
    data = json.dumps(payload).encode()
    req = Request(url, data=data, headers={**headers, 'Content-Type':'application/json'}, method='PUT')
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except error.HTTPError as e:
        print('HTTP PUT error', e.code, e.reason, file=sys.stderr)
        print(e.read().decode(), file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print('PUT failed', e, file=sys.stderr)
        sys.exit(2)

me = get_json(f'{API_BASE}/users/@me')
app_id = me.get('id')
print('Bot user id:', app_id)

# fetch current guild commands
current = get_json(f'{API_BASE}/applications/{app_id}/guilds/{guild}/commands')
print('Current guild command count:', len(current))

# desired commands to ensure exist
desired = [
    {
        'name': 'surah',
        'type': 1,
        'description': 'Show metadata for a chapter of the Quran',
        'options': [
            {'type': 4, 'name': 'surah', 'description': 'Chapter number', 'required': True}
        ]
    },
    {
        'name': 'surahinfo',
        'type': 1,
        'description': 'Show metadata for a chapter of the Quran',
        'options': [
            {'type': 4, 'name': 'surah', 'description': 'Chapter number', 'required': True}
        ]
    }
]

# merge: keep existing commands, add missing by name
existing_names = {c['name'] for c in current}
merged = list(current)  # existing command objects
for d in desired:
    if d['name'] not in existing_names:
        merged.append(d)

print('Pushing', len(merged), 'commands to guild')
res = put_json(f'{API_BASE}/applications/{app_id}/guilds/{guild}/commands', merged)
print('Guild now has', len(res), 'commands')
print(json.dumps(res, indent=2))
