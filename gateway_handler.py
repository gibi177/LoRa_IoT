import serial
import time
import json
import requests
from datetime import datetime, timezone

# Configurações
SERIAL_PORT = '/dev/ttyACM0'  # Altere para a porta serial onde seu Arduino está conectado (exemplo: COM3 no Windows, /dev/ttyUSB0 no Linux)
BAUD_RATE = 9600
SERVER_URL = 'http://localhost:8000/data'  # URL do seu backend para envio dos dados

def parse_sensor_data(line):
    try:
        # A linha vem como: 33.07,27.49,123,36.58
        parts = line.strip().split(',')
        if len(parts) != 4:
            print(f"Formato inválido: {line}")
            return None
        
        temperature = float(parts[0])
        humidity = float(parts[1])
        dust_level = float(parts[2])
        battery = float(parts[3])

        data = {
            "node_id": "sala_B_02",  # Exemplo fixo, adapte conforme sua rede
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {
                "temperature": temperature,
                "humidity": humidity,
                "dust_level": dust_level,
                "battery": battery
            }
        }
        return data
    except Exception as e:
        print(f"Erro ao interpretar linha: {e}")
        return None

def main():
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        print(f"Lendo dados da porta serial {SERIAL_PORT}...")
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"Recebido: {line}")
                    json_data = parse_sensor_data(line)
                    if json_data:
                        try:
                            response = requests.post(SERVER_URL, json=json_data)
                            if response.status_code == 200:
                                print("Dados enviados com sucesso")
                            else:
                                print(f"Falha no envio: {response.status_code} - {response.text}")
                        except Exception as e:
                            print(f"Erro ao enviar dados para servidor: {e}")
            time.sleep(0.1)

if __name__ == '__main__':
    main()
