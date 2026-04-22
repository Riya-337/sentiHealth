import requests
import time
import threading
from datetime import datetime

print(f"Start timestamp: {datetime.now().isoformat()}")
def send_req():
    try:
        start = time.time()
        requests.get("http://localhost:3000/health")
        print(f"{datetime.now().isoformat()} - Response time: {(time.time() - start)*1000:.2f}ms")
    except:
        pass

for _ in range(750):
    threading.Thread(target=send_req).start()
    time.sleep(90/750.0)
print(f"End timestamp: {datetime.now().isoformat()}")
