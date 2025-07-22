import streamlit as st
import json
import os
from venue_manager import venue_management_view
from helpers import load_json, save_json, load_categorical_options

# -----------------------------
# LOADERS AND HELPERS
# -----------------------------

def match_score(user_profile, venue_profile):
    # Tags: required filter
    for tag, required in user_profile.get("tags", {}).items():
        if required == 1 and venue_profile.get("tags", {}).get(tag) != 1:
            return None  # disqualified

    score = 0.0

    # Scalars (dot product)
    for k, v in user_profile.get("scalars", {}).items():
        score += v * venue_profile.get("scalars", {}).get(k, 0)

    # Categorical overlap
    for cat, user_vals in user_profile.get("categoricals", {}).items():
        venue_vals = venue_profile.get("categoricals", {}).get(cat, [])
        if user_vals and venue_vals:
            overlap = set(user_vals) & set(venue_vals)
            if overlap:
                score += len(overlap) / len(user_vals)

    return score

# -----------------------------
# USER PROFILE HANDLING
# -----------------------------
def get_user_list():
    return [name for name in os.listdir('users') if os.path.isdir(os.path.join('users', name))]

def load_user_profile(username):
    path = f'users/{username}/base_profile.json'
    return load_json(path)

def save_user_profile(username, profile):
    path = f'users/{username}/base_profile.json'
    save_json(path, profile)

def create_new_user(username):
    os.makedirs(f'users/{username}', exist_ok=True)
    default_profile = load_json('defaults/base_profile.json')
    save_user_profile(username, default_profile)
    return default_profile

# -----------------------------
# VIEWS
# -----------------------------
def user_preferences_view(username):
    st.markdown("### ⚙️ Update Preferences")
    profile = load_user_profile(username)

    with st.expander("🔢 Scalar Preferences", expanded=True):
        for trait, value in profile.get("scalars", {}).items():
            label = trait.replace('_', ' ').title()
            profile["scalars"][trait] = st.number_input(label, 0, 10, int(value * 10), step=1)

    with st.expander("✅ Tags (Required)", expanded=False):
        for tag, value in profile.get("tags", {}).items():
            label = tag.replace('_', ' ').title()
            profile["tags"][tag] = 1 if st.checkbox(label, value == 1) else 0

    with st.expander("🎨 Categoricals", expanded=False):
        options = load_categorical_options()

        for cat, choices in options.items():
            selected = st.multiselect(f"{cat.replace('_', ' ').title()} (optional)", choices, default=profile.get("categoricals", {}).get(cat, []))
            profile.setdefault("categoricals", {})[cat] = selected

    if st.button("Save Preferences"):
        save_user_profile(username, profile)
        st.success("Preferences saved.")

def user_scenario_view(base_profile, username):
    st.markdown("### 🎯 Start a Scenario")
    venues = load_json('venues.json')
    template_dir = f'users/{username}/templates'
    os.makedirs(template_dir, exist_ok=True)

    template_files = [f for f in os.listdir(template_dir) if f.endswith(".json")]
    template_names = [os.path.splitext(f)[0] for f in template_files]
    selected_template = st.selectbox("📂 Load a scenario template:", ["None"] + template_names)
    if selected_template != "None":
        base_profile = load_json(os.path.join(template_dir, f"{selected_template}.json"))
        st.info(f"Loaded template: {selected_template}")

    session_profile = {"scalars": {}, "tags": {}, "categoricals": {}}

    with st.expander("🔢 Scalar Preferences (for this scenario)", expanded=True):
        for trait, value in base_profile.get("scalars", {}).items():
            label = trait.replace('_', ' ').title()
            session_profile["scalars"][trait] = st.number_input(label, 0, 10, int(value * 10), step=1, key=f"scalar_{trait}") / 10.0

    with st.expander("✅ Tags (Required)", expanded=False):
        for tag, value in base_profile.get("tags", {}).items():
            label = tag.replace('_', ' ').title()
            session_profile["tags"][tag] = 1 if st.checkbox(label, value == 1, key=f"tag_{tag}") else 0

    with st.expander("🎨 Categoricals", expanded=False):
        options = load_categorical_options()

        for cat, choices in options.items():
            selected = st.multiselect(f"{cat.replace('_', ' ').title()} (optional)", choices, default=base_profile.get("categoricals", {}).get(cat, []), key=f"cat_{cat}")
            session_profile["categoricals"][cat] = selected

    with st.expander("💾 Save this scenario as a template"):
        template_name = st.text_input("Template name")
        if st.button("Save Scenario Template"):
            if not template_name:
                st.warning("Please enter a name.")
            else:
                save_json(os.path.join(template_dir, f"{template_name}.json"), session_profile)
                st.success(f"Template '{template_name}' saved.")
                st.rerun()

    with st.expander("🎯 Scenario Profile", expanded=False):
        st.json(session_profile)

    # Match venues
    scores = []
    for name, profile in venues.items():
        s = match_score(session_profile, profile)
        if s is not None:
            scores.append((name, s))

    total_matches = len(scores)

    st.subheader("🏪 Venue Match Scores")
    if total_matches == 0:
        st.warning("No venues match your required tag preferences.")
    else:
        scores = sorted(scores, key=lambda x: x[1], reverse=True)
        shown = min(3, total_matches)
        st.markdown(f"**{total_matches} match{'es' if total_matches != 1 else ''} found, showing top {shown}:**")
        for name, score in scores[:shown]:
            st.write(f"**{name}** — Score: {score:.2f}")

def user_templates_view():
    st.markdown("### 🧩 Manage Templates")
    st.info("Template management features coming soon.")

# -----------------------------
# MAIN APP
# -----------------------------
st.set_page_config(page_title="Affinari Match Engine", layout="centered")
st.title("Affinari Test Engine")

st.header("Who are you today?")
user_type = st.radio("Choose your role:", ["Select...", "User", "Vendor"], index=0, horizontal=True)

if user_type == "User":
    st.divider()
    st.subheader("👤 Select or Create User")
    user_list = get_user_list()
    user_options = ["Create new user..."] + user_list
    default_index = 1 if len(user_list) == 1 else 0
    user_select = st.selectbox("Choose an existing user or create a new one:", user_options, index=default_index)

    if user_select == "Create new user...":
        new_username = st.text_input("Enter new username")
        if new_username:
            if new_username in user_list:
                st.error("This user already exists.")
            else:
                base_profile = create_new_user(new_username)
                st.success(f"User '{new_username}' created.")
                st.rerun()
    else:
        base_profile = load_user_profile(user_select)
        st.subheader("📋 User Menu")
        menu_choice = st.selectbox("What would you like to do?", [
            "Choose...",
            "Start a Scenario",
            "Update Preferences",
            "Manage Templates"
        ])

        if menu_choice == "Start a Scenario":
            user_scenario_view(base_profile, user_select)
        elif menu_choice == "Update Preferences":
            user_preferences_view(user_select)
        elif menu_choice == "Manage Templates":
            user_templates_view()
        else:
            st.warning("Please select a task to begin.")

elif user_type == "Vendor":
    st.divider()
    st.subheader("🧑‍🍳 Vendor Mode")
    vendor_choice = st.selectbox("Vendor options", [
        "Choose...", "Manage Venues"
    ])

    if vendor_choice == "Manage Venues":
        venue_management_view()
    else:
        st.info("Select an option to begin.")
else:
    st.warning("Please select your role to continue.")
