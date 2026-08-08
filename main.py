from datetime import datetime, date
import zmq

def home():
    print("🧳 Trip Packer")
    print("------------------------------")
    print("Your trip packing assistant to help you get ready for your trip!")
    print("⏱ Takes about 2 minutes to complete")
    print()
    print("1. New Trip")
    print("2. Saved Trips")
    print("3. Exit")
    print()

    choice = input("Choose Option and [enter]: ").strip()

    if choice == "1":
        enter_trip_dates()
    elif choice == "2":
        saved_trips()
    elif choice == "3":
        print("Goodbye! Safe travels! 🧳")
    else:
        print("Invalid option. Please try again.")
        home()

def get_next_choice():
    print()
    choice = input("Next [Y/Enter], Restart [R], Quit [Q]: ").strip().lower()

    if choice == "q":
        confirm = input("⚠️ Are you sure you want to quit? All current info will be lost. [Y/N]: ").strip().lower()
        if confirm == "y":
            print("Goodbye! Safe travels! 🧳")
            exit()
        else:
            return get_next_choice()

    return choice

def get_laundry():
    print("Laundry access during trip?")
    print("1. None")
    print("2. Mid-trip")
    print("3. Daily")
    choice = input("Choose 1, 2, or 3: ").strip()
    laundry_map = {"1": "none", "2": "mid-trip", "3": "daily"}
    if choice not in laundry_map:
        print("⚠️ Invalid option. Please try again.")
        return get_laundry()
    return laundry_map[choice]

def outfit_counts(duration, laundry):
    if laundry == "daily":
        tops = min(3, duration)
        bottoms = min(2, duration)
        underwear = min(3, duration)
    elif laundry == "mid-trip":
        tops = max(3, min(7, (duration + 1) // 2))
        bottoms = max(2, min(7, round(duration / 5)))
        underwear = max(3, (duration + 1) // 2)
    else:
        if duration <= 3:
            tops = duration
        elif duration <= 7:
            tops = 5
        else:
            tops = 7
        bottoms = min(tops, max(2, round(duration / 3)))
        underwear = duration
    return tops, bottoms, underwear

def get_location(destination):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.LINGER, 0)
    socket.setsockopt(zmq.RCVTIMEO, 60000)
    socket.connect("tcp://localhost:3010")

    socket.send_json({"query": destination})

    try:
        response = socket.recv_json()
    except zmq.Again:
        print("⚠️ Map-location service timed out. Continuing without location data.")
        return None
    finally:
        socket.close()
        context.term()

    if "error" in response:
        print(f"⚠️ {response['error']}")
        return None

    return response

def get_weather(latitude, longitude, departure, return_date):
    dep = datetime.strptime(departure, "%m/%d/%Y").strftime("%Y-%m-%d")
    ret = datetime.strptime(return_date, "%m/%d/%Y").strftime("%Y-%m-%d")

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.LINGER, 0)
    socket.setsockopt(zmq.RCVTIMEO, 60000)
    socket.connect("tcp://localhost:3015")

    socket.send_json({
        "latitude": latitude,
        "longitude": longitude,
        "start_date": dep,
        "end_date": ret
    })

    try:
        response = socket.recv_json()
    except zmq.Again:
        print("⚠️ Weather service timed out. Continuing without weather data.")
        return None
    finally:
        socket.close()
        context.term()

    if "error" in response:
        print(f"⚠️ {response['error']}")
        return None

    return response

def convert_temperature(celsius):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.LINGER, 0)
    socket.setsockopt(zmq.RCVTIMEO, 10000)
    socket.connect("tcp://localhost:3011")

    socket.send_json({"conversion": "c_to_f", "value": celsius})

    try:
        response = socket.recv_json()
    except zmq.Again:
        print("⚠️ Unit-converter service timed out. Skipping Fahrenheit conversion.")
        return None
    finally:
        socket.close()
        context.term()

    if response.get("status") != "success":
        print(f"⚠️ {response.get('message', 'Unit conversion failed.')}")
        return None

    return response["result"]

