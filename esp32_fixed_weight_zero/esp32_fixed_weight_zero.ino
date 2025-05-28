#include "HX711.h"

#define DOUT 13
#define CLK 14

HX711 scale;

// Adjust these values based on your testing
long offset = -6550;        // The raw value when no weight is on the scale (measured manually)
float scale_factor = 11550; // Raw difference for 1kg weight (calibrate this!)

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  scale.begin(DOUT, CLK);

  Serial.println("HX711 Weight Sensor Test with Manual Offset");
}

void loop() {
  if (scale.is_ready()) {
    long raw_reading = scale.read_average(10);  // Average of 10 readings
    float weight = (raw_reading - offset) / scale_factor;

    Serial.print("Raw reading: ");
    Serial.print(raw_reading);
    Serial.print(" | Weight (kg): ");
    Serial.println(weight, 3);  // Print weight with 3 decimal places

  } else {
    Serial.println("HX711 not found.");
  }

  delay(1000);  // 1-second delay
}