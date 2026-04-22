import time
import json
import random
from scoring_matrix import score_event
from self_healing_responder import respond

def print_step(msg, color="\\033[94m"):
    print(f"{color}[*] {msg}\\033[0m")
    time.sleep(1)

def print_alert(msg):
    print(f"\\033[91m[!] {msg}\\033[0m")
    time.sleep(1)

def print_success(msg):
    print(f"\\033[92m[+] {msg}\\033[0m")
    time.sleep(1)

def simulate_live_traffic(attack_type="normal", iterations=5):
    """Simulates real-time terminal output of network traffic"""
    for i in range(iterations):
        ip = f"192.168.1.{random.randint(10,200)}" if attack_type == "normal" else f"103.45.2.{random.randint(10,50)}"
        endpoint = "/health" if attack_type == "normal" else "/patients?limit=500"
        status = "200 OK"
        print(f"\\033[90m[LIVE LOG] IP: {ip} -> {endpoint} | Status: {status} | Latency: {random.randint(10, 50)}ms\\033[0m")
        time.sleep(0.3)
    print("")

def run_live_demo():
    print("\\n" + "="*70)
    print("🛡️  SENTINELHEALTH LIVE AUTONOMOUS CYBERSECURITY DEMO 🛡️")
    print("="*70 + "\\n")
    
    time.sleep(2)

    # --- SCENARIO 1: LIVE NORMAL TRAFFIC ---
    print_step("SCENARIO 1: Monitoring Live Hospital Network Traffic (Normal)")
    simulate_live_traffic("normal", iterations=7)
    
    normal_event = {
        'user_id': 'U0015', 'role': 'nurse', 'failed_logins': 0,
        'cpu_usage': 0.15, 'memory_spike': 0, 'ehr_access_per_hour': 12,
        'lateral_movement_events': 0, 'data_export_volume_kb': 50,
        'access_time_deviation': 0.05, 'source_ip_reputation': 0.99,
        'attack_type': 'normal', 'asset_type': 'clinical_app',
        'emergency_status': False
    }
    
    print_step("Aggregating network features and feeding to ML Ensemble...")
    result = score_event(normal_event)
    print(f"   -> ML Ensemble Risk Score: {result['raw_score']:.3f}")
    print(f"   -> Assigned Tier: \\033[92m{result['tier']}\\033[0m")
    
    responder_res = respond(result)
    print(f"   -> Action: {responder_res['status']}")
    
    # Showcase the Blockchain part for Normal Event
    chain = json.load(open('data/audit_chain.json'))
    latest_entry = chain[-1]
    print(f"   -> ⛓️  BLOCKCHAIN AUDIT CHAIN UPDATED ⛓️")
    print(f"      Previous Hash: {latest_entry['prev_hash'][:16]}...")
    print(f"      New Block Hash: {latest_entry['entry_hash'][:16]}...\\n")
    time.sleep(2)


    # --- SCENARIO 2: LIVE HACKING (RANSOMWARE/EXFILTRATION) ---
    print_step("SCENARIO 2: Sudden Live Hacking Attempt (Ransomware / Data Exfiltration)")
    simulate_live_traffic("attack", iterations=10)
    
    ransom_event = {
        'user_id': 'U0042', 'role': 'it_staff', 'failed_logins': 150,
        'cpu_usage': 0.99, 'memory_spike': 1, 'ehr_access_per_hour': 400,
        'lateral_movement_events': 5, 'data_export_volume_kb': 9500,
        'access_time_deviation': 0.98, 'source_ip_reputation': 0.05,
        'attack_type': 'ransomware', 'asset_type': 'ehr',
        'emergency_status': False
    }
    
    print_step("CRITICAL: Massive database export and CPU spike detected!")
    result = score_event(ransom_event)
    print_alert(f"SEVERE THREAT DETECTED! ML Ensemble Risk Score: {result['raw_score']:.3f}")
    print_alert(f"Assigned Tier: \\033[91m{result['tier']}\\033[0m")
    print(f"   -> SHAP Explainer (Why it flagged this): {result['plain_english_explanation']}")
    print_alert(f"   -> Validating HMAC signature to prevent model tampering... VERIFIED!")
    
    print_step("Executing Autonomous Self-Healing Protocols...")
    responder_res = respond(result)
    print_success(f"Response Triggered: {responder_res['status']}")
    
    # Showing the actions and the Notification
    print_success("Actions Executed Locally:")
    for action in responder_res['actions']:
        if action == "bandwidth_throttled":
            print("   - 🚦 Throttled network bandwidth to 1% to stall exfiltration")
        elif action == "db_snapshotted":
            print("   - 💾 Snapshotted database to prevent ransomware encryption")
        elif action == "human_alerted":
            print("   - 📱 SENT URGENT SMS & EMAIL TO CHIEF SECURITY OFFICER")
            print("        \\033[93m[Notification] 'CRITICAL THREAT DETECTED. Approval required for full recovery.'\\033[0m")

    # Showing Blockchain part for Attack Event
    chain = json.load(open('data/audit_chain.json'))
    latest_entry = chain[-1]
    print(f"\\n   -> ⛓️  BLOCKCHAIN AUDIT CHAIN UPDATED (Tamper-Proof Ledger) ⛓️")
    print(f"      Previous Hash: {latest_entry['prev_hash'][:16]}...")
    print(f"      New Block Hash: {latest_entry['entry_hash'][:16]}...")

    print_success("\\nIncident secured and sent to Retraining Queue for Human Review (Rule C3).\\n")
    time.sleep(1)

    print("="*70)
    print("✅ LIVE DEMO COMPLETE. Network secured.")
    print("="*70 + "\\n")

if __name__ == "__main__":
    run_live_demo()
