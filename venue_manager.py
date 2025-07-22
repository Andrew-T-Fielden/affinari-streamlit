import streamlit as st
import json
import os
from helpers import (
    load_json, save_json,
    load_categorical_options,
    load_scalar_traits,
    load_tag_options
)

VENUE_FILE = 'venues.json'

def load_venues():
    if os.path.exists(VENUE_FILE):
        with open(VENUE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_venues(venues):
    with open(VENUE_FILE, 'w') as f:
        json.dump(venues, f, indent=2)

def venue_management_view():
    st.markdown("## 🏪 Venue Manager")
    venues = load_venues()

    all_venue_names = sorted(venues.keys())
    selected_name = st.selectbox("Select venue to edit", ["Add new venue..."] + all_venue_names)

    is_new = selected_name == "Add new venue..."
    venue_name = "" if is_new else selected_name
    venue_data = venues.get(selected_name, {
        "scalars": {},
        "tags": {},
        "categoricals": {}
    })

    venue_name = st.text_input("Venue name", value=venue_name)

    scalar_traits = load_scalar_traits()
    with st.expander("🔢 Scalars", expanded=True):
        for trait in scalar_traits:
            default_val = venue_data.get("scalars", {}).get(trait, 0.5)
            venue_data.setdefault("scalars", {})[trait] = st.slider(
                trait.replace('_', ' ').title(), 0.0, 1.0, default_val, 0.1
            )

    tag_options = load_tag_options()
    with st.expander("✅ Tags"):
        for tag in tag_options:
            default = venue_data.get("tags", {}).get(tag, 0)
            venue_data.setdefault("tags", {})[tag] = 1 if st.checkbox(
                tag.replace('_', ' ').title(), value=default == 1
            ) else 0

    with st.expander("🎨 Categoricals"):
        category_options = load_categorical_options()
        for cat, choices in category_options.items():
            selected = st.multiselect(
                cat.replace('_', ' ').title(),
                choices,
                default=venue_data.get("categoricals", {}).get(cat, [])
            )
            venue_data.setdefault("categoricals", {})[cat] = selected

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗒 Save Venue"):
            if not venue_name.strip():
                st.warning("Please enter a venue name.")
            else:
                venues[venue_name.strip()] = venue_data
                save_venues(venues)
                st.success(f"Venue '{venue_name}' saved.")
                st.rerun()

    with col2:
        if not is_new and st.button("🗑 Delete Venue"):
            venues.pop(selected_name, None)
            save_venues(venues)
            st.success(f"Venue '{selected_name}' deleted.")
            st.rerun()
