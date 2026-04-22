COST = {
    "high_as_low": 10,      # missed ransomware → $7500/min damage
    "high_as_medium": 4,    # delayed High response
    "medium_as_low": 3,     # missed brute force
    "low_as_medium": 1,     # false alert, workflow disruption
    "low_as_high": 1,       # false emergency lockdown
    "medium_as_high": 2,    # unnecessary escalation
}
# Clinical justification: high_as_low=10 because average
# healthcare breach costs $10.93M (IBM 2024); hospital
# downtime costs $7,500/min (AHA 2024).
