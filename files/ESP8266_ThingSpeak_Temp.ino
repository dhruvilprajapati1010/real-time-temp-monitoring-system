/*
 * ESP8266_ThingSpeak_DHT22.ino
 * ─────────────────────────────────────────────────────────────
 * Reads temperature & humidity from DHT22 every 20 seconds
 * and uploads to ThingSpeak (Field1 = Temp, Field2 = Humidity)
 */

#include <ESP8266WiFi.h>
#include <ThingSpeak.h>
#include <DHT.h>

// ── User configuration ───────────────────────────────────────
const char* WIFI_SSID      = "Dhruvil";
const char* WIFI_PASSWORD  = "dhruvil1010";

unsigned long CHANNEL_ID   = 3134042;
const char* WRITE_API_KEY  = "PLBN60EMMAH31KPA";

#define DHTPIN D4          // GPIO2 (NodeMCU D4)
#define DHTTYPE DHT22

const int SEND_INTERVAL = 20000; // ≥ 15000 ms (ThingSpeak rule)
// ────────────────────────────────────────────────────────────

// Objects
DHT dht(DHTPIN, DHTTYPE);
WiFiClient wifiClient;

unsigned long lastSendTime = 0;

// ── Setup ───────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(100);

  Serial.println("\n🌡️ ESP8266 DHT22 Logger — Starting...");

  // Init DHT sensor
  dht.begin();
  Serial.println("✅ DHT22 initialized");

  // Connect WiFi
  connectWiFi();

  // Init ThingSpeak
  ThingSpeak.begin(wifiClient);
  Serial.println("✅ ThingSpeak initialized");
}

// ── Loop ────────────────────────────────────────────────────
void loop() {

  // Reconnect WiFi if needed
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️ WiFi lost, reconnecting...");
    connectWiFi();
  }

  unsigned long now = millis();

  if (now - lastSendTime >= SEND_INTERVAL) {
    lastSendTime = now;

    // ── Read Sensor ───────────────────────────────────────
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    // Check validity
    if (isnan(temperature) || isnan(humidity)) {
      Serial.println("❌ Failed to read from DHT sensor!");
      return;
    }

    Serial.print("🌡️ Temp: ");
    Serial.print(temperature);
    Serial.print(" °C | 💧 Humidity: ");
    Serial.print(humidity);
    Serial.println(" %");

    // ── Send to ThingSpeak ────────────────────────────────
    ThingSpeak.setField(1, temperature);
    ThingSpeak.setField(2, humidity);

    int httpCode = ThingSpeak.writeFields(CHANNEL_ID, WRITE_API_KEY);

    if (httpCode == 200) {
      Serial.println("✅ Data sent to ThingSpeak");
    } else {
      Serial.print("❌ Error sending data. HTTP code: ");
      Serial.println(httpCode);
    }
  }
}

// ── WiFi Connect Function ───────────────────────────────────
void connectWiFi() {
  Serial.printf("📡 Connecting to %s", WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("\n✅ Connected! IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ WiFi failed. Will retry...");
  }
