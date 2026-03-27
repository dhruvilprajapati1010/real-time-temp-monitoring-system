# ESP32 DHT22 Realtime Dashboard

This project bridges your ESP32's temperature and humidity data (sent to ThingSpeak) with Firebase Realtime Database to display it on a beautiful live dashboard.

## Components

1. **`fetch_and_push.py`**
   - A Python script that polls your ThingSpeak channel every 15 seconds.
   - It fetches the latest temperature and humidity values.
   - It then pushes these values to your Firebase Realtime Database under the `/temperatures` node and updates the device status under `/devices`.

2. **`dashboard.html`**
   - A modern, responsive dashboard built with HTML, CSS, and JS.
   - It connects directly to your Firebase Realtime Database.
   - It listens for live updates to the `/temperatures` node and displays the latest values using animated stat cards, history charts (via Chart.js), and a data table.

## Setup Instructions

### 1. Python Bridge (`fetch_and_push.py`)
This script acts as the bridge between ThingSpeak and Firebase.

1. Install the required Python packages (already done in this workspace):
   ```bash
   pip install -r requirements.txt
   ```
2. Run the script:
   ```bash
   python fetch_and_push.py
   ```
3. Keep this script running in the background. It will fetch data every 15 seconds.

### 2. Live Dashboard (`dashboard.html`)
The dashboard runs entirely in the browser and requires no server to host.

1. Locate `dashboard.html` in your project folder.
2. Double-click it to open it in your web browser (Chrome, Edge, Firefox, etc.).
3. Once opened, it will connect to Firebase. When the Python script pushes new data, the dashboard will update automatically in real-time.

---

### What's Next?
- Ensure your ESP32 is powered on and successfully sending data to ThingSpeak (Channel `3134042`).
- Check the console output of the Python script to verify it's successfully reading from ThingSpeak and pushing to Firebase.
- Open `dashboard.html` and watch the live data flow in!
