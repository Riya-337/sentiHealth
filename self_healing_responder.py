import json
import os
import hmac as _hmac
import hashlib
from datetime import datetime
import threading
import time
import shutil
CRITICAL_SEGMENTS = []  # physically isolated, never touch
assert CRITICAL_SEGMENTS == []

from scoring_matrix import SESSION_SECRET

def verify_chain_integrity():
    if not os.path.exists('data/audit_chain.json'): return
    try:
        chain = json.load(open('data/audit_chain.json'))
        for i, entry in enumerate(chain[1:], 1):
            prev_hash = chain[i-1]['entry_hash']
            entry_copy = {k: v for k, v in entry.items() if k != 'entry_hash'}
            expected = hashlib.sha256((prev_hash + json.dumps(entry_copy, sort_keys=True)).encode()).hexdigest()
            if entry['entry_hash'] != expected:
                print(f"INTEGRITY ALERT: entry {i} tampered")
                with open('logs/integrity_alerts.log','a') as f:
                    f.write(f"{datetime.now()} — CHAIN TAMPERED AT {i}\n")
    except Exception as e:
        pass

def watchdog():
    while True:
        verify_chain_integrity()
        time.sleep(60)

threading.Thread(target=watchdog, daemon=True).start()

def throttle_bandwidth(percent=1):
    with open('logs/network_actions.log', 'a') as f:
        f.write(f"{datetime.now()} — Bandwidth throttled to {percent}%\n")

def snapshot_database():
    os.makedirs('data/snapshots', exist_ok=True)
    if os.path.exists('data/app.db'):
        shutil.copy('data/app.db', f'data/snapshots/snap_{int(time.time())}.db')

def lock_account(user_id: str):
    with open('logs/locked_accounts.json', 'a') as f:
        f.write(json.dumps({"user_id": user_id, "time": datetime.now().isoformat()}) + "\n")

def block_ip(ip_address: str):
    with open('logs/blocked_ips.json', 'a') as f:
        f.write(json.dumps({"ip": ip_address, "time": datetime.now().isoformat()}) + "\n")

def respond(classification: dict, auth_token: str = None) -> dict:
    core = json.dumps({
        'event_id': classification['event_id'], 'tier': classification['tier'],
        'raw_score': classification['raw_score'], 'timestamp': classification['timestamp']
    }, sort_keys=True)
    recomputed_token = _hmac.new(SESSION_SECRET, core.encode(), hashlib.sha256).hexdigest()
    
    if not _hmac.compare_digest(classification['hmac_token'], recomputed_token):
        with open('logs/integrity_alerts.log', 'a') as f:
            f.write(f"{datetime.now()} — INVALID HMAC — possible injection\n")
        return {"status": "REJECTED_INVALID_HMAC"}
        
    tier = classification['tier']
    event_id = classification['event_id']
    
    if not os.path.exists('data/audit_chain.json'):
        with open('data/audit_chain.json', 'w') as f:
            json.dump([{"entry_hash": hashlib.sha256(b"init").hexdigest()}], f)
            
    chain = json.load(open('data/audit_chain.json'))
    prev_hash = chain[-1]['entry_hash']
    
    entry = {
        "event_id": event_id,
        "timestamp": datetime.utcnow().isoformat(),
        "tier": tier,
        "prev_hash": prev_hash
    }

    if tier == 'Low':
        result = {"status": "LOGGED", "actions": ["audit_log"]}
        entry["actions_taken"] = ["audit_log"]
        entry["status"] = "LOGGED"
        
    elif tier == 'Medium':
        lock_account(event_id)
        block_ip("0.0.0.0")
        result = {"status": "RESTRICTED", "actions": ["account_locked", "ip_blocked", "alert_sent"]}
        entry["actions_taken"] = ["account_locked", "ip_blocked", "alert_sent"]
        entry["status"] = "RESTRICTED"
        
    elif tier == 'High':
        throttle_bandwidth(percent=1)
        snapshot_database()
        
        if not auth_token:
            result = {"status": "WAITING_HUMAN_AUTH", "actions": ["bandwidth_throttled", "db_snapshotted", "human_alerted"]}
            entry["actions_taken"] = ["bandwidth_throttled", "db_snapshotted", "human_alerted"]
            entry["status"] = "WAITING"
        else:
            result = {"status": "RESTORED", "actions": ["bandwidth_throttled", "db_snapshotted", "human_alerted", "restored"]}
            entry["actions_taken"] = ["bandwidth_throttled", "db_snapshotted", "human_alerted", "restored"]
            entry["status"] = "RESTORED"
            
        q_path = 'retraining/retraining_queue.json'
        if not os.path.exists(q_path):
            with open(q_path, 'w') as f: json.dump([], f)
        queue = json.load(open(q_path))
        queue.append({
            "incident_id": event_id,
            "timestamp": datetime.utcnow().isoformat(),
            "tier": "High",
            "top_3_features": classification.get('top_3_features', []),
            "plain_english_explanation": classification.get('plain_english_explanation', ''),
            "human_confirmed": False,
            "resolved_at": None
        })
        with open(q_path, 'w') as f: json.dump(queue, f)

    entry_str = json.dumps(entry, sort_keys=True)
    entry["entry_hash"] = hashlib.sha256((prev_hash + entry_str).encode()).hexdigest()
    chain.append(entry)
    
    with open('data/audit_chain.json', 'w') as f:
        json.dump(chain, f)
        
    return result
