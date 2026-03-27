"""
Flask + ThingSpeak to Firebase integrated background worker.
"""

import time
import requests
import threading
from datetime import datetime, timezone
from flask import Flask, render_template

app = Flask(__name__)

THINGSPEAK_CHANNEL_ID = "3134042"
THINGSPEAK_READ_API_KEY = ""
THINGSPEAK_BASE_URL = "https://api.thingspeak.com"

FIREBASE_DATABASE_URL = "https://realtime-database-71db5-default-rtdb.firebaseio.com"
DEVICE_ID   = "ESP32-001"
DEVICE_NAME = "ESP32 DHT22 Sensor"
LOCATION    = "Main Room"
POLL_INTERVAL_SECONDS = 15

def fetch_latest_from_thingspeak() -> dict | None:
    url = f"{THINGSPEAK_BASE_URL}/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json"
    params = {"results": 1}
    if THINGSPEAK_READ_API_KEY:
        params["api_key"] = THINGSPEAK_READ_API_KEY

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        feeds = data.get("feeds", [])
        if not feeds:
            return None

        latest = feeds[-1]
        temp_raw = latest.get("field1")
        hum_raw  = latest.get("field2")

        if temp_raw is None or hum_raw is None:
            return None

        return {
            "temperature": float(temp_raw),
            "humidity":    float(hum_raw),
            "ts_timestamp": latest.get("created_at", ""),
        }
    except Exception as e:
        print(f"❌ ThingSpeak error: {e}")
        return None

def push_to_firebase(temperature: float, humidity: float, ts_timestamp: str) -> bool:
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
        print(f"✅ Firebase push OK!")
        
        # Keep device status updated
        requests.patch(f"{FIREBASE_DATABASE_URL}/devices/{DEVICE_ID}.json", json={"status": "online"}, timeout=5)
        return True
    except Exception as e:
        print(f"❌ Firebase error: {e}")
        return False

def background_sync_task():
    print("=" * 60)
    print("  ThingSpeak → Firebase Bridge (Background Thread Restored)")
    print("=" * 60)
    time.sleep(2)
    last_ts_timestamp = None

    while True:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Fetching from ThingSpeak …")
        reading = fetch_latest_from_thingspeak()

        if reading:
            temp = reading["temperature"]
            hum  = reading["humidity"]
            ts   = reading["ts_timestamp"]

            if ts == last_ts_timestamp:
                print(f"  ⏳ No new data on ThingSpeak since last check ({ts}). Skipping push.")
            else:
                print(f"  🌡  Temperature : {temp} °C | 💧 Humidity    : {hum} %")
                print(f"  🕒 TS Time     : {ts} (NEW READING!)")

                if push_to_firebase(temp, hum, ts):
                    last_ts_timestamp = ts
        else:
            print("  ⚠️  Skipping Firebase push (no valid reading).")

        time.sleep(POLL_INTERVAL_SECONDS)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    sync_thread = threading.Thread(target=background_sync_task, daemon=True)
    sync_thread.start()
    app.run(host="0.0.0.0", port=5000, debug=False)
