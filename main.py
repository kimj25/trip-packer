import time

def main():
    home()

def home():
    #home screen for the trip packing assistant
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
    # prompts user to continue to the next step, restart current step, or quit
    print()
    choice = input("Next [Y/Enter], Restart [R], Quit [Q]: ").strip().lower()
    
    if choice == "q":
        confirm = input("⚠️ Are you sure you want to quit? All current info will be lost. [Y/N]: ").strip().lower()
        if confirm == "y":
            print("Goodbye! Safe travels! 🧳")
            exit()
        else:
            return get_next_choice()  # ask again if user changes mind
    
    return choice

def enter_trip_dates():
    print("\nEnter Trip Dates [Step 1/4]")
    print("------------------------------")
    print("Format: MM/DD/YYYY")
    print()
    
    departure = input("Departure Date: ").strip()
    return_date = input("Return Date: ").strip()
    
    # Calculate trip duration
    from datetime import datetime
    try:
        dep = datetime.strptime(departure, "%m/%d/%Y")
        ret = datetime.strptime(return_date, "%m/%d/%Y")
        duration = (ret - dep).days
        
        if duration <= 0:
            # if return date is before or same as departure date, prompt user to re-enter
            print("⚠️ Return date must be after departure date. Please try again.")
            enter_trip_dates()
            return
            
        print(f"\nDeparture: {departure}")
        print(f"Return: {return_date}")
        print(f"Trip duration: {duration} days")
        
    except ValueError:
        # if the date format is invalid, prompt user to re-enter
        print("⚠️ Invalid date format. Please use MM/DD/YYYY.")
        enter_trip_dates()
        return
    
    next_choice = get_next_choice()
    
    if next_choice == "r":
        enter_trip_dates()  # restart current step
    else:
        enter_destination(departure, return_date, duration)  # proceed

def enter_destination(departure, return_date, duration):
    print("\nEnter Destination [Step 2/4]")
    print("------------------------------")
    print("Trip is...")
    print("1. Domestic (USA)")
    print("2. International")
    print()
    
    choice = input("Choose 1 or 2: ").strip()
    
    if choice == "1":
        # domestic trip
        city = input("City: ").strip()
        state = input("State: ").strip()
        destination = f"{city}, {state}"
        is_international = False
    elif choice == "2":
        # international trip
        city = input("City: ").strip()
        country = input("Country: ").strip()
        destination = f"{city}, {country}"
        is_international = True
    else:
        print("⚠️ Invalid option. Please try again.")
        enter_destination(departure, return_date, duration)
        return
    
    print(f"\nDestination confirmed: {destination}")
    
    next_choice = get_next_choice()
    
    if next_choice == "r":
        enter_destination(departure, return_date, duration)
    else:
        traveler_profile(departure, return_date, duration, destination, is_international)

def traveler_profile(departure, return_date, duration, destination, is_international):
    # collect traverler and traveler's group information
    print("\nTraveler Profile Builder [Step 3/4]")
    print("------------------------------")
    
    # get number of travelers
    try:
        num_adults = int(input("Number of Adults: ").strip())
        num_children = int(input("Number of Children: ").strip())
    except ValueError:
        print("⚠️ Please enter a valid number.")
        traveler_profile(departure, return_date, duration, destination)
        return
    
    travelers = []
    
    # collect adult info
    for i in range(num_adults):
        print(f"\n--- Adult {i+1} ---")
        age = input("Age: ").strip()
        sex = input("Sex (M/F/Other): ").strip()
        
        # dietary information
        dietary = input("Dietary Restriction? (Y/N): ").strip().lower()
        dietary_info = ""
        if dietary == "y":
            dietary_info = input("Please describe: ").strip()
        
        # custom needs
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
    
    # collect children info
    for i in range(num_children):
        print(f"\n--- Child {i+1} ---")
        age = input("Age: ").strip()
        sex = input("Sex (M/F/Other): ").strip()
        
        dietary = input("Dietary Restriction? (Y/N): ").strip().lower()
        dietary_info = ""
        if dietary == "y":
            dietary_info = input("Please describe: ").strip()
        
        special = input("Special Needs? (Y/N): ").strip().lower()
        special_info = ""
        if special == "y":
            print("1. Diapers")
            print("2. Medications")
            print("3. Other")
            special_choice = input("> ").strip()
            special_map = {"1": "Diapers", "2": "Medications", "3": "Other"}
            special_info = special_map.get(special_choice, "None")
        
        travelers.append({
            "type": "child",
            "age": age,
            "sex": sex,
            "dietary": dietary_info,
            "special": special_info
        })
    
    # show summary
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
        traveler_profile(departure, return_date, duration, destination, is_international)
    else:
        packing_list(departure, return_date, duration, destination, travelers, is_international)

