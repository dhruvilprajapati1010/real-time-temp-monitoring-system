# 🌡️ Real-Time Temperature Monitoring System

A complete IoT solution for real-time temperature monitoring with wireless sensor (ESP8266), cloud data storage (ThingSpeak), Flask backend API, and React dashboard.

## 📋 Project Structure

```
├── backend/                 # Python Flask API
│   ├── config/             # Configuration & settings
│   ├── models/             # Data models
│   ├── services/           # Business logic & integrations
│   ├── routes/             # API endpoints
│   ├── utils/              # Database helpers
│   ├── app.py              # Flask app factory
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Environment configuration
│
├── frontend/               # React + Vite dashboard
│   ├── src/               # React components
│   ├── package.json       # Node.js dependencies
│   ├── vite.config.js    # Vite configuration
│   └── .env          # Frontend env vars
│
├── files/                  # Documentation & Arduino sketch
│   ├── ESP8266_ThingSpeak_Temp.ino    # ESP8266 firmware
│   ├── ARDUINO_SETUP.md              # Arduino setup guide
│   └── README.md                      # Project docs
│
└── .git/                   # Git version control
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ with pip
- Node.js 16+ with npm
- Arduino IDE (for ESP8266 programming)
- MongoDB (optional - uses mock DB for development)

### 1. Backend Setup

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Configure environment
# Edit backend/.env and add your:
# - ThingSpeak API keys
# - Twilio credentials (optional, for SMS alerts)
# - MongoDB connection string (default: localhost:27017)

# Add your real credentials to the env
```

**Backend .env Configuration:**
```env
MONGO_URI=mongodb://localhost:27017
THINGSPEAK_CHANNEL_ID=3134042
THINGSPEAK_READ_API_KEY=YOUR_API_KEY
TEMP_HIGH_THRESHOLD=40.0
TEMP_LOW_THRESHOLD=0.0
```

### 2. Start Backend

```bash
# From project root
set PYTHONPATH=.
python -m flask --app backend.app run --port 5000
```

Backend will start at: **http://localhost:5000**

### 3. Frontend Setup

```bash
# Install dependencies
cd frontend
npm install

# Configure environment (.env already set with API URL)
```

### 4. Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will start at: **http://localhost:3002** (or next available port)

### 5. ESP8266 Arduino Setup

**See [ARDUINO_SETUP.md](files/ARDUINO_SETUP.md) for detailed instructions**

Quick summary:
1. Install Arduino IDE
2. Add ESP8266 board support
3. Install libraries: ThingSpeak, OneWire, DallasTemperature
4. Update WiFi & ThingSpeak credentials in `.ino` file
5. Connect ESP8266 via USB and upload

---

## 🔧 System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   Cloud / Web                                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  React Dashboard (Frontend)                            │  │
│  │  - Real-time temperature chart                         │  │
│  │  - Alert history & status                              │  │
│  │  - Gauge visualization                                 │  │
│  └────────────────────────────────────────────────────────┘  │
│                           ↑↓ (HTTP/REST)                      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Flask Backend API                                     │  │
│  │  - GET /api/temperature (current + history)            │  │
│  │  - GET /api/alerts (alert logs)                        │  │
│  │  - POST /api/alerts/action (dismiss alerts)            │  │
│  │  - Background poller (queries ThingSpeak)              │  │
│  └────────────────────────────────────────────────────────┘  │
│                           ↑↓ (HTTP)                           │
└───────────────────────────┬────────────────────────────────────┘
                            ↑↓ (WiFi)
        ┌───────────────────────────────────┐
        │  ESP8266 (NodeMCU)                │
        │  - DHT22/DS18B20 sensor           │
        │  - WiFi connectivity              │
        │  - Posts to ThingSpeak            │
        │  - Every 30 seconds               │
        └──────────────┬──────────────────┘
                       ↑↓
        ┌──────────────────────────────┐
        │  ThingSpeak Cloud IoT        │
        │  - Data storage              │
        │  - API endpoints             │
        │  - Visualization             │
        └──────────────────────────────┘
        
         └─→ Backend polls ThingSpeak
            every 30 seconds
            └─→ Stores in MongoDB
               └─→ Fetches when requested
                  by Frontend
```

---

## 📡 API Endpoints

### Temperature
- `GET /api/temperature` - Current & recent readings
- Response: `{ "data": { "current": 23.5, "history": [...] } }`

### Alerts
- `GET /api/alerts` - Alert history
- `POST /api/alerts/dismiss/:alertId` - Mark alert as read
- `POST /api/alerts/sms` - Send SMS alert (requires Twilio)

### Health
- `GET /health` - Server status

---

## 🛠️ Configuration Reference

### Backend (.env)
| Variable | Description | Default |
|----------|-------------|---------|
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `DB_NAME` | Database name | `iot_temp_monitor` |
| `THINGSPEAK_CHANNEL_ID` | ThingSpeak channel | `3134042` |
| `THINGSPEAK_READ_API_KEY` | ThingSpeak API key | `` |
| `TEMP_HIGH_THRESHOLD` | Alert threshold (°C) | `40.0` |
| `TEMP_LOW_THRESHOLD` | Alert threshold (°C) | `0.0` |
| `RAPID_RISE_DELTA` | Alert threshold (°C/5min) | `5.0` |
| `POLL_INTERVAL_SECONDS` | ThingSpeak update freq | `30` |

### Frontend (.env)
| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:5000` |

### Arduino (.ino)
```cpp
const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_PASSWORD";
unsigned long CHANNEL_ID = YOUR_THINGSPEAK_CHANNEL_ID;
const char* WRITE_API_KEY = "YOUR_WRITE_API_KEY";
```

---

## 🔌 Hardware Connections

### DS18B20 Temperature Sensor (Recommended)
```
DS18B20    NodeMCU D1 Mini
───────────────────────
GND    →   GND
DATA   →   D4 (GPIO2) + 4.7kΩ pull-up to 3.3V
VCC    →   3.3V
```

### DHT22 Temperature & Humidity (Alternative)
```
DHT22      NodeMCU D1 Mini
───────────────────────
-          GND
+          3.3V
DATA       D4 (GPIO2) + 10kΩ pull-up to 3.3V
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python environment
set PYTHONPATH=.
python -m flask --app backend.app run

# If import errors, reinstall dependencies
pip install --force-reinstall -r backend/requirements.txt
```

### Frontend port already in use
```bash
# Vite will auto-find next available port
npm run dev
# Will start on 3002, 3003, etc if 5173 is busy
```

### Arduino sketch won't upload
1. Check COM port: `Tools → Port`
2. Select board: `Tools → Board → ESP8266 → NodeMCU 1.0`
3. Install CH340 driver if "port not found": https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
4. Hold GPIO0 to GND while uploading if compilation succeeds but upload fails

### MongoDB connection error
- Backend falls back to in-memory mock DB (data won't persist)
- To use MongoDB:
  - **Local**: Install from https://www.mongodb.com/try/download/community
  - **Cloud**: Use MongoDB Atlas: https://www.mongodb.com/products/platform/atlas

---

## 📚 Useful Links

- **ThingSpeak**: https://thingspeak.com/
- **Arduino ESP8266**: https://arduino-esp8266.readthedocs.io/
- **Flask Docs**: https://flask.palletsprojects.com/
- **React Docs**: https://react.dev/
- **Vite Docs**: https://vitejs.dev/

---

## 📝 License

MIT License - see LICENSE file

---

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

**Project Repository**: https://github.com/dhruvilprajapati1010/real-time-temp-monitoring-system