def build_weather_section(weather):
    if not weather:
        return []

    daily = weather.get("daily", [])
    if not daily:
        return []

    highs = [d["high"] for d in daily if d["high"] != "N/A"]
    lows = [d["low"] for d in daily if d["low"] != "N/A"]

    rainy = sum(1 for d in daily if any(k in d["conditions"] for k in ("Rain", "Drizzle", "Thunder")))
    snowy = sum(1 for d in daily if "Snow" in d["conditions"])

    avg_high = round(sum(highs) / len(highs)) if highs else "N/A"
    avg_low = round(sum(lows) / len(lows)) if lows else "N/A"

    section = ["\n🌤️ WEATHER FORECAST:"]
    if avg_high != "N/A" and avg_low != "N/A":
        line = f"  🌡️ Average: {avg_low}°C - {avg_high}°C"
        f_low = convert_temperature(avg_low)
        f_high = convert_temperature(avg_high)
        if f_low is not None and f_high is not None:
            line += f" / {round(f_low)}°F - {round(f_high)}°F"
        section.append(line)
    section.append(f"  ☔ Rain: {rainy} day(s)")
    section.append(f"  ❄️ Snow: {snowy} day(s)")
    return section

def get_clothing(weather, duration, travelers, laundry="none"):
    daily = weather.get("daily", []) if weather else []

    highs = [d["high"] for d in daily if d["high"] != "N/A"]
    lows = [d["low"] for d in daily if d["low"] != "N/A"]
    rainy = sum(1 for d in daily if any(k in d["conditions"] for k in ("Rain", "Drizzle", "Thunder")))
    snowy = sum(1 for d in daily if "Snow" in d["conditions"])

    avg_high = round(sum(highs) / len(highs)) if highs else None
    avg_low = round(sum(lows) / len(lows)) if lows else None

    if avg_high is None or avg_low is None:
        return None

    weather_summary = {
        "avg_high_c": avg_high,
        "avg_low_c": avg_low,
        "rainy_days": rainy,
        "snowy_days": snowy,
        "daily": [{"date": d["date"], "high": d["high"], "low": d["low"]} for d in daily if d["high"] != "N/A"]
    }
    travelers_summary = [{"type": t["type"], "age": t["age"], "sex": t["sex"]} for t in travelers]

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.LINGER, 0)
    socket.setsockopt(zmq.RCVTIMEO, 60000)
    socket.connect("tcp://localhost:3016")

    socket.send_json({
        "weather": weather_summary,
        "trip": {"duration_days": duration, "laundry": laundry},
        "travelers": travelers_summary,
    })

    try:
        response = socket.recv_json()
    except zmq.Again:
        print("⚠️ Clothing-recommender service timed out. Using local clothing logic.")
        return None
    finally:
        socket.close()
        context.term()

    if "error" in response:
        print(f"⚠️ {response['error']}")
        return None

    return response["clothing"]

def enter_trip_dates():
    print("\nEnter Trip Dates [Step 1/4]")
    print("------------------------------")
    print("Format: MM/DD/YYYY")
    print()

    departure = input("Departure Date: ").strip()
    return_date = input("Return Date: ").strip()

    try:
        dep = datetime.strptime(departure, "%m/%d/%Y")
        ret = datetime.strptime(return_date, "%m/%d/%Y")
        duration = (ret - dep).days

        if dep.date() < date.today():
            print("⚠️ Departure date cannot be in the past. Please try again.")
            enter_trip_dates()
            return

        if duration <= 0:
            print("⚠️ Return date must be after departure date. Please try again.")
            enter_trip_dates()
            return

        print(f"\nDeparture: {departure}")
        print(f"Return: {return_date}")
        print(f"Trip duration: {duration} days")

    except ValueError:
        print("⚠️ Invalid date format. Please use MM/DD/YYYY.")
        enter_trip_dates()
        return

    laundry = get_laundry()
    print(f"Laundry access: {laundry}")

    next_choice = get_next_choice()

    if next_choice == "r":
        enter_trip_dates()
    else:
        enter_destination(departure, return_date, duration, laundry)

