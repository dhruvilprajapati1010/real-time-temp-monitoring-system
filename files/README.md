# 🌡️ ThermoWatch — IoT Temperature Monitoring System

A **production-level, full-stack IoT monitoring system** built with:
- **Hardware**: ESP8266 + DS18B20 temperature sensor
- **Cloud**: ThingSpeak (data ingestion) → MongoDB Atlas (storage)
- **Backend**: Python Flask REST API + Twilio SMS alerts
- **Frontend**: React.js + Chart.js + Tailwind CSS

---

## 📁 Folder Structure

```
iot-temp-monitor/
│
├── backend/
│   ├── app.py                  ← Flask application factory
│   ├── requirements.txt        ← Python dependencies
│   ├── .env.example            ← Environment variables template
│   │
│   ├── config/
│   │   └── settings.py         ← Centralised config (reads from .env)
│   │
│   ├── models/
│   │   └── temperature.py      ← MongoDB document schemas
│   │
│   ├── routes/
│   │   ├── temperature.py      ← /api/temperature/* endpoints
│   │   └── alerts.py           ← /api/alerts/* endpoints
│   │
│   ├── services/
│   │   ├── thingspeak.py       ← ThingSpeak API client
│   │   ├── alert.py            ← Threshold + rapid-rise detection
│   │   ├── sms.py              ← Twilio SMS integration
│   │   └── poller.py           ← Background polling thread
│   │
│   └── utils/
│       └── db.py               ← MongoDB connection singleton
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── .env.example
│   │
│   └── src/
│       ├── main.jsx            ← React entry point
│       ├── App.jsx             ← Root component + navigation
│       ├── index.css           ← Tailwind directives
│       │
│       ├── pages/
│       │   ├── Dashboard.jsx   ← Main live dashboard
│       │   └── AlertHistory.jsx← Full alert log + stats
│       │
│       ├── components/
│       │   ├── ThermometerGauge.jsx ← Animated SVG gauge
│       │   ├── TemperatureChart.jsx ← Chart.js line chart
│       │   ├── StatsCards.jsx       ← Min/Max/Avg/Count cards
│       │   └── AlertBadge.jsx       ← Individual alert row
│       │
│       ├── hooks/
│       │   └── useTemperature.js    ← Auto-refreshing data hooks
│       │
│       └── utils/
│           └── api.js               ← All fetch() calls to Flask
│
└── ESP8266_ThingSpeak_Temp.ino  ← Arduino sketch for the device
```

---

## 🔑 API Keys Setup

### 1. ThingSpeak
1. Go to [thingspeak.com](https://thingspeak.com) → Sign up / Log in
2. **Channels → New Channel** → Add field "Temperature"
3. Copy your **Channel ID** from the channel page
4. Go to **API Keys** tab → copy the **Read API Key**
5. Also copy the **Write API Key** (for the ESP8266 sketch)

### 2. MongoDB Atlas
1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas) → Create free account
2. Create a **free M0 cluster** (512 MB, always free)
3. **Database Access** → Add a database user with username + password
4. **Network Access** → Add IP `0.0.0.0/0` (allow all) for dev, or your server IP for production
5. **Connect → Drivers** → Copy the connection string, replace `<password>` with your password

