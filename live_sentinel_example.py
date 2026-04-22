import os
import time
import json
import requests
from collections import defaultdict
from datetime import datetime, timedelta
from scoring_matrix import score_event
from self_healing_responder import respond

# --- CONFIGURATION ---
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

def send_telegram_message(msg):
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print(f"\033[93m[TELEGRAM SIMULATOR]\033[0m {msg}")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def wait_for_telegram_approval(prompt_msg):
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print(f"\033[93m[TELEGRAM SIMULATOR]\033[0m Waiting for approval... type 'YES' here:")
        return input(">> ").strip().upper() == "YES"
        
    send_telegram_message(prompt_msg)
    print(f"\033[94m[*] Waiting for Telegram reply ('YES') from admin...\033[0m")
    
    # Get the latest update ID to only read new messages
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    try:
        init_req = requests.get(url).json()
        last_update_id = 0
        if init_req.get("ok") and len(init_req["result"]) > 0:
            last_update_id = init_req["result"][-1]["update_id"]
    except:
        last_update_id = 0

    while True:
        time.sleep(2)
        try:
            resp = requests.get(f"{url}?offset={last_update_id + 1}&timeout=5").json()
            if resp.get("ok") and len(resp["result"]) > 0:
                for update in resp["result"]:
                    last_update_id = update["update_id"]
                    if "message" in update and "text" in update["message"]:
                        text = update["message"]["text"].strip().upper()
                        if text == "YES":
                            return True
                        elif text == "NO":
                            return False
        except Exception as e:
            pass

def tail_logs(filepath):
    """Generator to continuously yield new lines from a file."""
    with open(filepath, 'r') as f:
        f.seek(0, 2)  # Go to end of file
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            yield line

def run_live_sentinel():
    print("="*60)
    print("🛡️  SENTINELHEALTH LIVE WATCHDOG ACTIVATED 🛡️")
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("\033[91mWARNING: Telegram not configured. Running in local simulation mode.\033[0m")
    else:
        print("\033[92mTELEGRAM CONNECTED. Waiting for live web traffic...\033[0m")
    print("="*60)

    log_file = 'logs/events.jsonl'
    
    # Ensure log file exists before tailing
    os.makedirs('logs', exist_ok=True)
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f: pass

    # State tracking for sliding window
    traffic_window = []
    last_eval_time = time.time()
    locked_ips = set()

    for line in tail_logs(log_file):
        try:
            event = json.loads(line)
            traffic_window.append(event)
            print(f"\033[90m[LIVE TRAFFIC] {event['ip_address']} -> {event['endpoint']} | {event['response_time_ms']}ms\033[0m")
        except json.JSONDecodeError:
            continue

        current_time = time.time()
        # Evaluate every 5 seconds
        if current_time - last_eval_time > 5:
            last_eval_time = current_time
            
            # Prune window to last 30 seconds
            thirty_secs_ago_str = (datetime.utcnow() - timedelta(seconds=30)).isoformat()
            traffic_window = [e for e in traffic_window if e['timestamp'] >= thirty_secs_ago_str]

            if not traffic_window:
                continue

            # Aggregate per IP
            ip_stats = defaultdict(lambda: {'login': 0, 'patient': 0, 'total': 0})
            for e in traffic_window:
                if e['ip_address'] in locked_ips: continue
                ip_stats[e['ip_address']]['total'] += 1
                if e['endpoint'] == '/login': ip_stats[e['ip_address']]['login'] += 1
                if e['endpoint'] == '/patients': ip_stats[e['ip_address']]['patient'] += 1

            for ip, stats in ip_stats.items():
                if stats['total'] < 3: 
                    continue # Ignore very low traffic

                # Construct ML feature dict
                features = {
                    'user_id': 'U_LIVE',
                    'role': 'it_staff',
                    'failed_logins': stats['login'],
                    'cpu_usage': min(0.99, 0.1 + (stats['total'] / 100.0)),
                    'memory_spike': 1 if stats['total'] > 20 else 0,
                    'ehr_access_per_hour': stats['patient'] * 120, # Extrapolate 30s to 1 hour
                    'lateral_movement_events': 0,
                    'data_export_volume_kb': stats['patient'] * 200, # Approx 200kb per request
                    'access_time_deviation': 0.1,
                    'source_ip_reputation': 0.05 if stats['total'] > 50 else 0.9,
                    'attack_type': 'normal',
                    'asset_type': 'ehr',
                    'emergency_status': False
                }

                # Simple heuristic mapping for ML model expectations
                if features['failed_logins'] > 15:
                    features['attack_type'] = 'brute_force'
                elif features['ehr_access_per_hour'] > 300:
                    features['attack_type'] = 'exfiltration'

                result = score_event(features)
                
                if result['tier'] in ['Medium', 'High']:
                    print(f"\\n\033[91m[!] THREAT DETECTED FROM {ip} | Tier: {result['tier']} | Score: {result['raw_score']:.3f}\033[0m")
                    print(f"   -> SHAP Insights: {result['plain_english_explanation']}")
                    
                    responder_res = respond(result)
                    
                    if responder_res['status'] == 'WAITING_HUMAN_AUTH':
                        locked_ips.add(ip)
                        
                        alert_msg = (
                            f"🚨 SENTINELHEALTH CRITICAL ALERT 🚨\\n\\n"
                            f"Target: Database Server\\n"
                            f"Attacker IP: {ip}\\n"
                            f"Threat: {features['attack_type'].upper()}\\n"
                            f"Confidence Score: {result['raw_score']:.3f}\\n\\n"
                            f"System is holding containment. Reply 'YES' to authorize full lockdown and restore."
                        )
                        
                        start_wait = time.time()
                        approved = wait_for_telegram_approval(alert_msg)
                        resolve_time = time.time() - start_wait
                        
                        if approved:
                            print("\\n\033[92m[+] Authorization verified via Telegram. Restoring system.\033[0m")
                            final_res = respond(result, auth_token="admin_approved_123")
                            print(f"   -> Final Status: {final_res['status']}")
                            summary = (
                                f"✅ INCIDENT RESOLVED\\n"
                                f"Attack Tier: {result['tier'].upper()} ({features['attack_type'].upper()})\\n"
                                f"Resolution Time: {resolve_time:.1f} seconds\\n"
                                f"Attacker {ip} permanently blocked.\\n"
                                f"Database snapshotted and secured.\\n"
                                f"Incident added to retraining queue."
                            )
                            send_telegram_message(summary)
                        else:
                            print("\\n\033[93m[-] Authorization denied or timed out. System holding defensive posture.\033[0m")
                            send_telegram_message("❌ Action aborted. Defensive posture maintained.")

if __name__ == "__main__":
    run_live_sentinel()
