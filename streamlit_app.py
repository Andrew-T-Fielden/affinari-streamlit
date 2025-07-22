import streamlit as st
import json

# Load data from JSON files
def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

base_profile = load_json('base_profile.json')
venues = load_json('venues.json')

# UI Sliders for context modifier
st.title("Affinari Context Explorer")

st.header("🔧 Context Modifiers")

context_modifier = {}
for k, v in base_profile.items():
    context_modifier[k] = st.slider(
        label=f"{k.replace('_', ' ').title()} Modifier",
        min_value=-1.0,
        max_value=1.0,
        value=0.0,
        step=0.1
    )

# Compute session profile
session_profile = {
    k: max(0.0, min(1.0, base_profile[k] + context_modifier.get(k, 0)))
    for k in base_profile
}

# Score matching
def match_score(user_profile, venue_profile):
    return sum(user_profile[k] * venue_profile.get(k, 0) for k in user_profile)

# Display session profile
st.header("🎯 Session Profile (after modifiers)")
st.json({k: round(v, 2) for k, v in session_profile.items()})

# Display venue match scores
st.header("🏪 Venue Match Scores")
scores = [(name, match_score(session_profile, profile)) for name, profile in venues.items()]
scores = sorted(scores, key=lambda x: x[1], reverse=True)

for name, score in scores:
    st.write(f"**{name}** — Score: {score:.2f}")
