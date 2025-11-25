import sqlite3
import logging

DATABASE_FILE = "sensors.db"

def initialize_db():
    """Cria a tabela de dados se ela não existir"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            node_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            temperature REAL,
            humidity REAL,
            dust REAL,
            battery REAL,
            seq_no INTEGER,
            rssi REAL,
            snr REAL
        )
        """)
        conn.commit()
        conn.close()
        logging.info("Banco de dados inicializado com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao inicializar o banco de dados: {e}")

def write_data(node_id, timestamp, data, network):
    """Escreve uma nova leitura no banco de dados.
       'data' contém as informações dos sensores. 
       'network' contém as métricas de rede.
    """
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Readings (node_id, timestamp, temperature, humidity, dust, battery, seq_no, rssi, snr)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                node_id, 
                timestamp, 
                data.get('temperature'), 
                data.get('humidity'), 
                data.get('dust_level'), 
                data.get('battery'),
                network.get('sequence_number'),
                network.get('rssi'),
                network.get('snr')
            ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logging.error(f"Erro ao salvar dados: {e}")
        return False

def read_last_data(limit=15):
    """Lê as últimas 'limit' leituras do banco de dados."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Readings ORDER BY id DESC LIMIT ?", (limit,))
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Exception as e:
        logging.error(f"Erro ao ler dados: {e}")
        return []
