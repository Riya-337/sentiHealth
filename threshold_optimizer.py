import numpy as np
import json
from datetime import datetime
from cost_matrix import COST

def _single_threshold_search(val_scores: np.ndarray, val_labels: np.ndarray, cost_matrix: dict) -> dict:
    best_mh = 0.85
    best_high_recall = -1
    
    for t in np.arange(0.50, 0.86, 0.01):
        preds = val_scores >= t
        tp = np.sum((preds == True) & (val_labels == 'High'))
        fn = np.sum((preds == False) & (val_labels == 'High'))
        fp = np.sum((preds == True) & (val_labels != 'High'))
        tn = np.sum((preds == False) & (val_labels != 'High'))
        
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        
        if fpr <= 0.15 and recall > best_high_recall:
            best_high_recall = recall
            best_mh = t
            
    best_lm = 0.55
    best_low_spec = -1
    
    for t in np.arange(0.20, 0.56, 0.01):
        preds = val_scores >= t
        fp = np.sum((preds == True) & (val_labels == 'Low'))
        tn = np.sum((preds == False) & (val_labels == 'Low'))
        
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        
        if fpr <= 0.08 and spec > best_low_spec:
            best_low_spec = spec
            best_lm = t
            
    return {'low_medium_boundary': round(best_lm, 2), 'medium_high_boundary': round(best_mh, 2)}

def derive_thresholds(val_scores: np.ndarray, val_labels: np.ndarray, cost_matrix: dict) -> dict:
    results = []
    for seed in range(10):
        np.random.seed(seed)
        t = _single_threshold_search(val_scores, val_labels, cost_matrix)
        results.append(t)
        
    median_lm = np.median([r['low_medium_boundary'] for r in results])
    median_mh = np.median([r['medium_high_boundary'] for r in results])
    
    std_lm = np.std([r['low_medium_boundary'] for r in results])
    std_mh = np.std([r['medium_high_boundary'] for r in results])
    
    output = {
        "low_medium_boundary": float(median_lm),
        "low_medium_boundary_std": float(std_lm),
        "medium_high_boundary": float(median_mh),
        "medium_high_boundary_std": float(std_mh),
        "derived_on": datetime.now().isoformat(),
        "n_seeds": 10
    }
    
    with open('config/thresholds.json', 'w') as f:
        json.dump(output, f)
        
    return output

if __name__ == '__main__':
    val_scores = np.random.uniform(0, 1, 1000)
    val_labels = np.random.choice(['Low', 'Medium', 'High'], 1000)
    derive_thresholds(val_scores, val_labels, COST)