def enter_destination(departure, return_date, duration, laundry):
    print("\nEnter Destination [Step 2/4]")
    print("------------------------------")
    print("Trip is...")
    print("1. Domestic (USA)")
    print("2. International")
    print()

    choice = input("Choose 1 or 2: ").strip()

    if choice == "1":
        city = input("City: ").strip()
        state = input("State: ").strip()
        destination = f"{city}, {state}"
        is_international = False
    elif choice == "2":
        city = input("City: ").strip()
        country = input("Country: ").strip()
        destination = f"{city}, {country}"
        is_international = True
    else:
        print("⚠️ Invalid option. Please try again.")
        enter_destination(departure, return_date, duration, laundry)
        return

    print(f"\nDestination confirmed: {destination}")

    print("🔍 Fetching location details...")
    loc_data = get_location(destination)

    if loc_data:
        print("Location details fetched successfully!")
        print(f"latitude: {loc_data.get('latitude', 'N/A')}, longitude: {loc_data.get('longitude', 'N/A')}")
        print(f"Timezone: {loc_data.get('timezone', 'N/A')}")
        print(f"Map Link: {loc_data.get('map_url', 'N/A')}")

    next_choice = get_next_choice()

    if next_choice == "r":
        enter_destination(departure, return_date, duration, laundry)
    else:
        traveler_profile(departure, return_date, duration, destination, is_international, loc_data, laundry)

def traveler_profile(departure, return_date, duration, destination, is_international, loc_data, laundry):
    print("\nTraveler Profile Builder [Step 3/4]")
    print("------------------------------")

    try:
        num_adults = int(input("Number of Adults: ").strip())
        num_children = int(input("Number of Children: ").strip())
    except ValueError:
        print("⚠️ Please enter a valid number.")
        traveler_profile(departure, return_date, duration, destination, is_international, loc_data, laundry)
        return

    travelers = []

    for i in range(num_adults):
        print(f"\n--- Adult {i+1} ---")
        age = input("Age: ").strip()
        sex = input("Sex (M/F/Other): ").strip()

        dietary = input("Dietary Restriction? (Y/N): ").strip().lower()
        dietary_info = ""
        if dietary == "y":
            dietary_info = input("Please describe: ").strip()

        special = input("Special Needs? (Y/N): ").strip().lower()
        special_info = ""
        if special == "y":
            special_info = input("Please list items with comma in between ex) item1, item2,...: ").strip()

        travelers.append({
            "type": "adult",
            "age": age,
            "sex": sex,
            "dietary": dietary_info,
            "special": special_info
        })

    for i in range(num_children):
        print(f"\n--- Child {i+1} ---")
        age = input("Age: ").strip()
        sex = input("Sex (M/F/Other): ").strip()

        dietary = input("Dietary Restriction? (Y/N): ").strip().lower()
        dietary_info = ""
        if dietary == "y":
            dietary_info = input("Please describe: ").strip()

        special = input("Special Needs? (Y/N): ").strip().lower()
        special_items = []
        if special == "y":
            print("Select items (choose one at a time):")
            special_map = {
                "1": "Diapers",
                "2": "Medications",
                "3": "Baby formula",
                "4": "Car seat",
                "5": "Other",
            }
            while True:
                print()
                for key, label in special_map.items():
                    print(f"{key}. {label}")
                print("0. Done")
                choice = input("> ").strip()
                if choice == "0":
                    break
                elif choice == "5":
                    custom = input("Describe the item: ").strip()
                    if custom:
                        special_items.append(custom)
                    else:
                        print("⚠️ No description entered.")
                elif choice in special_map:
                    item = special_map[choice]
                    if item not in special_items:
                        special_items.append(item)
                    else:
                        print("⚠️ Already added.")
                else:
                    print("⚠️ Invalid choice.")
                if special_items:
                    print(f"Added so far: {', '.join(special_items)}")
                print("Any more items needed?")
        special_info = ", ".join(special_items)

        travelers.append({
            "type": "child",
            "age": age,
            "sex": sex,
            "dietary": dietary_info,
            "special": special_info
        })

    print(f"\nTravelers: {num_adults} Adult(s), {num_children} Child(ren)")
    for i, t in enumerate(travelers):
        print(f"{t['type'].capitalize()} {i+1}: Age {t['age']}, {t['sex']}", end="")
        if t['dietary']:
            print(f", Dietary: {t['dietary']}", end="")
        if t['special']:
            print(f", Special: {t['special']}", end="")
        print()

    next_choice = get_next_choice()

    if next_choice == "r":
        traveler_profile(departure, return_date, duration, destination, is_international, loc_data, laundry)
    else:
        packing_list(departure, return_date, duration, destination, travelers, is_international, loc_data, laundry)

