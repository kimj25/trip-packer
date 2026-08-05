# trip-packer v1.0

CS 361 Project — A CLI-based trip packing assistant that generates personalized packing lists based on trip details, traveler profiles, and destination data.

## Features

- Generate packing lists based on trip duration, destination, and group size
- Customizable traveler profiles (age, sex, dietary restrictions, special needs)
- Automatic clothing quantities calculated from trip length
- International travel extras (passport, adapters, currency)
- Save and retrieve past trip packing lists
- Fetches destination info (coordinates, timezone, map link) via ZeroMQ location-map microservice
- Generates the adult clothing list via ZeroMQ clothing-recommender microservice (temperature- and weather-aware)

## Prerequisites

- Python 3.6+
- [location-map-microservice](https://github.com/your-repo/location-map-microservice) running on `tcp://localhost:3010`
- [clothing-recommender-microservice](https://github.com/your-repo/clothing-recommender) running on `tcp://localhost:3016`

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Start the **location-map-microservice** first (must be listening on port 3010)
2. Start the **clothing-recommender-microservice** (must be listening on port 3016)
3. Run the app:
   ```bash
   python main.py
   ```
4. Follow the on-screen prompts:
   - **Step 1:** Enter departure and return dates
   - **Step 2:** Enter destination (domestic or international)
   - **Step 3:** Build traveler profiles
   - **Step 4:** View and save your packing list

## ZeroMQ Communication

Trip-packer connects to `location-map-microservice` using ZeroMQ REQ/REP pattern on `tcp://localhost:3010`.

- **Request:** `{"query": "city, state/country"}`
- **Response:** `{"latitude": ..., "longitude": ..., "timezone": ..., "map_url": ...}`

If the service is unavailable, the app prints a warning and continues without location data.

Trip-packer also connects to `clothing-recommender-microservice` using ZeroMQ REQ/REP pattern on `tcp://localhost:3016`. It sends the summarized weather (avg high/low in °C, rainy/snowy day counts, and per-day highs/lows) plus trip duration and traveler profiles, and receives the adult clothing list. If the service is unavailable, the app falls back to its built-in clothing logic.

## Project Structure

```
trip-packer/
├── main.py             # Application entry point and all logic
├── requirements.txt    # Python dependencies (pyzmq)
├── saved_trips.txt     # Stored packing lists
└── README.md
```

## Saved Trips

Packing lists are saved locally to `saved_trips.txt`. You can view past trips from the home screen.
