from datetime import date
import os

import streamlit as st

from main import (
    get_location,
    get_weather,
    build_packing_list,
)

SAVED_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "saved_trips.txt"
)

st.set_page_config(page_title="Trip Packer", page_icon="🧳", layout="centered")

st.title("🧳 Trip Packer")
st.caption("Personalized packing lists powered by four microservices.")

with st.sidebar:
    st.subheader("About")
    st.write(
        "Trip Packer generates personalized packing lists from trip dates, "
        "destination, and traveler profiles."
    )
    st.markdown("**Microservices (ZeroMQ)**")
    st.markdown("- **3010** Map & location")
    st.markdown("- **3011** Unit converter")
    st.markdown("- **3015** Weather forecast")
    st.markdown("- **3016** Clothing recommender")
    st.caption("Showcase built with Streamlit.")

    st.markdown("---")
    st.subheader("Saved trips")
    try:
        with open(SAVED_FILE, "r", encoding="utf-8") as f:
            saved_content = f.read()
    except FileNotFoundError:
        saved_content = ""
    trips = [t for t in saved_content.strip().split("===\n") if t.strip()]
    if not trips:
        st.caption("No saved trips yet.")
    else:
        for trip in trips:
            trip_data = {}
            for line in trip.strip().split("\n"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    trip_data[key] = value
            with st.expander(f"📍 {trip_data.get('destination', 'Unknown')}"):
                st.caption(
                    f"{trip_data.get('departure', '')} - {trip_data.get('return', '')}"
                )
                for item in trip_data.get("items", "").split("^"):
                    st.markdown(item)

# ---------- cached service calls ----------

@st.cache_data(ttl=1800, show_spinner=False)
def cached_location(destination):
    return get_location(destination)


@st.cache_data(ttl=1800, show_spinner=False)
def cached_weather(latitude, longitude, departure, return_date):
    return get_weather(latitude, longitude, departure, return_date)


@st.cache_data(ttl=1800, show_spinner=False)
def cached_packing(duration, travelers_tuple, is_international, laundry, weather):
    travelers = [
        {"type": t[0], "age": t[1], "sex": t[2], "dietary": t[3], "special": t[4]}
        for t in travelers_tuple
    ]
    return build_packing_list(duration, travelers, is_international, laundry, weather)


# ---------- session state ----------

if "step" not in st.session_state:
    st.session_state.step = 1


def go(step):
    st.session_state.step = step
    st.rerun()


def append_saved_trip(destination, departure, return_date, packing):
    with open(SAVED_FILE, "a", encoding="utf-8") as f:
        f.write("===\n")
        f.write(f"destination={destination}\n")
        f.write(f"departure={departure}\n")
        f.write(f"return={return_date}\n")
        f.write(f"items={'^'.join(packing)}\n")


def do_save(destination, departure, return_date, packing):
    append_saved_trip(destination, departure, return_date, packing)
    st.session_state["saved_msg"] = (
        f"Saved {destination} to saved_trips.txt"
    )


CHILD_SPECIAL_OPTIONS = [
    "Diapers",
    "Medications",
    "Baby formula",
    "Car seat",
    "Other",
]


def add_special_item(i):
    items = st.session_state.setdefault(f"c_special_{i}", [])
    choice = st.session_state.get(f"c_spec_select_{i}", "")
    if choice == "Other":
        custom = st.session_state.get(f"c_spec_other_{i}", "").strip()
        if custom:
            items.append(custom)
    elif choice and choice not in items:
        items.append(choice)


def undo_special_item(i):
    items = st.session_state.get(f"c_special_{i}", [])
    if items:
        items.pop()


# ---------- Step 1: trip dates ----------

if st.session_state.step == 1:
    st.subheader("Step 1: Trip Dates")
    col1, col2 = st.columns(2)
    with col1:
        departure = st.date_input(
            "Departure date",
            value=None,
            min_value=date.today(),
            format="MM/DD/YYYY",
        )
    with col2:
        return_date = st.date_input(
            "Return date",
            value=None,
            min_value=date.today(),
            format="MM/DD/YYYY",
        )

    laundry = st.radio(
        "Laundry access during the trip?",
        ["None", "Mid-trip", "Daily"],
        horizontal=True,
        help="Pack fewer clothes if you can wash them mid-trip.",
    )

    if departure and return_date:
        duration = (return_date - departure).days
        if duration <= 0:
            st.error("Return date must be after the departure date.")
        else:
            st.success(f"Trip duration: **{duration} days**")
            if st.button("Next", type="primary"):
                st.session_state.departure = departure
                st.session_state.return_date = return_date
                st.session_state.duration = duration
                st.session_state.laundry = laundry.lower()
                go(2)

# ---------- Step 2: destination ----------

elif st.session_state.step == 2:
    st.subheader("Step 2: Destination")
    trip_type = st.radio(
        "Trip is...", ["Domestic (USA)", "International"], horizontal=True
    )
    city = st.text_input("City")
    second = st.text_input("State" if trip_type == "Domestic (USA)" else "Country")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", use_container_width=True):
            go(1)
    with col2:
        if st.button("Fetch location details", type="primary", use_container_width=True):
            if not city.strip() or not second.strip():
                st.error("Please enter both city and state/country.")
            else:
                destination = f"{city.strip()}, {second.strip()}"
                with st.spinner("Fetching location details..."):
                    loc_data = cached_location(destination)
                st.session_state.destination = destination
                st.session_state.is_international = trip_type == "International"
                st.session_state.loc_data = loc_data
                if loc_data:
                    st.success("Location details fetched!")
                    st.write(
                        f"Coordinates: {loc_data.get('latitude', 'N/A')}, "
                        f"{loc_data.get('longitude', 'N/A')}"
                    )
                    st.write(f"Timezone: {loc_data.get('timezone', 'N/A')}")
                    map_url = loc_data.get("map_url")
                    if map_url:
                        st.write(f"Map: [{map_url}]({map_url})")
                else:
                    st.warning(
                        "Could not fetch location details - continuing without coordinates."
                    )

    if st.session_state.get("destination"):
        if st.button("Next", type="primary"):
            go(3)

# ---------- Step 3: travelers ----------

elif st.session_state.step == 3:
    st.subheader("Step 3: Travelers")
    num_adults = st.number_input("Number of adults", 0, 10, 1, key="num_adults")
    num_children = st.number_input("Number of children", 0, 10, 0, key="num_children")

    travelers = []
    for i in range(int(num_adults)):
        with st.container(border=True):
            st.markdown(f"**Adult {i + 1}**")
            age = st.number_input("Age", 1, 120, 30, key=f"a_age_{i}")
            sex = st.radio(
                "Sex", ["M", "F", "Other"], horizontal=True, key=f"a_sex_{i}"
            )
            dietary = st.checkbox("Has dietary restriction", key=f"a_diet_{i}")
            dietary_info = (
                st.text_input("Dietary restriction", key=f"a_diet_info_{i}")
                if dietary
                else ""
            )
            special = st.checkbox("Has special needs", key=f"a_spec_{i}")
            special_info = (
                st.text_input("Special items (comma separated)", key=f"a_spec_info_{i}")
                if special
                else ""
            )
        travelers.append(
            {
                "type": "adult",
                "age": str(age),
                "sex": sex,
                "dietary": dietary_info,
                "special": special_info,
            }
        )

    for i in range(int(num_children)):
        with st.container(border=True):
            st.markdown(f"**Child {i + 1}**")
            age = st.number_input("Age", 0, 17, 5, key=f"c_age_{i}")
            sex = st.radio(
                "Sex", ["M", "F", "Other"], horizontal=True, key=f"c_sex_{i}"
            )
            dietary = st.checkbox("Has dietary restriction", key=f"c_diet_{i}")
            dietary_info = (
                st.text_input("Dietary restriction", key=f"c_diet_info_{i}")
                if dietary
                else ""
            )
            st.markdown("**Special needs**")
            choice = st.selectbox(
                "Choose an item",
                CHILD_SPECIAL_OPTIONS,
                key=f"c_spec_select_{i}",
            )
            if choice == "Other":
                st.text_input("Describe the item", key=f"c_spec_other_{i}")
            st.button(
                "➕ Add item",
                on_click=add_special_item,
                args=(i,),
                key=f"c_spec_add_{i}",
            )
            special_items = st.session_state.get(f"c_special_{i}", [])
            if special_items:
                st.write(f"Added: {', '.join(special_items)}")
                st.button(
                    "Undo last",
                    on_click=undo_special_item,
                    args=(i,),
                    key=f"c_spec_undo_{i}",
                )
                st.caption("Any more items needed? Pick from the list above.")
            special_info = ", ".join(special_items)
        travelers.append(
            {
                "type": "child",
                "age": str(age),
                "sex": sex,
                "dietary": dietary_info,
                "special": special_info,
            }
        )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back", use_container_width=True):
            go(2)
    with col2:
        if int(num_adults) + int(num_children) == 0:
            st.warning("Add at least one traveler.")
        elif st.button(
            "Generate packing list", type="primary", use_container_width=True
        ):
            st.session_state.travelers = travelers
            go(4)

# ---------- Step 4: packing list ----------

elif st.session_state.step == 4:
    st.subheader("Your Packing List")
    destination = st.session_state.destination
    duration = st.session_state.duration
    laundry = st.session_state.laundry
    travelers = st.session_state.travelers
    is_international = st.session_state.is_international
    loc_data = st.session_state.get("loc_data")
    departure = st.session_state.departure
    return_date = st.session_state.return_date

    st.caption(
        f"Destination: {destination} | {duration} days | Laundry: {laundry}"
    )

    weather = None
    if (
        loc_data
        and loc_data.get("latitude") is not None
        and loc_data.get("longitude") is not None
    ):
        with st.spinner("Fetching weather forecast..."):
            weather = cached_weather(
                loc_data["latitude"],
                loc_data["longitude"],
                departure.strftime("%m/%d/%Y"),
                return_date.strftime("%m/%d/%Y"),
            )
        if weather and "error" in weather:
            st.warning(weather["error"])
            weather = None

    travelers_tuple = tuple(
        (t["type"], t["age"], t["sex"], t["dietary"], t["special"])
        for t in travelers
    )
    with st.spinner("Generating packing list..."):
        packing = cached_packing(
            duration, travelers_tuple, is_international, laundry, weather
        )

    st.markdown("---")
    for item in packing:
        st.markdown(item)
    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.button(
            "Save this trip",
            on_click=do_save,
            args=(
                destination,
                departure.strftime("%m/%d/%Y"),
                return_date.strftime("%m/%d/%Y"),
                packing,
            ),
            use_container_width=True,
        )
        if st.session_state.get("saved_msg"):
            st.success(st.session_state["saved_msg"])
    with col_b:
        if st.button("Start a new trip", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.cache_data.clear()
            st.rerun()
