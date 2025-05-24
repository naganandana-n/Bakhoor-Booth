#include <WiFi.h>
#include <WebServer.h>
#include "HX711.h"
#include "max6675.h"

// HX711 pins
#define HX711_DOUT 12
#define HX711_SCK  14

// MAX6675 pins
#define MAX6675_DO  19
#define MAX6675_CS  23
#define MAX6675_CLK 5

// Serial2: RX=16, TX=17
#define SERIAL2_RX 16
#define SERIAL2_TX 17

HX711 scale;
MAX6675 thermocouple(MAX6675_CLK, MAX6675_CS, MAX6675_DO);

enum Mode { MODE_REALTIME, MODE_LOW, MODE_HIGH };
Mode tempMode = MODE_REALTIME;
Mode weightMode = MODE_REALTIME;

WebServer server(80);

void setup() {
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, SERIAL2_RX, SERIAL2_TX);

  // Initialize HX711
  scale.begin(HX711_DOUT, HX711_SCK);
  delay(500);
  if (!scale.is_ready()) {
    Serial.println("HX711 not found.");
  } else {
    Serial.println("HX711 ready.");
    scale.set_scale(21.813);  // Adjust this as per calibration
    scale.tare();
  }

  // Initialize Thermocouple
  delay(500);
  Serial.println("MAX6675 ready.");

  // Start WiFi AP
  WiFi.softAP("Bakhoor-Fallback-AP", "12345678");
  Serial.print("AP IP address: ");
  Serial.println(WiFi.softAPIP());

  // Web Routes
  server.on("/", HTTP_GET, handleRoot);

  server.on("/temp/realtime", []() {
    tempMode = MODE_REALTIME;
    server.send(200, "text/plain", "Temperature Mode: Real-Time");
  });
  server.on("/temp/low", []() {
    tempMode = MODE_LOW;
    server.send(200, "text/plain", "Temperature Mode: 25°C");
  });
  server.on("/temp/high", []() {
    tempMode = MODE_HIGH;
    server.send(200, "text/plain", "Temperature Mode: 400°C");
  });

  server.on("/weight/realtime", []() {
    weightMode = MODE_REALTIME;
    server.send(200, "text/plain", "Weight Mode: Real-Time");
  });
  server.on("/weight/low", []() {
    weightMode = MODE_LOW;
    server.send(200, "text/plain", "Weight Mode: 0kg");
  });
  server.on("/weight/high", []() {
    weightMode = MODE_HIGH;
    server.send(200, "text/plain", "Weight Mode: 60kg");
  });

  server.begin();
}

void loop() {
  server.handleClient();

  if (Serial2.available() | Serial.available()) {
    
    String command;
    command = Serial2.readStringUntil('\n');
    command.trim();
    
    // if(Serial2.available())
    // {
    //   command = Serial2.readStringUntil('\n');
    // command.trim();
    // }
    // else if(Serial.available())
    // {
    //   command = Serial.readStringUntil('\n');
    // command.trim();
    // }

    if (command == "get_weight") {
      float weight = getWeight();
      Serial2.print("KG:");
      Serial2.println(weight, 2);
      Serial.print("KG:");
      Serial.println(weight, 2);
    }
    else if (command == "get_temp") {
      float tempC = getTemp();
      Serial2.print("TEMP:");
      Serial2.println(tempC, 2);
      Serial.println(tempC, 2);
    }
    else {
      Serial2.println("Invalid command");
    }
  }

  delay(50);
}

float getTemp() {
  switch (tempMode) {
    case MODE_LOW: return 25.0;
    case MODE_HIGH: return 400.0;
    default: return thermocouple.readCelsius();
  }
}

float getWeight() {
  switch (weightMode) {
    case MODE_LOW: return 0.0;
    case MODE_HIGH: return 60.0;
    default: {
      float w = scale.get_units(5);
      return (w < 0) ? 0 : w;
    }
  }
}

void handleRoot() {
  String html = R"rawliteral(
    <html>
    <head>
      <title>Bakhoor Control Panel</title>
      <script>
        function sendCommand(path) {
          fetch(path)
            .then(response => response.text())
            .then(text => {
              document.getElementById("status").innerText = text;
            });
        }
      </script>
    </head>
    <body>
      <h2>Temperature Control</h2>
      <button onclick="sendCommand('/temp/realtime')">Real-Time</button>
      <button onclick="sendCommand('/temp/low')">Set to 25°C</button>
      <button onclick="sendCommand('/temp/high')">Set to 400°C</button>

      <h2>Weight Control</h2>
      <button onclick="sendCommand('/weight/realtime')">Real-Time</button>
      <button onclick="sendCommand('/weight/low')">Set to 0kg</button>
      <button onclick="sendCommand('/weight/high')">Set to 60kg</button>

      <p id="status" style="margin-top:20px; font-weight: bold; color: green;"></p>
    </body>
    </html>
  )rawliteral";
  server.send(200, "text/html", html);
}
