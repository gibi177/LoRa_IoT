import sqlite3
import logging

DATABASE_FILE = "sensors.db"

def initialize_db():
    """Cria a tabela de dados se ela não existir"""

    try:
        conn = sqlite3.connect(DATABASE_FILE) # Conecta ao banco de dados
        cursor = conn.cursor() # Cria cursor, objeto usado para executar comandos SQL
        # Note que id é uma coluna do dataset em que cada valor é único e não pode ser NULL.
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            node_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            temperature REAL,
            humidity REAL,
            dust REAL,
            battery REAL
        )
        """)
        conn.commit() # Salvar mudanças 
        conn.close()  
        logging.info("Banco de dados inicializado com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao inicializar o banco de dados: {e}")

def write_data(node_id, timestamp, data):
    """Escreve uma nova leitura no banco de dados"""

    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        # As interrogações são placeholders que serão substituídos pelas informações correspondentes dos sensores. Usado para evitar SQL injection 
        cursor.execute("""
            INSERT INTO Readings (node_id, timestamp, temperature, humidity, dust, battery)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (node_id, timestamp, data.get('temperature'), data.get('humidity'), data.get('dust_level'), data.get('battery')))
        conn.commit()
        conn.close()
        return True

    except Exception as e:
        logging.error(f"Erro ao salvar dados: {e}")
        return False

def read_last_data(limit=10):
    """Lê as últimas 'limit' leituras do banco de dados."""

    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row # Permite acessar colunas pelo nome
        cursor = conn.cursor()
        # Seleciona últimas 'limit' leituras dos sensores 
        cursor.execute("SELECT * FROM Readings ORDER BY id DESC LIMIT ?", (limit,))
        dados = cursor.fetchall() # Busca os resultados da consulta SQL
        conn.close()
        return dados

    except Exception as e:
        logging.error(f"Erro ao ler dados: {e}")
        return []

