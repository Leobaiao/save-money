import sqlite3
import os
import sys
import shutil
from contextlib import contextmanager
from typing import List, Any, Optional

# Localização do banco de dados persistente
def get_db_path():
    # Tenta obter uma pasta de dados persistente
    # No Android (APK), o home costuma ser o diretório privado do app.
    # No Desktop, usamos uma pasta escondida no home do usuário para evitar bundling de dados de teste.
    home = os.path.expanduser("~")
    
    # Se estivermos no Android (via Flet/Buildozer), podemos tentar caminhos específicos se necessário, 
    # mas expanduser("~") costuma ser seguro para dados internos.
    db_dir = os.path.join(home, ".savemoney")
    
    try:
        os.makedirs(db_dir, exist_ok=True)
    except Exception:
        # Fallback para o diretório atual se o home não for gravável
        db_dir = os.path.join(os.getcwd(), "data")
        os.makedirs(db_dir, exist_ok=True)
        
    path = os.path.join(db_dir, "save_money.db")
    # Este print ajudará a identificar onde o banco está sendo criado no APK (via logcat)
    print(f"--- DATABASE PATH: {path} ---")
    return path

DB_PATH = get_db_path()

class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self):
        with self.get_connection() as conn:
            # Table: transactions
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id TEXT PRIMARY KEY,
                    description TEXT,
                    amount REAL,
                    type TEXT,
                    category_id TEXT,
                    date TEXT,
                    due_date TEXT,
                    payment_date TEXT,
                    notes TEXT,
                    is_paid INTEGER,
                    is_fixed INTEGER,
                    is_recurring INTEGER,
                    recurrence_type TEXT DEFAULT 'none',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Verificação de colunas existentes (migração automática autoritativa)
            cursor = conn.execute("PRAGMA table_info(transactions)")
            existing_columns = [row[1] for row in cursor.fetchall()]

            required_columns = {
                "due_date": "TEXT",
                "payment_date": "TEXT",
                "notes": "TEXT",
                "is_paid": "INTEGER",
                "is_fixed": "INTEGER",
                "is_recurring": "INTEGER",
                "recurrence_type": "TEXT DEFAULT 'none'",
                "created_at": "TEXT DEFAULT CURRENT_TIMESTAMP"
            }

            for col, definition in required_columns.items():
                if col not in existing_columns:
                    try:
                        conn.execute(f"ALTER TABLE transactions ADD COLUMN {col} {definition}")
                        print(f"Coluna {col} adicionada à tabela transactions.")
                    except Exception as e:
                        print(f"Erro ao adicionar coluna {col}: {e}")
            
            # Table: categories
            conn.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    icon TEXT,
                    color TEXT,
                    type TEXT
                )
            """)
            
            # Table: settings
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

    def execute(self, query: str, params: tuple = ()) -> int:
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.rowcount

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchone()

    def fetch_all(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()

    def reset_database(self):
        """Apaga o arquivo do banco de dados e reinicializa."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            self.init_db()
            return True
        return False

    def export_database(self) -> Optional[str]:
        """Copia o banco de dados para a pasta Downloads do sistema."""
        try:
            home = os.path.expanduser("~")
            downloads_dir = os.path.join(home, "Downloads")
            if not os.path.exists(downloads_dir):
                # Fallback para o home se Downloads não existir (raro no Android/Windows)
                downloads_dir = home
            
            dest_path = os.path.join(downloads_dir, "save_money_export.db")
            shutil.copy2(self.db_path, dest_path)
            return dest_path
        except Exception as e:
            print(f"Erro ao exportar banco: {e}")
            return None