def packing_list(departure, return_date, duration, destination, travelers, is_international, loc_data, laundry):
    print("\nPacking List Result [Step 4/4]")
    print("------------------------------")
    print(f"Here is your packing list for your trip to {destination}!")
    print(f"Trip duration: {duration} days")
    print()

    weather = None
    if loc_data and loc_data.get("latitude") is not None and loc_data.get("longitude") is not None:
        print("🌤️ Fetching weather forecast...")
        weather = get_weather(loc_data["latitude"], loc_data["longitude"], departure, return_date)

def build_packing_list(duration, travelers, is_international, laundry, weather):
    packing = build_weather_section(weather)

    clothing = get_clothing(weather, duration, travelers, laundry)

    tops, bottoms, underwear = outfit_counts(duration, laundry)
    outfits = tops

    packing.append("👗 CLOTHING:")
    if clothing:
        packing.extend(f"  {item}" for item in clothing)
    else:
        has_female = any(t["sex"].upper() == "F" for t in travelers)
        has_male = any(t["sex"].upper() == "M" for t in travelers)

        if has_female:
            packing.append(f"  👚 {tops} tops")
            packing.append(f"  👖 {bottoms} bottoms (pants/skirts)")
            packing.append("  👗 1 dress")
            packing.append("  👟 comfortable walking shoes")
            packing.append("  👠 1 pair dressy shoes")
        if has_male:
            packing.append(f"  👔 {tops} shirts")
            packing.append(f"  👖 {bottoms} pants/shorts")
            packing.append("  👟 comfortable walking shoes")
            packing.append("  👞 1 pair dressy shoes")
        packing.append(f"  🧦 {underwear} pairs of underwear and socks")
        packing.append("  🧥 1 jacket/sweater")

    has_children = False
    children_items = []
    for t in travelers:
        if t["type"] == "child":
            has_children = True
            age = int(t["age"])
            if age < 3:
                children_items.append("  🍼 Diapers and baby wipes")
                children_items.append("  🍼 Baby formula/food")
                children_items.append(f"  👶 {outfits + 2} outfits (extra for accidents)")
            elif age <= 10:
                children_items.append("  🍎 Kids snacks")
                children_items.append("  🧸 Entertainment (toys, tablet)")
                children_items.append(f"  👕 {outfits + 1} outfits (extra change)")
            else:
                children_items.append("  📱 Charger/entertainment")
                children_items.append(f"  👕 {outfits} outfits")

    if has_children:
        packing.append("\n👶 CHILDREN'S ITEMS:")
        packing.extend(children_items)

    special_items = []
    for t in travelers:
        if t["special"]:
            items = t["special"].split(",")
            for item in items:
                special_items.append(f"  ⭐ {item.strip()}")

    if special_items:
        packing.append("\n⭐ SPECIAL NEEDS ITEMS:")
        packing.extend(special_items)

    packing.append("\n🎒 ESSENTIALS:")
    packing.append("  🧴 Toiletries (shampoo, toothbrush, etc.)")
    packing.append("  💊 Medications")
    packing.append("  📱 Phone + charger")
    packing.append("  💼 Suitcase/backpack")

    if is_international:
        packing.append("\n🌍 INTERNATIONAL TRAVEL:")
        packing.append("  🛂 Passport")
        packing.append("  💱 Local currency / notify your bank")
        packing.append("  🔌 Travel adapter/converter")
        packing.append("  📋 Copies of important documents")
        packing.append("  🗺️ Travel insurance documents")

    return packing

