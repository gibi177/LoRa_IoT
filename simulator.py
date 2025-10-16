# simulador.py
import requests
import json
import time
import random
from datetime import datetime, timezone

SERVER_URL = "http://localhost:8000/data"

def gerar_dados_simulados():
    """Gera um payload de dados falsos."""
    return {
        "node_id": "sala_B_02",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {
            "temperature": round(random.uniform(20.0, 35.0), 2),
            "humidity": round(random.uniform(40.0, 75.0), 2),
            "dust_level": round(random.uniform(50.0, 300.0), 2)
        }
    }

if __name__ == "__main__":
    while True:
        try:
            payload = gerar_dados_simulados()
            print(f"Enviando dados: {payload}")
            
            response = requests.post(SERVER_URL, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                print("Dados enviados com sucesso!")
            else:
                print(f"Erro ao enviar dados: {response.status_code} - {response.text}")
        
        except requests.exceptions.RequestException as e:
            print(f"Não foi possível conectar ao servidor: {e}")
        
        # Espera 10 segundos para o próximo envio
        time.sleep(10)
