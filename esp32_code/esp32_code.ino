#include "HX711.h"
#include "max6675.h"

// HX711 pins
#define HX711_DOUT 13 // 12 to 13
#define HX711_SCK  14

// MAX6675 pins
#define MAX6675_DO  19
#define MAX6675_CS  23
#define MAX6675_CLK 5

HX711 scale;
MAX6675 thermocouple(MAX6675_CLK, MAX6675_CS, MAX6675_DO);

void setup() {
  Serial.begin(115200);      
  Serial2.begin(9600, SERIAL_8N1, 16, 17);  // Serial2: RX=16, TX=17

  // Initialize HX711
  scale.begin(HX711_DOUT, HX711_SCK);
  delay(500);
  if (!scale.is_ready()) {
    Serial.println("HX711 not found.");
  } else {
    Serial.println("HX711 ready.");
    scale.set_scale(21.813);  // Replace with actual calibration factor
    scale.tare();             
  }

  // Initialize MAX6675
  delay(500);
  Serial.println("MAX6675 ready.");
}

void loop() {
  if (Serial2.available()) {
    String command = Serial2.readStringUntil('\n');
    command.trim();

    if (command == "get_weight") {
      float weight = scale.get_units(5);  // Average of 5 readings
      if (weight < 0) weight = 0;
      Serial2.print("KG:");
      Serial2.println(weight, 2);  
      Serial.print("KG:");
      Serial.println(weight, 2);
    }
    else if (command == "get_temp") {
      // float tempC = thermocouple.readCelsius();
      float totalTemp = 0.0;
      int numReadings = 5;
      for (int i = 0; i < numReadings; i++) {
        totalTemp += thermocouple.readCelsius();
        delay(50);  // Small delay between readings
      }
      float avgTemp = totalTemp / numReadings;
      Serial2.print("TEMP:");
      // Serial2.println(tempC, 2);          // Send temperature in °C
      Serial2.println(avgTemp, 2);          // Send average temperature in °C
      Serial.print("TEMP:");
      // Serial.println(tempC, 2); 
      Serial.println(avgTemp, 2); 
    }
    else {
      Serial2.println("Invalid command");
    }
  }

  delay(50);  // Prevent flooding
}