def packing_list(departure, return_date, duration, destination, travelers, is_international, loc_data, laundry):
    print("\nPacking List Result [Step 4/4]")
    print("------------------------------")
    print(f"Here is your packing list for your trip to {destination}!")
    print(f"Trip duration: {duration} days")
    print()

    weather = None
    if loc_data and loc_data.get("latitude") is not None and loc_data.get("longitude") is not None:
        print("🌤️ Fetching weather forecast...")
        weather = get_weather(loc_data["latitude"], loc_data["longitude"], departure, return_date)

    packing = build_packing_list(duration, travelers, is_international, laundry, weather)

    print("Your Packing List:")
    print("-" * 30)
    for item in packing:
        print(item)

    packing_list_menu(departure, return_date, duration, destination, travelers, is_international, loc_data, laundry, packing)

def packing_list_menu(departure, return_date, duration, destination, travelers, is_international, loc_data, laundry, packing):
    print()
    print("1. 💾 Save List")
    print("2. 🆕 New Trip")
    print("3. 🏠 Home")
    print()

    choice = input("Choose from options above: ").strip()

    if choice == "1":
        save_list(destination, departure, return_date, packing)
    elif choice == "2":
        confirm = input("⚠️ Going back will lose current list. Continue? [Y/N]: ").strip().lower()
        if confirm == "y":
            enter_trip_dates()
        else:
            packing_list_menu(departure, return_date, duration, destination, travelers, is_international, loc_data, laundry, packing)
    elif choice == "3":
        confirm = input("⚠️ Going back will lose current list. Continue? [Y/N]: ").strip().lower()
        if confirm == "y":
            home()
        else:
            packing_list_menu(departure, return_date, duration, destination, travelers, is_international, loc_data, laundry, packing)
    else:
        print("⚠️ Invalid option. Please try again.")
        packing_list_menu(departure, return_date, duration, destination, travelers, is_international, loc_data, laundry, packing)

def save_list(destination, departure, return_date, packing):
    filename = "saved_trips.txt"

    with open(filename, "a", encoding="utf-8") as f:
        f.write("===\n")
        f.write(f"destination={destination}\n")
        f.write(f"departure={departure}\n")
        f.write(f"return={return_date}\n")
        f.write(f"items={'^'.join(packing)}\n")

    print("⚠️ Will be saved locally on your device only.")
    print("✅ Saved!")
    print()

    input("Press [Enter] to go back to Home: ")
    home()

def saved_trips():
    print("\nSaved Trips:")
    print("------------------------------")

    try:
        with open("saved_trips.txt", "r", encoding="utf-8") as f:
            content = f.read()

        trips = content.strip().split("===\n")
        trips = [t for t in trips if t.strip()]

        if not trips:
            print("No saved trips yet!")
            print()
            input("Press [Enter] to go back to Home: ")
            home()
            return

        for i, trip in enumerate(trips):
            lines = trip.strip().split("\n")
            trip_data = {}
            for line in lines:
                if "=" in line:
                    key, value = line.split("=", 1)
                    trip_data[key] = value
            print(f"{i+1}. {trip_data.get('destination', 'Unknown')} | {trip_data.get('departure', '')} - {trip_data.get('return', '')}")

        print(f"{len(trips)+1}. 🏠 Back to Home")
        print()

        choice = input("Choose trip to view: ").strip()

        if choice == str(len(trips)+1):
            home()
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(trips):
                    view_saved_list(trips[idx])
                else:
                    print("⚠️ Invalid option. Please try again.")
                    saved_trips()
            except ValueError:
                print("⚠️ Invalid option. Please try again.")
                saved_trips()

    except FileNotFoundError:
        print("No saved trips yet!")
        print()
        input("Press [Enter] to go back to Home: ")
        home()

def view_saved_list(trip):
    print("\nViewing List")
    print("------------------------------")

    lines = trip.strip().split("\n")
    trip_data = {}
    for line in lines:
        if "=" in line:
            key, value = line.split("=", 1)
            trip_data[key] = value

    print(f"📍 {trip_data.get('destination', 'Unknown')}")
    print(f"📅 {trip_data.get('departure', '')} - {trip_data.get('return', '')}")
    print()
    print("Your Packing List:")
    print("-" * 30)

    items = trip_data.get('items', '').split('^')
    for item in items:
        print(item)

    print()
    print("1. 📋 View another trip")
    print("2. 🏠 Home")
    print()

    choice = input("Choose from the above option: ").strip()

    if choice == "1":
        saved_trips()
    else:
        home()

if __name__ == "__main__":
    home()
