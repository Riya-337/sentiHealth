import time
import json
import random
from scoring_matrix import score_event
from self_healing_responder import respond

def print_step(msg, color="\\033[94m"):
    print(f"\\n{color}[*] {msg}\\033[0m")
    time.sleep(1)

def print_alert(msg):
    print(f"\\033[91m[!] {msg}\\033[0m")
    time.sleep(1)

def print_success(msg):
    print(f"\\033[92m[+] {msg}\\033[0m")
    time.sleep(1)

def simulate_fast_traffic(ip, endpoint, iterations=15, speed=0.1):
    """Simulates high-speed hacking terminal output"""
    for _ in range(iterations):
        print(f"\\033[90m[LIVE] Incoming request from IP: {ip} -> {endpoint} | Status: 200 OK\\033[0m")
        time.sleep(speed)

def run_interactive_demo():
    print("\\n" + "="*75)
    print("🛡️  SENTINELHEALTH INTERACTIVE LIVE PRESENTATION 🛡️")
    print("="*75)

    # ---------------------------------------------------------
    # SCENARIO 1: LOW LEVEL EVENT (Workflow Disruption/False Alert)
    # ---------------------------------------------------------
    print_step("SCENARIO 1: Low Level Anomaly (Minor Deviation)")
    print("Simulating a nurse accessing files slightly outside normal hours...")
    
    low_event = {
        'user_id': 'U0188', 'role': 'nurse', 'failed_logins': 1,
        'cpu_usage': 0.20, 'memory_spike': 0, 'ehr_access_per_hour': 25,
        'lateral_movement_events': 0, 'data_export_volume_kb': 50,
        'access_time_deviation': 0.6, 'source_ip_reputation': 0.95,
        'attack_type': 'normal', 'asset_type': 'workstation',
        'emergency_status': False
    }
    
    result = score_event(low_event)
    print(f"   -> ML Risk Score: {result['raw_score']:.3f}")
    print(f"   -> Assigned Tier: \\033[92m{result['tier']}\\033[0m")
    
    responder_res = respond(result)
    print(f"   -> Action Taken: {responder_res['status']} (Silent Audit Logging, No disruption)\\n")
    time.sleep(2)


    # ---------------------------------------------------------
    # SCENARIO 2: LIVE HACKING (Trying to lock admin out / steal data)
    # ---------------------------------------------------------
    print_step("SCENARIO 2: Live High-Speed Attack (Exfiltration / DoS)")
    attacker_ip = "192.168.1.100" # Simulating the presentation IP
    print(f"Malicious actor at {attacker_ip} is launching a high-speed attack against the DB...")
    time.sleep(1)
    
    # Simulating the high-speed traffic
    simulate_fast_traffic(attacker_ip, "/api/patients/export", iterations=15, speed=0.05)
    
    ransom_event = {
        'user_id': 'U0042', 'role': 'admin', 'failed_logins': 200,
        'cpu_usage': 0.99, 'memory_spike': 1, 'ehr_access_per_hour': 900,
        'lateral_movement_events': 5, 'data_export_volume_kb': 15000,
        'access_time_deviation': 1.0, 'source_ip_reputation': 0.01,
        'attack_type': 'ransomware', 'asset_type': 'ehr',
        'emergency_status': False
    }
    
    print_step("SYSTEM TRIGGERED! Massive DB export and login flooding detected.")
    result = score_event(ransom_event)
    print_alert(f"SEVERE THREAT DETECTED! ML Ensemble Risk Score: {result['raw_score']:.3f}")
    print_alert(f"Assigned Tier: \\033[91m{result['tier']}\\033[0m")
    print(f"   -> SHAP Explainer: {result['plain_english_explanation']}\\n")
    
    # ---------------------------------------------------------
    # INTERACTIVE AUTHORIZATION (Human in the Loop)
    # ---------------------------------------------------------
    print_alert("Executing preliminary defense: Throttling bandwidth & snapshotting DB...")
    print_alert("SYSTEM HALTED. Admin authorization required for full account lock and system restoration.")
    
    print("\\n\\033[93m" + "-"*60)
    print("📱 URGENT MESSAGE RECEIVED ON AUTHORIZED DEVICE")
    print("From: SentiHealth AI Watchdog")
    print("Subject: CRITICAL AUTHORIZATION REQUIRED")
    print(f"Summary: The IP {attacker_ip} is attempting a critical breach.")
    print("Action Requested: Approve AI to fully restore the system?")
    print("-" * 60 + "\\033[0m\\n")

    # Waiting for the live presenter to type Yes or No
    decision = input(">> As the Authorized Person, do you approve this action? (Y/N): ").strip().upper()
    
    print("\\n")
    if decision == 'Y':
        # Pass a valid auth_token to simulate approval
        print_success("Authorization verified. Resuming SentiHealth autonomous restoration...")
        responder_res = respond(result, auth_token="admin-override-token-8842")
        print_success(f"Final Status: \\033[92m{responder_res['status']}\\033[0m")
        print_success(f"Actions Executed: {', '.join(responder_res['actions'])}")
        
        # Summary sent back to the admin
        print("\\n\\033[96m" + "-"*60)
        print("✉️  POST-INCIDENT SUMMARY SENT TO ADMIN:")
        print("- Threat Neutralized: Ransomware/Exfiltration Blocked.")
        print("- Attack Source Isolated.")
        print("- System Restored from Snapshot.")
        print("- Data Sent to Retraining Queue for Future Accuracy.")
        print("-" * 60 + "\\033[0m")
        
    else:
        # Do not pass an auth_token
        print_alert("Authorization denied or ignored.")
        responder_res = respond(result, auth_token=None)
        print_alert(f"Final Status: {responder_res['status']} (Awaiting further instructions)")
        print_alert("System remains locked down in defensive posture.")

    print("\\n" + "="*75)
    print("✅ PRESENTATION DEMO COMPLETE.")
    print("="*75 + "\\n")

if __name__ == "__main__":
    run_interactive_demo()
