// ===================================================
// == FIRMWARE PARA O GATEWAY (RECEPTOR)            ==
// == Arduino UNO #2                                ==
// ===================================================

#include <SPI.h>
#include <LoRa.h>

// --- CONFIGURAÇÃO DOS PINOS LORA ---
// Devem ser os mesmos pinos usados no transmissor
const int LORA_CS_PIN   = 10;
const int LORA_RST_PIN  = 9;
const int LORA_IRQ_PIN  = 2;

void setup() {
  // Inicia a comunicação serial. ESSA É A PONTE PARA O PYTHON!
  Serial.begin(9600);
  while (!Serial);

  Serial.println("LoRa - Gateway (Receptor)");

  LoRa.setPins(LORA_CS_PIN, LORA_RST_PIN, LORA_IRQ_PIN);

  // Inicia o módulo LoRa na frequência correta
  // DEVE SER A MESMA FREQUÊNCIA DO TRANSMISSOR!
  if (!LoRa.begin(915E6)) {
    Serial.println("Erro fatal: falha ao iniciar o módulo LoRa!");
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
    // Um pacote foi recebido, vamos ler o conteúdo
    String payload = "";
    while (LoRa.available()) {
      payload += (char)LoRa.read();
    }

    // IMPRIME O PAYLOAD NA PORTA SERIAL
    // O script Python no PC vai ler esta linha!
    Serial.println(payload);
  }
}