import http.server
import socketserver
import json
import logging
from database import write_data, initialize_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PORT = 8000

class DataHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/data':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                payload = json.loads(post_data.decode('utf-8'))
                
                # Extrai dados dos sensores e dados da rede
                sensor_data = payload.get('data', {})
                network_data = payload.get('network_metrics', {})

                logging.info(f"RX de {payload.get('node_id')}: Temp={sensor_data.get('temperature')} RSSI={network_data.get('rssi')}")

                # Passa ambos os dicionários para a função write_data
                if write_data(payload['node_id'], payload['timestamp'], sensor_data, network_data):
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "sucesso"}).encode('utf-8'))
                else:
                    self.send_response(500)
                    self.end_headers()

            except (json.JSONDecodeError, KeyError) as e:
                logging.error(f"Erro no payload JSON: {e}")
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "erro", "message": "Payload inválido"}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    initialize_db()
    with socketserver.TCPServer(("", PORT), DataHandler) as httpd:
        logging.info(f"Servidor de dados iniciado na porta {PORT}")
        httpd.serve_forever()
