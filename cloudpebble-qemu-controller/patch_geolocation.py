"""Replace pypkjs geolocation to use ip-api.com with client IP from env var."""
import os

GEOLOC_PATH = '/usr/local/lib/python3.11/site-packages/pypkjs/javascript/navigator/geolocation.py'

NEW_GET_POSITION = '''
    def _get_position(self, success, failure):
        try:
            ip = os.environ.get('PYPKJS_CLIENT_IP', '')
            url = 'http://ip-api.com/json/%s' % ip if ip else 'http://ip-api.com/json'
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if data.get('status') != 'success':
                if callable(failure):
                    self.runtime.enqueue(failure)
                return
            self.runtime.enqueue(success, Position(self.runtime, Coordinates(self.runtime, data['lon'], data['lat'], 1000), round(time.time() * 1000)))
        except (requests.RequestException, KeyError, ValueError):
            if callable(failure):
                self.runtime.enqueue(failure)
'''

with open(GEOLOC_PATH, 'r') as f:
    content = f.read()

# Find and replace the _get_position method
import re
pattern = r'    def _get_position\(self.*?\n(?=    def _enabled)'
replacement = NEW_GET_POSITION.lstrip('\n') + '\n'
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

if new_content == content:
    print("WARNING: _get_position pattern not found, no changes made")
else:
    with open(GEOLOC_PATH, 'w') as f:
        f.write(new_content)
    print("Patched geolocation to use ip-api.com")
