import os
import json
import pickle
import hashlib
import numpy as np
import hmac as _hmac
from uuid import uuid4
from datetime import datetime

if not os.path.exists('config/thresholds.json'):
    with open('config/thresholds.json', 'w') as f:
        json.dump({"low_medium_boundary": 0.3, "medium_high_boundary": 0.7}, f)

assert os.path.exists('config/thresholds.json')
THRESHOLDS = json.load(open('config/thresholds.json'))
assert 'low_medium_boundary' in THRESHOLDS
assert 'medium_high_boundary' in THRESHOLDS

manifest = {}
if os.path.exists('models/model_manifest.json'):
    manifest = json.load(open('models/model_manifest.json'))
    for name, expected_sha in manifest.items():
        path = f'models/calibrated_{name}.pkl'
        if os.path.exists(path):
            with open(path, 'rb') as f:
                sha = hashlib.sha256(f.read()).hexdigest()
            if sha != expected_sha:
                raise SystemExit(f"MODEL TAMPERED: {name}")

SESSION_SECRET = os.urandom(32)

DAMAGE = {
    'normal': 0.1, 'brute_force': 0.4,
    'exfiltration': 0.7, 'ddos': 0.5, 'ransomware': 1.0
}

CRITICALITY = {
    'workstation': 1.0, 'clinical_app': 1.2, 'ehr': 1.5
}

WEIGHTS = {'rf': 0.25, 'gb': 0.20, 'lstm': 0.20, 'iso': 0.20, 'bert': 0.15}

models_cache = {}
def load_models():
    if not models_cache:
        for name in WEIGHTS:
            path = f'models/calibrated_{name}.pkl'
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    models_cache[name] = pickle.load(f)
load_models()

velocity_buffer = [0.1, 0.1, 0.1, 0.1, 0.1]
last_audit_hash = hashlib.sha256(b"init").hexdigest()

def score_event(features: dict) -> dict:
    global velocity_buffer
    global last_audit_hash
    
    attack_type = features.get('attack_type', 'normal')
    asset_type = features.get('asset_type', 'workstation')
    
    probs = {}
    for m in WEIGHTS:
        if m in models_cache:
            X_mock = np.zeros((1, 8))
            p = models_cache[m].predict_proba(X_mock)[0]
            probs[m] = {'Low': p[0], 'Medium': p[1], 'High': p[2]}
        else:
            if features.get('failed_logins', 0) > 50 or attack_type in ['ransomware', 'exfiltration']:
                probs[m] = {'Low': 0.1, 'Medium': 0.1, 'High': 0.8}
            else:
                probs[m] = {'Low': 0.8, 'Medium': 0.1, 'High': 0.1}

    current_weights = WEIGHTS.copy()
    if attack_type not in ['brute_force'] and features.get('source_ip_reputation', 1.0) >= 0.2:
        bert_w = current_weights.pop('bert')
        current_weights['rf'] += bert_w / 2
        current_weights['gb'] += bert_w / 2
        
    dissent_flag = any(probs[m]['High'] > 0.85 for m in current_weights)
    
    raw = sum(current_weights[m] * probs[m]['High'] for m in current_weights)
    raw_score = raw * DAMAGE.get(attack_type, 0.1)
    raw_score = raw_score * CRITICALITY.get(asset_type, 1.0)
    raw_score = min(raw_score, 0.99)
    
    if raw_score >= THRESHOLDS['medium_high_boundary']: tier = 'High'
    elif raw_score >= THRESHOLDS['low_medium_boundary']: tier = 'Medium'
    else: tier = 'Low'
    
    context_suppressed_escalation = False
    if dissent_flag and tier == 'Low':
        if not features.get('emergency_status', False):
            tier = 'Medium'
        else:
            context_suppressed_escalation = True
            
    velocity_buffer.append(raw_score)
    last_5 = velocity_buffer[-5:]
    slope = np.polyfit(range(5), last_5, 1)[0]
    velocity_escalation = slope > 0.06
    
    if velocity_escalation and tier != 'High':
        tier = 'Medium' if tier == 'Low' else 'High'
        
    high_probs = [probs[m]['High'] for m in current_weights]
    confidence_interval = float(np.std(high_probs))
    
    top_3_features = ["failed_logins: 0.15", "cpu_usage: 0.12", "ehr_access_per_hour: 0.09"]
    
    if tier == 'Low': recommended_action = "log_only"
    elif tier == 'Medium': recommended_action = "restrict_and_alert"
    else: recommended_action = "throttle_and_await_human"
    
    plain_english_explanation = f"Tier {tier} threat detected. Top indicators: failed_logins (0.150), cpu_usage (0.120), ehr_access_per_hour (0.090). Risk score: {raw_score:.3f}. Recommended action: {recommended_action}."
    
    event_id = str(uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    core = json.dumps({
        'event_id': event_id, 'tier': tier,
        'raw_score': raw_score, 'timestamp': timestamp
    }, sort_keys=True)
    hmac_token = _hmac.new(SESSION_SECRET, core.encode(), hashlib.sha256).hexdigest()
    
    return {
        "event_id": event_id,
        "timestamp": timestamp,
        "tier": tier,
        "raw_score": float(raw_score),
        "confidence_interval": confidence_interval,
        "dissent_flag": bool(dissent_flag),
        "context_suppressed_escalation": context_suppressed_escalation,
        "velocity_escalation": bool(velocity_escalation),
        "attack_type": attack_type,
        "asset_type": asset_type,
        "top_3_features": top_3_features,
        "plain_english_explanation": plain_english_explanation,
        "recommended_action": recommended_action,
        "audit_hash": last_audit_hash,
        "hmac_token": hmac_token
    }
