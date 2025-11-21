/*
 * Cliente LoRa OTIMIZADO v3 (Transmissor)
 * Inclui Sequence Number no Payload para detecção de perda de pacotes.
 */

#include <Arduino.h>
#include <RadioLib.h>

#define NSS_PIN 41
#define DIO1_PIN 39
#define RST_PIN 42
#define BUSY_PIN 40

SX1262 radio = new Module(NSS_PIN, DIO1_PIN, RST_PIN, BUSY_PIN);

// --- PAYLOAD BINÁRIO ATUALIZADO (10 BYTES) ---
struct __attribute__((packed)) SensorData
{
  int16_t temp_raw;
  uint16_t humid_raw;
  uint16_t dust_raw;
  uint16_t batt_raw;
  uint16_t seq_no; // NOVO: Contador de pacotes (0 a 65535)
};

// Variáveis RTC
RTC_DATA_ATTR float last_temp = 0.0;
RTC_DATA_ATTR float last_humid = 0.0;
RTC_DATA_ATTR float last_dust = 0.0;
RTC_DATA_ATTR int boot_count = 0;
RTC_DATA_ATTR uint16_t packet_counter = 0; // NOVO: Mantém contagem no Deep Sleep

#define SLEEP_TIME_SEC 10
#define FORCE_SEND_CYCLES 6
#define THRESH_TEMP 0.5
#define THRESH_HUMID 2.0
#define THRESH_DUST 10.0

void setup()
{
  Serial.begin(115200);
  unsigned long start = millis();
  while (!Serial && millis() - start < 2000)
    ;

  Serial.print("Boot #");
  Serial.println(boot_count);
  boot_count++;

  // Geração de dados simulados
  float temperature = random(1500, 4500) / 100.0;
  float humidity = random(500, 10000) / 100.0;
  float dust = random(50, 300);
  float battery = random(0, 10000) / 100.0;

  bool should_send = false;
  String motivo = "";

  if (abs(temperature - last_temp) >= THRESH_TEMP)
  {
    should_send = true;
    motivo += "[Temp] ";
  }
  if (abs(humidity - last_humid) >= THRESH_HUMID)
  {
    should_send = true;
    motivo += "[Umid] ";
  }
  if (abs(dust - last_dust) >= THRESH_DUST)
  {
    should_send = true;
    motivo += "[Poeira] ";
  }
  if (boot_count % FORCE_SEND_CYCLES == 0)
  {
    should_send = true;
    motivo += "[Heartbeat]";
  }
  if (boot_count == 1)
    should_send = true;

  if (should_send)
  {
    last_temp = temperature;
    last_humid = humidity;
    last_dust = dust;

    Serial.print(">> ENVIANDO Packet #");
    Serial.print(packet_counter);
    Serial.print(". Motivo: ");
    Serial.println(motivo);

    int state = radio.begin(915.0);
    if (state == RADIOLIB_ERR_NONE)
    {
      radio.setSpreadingFactor(10);
      radio.setCodingRate(6);
      radio.setOutputPower(10);

      SensorData packet;
      packet.temp_raw = (int16_t)(temperature * 100);
      packet.humid_raw = (uint16_t)(humidity * 100);
      packet.dust_raw = (uint16_t)dust;
      packet.batt_raw = (uint16_t)(battery * 100);
      packet.seq_no = packet_counter; // Insere o contador atual

      state = radio.transmit((uint8_t *)&packet, sizeof(packet));

      if (state == RADIOLIB_ERR_NONE)
      {
        Serial.println(" Sucesso!");
        packet_counter++; // Incrementa SÓ se enviou com sucesso
        radio.sleep();
      }
      else
      {
        Serial.print(" Erro TX: ");
        Serial.println(state);
      }
    }
  }
  else
  {
    Serial.println(">> Nenhuma mudança. Economizando...");
  }

  esp_sleep_enable_timer_wakeup(SLEEP_TIME_SEC * 1000000ULL);
  esp_deep_sleep_start();
}

void loop() {}
