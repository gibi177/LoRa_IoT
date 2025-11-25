#include <Arduino.h>
#include <RadioLib.h>

// Pinagem
#define NSS_PIN   41
#define DIO1_PIN  39
#define RST_PIN   42
#define BUSY_PIN  40

SX1262 radio = new Module(NSS_PIN, DIO1_PIN, RST_PIN, BUSY_PIN);

// Payload binário de 10 bytes
struct __attribute__((packed)) SensorData {
  int16_t temp_raw;
  uint16_t humid_raw;
  uint16_t dust_raw;
  uint16_t batt_raw;
  uint16_t seq_no;
};

RTC_DATA_ATTR float last_temp = 0.0;
RTC_DATA_ATTR float last_humid = 0.0;
RTC_DATA_ATTR float last_dust = 0.0;
RTC_DATA_ATTR int boot_count = 0;
RTC_DATA_ATTR uint16_t packet_counter = 0; // Conta os pacotes mesmo no deep sleep

#define SLEEP_TIME_SEC 5
#define FORCE_SEND_CYCLES 6 // Usa packet_counter para updates obrigatórios a cada 6 ciclos
#define THRESH_TEMP  0.5
#define THRESH_HUMID 2.0
#define THRESH_DUST  10.0

void get_test_data(float &t, float &h, float &d, float &b) {
  t = 25.0; h = 60.0; d = 100.0; b = 95.0;
  if (boot_count <= 2) {
    t = 25.0 + (boot_count * 0.1);
  }
  else if (boot_count == 3) {
    t = 26.0; 
  }
  else if (boot_count <= 5) {
    t = 26.1;
  }
  else if (boot_count == 6) {
    t = 26.2;
  }
  else if (boot_count == 7) {
    h = 65.0; 
  }
  else if (boot_count == 8) {
    d = 120.0; 
  }
  else if (boot_count == 9) {
    t = 24.0; 
  }
  else if (boot_count == 10) {
    t = 50.5;
  }
  else {
    t = 25.0; h = 60.0; d = 100.0;
  }
}

void setup() {
  // Inicia a Serial
  Serial.begin(115200);
  
  // Espera até 5 segundos pela conexão Serial.
  unsigned long start = millis();
  while (!Serial && (millis() - start) < 5000) {
    delay(10);
  }
  
  // Delay extra para garantir que o terminal acordou
  delay(1000); 

  float temperature, humidity, dust, battery;
  get_test_data(temperature, humidity, dust, battery);

  bool should_send = false;

  if (abs(temperature - last_temp) >= THRESH_TEMP) { should_send = true;}
  if (abs(humidity - last_humid) >= THRESH_HUMID) { should_send = true;}
  if (abs(dust - last_dust) >= THRESH_DUST) { should_send = true;}
  
  // Envio de heartbeat forçado
  if (boot_count > 0 && boot_count % FORCE_SEND_CYCLES == 0) { 
    should_send = true; 
  }

  // Primeiro envio, obrigatório
  if (boot_count == 0) { 
    should_send = true; 
  }

  if (should_send) {
    last_temp = temperature;
    last_humid = humidity;
    last_dust = dust;

    int state = radio.begin(915.0);
    if (state == RADIOLIB_ERR_NONE) {
      // Configurações precisam ser idênticas ao gateway
      radio.setSpreadingFactor(10);
      radio.setCodingRate(6);
      radio.setOutputPower(10);

      // Pacote de dados binario
      SensorData packet;
      packet.temp_raw = (int16_t)(temperature * 100);
      packet.humid_raw = (uint16_t)(humidity * 100);
      packet.dust_raw = (uint16_t)dust;
      packet.batt_raw = (uint16_t)(battery * 100);
      packet.seq_no = packet_counter;

      state = radio.transmit((uint8_t *)&packet, sizeof(packet));
      
      if (state == RADIOLIB_ERR_NONE) { // Envio bem sucedido
        packet_counter++;
        radio.sleep();
      } else {
        Serial.print(">> Rádio: Erro TX: "); Serial.println(state);
      }
    } else {
      Serial.print(">> Falha ao iniciar Rádio. Código: ");
      Serial.println(state);
    }
  }

  boot_count++;
  
  Serial.flush(); // Garante que tudo foi enviado antes de desligar o USB
  
  // Deepsleep por 5 seg
  esp_sleep_enable_timer_wakeup(SLEEP_TIME_SEC * 1000000ULL); 
  esp_deep_sleep_start();
}

void loop() {}