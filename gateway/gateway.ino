#include <SPI.h>
#include <LoRa.h>

// A config dos pinos deve ser a mesma do outro arduino
const int LORA_CS_PIN   = 10;
const int LORA_RST_PIN  = 9;
const int LORA_IRQ_PIN  = 2;

void setup() {
  Serial.begin(9600);
  while (!Serial);

  Serial.println("LoRa - Gateway (Receptor)");

  LoRa.setPins(LORA_CS_PIN, LORA_RST_PIN, LORA_IRQ_PIN);

  // A frequência deve ser a mesma do transmissor
  if (!LoRa.begin(915E6)) {
    Serial.println("Falha ao iniciar o módulo LoRa");
    while (1);
  }

  // Ativa o modo de recepção contínua
  LoRa.receive();
  Serial.println("Aguardando pacotes...");
}

void loop() {
  // Verifica se um pacote foi recebido
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    String payload = "";
    while (LoRa.available()) {
      payload += (char)LoRa.read();
    }

    // Imprime o payload na porta serial, que será lida pelo PC
    Serial.println(payload);
  }
}