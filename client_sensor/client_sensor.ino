#include <SPI.h>
#include <LoRa.h>

// Definição dos pinos do módulo LoRa 
#define SS 10
#define RST 9
#define DIO0 2

void setup() {
  Serial.begin(9600);
  while (!Serial);

  LoRa.setPins(SS, RST, DIO0);

  if (!LoRa.begin(915E6)) { // Frequência de 915 MHz
    Serial.println("Falha ao iniciar LoRa");
    while (1);
  } 
}

void loop() {
  // Gera dados simulados
  float temperature = random(1500, 4500) / 100.0;  // 15.00 a 45.00 °C
  float humidity = random(500, 10000) / 100.0;     // 5.00 a 100.00 %
  float dust = random(50, 300);                     // 50 a 300 (sem unidade por enquanto)
  float battery = random(0, 10000) / 100.0;        // 0 a 100 %

  // Monta a mensagem em formato de string, em que cada elem é separado por vírgulas
  String message = String(temperature, 2) + "," + String(humidity, 2) + "," + String(dust, 0) + "," + String(battery, 2);

  Serial.println(message);

  LoRa.beginPacket();
  LoRa.print(message);
  LoRa.endPacket();

  delay(30000); // espera 30 segundos antes da próxima transmissão (reavaliar na prox entrega)
}
