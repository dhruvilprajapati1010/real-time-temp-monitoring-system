"""
ESP32 DHT22 → ThingSpeak → Firebase Realtime Database Bridge
Fetches latest temperature & humidity from ThingSpeak every 15 seconds
and pushes them into Firebase Realtime Database under /temperatures.
"""

import time
import requests
import json
from datetime import datetime, timezone

# ──────────────────────────────────────────────
#  ThingSpeak Configuration (from ESP32 sketch)
# ──────────────────────────────────────────────
THINGSPEAK_CHANNEL_ID = "3134042"
THINGSPEAK_READ_API_KEY = ""          # Leave blank if channel is public, else add your Read API Key
THINGSPEAK_BASE_URL = "https://api.thingspeak.com"

# Field mapping (matches ESP32 sketch):
#   Field 1 → Temperature (°C)
#   Field 2 → Humidity (%)

# ──────────────────────────────────────────────
#  Firebase Realtime Database Configuration
# ──────────────────────────────────────────────
FIREBASE_DATABASE_URL = "https://realtime-database-71db5-default-rtdb.firebaseio.com"

# Device info (matches your existing database schema)
DEVICE_ID   = "ESP32-001"
DEVICE_NAME = "ESP32 DHT22 Sensor"
LOCATION    = "Main Room"

# ──────────────────────────────────────────────
#  Polling interval
# ──────────────────────────────────────────────
POLL_INTERVAL_SECONDS = 15   # ThingSpeak minimum is 15 s


def fetch_latest_from_thingspeak() -> dict | None:
    """
    Fetches the single most-recent entry from the ThingSpeak channel.
    Returns a dict with 'temperature' and 'humidity', or None on failure.
    """
    url = f"{THINGSPEAK_BASE_URL}/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json"
    params = {
        "results": 1,   # only the latest reading
    }
    if THINGSPEAK_READ_API_KEY:
        params["api_key"] = THINGSPEAK_READ_API_KEY

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        feeds = data.get("feeds", [])
        if not feeds:
            print("⚠️  No feeds returned from ThingSpeak.")
            return None

        latest = feeds[-1]
        temp_raw = latest.get("field1")
        hum_raw  = latest.get("field2")

        if temp_raw is None or hum_raw is None:
            print(f"⚠️  Missing fields in ThingSpeak feed: {latest}")
            return None

        return {
            "temperature": float(temp_raw),
            "humidity":    float(hum_raw),
            "ts_timestamp": latest.get("created_at", ""),
        }

    except requests.exceptions.RequestException as e:
        print(f"❌ ThingSpeak fetch error: {e}")
        return None
    except (ValueError, KeyError) as e:
        print(f"❌ ThingSpeak parse error: {e}")
        return None


def push_to_firebase(temperature: float, humidity: float, ts_timestamp: str) -> bool:
    """
    Pushes a new temperature/humidity reading to Firebase under /temperatures.
    Uses the Firebase REST API (POST → auto-generates a push key).
    """
    now_utc = datetime.now(timezone.utc).isoformat()

    payload = {
        "deviceId":   DEVICE_ID,
        "deviceName": DEVICE_NAME,
        "location":   LOCATION,
        "temperature": round(temperature, 2),
        "humidity":    round(humidity, 2),
        "source":      "thingspeak-live",
        "status":      "active",
        "timestamp":   now_utc,
        "tsTimestamp": ts_timestamp,
    }

    url = f"{FIREBASE_DATABASE_URL}/temperatures.json"

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        push_key = result.get("name", "unknown")
        print(f"✅ Firebase push OK  →  key: {push_key}")

        # Also update /devices/<DEVICE_ID>/lastOnline and /latestReading
        _update_device_status(temperature, humidity, now_utc)
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Firebase push error: {e}")
        return False


def _update_device_status(temperature: float, humidity: float, timestamp: str) -> None:
    """
    Keeps /devices/<device_id> up-to-date with the latest reading and online status.
    Uses PATCH (update) so existing fields are preserved.
    """
    url = f"{FIREBASE_DATABASE_URL}/devices/{DEVICE_ID}.json"
    payload = {
        "deviceId":   DEVICE_ID,
        "deviceName": DEVICE_NAME,
        "location":   LOCATION,
        "status":     "online",
        "lastOnline": timestamp,
        "latestReading": {
            "temperature": round(temperature, 2),
            "humidity":    round(humidity, 2),
            "timestamp":   timestamp,
        },
    }
    try:
        requests.patch(url, json=payload, timeout=10)
    except requests.exceptions.RequestException:
        pass   # best-effort update; main push already succeeded


def main():
    print("=" * 60)
    print("  ESP32 DHT22 → ThingSpeak → Firebase Bridge")
    print(f"  Channel  : {THINGSPEAK_CHANNEL_ID}")
    print(f"  Device   : {DEVICE_NAME} ({DEVICE_ID})")
    print(f"  Interval : {POLL_INTERVAL_SECONDS}s")
    print("=" * 60)

    while True:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Fetching from ThingSpeak …")
        reading = fetch_latest_from_thingspeak()

        if reading:
            temp = reading["temperature"]
            hum  = reading["humidity"]
            ts   = reading["ts_timestamp"]

            print(f"  🌡  Temperature : {temp} °C")
            print(f"  💧 Humidity    : {hum} %")
            print(f"  🕒 TS Time     : {ts}")

            push_to_firebase(temp, hum, ts)
        else:
            print("  ⚠️  Skipping Firebase push (no valid reading).")

        print(f"  ⏱  Sleeping {POLL_INTERVAL_SECONDS}s …")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
