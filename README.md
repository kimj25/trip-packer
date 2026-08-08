# trip-packer v1.0

CS 361 Project — A trip packing assistant with a **Streamlit web UI** that generates personalized packing lists based on trip details, traveler profiles, and destination data. A CLI version is also included.

## Features

- Generate packing lists based on trip duration, destination, and group size
- Customizable traveler profiles (age, sex, dietary restrictions, special needs)
- Children can select multiple special needs (Diapers, Medications, Baby formula, Car seat, Other)
- Past dates cannot be selected for trips
- Automatic clothing quantities calculated from trip length and laundry access
- International travel extras (passport, adapters, currency)
- Save and retrieve past trip packing lists
- Fetches destination info (coordinates, timezone, map link) via ZeroMQ location-map microservice
- Generates the adult clothing list via ZeroMQ clothing-recommender microservice (temperature- and weather-aware)

## Prerequisites

- Python 3.6+
- [location-map-microservice](https://github.com/your-repo/location-map-microservice) running on `tcp://localhost:3010`
- [unit-converter-microservice](https://github.com/your-repo/unit-converter-microservice) running on `tcp://localhost:3011`
- [weather-microservice](https://github.com/your-repo/weather-microservice) running on `tcp://localhost:3015`
- [clothing-recommender-microservice](https://github.com/your-repo/clothing-recommender) running on `tcp://localhost:3016`

## Installation

```bash
pip install -r requirements.txt
```

## Usage (Streamlit — primary interface)

1. Start all four microservices (ports 3010, 3011, 3015, 3016)
2. Launch the app:
   ```bash
   ./run.sh
   ```
   or directly: `streamlit run app.py`
3. Follow the wizard:
   - **Step 1:** Enter departure and return dates (past dates not allowed) and laundry access
   - **Step 2:** Enter destination (domestic or international)
   - **Step 3:** Build traveler profiles (children can add multiple special needs)
   - **Step 4:** View, save, and reload your packing list

Service fetches and packing generation are cached with `st.cache_data` (1800s TTL).
If a microservice is unavailable, the app warns and continues without its data.

## Usage (CLI)

The original CLI is still available and shares the same packing logic:

```bash
python main.py
```

## ZeroMQ Communication

Trip-packer connects to `location-map-microservice` using ZeroMQ REQ/REP pattern on `tcp://localhost:3010`.

- **Request:** `{"query": "city, state/country"}`
- **Response:** `{"latitude": ..., "longitude": ..., "timezone": ..., "map_url": ...}`

If the service is unavailable, the app prints a warning and continues without location data.

Trip-packer also connects to `clothing-recommender-microservice` using ZeroMQ REQ/REP pattern on `tcp://localhost:3016`. It sends the summarized weather (avg high/low in °C, rainy/snowy day counts, and per-day highs/lows) plus trip duration and traveler profiles, and receives the adult clothing list. If the service is unavailable, the app falls back to its built-in clothing logic.

## Project Structure

```
trip-packer/
├── app.py             # Streamlit web UI (primary interface)
├── main.py            # Shared packing logic + microservice clients (also the CLI)
├── run.sh             # One-command launcher for the Streamlit app
├── requirements.txt   # Python dependencies (pyzmq, streamlit)
├── saved_trips.txt    # Stored packing lists
└── README.md
```

## Saved Trips

Packing lists are saved locally to `saved_trips.txt` and are viewable in the Streamlit sidebar or from the CLI home screen.
