import http.server
import socketserver
import logging
from database import read_last_data

# Servidor ficará disponível em página web, porta 8080
DASHBOARD_PORT = 8080

class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Define cabeçalho com tipo de conteúto que será enviado (html)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

        # Busca os últimos dados do database
        data = read_last_data(15)

        # Gera o HTML dinamicamente
        html = "<html><head><title>Dashboard de Monitoramento</title>"
        # Refresh cada 5 segundos
        html += '<meta http-equiv="refresh" content="5">'
        html += "<style> body { font-family: sans-serif; } table { border-collapse: collapse; width: 100%; } th, td { border: 1px solid #dddddd; text-align: left; padding: 8px; } </style>"
        html += "</head><body>"
        html += "<h1>Dashboard de Monitoramento Ambiental</h1>"
        
        if not data:
            html += "<p>Aguardando recebimento dos dados...</p>"
        else:
            # TODO: Checar unidade do sensor de poeira
            html += "<table><tr><th>ID do Nó</th><th>Timestamp</th><th>Temperatura (°C)</th><th>Umidade (%)</th><th>Poeira (a definir unidade)</th><th>Bateria (%)</th></tr>"
            for line in data:
                html += f"<tr><td>{line['node_id']}</td><td>{line['timestamp']}</td><td>{line['temperature']}</td><td>{line['humidity']}</td><td>{line['dust']}</td><td>{line['battery']}</td></tr>"
            html += "</table>"
            
        html += "</body></html>"
        
        self.wfile.write(html.encode('utf-8'))

if __name__ == "__main__":
    with socketserver.TCPServer(("", DASHBOARD_PORT), DashboardHandler) as httpd:
        logging.info(f"Dashboard disponível em http://localhost:{DASHBOARD_PORT}")
        httpd.serve_forever() # Funciona continuamente
