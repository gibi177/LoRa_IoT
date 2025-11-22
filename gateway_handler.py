import serial
import time
import json
import requests
from datetime import datetime, timezone, timedelta

# --- CONFIGURAÇÃO ---
SERIAL_PORT = '/dev/ttyACM0'  # Verifique sua porta!
BAUD_RATE = 115200
SERVER_URL = 'http://localhost:8000/data'  

def parse_sensor_data(line):
    try:
        # Formato esperado: temp,humid,dust,batt,seq_no,rssi,snr
        parts = line.strip().split(',')
        
        # Se recebermos CRC_ERROR ou lixo, ignoramos
        if len(parts) != 7:
            print(f"Formato inválido ou incompleto ({len(parts)} campos): {line}")
            return None
        
        temperature = float(parts[0])
        humidity = float(parts[1])
        dust_level = float(parts[2])
        battery = float(parts[3])
        seq_no = int(parts[4])     # NOVO
        rssi = float(parts[5])     # NOVO
        snr = float(parts[6])      # NOVO

        data = {
            "node_id": "sala_B_02", 
            "timestamp": datetime.now(timezone(timedelta(hours=-3))).isoformat(),
            "data": {
                "temperature": temperature,
                "humidity": humidity,
                "dust_level": dust_level,
                "battery": battery
            },
            "network_metrics": {    # Novo objeto JSON separado para métricas
                "sequence_number": seq_no,
                "rssi": rssi,
                "snr": snr
            }
        }
        return data
    except Exception as e:
        print(f"Erro ao interpretar linha: {e}")
        return None

def main():
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            print(f"Conectado ao Gateway na porta {SERIAL_PORT}...")
            while True:
                if ser.in_waiting > 0:
                    try:
                        line = ser.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            print(f"Recebido Serial: {line}")
                            json_data = parse_sensor_data(line)
                            if json_data:
                                try:
                                    # Envia para o servidor
                                    response = requests.post(SERVER_URL, json=json_data)
                                    if response.status_code == 200:
                                        print(f"Sucesso! [Seq: {json_data['network_metrics']['sequence_number']} | RSSI: {json_data['network_metrics']['rssi']} dBm]")
                                    else:
                                        print(f"Falha HTTP: {response.status_code}")
                                except Exception as e:
                                    print(f"Erro HTTP: {e}")
                    except Exception as e:
                        print(f"Erro Serial: {e}")
                time.sleep(0.1)
    except serial.SerialException as e:
        print(f"ERRO FATAL: Não foi possível abrir a porta {SERIAL_PORT}.")
        print(f"Detalhe: {e}")

if __name__ == '__main__':
    main()
