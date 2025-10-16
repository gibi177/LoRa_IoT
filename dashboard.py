# dashboard.py
import http.server
import socketserver
import logging
from database import ler_ultimos_dados

DASHBOARD_PORT = 8080

class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

        # Busca os últimos dados do banco
        dados = ler_ultimos_dados(15)

        # Gera o HTML dinamicamente
        html = "<html><head><title>Dashboard de Monitoramento</title>"
        # Adiciona auto-refresh a cada 5 segundos
        html += '<meta http-equiv="refresh" content="5">'
        html += "<style> body { font-family: sans-serif; } table { border-collapse: collapse; width: 100%; } th, td { border: 1px solid #dddddd; text-align: left; padding: 8px; } </style>"
        html += "</head><body>"
        html += "<h1>Dashboard de Monitoramento Ambiental</h1>"
        
        if not dados:
            html += "<p>Aguardando recebimento de dados...</p>"
        else:
            html += "<table><tr><th>ID do Nó</th><th>Timestamp</th><th>Temperatura (°C)</th><th>Umidade (%)</th><th>Poeira (µg/m³)</th></tr>"
            for linha in dados:
                html += f"<tr><td>{linha['node_id']}</td><td>{linha['timestamp']}</td><td>{linha['temperatura']}</td><td>{linha['umidade']}</td><td>{linha['poeira']}</td></tr>"
            html += "</table>"
            
        html += "</body></html>"
        
        self.wfile.write(html.encode('utf-8'))

if __name__ == "__main__":
    with socketserver.TCPServer(("", DASHBOARD_PORT), DashboardHandler) as httpd:
        logging.info(f"Dashboard disponível em http://localhost:{DASHBOARD_PORT}")
        httpd.serve_forever()
