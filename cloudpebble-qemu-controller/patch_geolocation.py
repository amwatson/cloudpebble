"""Replace pypkjs geolocation to use ip-api.com with client IP from env var."""
import os

GEOLOC_PATH = '/usr/local/lib/python3.11/site-packages/pypkjs/javascript/navigator/geolocation.py'

NEW_GET_POSITION = '''
    def _get_position(self, success, failure):
        import logging as _log
        try:
            ip = os.environ.get('PYPKJS_CLIENT_IP', '')
            url = 'http://ip-api.com/json/%s' % ip if ip else 'http://ip-api.com/json'
            _log.info("GEOLOC _get_position: ip=%r url=%s", ip, url)
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            _log.info("GEOLOC _get_position: response=%r", data)
            if data.get('status') != 'success':
                _log.warning("GEOLOC _get_position: ip-api returned status=%s", data.get('status'))
                if callable(failure):
                    self.runtime.enqueue(failure)
                return
            _log.info("GEOLOC _get_position: success lat=%s lon=%s city=%s", data.get('lat'), data.get('lon'), data.get('city'))
            self.runtime.enqueue(success, Position(self.runtime, Coordinates(self.runtime, data['lon'], data['lat'], 1000), round(time.time() * 1000)))
        except Exception as e:
            _log.exception("GEOLOC _get_position: failed: %s", e)
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
