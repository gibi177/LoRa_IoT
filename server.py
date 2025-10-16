# servidor.py
import http.server
import socketserver
import json
import logging
from database import salvar_dados, inicializar_db

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PORT = 8000

class DataHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/data':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                payload = json.loads(post_data.decode('utf-8'))
                logging.info(f"Dados recebidos de {payload.get('node_id')}: {payload.get('data')}")

                # Salva os dados no banco de dados
                if salvar_dados(payload['node_id'], payload['timestamp'], payload['data']):
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "sucesso"}).encode('utf-8'))
                else:
                    self.send_response(500) # Internal Server Error
                    self.end_headers()

            except (json.JSONDecodeError, KeyError) as e:
                logging.error(f"Erro no payload JSON: {e}")
                self.send_response(400) # Bad Request
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "erro", "message": "Payload inválido"}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        # Futuramente, pode ser usado para uma API de leitura
        self.send_response(404)
        self.end_headers()

if __name__ == "__main__":
    # Garante que o DB e a tabela existam antes de iniciar o servidor
    inicializar_db()

    with socketserver.TCPServer(("", PORT), DataHandler) as httpd:
        logging.info(f"Servidor de dados iniciado na porta {PORT}")
        httpd.serve_forever()