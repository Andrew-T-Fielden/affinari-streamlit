import json

# -----------------------------
# LOAD USER PROFILE AND MODIFIERS FROM FILES
# -----------------------------

def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

base_profile = load_json('base_profile.json')
context_modifier = load_json('context_modifier.json')

# Compute session profile
session_profile = {
    k: max(0.0, min(1.0, base_profile[k] + context_modifier.get(k, 0)))
    for k in base_profile
}

# -----------------------------
# LOAD VENUE PROFILES FROM FILE
# -----------------------------

venues = load_json('venues.json')

# -----------------------------
# MATCHING FUNCTION
# -----------------------------

def match_score(user_profile, venue_profile):
    return sum(user_profile[k] * venue_profile.get(k, 0) for k in user_profile)

# -----------------------------
# CLI TEST
# -----------------------------

print("Session Profile (weighted):")
print(json.dumps({k: round(v, 2) for k, v in session_profile.items()}, indent=2))
print("\nVenue Match Scores:")

scores = []
for name, profile in venues.items():
    score = match_score(session_profile, profile)
    scores.append((name, score))

for name, score in sorted(scores, key=lambda x: x[1], reverse=True):
    print(f"{name:15}: {score:.2f}")
