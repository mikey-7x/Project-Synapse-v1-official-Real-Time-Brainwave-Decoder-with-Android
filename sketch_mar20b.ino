// Project Synapse: ADS1115 16-Bit I2C Transmission
#include <Wire.h>
#include <Adafruit_ADS1X15.h>

Adafruit_ADS1115 ads;

unsigned long lastMicro = 0;
const unsigned long sampleInterval = 7142; // Exactly 140 Hz (1,000,000 / 140)

void setup() {
  Serial.begin(9600); // Standard HC-05 Bluetooth Baud

  // Initialize the ADS1115 module via I2C (SDA to A4, SCL to A5)
  if (!ads.begin()) {
    while (1); // Halt if ADS1115 is not detected
  }

  // Set the Gain to 2/3x to safely read your 5V Op-Amp signals
  // This allows the ADS1115 to measure up to +/- 6.144V with extreme precision
  ads.setGain(GAIN_TWOTHIRDS); 
  
  // Crank the ADS1115 sample rate to maximum (860 Samples Per Second)
  // This ensures the I2C reads never slow down our 140Hz Bluetooth loop!
  ads.setDataRate(RATE_ADS1115_860SPS); 
}

void loop() {
  unsigned long currentMicro = micros();
  
  // Non-blocking, microsecond-accurate pacing
  if (currentMicro - lastMicro >= sampleInterval) {
    lastMicro = currentMicro;

    // Read the 16-bit values from the external ADS1115 module!
    int16_t a0 = ads.readADC_SingleEnded(0);
    int16_t a1 = ads.readADC_SingleEnded(1);

    // 0xAA 0x55 Binary Handshake
    Serial.write(0xAA);
    Serial.write(0x55);

    // Send ADS1115 A0 (High then Low Byte)
    Serial.write(a0 >> 8);
    Serial.write(a0 & 0xFF);

    // Send ADS1115 A1 (High then Low Byte)
    Serial.write(a1 >> 8);
    Serial.write(a1 & 0xFF);
  }
}
