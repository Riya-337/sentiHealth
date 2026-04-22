import requests
import time
from datetime import datetime

print(f"Start timestamp: {datetime.now().isoformat()}")
for _ in range(45):
    try:
        resp = requests.get("http://localhost:3000/patients?limit=500")
        print(f"{datetime.now().isoformat()} - Volume: {len(resp.content)} bytes")
    except:
        pass
    time.sleep(2)
print(f"End timestamp: {datetime.now().isoformat()}")
