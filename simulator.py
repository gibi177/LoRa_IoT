import requests
import json
import time
import random
from datetime import datetime, timezone

SERVER_URL = "http://localhost:8000/data"

def generate_simulated_data():
    """Gera um payload de dados falsos."""
    return {
        "node_id": "sala_B_02",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {
            # Gera dados aletaórios dentro de um certo intervalo de valores e com precisão de duas casas decimais
            "temperature": round(random.uniform(20.0, 35.0), 2),
            "humidity": round(random.uniform(40.0, 75.0), 2),
            "dust_level": round(random.uniform(50.0, 300.0), 2)
        }
    }

if __name__ == "__main__":
    while True:
        try:
            payload = generate_simulated_data()
            print(f"Enviando dados: {payload}")
            
            # Envia uma requisição HTTP POST para um servidor, transmitindo os dados no formato JSON
            response = requests.post(SERVER_URL, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                print("Dados enviados com sucesso!")
            else:
                print(f"Erro ao enviar dados: {response.status_code} - {response.text}")
        
        except requests.exceptions.RequestException as e:
            print(f"Não foi possível conectar ao servidor: {e}")
        
        # Espera 10 segundos para o próximo envio
        time.sleep(10)
