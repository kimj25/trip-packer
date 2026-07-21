import time

def main():
    home()

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

if __name__ == "__main__":
    main()