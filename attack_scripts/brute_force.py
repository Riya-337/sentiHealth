import requests
import time
from faker import Faker
from datetime import datetime

print(f"Start timestamp: {datetime.now().isoformat()}")
fake = Faker()
for _ in range(180):
    try:
        resp = requests.post("http://localhost:3000/login", json={"username": fake.user_name(), "password": fake.password()})
        print(f"{datetime.now().isoformat()} - Response: {resp.status_code}")
    except:
        pass
    time.sleep(0.5)
print(f"End timestamp: {datetime.now().isoformat()}")
