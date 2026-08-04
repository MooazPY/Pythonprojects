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

if not token:
    print('DIS_TOKEN not found in .env', file=sys.stderr)
    sys.exit(2)
if not guild:
    print('DISCORD_GUILD_ID not found in .env', file=sys.stderr)
    sys.exit(2)

API_BASE = 'https://discord.com/api/v10'
headers = {
    'Authorization': f'Bot {token}',
    'User-Agent': 'DiscordBot (sync-script, 1.0)'
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

global_cmds = get_json(f'{API_BASE}/applications/{app_id}/commands')
print(f'Found {len(global_cmds)} global commands')

# Convert commands into payload suitable for creating guild commands
payload = []
for c in global_cmds:
    item = {
        'name': c.get('name'),
        'type': c.get('type',1),
        'description': c.get('description',''),
        'options': c.get('options') or []
    }
    payload.append(item)

print('Pushing to guild', guild)
res = put_json(f'{API_BASE}/applications/{app_id}/guilds/{guild}/commands', payload)
print('Guild now has', len(res), 'commands')
print(json.dumps(res, indent=2))
