import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker
from imblearn.over_sampling import SMOTE

def generate_dataset(n_rows=50000, output_path='data/sentinelhealth_dataset.csv') -> pd.DataFrame:
    fake = Faker()
    np.random.seed(42)
    random.seed(42)

    start_time = datetime(2023, 1, 1)
    timestamps = [start_time + timedelta(minutes=i) for i in range(n_rows)]
    
    roles = ['nurse', 'doctor', 'admin', 'billing', 'it_staff']
    users = [f"U{str(i).zfill(4)}" for i in range(1, 201)]
    user_roles = {u: random.choice(roles) for u in users}

    data = []
    
    emergency_blocks = set()
    total_emergency_minutes = int(n_rows * 0.05)
    while len(emergency_blocks) < total_emergency_minutes:
        block_start = random.randint(0, n_rows - 30)
        for i in range(30):
            emergency_blocks.add(block_start + i)

    attack_windows = []
    num_attack_windows = int(n_rows * 0.45 / 30)
    for _ in range(num_attack_windows):
        start = random.randint(0, n_rows - 45)
        duration = random.randint(15, 45)
        atype = random.choices(
            ['brute_force', 'exfiltration', 'ddos', 'ransomware'], 
            weights=[0.35, 0.40, 0.15, 0.10])[0]
        attack_windows.append({'start': start, 'end': start + duration, 'type': atype})

    for i in range(n_rows):
        ts = timestamps[i]
        hour = ts.hour
        is_weekend = ts.weekday() >= 5
        
        user_id = random.choice(users)
        role = user_roles[user_id]
        
        emergency_status = i in emergency_blocks
        
        attack_type = 'normal'
        for w in attack_windows:
            if w['start'] <= i <= w['end']:
                attack_type = w['type']
                break

        failed_logins = random.randint(0, 5)
        cpu_usage = random.uniform(0.1, 0.6)
        memory_spike = 0
        ehr_access_per_hour = random.randint(5, 30)
        lateral_movement_events = random.randint(0, 1)
        data_export_volume_kb = random.uniform(10, 500)
        access_time_deviation = random.uniform(0.0, 0.3)
        source_ip_reputation = random.uniform(0.8, 1.0)

        if (6 <= hour <= 7 and 45 <= ts.minute <= 59) or (18 <= hour <= 19 and 45 <= ts.minute <= 59) or \
           (hour == 7 and 0 <= ts.minute <= 15) or (hour == 19 and 0 <= ts.minute <= 15):
            failed_logins = int(failed_logins * 2.5)
            ehr_access_per_hour = int(ehr_access_per_hour * 2.5)

        if role in ['nurse', 'doctor']:
            ehr_access_per_hour = max(15, ehr_access_per_hour)
            
        if role == 'billing' and (is_weekend or hour < 5):
            ehr_access_per_hour = 0
            data_export_volume_kb = 0
            failed_logins = 0

        if attack_type == 'brute_force':
            failed_logins = random.randint(30, 200)
        elif attack_type == 'exfiltration':
            ehr_access_per_hour = random.randint(100, 400)
            data_export_volume_kb = random.uniform(2000, 10000)
        elif attack_type == 'ddos':
            cpu_usage = random.uniform(0.7, 1.0)
            memory_spike = 1
        elif attack_type == 'ransomware':
            cpu_usage = random.uniform(0.8, 1.0)
            memory_spike = 1
            lateral_movement_events = random.randint(3, 8)
            source_ip_reputation = random.uniform(0.0, 0.2)
            data_export_volume_kb = random.uniform(1000, 5000)

        tier_label = 'Low'
        if attack_type == 'normal':
            tier_label = 'Low'
        elif attack_type == 'brute_force':
            tier_label = 'Medium' if failed_logins < 50 else 'High'
        elif attack_type == 'exfiltration':
            tier_label = 'High'
        elif attack_type == 'ddos':
            tier_label = 'Medium' if cpu_usage < 0.8 else 'High'
        elif attack_type == 'ransomware':
            tier_label = 'High'

        data.append([
            ts, user_id, role, failed_logins, cpu_usage, memory_spike, 
            ehr_access_per_hour, lateral_movement_events, data_export_volume_kb, 
            access_time_deviation, source_ip_reputation, emergency_status, 
            attack_type, tier_label
        ])

    df = pd.DataFrame(data, columns=[
        'timestamp', 'user_id', 'role', 'failed_logins', 'cpu_usage',
        'memory_spike', 'ehr_access_per_hour', 'lateral_movement_events',
        'data_export_volume_kb', 'access_time_deviation',
        'source_ip_reputation', 'emergency_status', 'attack_type',
        'tier_label'
    ])

    # SMOTE IMPLEMENTATION (C7 enforced)
    network_features = ['failed_logins', 'cpu_usage', 'memory_spike',
                        'lateral_movement_events', 'source_ip_reputation',
                        'access_time_deviation']
    ehr_features = ['ehr_access_per_hour', 'data_export_volume_kb']
    
    sm_net = SMOTE(random_state=42)
    sm_ehr = SMOTE(random_state=42)
    
    X_net_res, y_res = sm_net.fit_resample(df[network_features], df['tier_label'])
    X_ehr_res, _ = sm_ehr.fit_resample(df[ehr_features], df['tier_label'])
    
    resampled_net = pd.DataFrame(X_net_res, columns=network_features)
    resampled_ehr = pd.DataFrame(X_ehr_res, columns=ehr_features)
    
    res_df = pd.concat([resampled_net, resampled_ehr, pd.Series(y_res, name='tier_label')], axis=1).sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Keep the initial valid columns and pad if necessary
    for col in df.columns:
        if col not in res_df.columns:
            res_df[col] = [df.iloc[i % len(df)][col] for i in range(len(res_df))]

    # Overrides for absolute rules
    res_df.loc[res_df['attack_type'] == 'ransomware', 'tier_label'] = 'High'
    res_df.loc[res_df['attack_type'] == 'exfiltration', 'tier_label'] = 'High'

    final_df = res_df.head(n_rows)
    final_df.to_csv(output_path, index=False)
    return final_df

if __name__ == '__main__':
    generate_dataset()