### 3. Twilio (SMS Alerts)
1. Go to [console.twilio.com](https://console.twilio.com) → Create free account
2. Get your **Account SID** and **Auth Token** from the dashboard
3. **Phone Numbers → Get a number** (free trial gives one number)
4. On a trial account, verify your personal number at **Verified Caller IDs**

---

## ⚙️ Environment Setup

### Backend

```bash
# 1. Clone / enter the project
cd iot-temp-monitor/backend

# 2. Create a Python virtual environment
python -m venv venv

# Activate (Linux/macOS):
source venv/bin/activate

# Activate (Windows):
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file
cp .env.example .env
# → Open .env in your editor and fill in all values
```

### Frontend

```bash
cd iot-temp-monitor/frontend

# 1. Install Node dependencies
npm install

# 2. Create your frontend .env
cp .env.example .env
# VITE_API_URL=http://localhost:5000  ← should already be correct for local dev
```

---

## 🚀 Step-by-Step Execution Guide

### Step 1 — Upload Arduino Sketch
1. Open `ESP8266_ThingSpeak_Temp.ino` in Arduino IDE
2. Fill in your `WIFI_SSID`, `WIFI_PASSWORD`, `CHANNEL_ID`, `WRITE_API_KEY`
3. Install board: **Tools → Board Manager → search "esp8266"** → install
4. Install libraries via **Library Manager**: `ThingSpeak`, `OneWire`, `DallasTemperature`
5. Select board: **NodeMCU 1.0 (ESP-12E Module)**
6. Upload → Open Serial Monitor at 115200 baud to verify

### Step 2 — Verify ThingSpeak is Receiving Data
- Go to your ThingSpeak channel → **Private View**
- You should see readings arriving every 30 seconds

### Step 3 — Start the Flask Backend

```bash
cd backend
source venv/bin/activate       # or venv\Scripts\activate on Windows
python app.py
```

Expected output:
```
✅  Connected to MongoDB Atlas
🔄  Poller started — interval: 30s
 * Running on http://0.0.0.0:5000
```

### Step 4 — Seed Test Data (Optional, if no device yet)
```bash
curl -X POST http://localhost:5000/api/temperature/seed \
     -H "Content-Type: application/json" \
     -d '{"count": 60, "base_temp": 25, "variance": 8}'
```

### Step 5 — Start the React Frontend

```bash
cd frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🌐 REST API Reference

### Temperature Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/temperature/latest` | Most recent reading |
| GET | `/api/temperature/history?limit=100&hours=24` | Historical readings |
| GET | `/api/temperature/stats?hours=24` | Min / Max / Avg stats |
| POST | `/api/temperature/seed` | Insert test data (dev only) |

### Alert Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/alerts?limit=50&type=HIGH` | Alert history |
| GET | `/api/alerts/stats` | Alert counts by type (7 days) |
| POST | `/api/alerts/test` | Send test SMS (dev only) |

### Health Check

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/health` | Service health check |

### Example Responses

**GET /api/temperature/latest**
```json
{
  "status": "ok",
  "data": {
    "value": 27.34,
    "source": "thingspeak",
    "timestamp": "2024-11-15T10:23:45.123Z"
  }
}
```

**GET /api/alerts**
```json
{
  "status": "ok",
  "count": 2,
  "data": [
    {
      "alert_type": "HIGH",
      "temperature": 42.1,
      "message": "🌡️ HIGH TEMP ALERT: 42.1°C — exceeds limit of 40.0°C",
      "sms_sent": true,
      "timestamp": "2024-11-15T10:20:00.000Z"
    }
  ]
}
```

---

## 🚨 Alert Logic Explained

### Threshold Alerts
- **HIGH**: Fires when `temperature >= TEMP_HIGH_THRESHOLD` (default 40°C)
- **LOW**: Fires when `temperature <= TEMP_LOW_THRESHOLD` (default 0°C)

### Rapid Rise Detection
- Looks back `RAPID_RISE_WINDOW` minutes (default 5 min) in MongoDB
- If the oldest reading in that window is `RAPID_RISE_DELTA`°C below current temperature → fires alert
- Useful for catching fire/heat events even if still within absolute limits

### Cooldown
- Once an alert type fires, it is suppressed for `ALERT_COOLDOWN_MINUTES` (default 15 min)
- Prevents SMS spam during sustained high-temperature conditions

---

## 🚢 Deployment

### Backend (on a Linux VPS / Render / Railway)

```bash
# Using Gunicorn (production WSGI server)
pip install gunicorn
gunicorn "app:create_app()" \
  --workers 2 \
  --bind 0.0.0.0:5000 \
  --access-logfile - \
  --error-logfile -

# Set FLASK_ENV=production in your environment
```

### Frontend (Vercel / Netlify)

```bash
cd frontend
npm run build    # outputs to dist/

# Vercel: just push to GitHub, connect repo in Vercel dashboard
# Set VITE_API_URL to your production Flask URL in Vercel env vars
```

### Environment variables in production
Never commit `.env` files. Use your platform's secret manager:
- Railway: Project Settings → Variables
- Render: Environment section
- Vercel (frontend): Project → Settings → Environment Variables

---

## 🧪 Sample Test Data

You can inject synthetic readings without a device:

```bash
# 60 readings over 24h, base 25°C ±8°C variation
curl -X POST http://localhost:5000/api/temperature/seed \
  -H "Content-Type: application/json" \
  -d '{"count": 60, "base_temp": 25, "variance": 8}'

# Simulate a hot environment to trigger HIGH alert
curl -X POST http://localhost:5000/api/temperature/seed \
  -H "Content-Type: application/json" \
  -d '{"count": 10, "base_temp": 43, "variance": 1}'

# Test the SMS alert manually
curl -X POST http://localhost:5000/api/alerts/test
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| `MongoDB connection failed` | Check your `MONGO_URI`, ensure IP is whitelisted in Atlas |
| `ThingSpeak returns None` | Verify `CHANNEL_ID` and `THINGSPEAK_READ_API_KEY` in `.env` |
| `Twilio error code 21608` | Your destination number is unverified (trial account limit) |
| `CORS error in browser` | Ensure Flask is running and `VITE_API_URL` matches its address |
| ESP8266 won't connect | Double-check SSID/password, ensure 2.4GHz network (not 5GHz) |
| No data in chart | Click "🌱 Seed Data" on the dashboard to generate test readings |

---

## 📈 Scaling Considerations

- **Multiple sensors**: Add `sensor_id` field to temperature documents; filter by it in the API
- **Multiple users**: Add authentication (Flask-JWT-Extended) and per-user thresholds
- **Higher poll rates**: ThingSpeak free tier limits updates to every 15 seconds minimum
- **WebSockets**: Replace polling with Flask-SocketIO for true real-time push to the browser
- **Docker**: A `docker-compose.yml` can be added to containerise Flask + a local MongoDB for dev