def packing_list(departure, return_date, duration, destination, travelers, is_international):
    print("\nPacking List Result [Step 4/4]")
    print("------------------------------")
    print(f"Here is your packing list for your trip to {destination}!")
    print(f"Trip duration: {duration} days")
    print()
    
    packing = []
    
    # determine number of outfits based on duration
    if duration <= 3:
        outfits = duration
    elif duration <= 7:
        outfits = 5
    else:
        outfits = 7
    
    # clothes based on sex
    has_female = any(t["sex"].upper() == "F" for t in travelers)
    has_male = any(t["sex"].upper() == "M" for t in travelers)
    
    packing.append("👗 CLOTHING:")
    if has_female:
        packing.append(f"  👚 {outfits} tops")
        packing.append(f"  👖 {outfits} bottoms (pants/skirts)")
        packing.append(f"  👗 1 dress")
        packing.append(f"  👟 comfortable walking shoes")
        packing.append(f"  👠 1 pair dressy shoes")
    if has_male:
        packing.append(f"  👔 {outfits} shirts")
        packing.append(f"  👖 {outfits} pants/shorts")
        packing.append(f"  👟 comfortable walking shoes")
        packing.append(f"  👞 1 pair dressy shoes")
    
    packing.append(f"  🧦 {duration} pairs of underwear and socks")
    packing.append(f"  🧥 1 jacket/sweater")
    
    # children extras
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
    
    # special needs
    special_items = []
    for t in travelers:
        if t["special"]:
            items = t["special"].split(",")
            for item in items:
                special_items.append(f"  ⭐ {item.strip()}")
    
    if special_items:
        packing.append("\n⭐ SPECIAL NEEDS ITEMS:")
        packing.extend(special_items)
    
    # essentials
    packing.append("\n🎒 ESSENTIALS:")
    packing.append("  🧴 Toiletries (shampoo, toothbrush, etc.)")
    packing.append("  💊 Medications")
    packing.append("  📱 Phone + charger")
    packing.append("  💼 Suitcase/backpack")
    packing.append("  🗺️ Travel insurance documents")
    
    # international extras
    if is_international:
        packing.append("\n🌍 INTERNATIONAL TRAVEL:")
        packing.append("  🛂 Passport")
        packing.append("  💱 Local currency / notify your bank")
        packing.append("  🔌 Travel adapter/converter")
        packing.append("  📋 Copies of important documents")
    
    # print packing list
    print("Your Packing List:")
    print("-" * 30)
    for item in packing:
        print(item)
    
    # After displaying the packing list, provide options to save, start a new trip, or go home
    packing_list_menu(departure, return_date, duration, destination, travelers, is_international, packing)

def packing_list_menu(departure, return_date, duration, destination, travelers, is_international, packing):
    # helper function to display save/new trip/exit options after packing list is generated
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
            packing_list_menu(departure, return_date, duration, destination, travelers, is_international, packing)
    elif choice == "3":
        confirm = input("⚠️ Going back will lose current list. Continue? [Y/N]: ").strip().lower()
        if confirm == "y":
            home()
        else:
            packing_list_menu(departure, return_date, duration, destination, travelers, is_international, packing)
    else:
        print("⚠️ Invalid option. Please try again.")
        packing_list_menu(departure, return_date, duration, destination, travelers, is_international, packing)

def save_list(destination, departure, return_date, packing):
    # save packing list to a text file
    filename = "saved_trips.txt"
    
    with open(filename, "a") as f:
        f.write(f"===\n")
        f.write(f"destination={destination}\n")
        f.write(f"departure={departure}\n")
        f.write(f"return={return_date}\n")
        f.write(f"items={'^'.join(packing)}\n")

    # inform user that list will be saved locally
    print("⚠️ Will be saved locally on your device only.") 
    print("✅ Saved!")
    print()
    
    input("Press [Enter] to go back to Home: ")
    home()

def saved_trips():
    # display saved trips from the text file
    print("\nSaved Trips:")
    print("------------------------------")
    
    try:
        with open("saved_trips.txt", "r") as f:
            content = f.read()
        
        # parse saved trips
        trips = content.strip().split("===\n")
        trips = [t for t in trips if t.strip()]  # remove empty
        
        if not trips:
            print("No saved trips yet!")
            print()
            input("Press [Enter] to go back to Home: ")
            home()
            return
        
        # display trips
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
            # go back to home
            home()
        else:
            # view selected trip
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
        # if no trips have been saved yet, inform the user
        print("No saved trips yet!")
        print()
        input("Press [Enter] to go back to Home: ")
        home()

def view_saved_list(trip):
    # view saved packing list of the chosen trip
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
    main()