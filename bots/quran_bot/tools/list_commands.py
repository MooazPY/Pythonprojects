import os
import json
import sys
from pathlib import Path
from urllib import request, error

# Load .env from project root
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
        if k == 'DIS_TOKEN' or k == 'DIS_TOKEN':
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
    'User-Agent': 'DiscordBot (list-commands-script, 1.0)'
}

def get_json(url):
    req = request.Request(url, headers=headers)
    try:
        with request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode()
            return json.loads(data)
    except error.HTTPError as e:
        print('HTTP error', e.code, e.reason, file=sys.stderr)
        try:
            print(e.read().decode(), file=sys.stderr)
        except Exception:
            pass
        sys.exit(2)
    except Exception as e:
        print('Request failed:', e, file=sys.stderr)
        sys.exit(2)

me = get_json(f'{API_BASE}/users/@me')
app_id = me.get('id')
print('Bot user id:', app_id)

cmds = get_json(f'{API_BASE}/applications/{app_id}/guilds/{guild}/commands')
print('Guild commands:')
print(json.dumps(cmds, indent=2))

# Also show global commands
cmds_global = get_json(f'{API_BASE}/applications/{app_id}/commands')
print('\nGlobal commands:')
print(json.dumps(cmds_global, indent=2))
