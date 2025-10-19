import http.server
import socketserver
import json
import logging  # Registra mensagens informativas e de erro em um formato padronizado
from database import write_data, initialize_db

# Configuração do logging definindo como cada linha de log será impressa (data/hora, nível do log e a mensagem)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PORT = 8000

# Cria classe principal que herda de BaseHTTPRequestHandler
class DataHandler(http.server.BaseHTTPRequestHandler):
    # Sobrescreve método do_POST
    def do_POST(self):
        if self.path == '/data':    # Verifica se a requisição foi feita para o caminho (endpoint) /data
            try:
                # Lê o corpo da requisição, obtendo o tamanho dos dados
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # Decodifica os dados em formato JSON e pega suas informações
                payload = json.loads(post_data.decode('utf-8'))
                logging.info(f"Dados recebidos de {payload.get('node_id')}: {payload.get('data')}")

                # Salva os dados no banco de dados
                if write_data(payload['node_id'], payload['timestamp'], payload['data']):
                    self.send_response(200) # Responde com sucesso
                    # Monta o cabeçalho da resposta
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    # Escreve mensagem de confirmação para o cliente
                    self.wfile.write(json.dumps({"status": "sucesso"}).encode('utf-8'))
                else:
                    self.send_response(500) # Internal Server Error
                    self.end_headers()

            except (json.JSONDecodeError, KeyError) as e:
                # Responde com erro (400) se o payload for inválido
                logging.error(f"Erro no payload JSON: {e}")
                self.send_response(400) # Bad Request
                # Monta mensagem de erro para o cliente
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "erro", "message": "Payload inválido"}).encode('utf-8'))
        else:
            # Lança erro caso a requisição seja feita para caminho errado
            self.send_response(404) # Not Found
            self.end_headers()


if __name__ == "__main__":
    # Garante que o banco de dados e a tabela existam antes de iniciar o servidor
    initialize_db()

    # Coloca o servidor para escutar em todos os endereços de rede disponíveis na máquina na porta 8000
    with socketserver.TCPServer(("", PORT), DataHandler) as httpd:
        logging.info(f"Servidor de dados iniciado na porta {PORT}")
        # Coloca o seervidor em loop infinito
        httpd.serve_forever()