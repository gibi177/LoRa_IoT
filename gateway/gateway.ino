/*
 * Gateway LoRa OTIMIZADO v3 (Receptor)
 * Recebe Struct Binária, extrai métricas de rede e envia CSV completo.
 */

#include <Arduino.h>
#include <RadioLib.h>

#define NSS_PIN 41
#define DIO1_PIN 39
#define RST_PIN 42
#define BUSY_PIN 40

SX1262 radio = new Module(NSS_PIN, DIO1_PIN, RST_PIN, BUSY_PIN);

struct __attribute__((packed)) SensorData
{
  int16_t temp_raw;
  uint16_t humid_raw;
  uint16_t dust_raw;
  uint16_t batt_raw;
  uint16_t seq_no; // NOVO CAMPO
};

volatile bool pacoteRecebido = false;

#if defined(ESP8266) || defined(ESP32)
ICACHE_RAM_ATTR
#endif
void setFlag(void)
{
  pacoteRecebido = true;
}

void setup()
{
  Serial.begin(115200);
  delay(2000);
  Serial.println("Gateway LoRa Iniciado (Métricas de Rede Ativas)");

  int state = radio.begin(915.0);
  if (state == RADIOLIB_ERR_NONE)
  {
    radio.setSpreadingFactor(10);
    radio.setCodingRate(6);
    radio.setDio1Action(setFlag);
    radio.startReceive();
  }
  else
  {
    while (true)
      ;
  }
}

void loop()
{
  if (pacoteRecebido)
  {
    pacoteRecebido = false;

    uint8_t byteArr[sizeof(SensorData)];
    int state = radio.readData(byteArr, sizeof(SensorData));

    if (state == RADIOLIB_ERR_NONE)
    {
      SensorData *packet = (SensorData *)byteArr;

      // Conversão dos dados
      float temp = packet->temp_raw / 100.0;
      float humid = packet->humid_raw / 100.0;
      float dust = packet->dust_raw;
      float batt = packet->batt_raw / 100.0;
      uint16_t seq = packet->seq_no;

      // NOVO: Coleta métricas de rede do pacote recebido
      float rssi = radio.getRSSI();
      float snr = radio.getSNR();

      // Formato CSV expandido:
      // temp,humid,dust,batt,seq_no,rssi,snr
      Serial.print(temp, 2);
      Serial.print(",");
      Serial.print(humid, 2);
      Serial.print(",");
      Serial.print(dust, 0);
      Serial.print(",");
      Serial.print(batt, 2);
      Serial.print(",");
      Serial.print(seq);
      Serial.print(","); // Sequence Number
      Serial.print(rssi, 1);
      Serial.print(",");      // RSSI
      Serial.println(snr, 2); // SNR
    }
    else if (state == RADIOLIB_ERR_CRC_MISMATCH)
    {
      Serial.println("CRC_ERROR");
    }

    radio.startReceive();
  }
}
