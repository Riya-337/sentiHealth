import time
import json
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

def run_demo():
    print("\\n" + "="*60)
    print("🛡️  SENTINELHEALTH AUTONOMOUS AI CYBERSECURITY DEMO 🛡️")
    print("="*60 + "\\n")
    
    time.sleep(2)

    # --- SCENARIO 1: NORMAL TRAFFIC ---
    print_step("SCENARIO 1: Normal Hospital Activity Monitoring")
    normal_event = {
        'user_id': 'U0015', 'role': 'nurse', 'failed_logins': 0,
        'cpu_usage': 0.15, 'memory_spike': 0, 'ehr_access_per_hour': 12,
        'lateral_movement_events': 0, 'data_export_volume_kb': 50,
        'access_time_deviation': 0.05, 'source_ip_reputation': 0.99,
        'attack_type': 'normal', 'asset_type': 'clinical_app',
        'emergency_status': False
    }
    
    print_step("Ingesting network telemetry: Nurse U0015 accessing EHR...")
    time.sleep(1)
    result = score_event(normal_event)
    print(f"   -> ML Ensemble Risk Score: {result['raw_score']:.3f}")
    print(f"   -> Assigned Tier: \\033[92m{result['tier']}\\033[0m")
    print(f"   -> Action: {result['recommended_action']}")
    
    responder_res = respond(result)
    print(f"   -> Autonomous Response: {responder_res['status']} \\n")
    time.sleep(2)

    # --- SCENARIO 2: BRUTE FORCE ATTACK ---
    print_step("SCENARIO 2: Medium Tier Threat - Credential Stuffing")
    brute_event = {
        'user_id': 'U0112', 'role': 'billing', 'failed_logins': 45,
        'cpu_usage': 0.45, 'memory_spike': 0, 'ehr_access_per_hour': 0,
        'lateral_movement_events': 0, 'data_export_volume_kb': 0,
        'access_time_deviation': 0.8, 'source_ip_reputation': 0.4,
        'attack_type': 'brute_force', 'asset_type': 'workstation',
        'emergency_status': False
    }
    
    print_step("Detecting multiple failed logins from an external IP...")
    result = score_event(brute_event)
    print_alert(f"Threat Detected! ML Ensemble Risk Score: {result['raw_score']:.3f}")
    print_alert(f"Assigned Tier: \\033[93m{result['tier']}\\033[0m")
    print(f"   -> SHAP Explainer: {result['plain_english_explanation']}")
    
    responder_res = respond(result)
    print_success(f"Autonomous Response Triggered: {responder_res['status']}")
    print_success(f"Actions Executed: {', '.join(responder_res['actions'])}\\n")
    time.sleep(2)

    # --- SCENARIO 3: RANSOMWARE EXFILTRATION ---
    print_step("SCENARIO 3: High Tier Threat - Ransomware / Exfiltration")
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
    print(f"   -> SHAP Explainer: {result['plain_english_explanation']}")
    
    print_step("Enacting Blast Radius Isolation (Rule SEC3)...")
    responder_res = respond(result)
    print_success(f"Autonomous Response Triggered: {responder_res['status']} (Awaiting Admin)")
    print_success(f"Actions Executed: {', '.join(responder_res['actions'])}")
    print_success("Incident sent to Retraining Queue for Human Review (Rule C3).\\n")
    time.sleep(1)

    print("="*60)
    print("✅ DEMO COMPLETE. System Audit Chain & Logs Updated.")
    print("="*60 + "\\n")

if __name__ == "__main__":
    run_demo()
