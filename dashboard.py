import http.server
import socketserver
import logging
from database import read_last_data

DASHBOARD_PORT = 8080

class DashboardHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

        data = read_last_data(15)

        html = "<html><head><title>Dashboard LoRa</title>"
        html += '<meta http-equiv="refresh" content="5">'
        html += """
        <style> 
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f9; padding: 20px; } 
            h1 { color: #333; }
            table { border-collapse: collapse; width: 100%; background-color: white; box-shadow: 0 0 20px rgba(0,0,0,0.1); } 
            th, td { border: 1px solid #dddddd; text-align: center; padding: 12px; } 
            th { background-color: #009879; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            
            /* Classes para qualidade de sinal RSSI */
            .good { color: green; font-weight: bold; }
            .weak { color: orange; font-weight: bold; }
            .bad { color: red; font-weight: bold; }

            /* Classe para ALERTA DE TEMPERATURA */
            .alert { 
                color: white; 
                background-color: #ff4d4d; /* Fundo vermelho claro */
                font-weight: bold;
                border: 1px solid #cc0000;
            }
        </style>
        """
        html += "</head><body>"
        html += "<h1>📡 Monitoramento Ambiental & Rede LoRa</h1>"
        
        if not data:
            html += "<p>Aguardando dados...</p>"
        else:
            html += "<table><thead><tr>"
            html += "<th>ID Nó</th><th>Timestamp</th>"
            html += "<th>Temp (°C)</th><th>Umid (%)</th><th>Poeira</th><th>Bat (%)</th>"
            html += "<th>Seq #</th><th>RSSI (dBm)</th><th>SNR (dB)</th>"
            html += "</tr></thead><tbody>"
            
            for line in data:
                # Lógica visual para qualidade do sinal RSSI
                rssi = line['rssi'] if line['rssi'] is not None else -999
                rssi_class = "good"
                if rssi < -100: rssi_class = "bad"
                elif rssi < -85: rssi_class = "weak"

                # Lógica visual para ALERTA DE TEMPERATURA (> 40°C)
                temp_val = line['temperature']
                temp_class = ""
                if temp_val > 40.0:
                    temp_class = "alert"

                html += f"<tr>"
                html += f"<td>{line['node_id']}</td>"
                # Mostra só a hora (HH:MM:SS) do timestamp
                timestamp_short = line['timestamp'].split('T')[1][:8] if 'T' in line['timestamp'] else line['timestamp']
                html += f"<td>{timestamp_short}</td>"
                
                # Aplica a classe de alerta na célula de temperatura
                html += f"<td class='{temp_class}'>{temp_val}</td>"
                
                html += f"<td>{line['humidity']}</td>"
                html += f"<td>{line['dust']}</td>"
                html += f"<td>{line['battery']}</td>"
                html += f"<td>{line['seq_no']}</td>"
                html += f"<td class='{rssi_class}'>{line['rssi']}</td>"
                html += f"<td>{line['snr']}</td>"
                html += f"</tr>"
            html += "</tbody></table>"
            
        html += "</body></html>"
        
        self.wfile.write(html.encode('utf-8'))

if __name__ == "__main__":
    with socketserver.TCPServer(("", DASHBOARD_PORT), DashboardHandler) as httpd:
        logging.info(f"Dashboard disponível em http://localhost:{DASHBOARD_PORT}")
        httpd.serve_forever()
