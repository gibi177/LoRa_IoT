# database.py
import sqlite3
import logging

DATABASE_FILE = "monitoramento.db"

def inicializar_db():
    """Cria a tabela de dados se ela não existir."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS leituras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            temperatura REAL,
            umidade REAL,
            poeira REAL
        )
        """)
        conn.commit()
        conn.close()
        logging.info("Banco de dados inicializado com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao inicializar o banco de dados: {e}")

def salvar_dados(node_id, timestamp, data):
    """Salva uma nova leitura no banco de dados."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO leituras (node_id, timestamp, temperatura, umidade, poeira)
        VALUES (?, ?, ?, ?, ?)
        """, (node_id, timestamp, data.get('temperature'), data.get('humidity'), data.get('dust_level')))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logging.error(f"Erro ao salvar dados: {e}")
        return False

def ler_ultimos_dados(limit=10):
    """Lê as últimas 'limit' leituras do banco de dados."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row # Permite acessar colunas pelo nome
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leituras ORDER BY id DESC LIMIT ?", (limit,))
        dados = cursor.fetchall()
        conn.close()
        return dados
    except Exception as e:
        logging.error(f"Erro ao ler dados: {e}")
        return []

