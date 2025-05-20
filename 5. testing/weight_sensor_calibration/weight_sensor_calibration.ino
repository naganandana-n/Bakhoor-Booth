/* 

calibration factor calc:
1. place a known weight, eg: 1kg
2. calibration_factor = raw_reading / known_weight
3. test and adjust

*/ 

#include "HX711.h"

#define DOUT 13
#define CLK 14

HX711 scale;

void setup() {
  Serial.begin(115200);
  scale.begin(DOUT, CLK);
  Serial.println("Remove all weight...");
  delay(2000);
  scale.tare(); // Reset the scale to 0
  Serial.println("Place a known weight on the scale...");
}

void loop() {
  if (scale.is_ready()) {
    long reading = scale.get_units(10);  // Average of 10 readings
    Serial.print("Reading: ");
    Serial.println(reading);
  } else {
    Serial.println("HX711 not found.");
  }
  delay(1000);
}