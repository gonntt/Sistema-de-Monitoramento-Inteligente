
#include <DHT.h>

#define DHTPIN 2 
#define DHTTYPE DHT11  

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(1200);
  dht.begin();
}

void loop() {
  delay(2000);  

  
float humidity = dht.readHumidity();
float temperature = dht.readTemperature();




Serial.print("{\"humidity\":");
Serial.print(humidity);
Serial.print(", \"temperature\":");
Serial.print(temperature);
Serial.println("}");



}



