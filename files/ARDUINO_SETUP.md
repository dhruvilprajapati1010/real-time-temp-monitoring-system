/*
 * ESP8266_ThingSpeak_Temp_SETUP.md
 * ─────────────────────────────────────────────────────────────────────────────
 * 
 * IMPORTANT: This file contains CREDENTIALS. Keep it SECURE!
 * NEVER commit this file to GitHub if it contains real credentials.
 * 
 * ═════════════════════════════════════════════════════════════════════════════
 *  SETUP INSTRUCTIONS
 * ═════════════════════════════════════════════════════════════════════════════
 * 
 * 1. ARDUINO IDE SETUP
 *    ──────────────────
 *    a) Download Arduino IDE from https://www.arduino.cc/en/software
 *    b) Open Arduino IDE → File → Preferences
 *    c) In "Additional Board Manager URLs", add:
 *       http://arduino.esp8266.com/stable/package_esp8266com_index.json
 *    d) Go to Tools → Board → Board Manager
 *    e) Search for "esp8266" and install
 *    f) Select your board: Tools → Board → ESP8266 → NodeMCU 1.0 (ESP-12E)
 * 
 * 2. INSTALL LIBRARIES
 *    ──────────────────
 *    Sketch → Include Library → Manage Libraries
 *    Search and install:
 *      - ThingSpeak (by MathWorks)
 *      - OneWire (by Paul Stoffregen)  [for DS18B20]
 *      - DallasTemperature (by Miles Burton)  [for DS18B20]
 *      OR
 *      - DHT (by Adafruit)  [for DHT22]
 * 
 * 3. CONFIGURE CREDENTIALS
 *    ──────────────────────
 *    Open ESP8266_ThingSpeak_Temp.ino and update:
 *    
 *    const char* WIFI_SSID = "YOUR_WIFI_NAME";
 *    const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
 *    
 *    unsigned long CHANNEL_ID = YOUR_THINGSPEAK_CHANNEL_ID;
 *    const char* WRITE_API_KEY = "YOUR_WRITE_API_KEY";
 * 
 *    Get ThingSpeak credentials from:
 *    → Go to https://thingspeak.com/
 *    → Sign in to your account
 *    → Channels → Your Channel → API Keys
 * 
 * 4. HARDWARE WIRING
 *    ────────────────
 *    
 *    For DS18B20:
 *    ┌─────────────┬─────────────┐
 *    │ DS18B20     │ NodeMCU     │
 *    ├─────────────┼─────────────┤
 *    │ GND (pin 4) │ GND         │
 *    │ DATA (pin2) │ D4 (GPIO2)  │
 *    │ VCC (pin 3) │ 3.3V        │
 *    └─────────────┴─────────────┘
 *    Add 4.7kΩ pull-up resistor between DATA and 3.3V
 *    
 *    For DHT22:
 *    ┌─────────────┬─────────────┐
 *    │ DHT22       │ NodeMCU     │
 *    ├─────────────┼─────────────┤
 *    │ - (GND)     │ GND         │
 *    │ + (VCC)     │ 3.3V        │
 *    │ DATA        │ D4 (GPIO2)  │
 *    └─────────────┴─────────────┘
 *    Add 10kΩ pull-up resistor between DATA and 3.3V
 * 
 * 5. UPLOAD CODE
 *    ────────────
 *    a) Connect ESP8266 to PC via USB
 *    b) Tools → Port → Select your COM port
 *    c) Arduino IDE → Upload (Ctrl+U)
 *    d) Wait for "Done uploading" message
 *    e) Serial Monitor (Tools → Serial Monitor, 115200 baud) to verify
 * 
 * 6. VERIFY
 *    ──────
 *    Open Serial Monitor and you should see:
 *    ```
 *    🌡️  ESP8266 Temperature Logger — Starting…
 *    ✅  DS18B20 initialised
 *    📡  Connecting to Dhruvil.
 *    ✅  Connected — IP: 192.168.x.x
 *    ✅  ThingSpeak client initialised
 *    🌡️  Temperature: 23.50°C
 *    ✅  Data sent to ThingSpeak
 *    ```
 * 
 * ═════════════════════════════════════════════════════════════════════════════
 *  TROUBLESHOOTING
 * ═════════════════════════════════════════════════════════════════════════════
 * 
 * Problem: "Sensor read failed"
 * → Check wiring: DATA pin should be on D4, GND and 3.3V connections correct
 * → Verify pull-up resistor is installed (4.7kΩ for DS18B20, 10kΩ for DHT22)
 * 
 * Problem: "Wi-Fi connection failed"
 * → Check WiFi SSID and password are correct (case-sensitive)
 * → Ensure network is 2.4GHz (ESP8266 doesn't support 5GHz)
 * → Check if that network is open/has no special characters
 * 
 * Problem: "ThingSpeak error: HTTP 400"
 * → Verify Channel ID and API Key are correct
 * → Check ThingSpeak channel exists: https://thingspeak.com/channels/3134042
 * 
 * Problem: Upload fails / "Port not found"
 * → Install CH340 driver: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
 * → Try different USB cable
 * → Restart Arduino IDE
 * 
 * ═════════════════════════════════════════════════════════════════════════════
 *  FOR MORE INFO
 * ═════════════════════════════════════════════════════════════════════════════
 * 
 * ThingSpeak Docs: https://thingspeak.com/docs/arduino
 * ESP8266 Docs: https://arduino-esp8266.readthedocs.io/
 * Sensor pinout: https://datasheets.maxim-ic.com/en/ds/DS18B20.pdf
 */
