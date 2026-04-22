import json
from datetime import datetime
import os

def review_queue():
    path = 'retraining/retraining_queue.json'
    if not os.path.exists(path):
        print("No retraining queue found.")
        return
    queue = json.load(open(path))
    unconfirmed = [e for e in queue if not e['human_confirmed']]
    print(f"\n{len(unconfirmed)} incidents pending review.\n")
    for i, entry in enumerate(unconfirmed):
        print(f"[{i+1}] {entry['incident_id']}")
        print(f"     Time: {entry['timestamp']}")
        print(f"     Why flagged: {entry['plain_english_explanation']}")
        decision = input("     Approve retraining? (y/n): ").strip()
        if decision == 'y':
            entry['human_confirmed'] = True
            entry['resolved_at'] = datetime.now().isoformat()
    json.dump(queue, open(path, 'w'), indent=2)
    print("Queue updated.")

if __name__ == '__main__':
    review_queue()
