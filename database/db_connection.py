"""
Database Connection Manager for Cooperative Bank Transaction Screening System.
Supports MySQL with automatic SQLite fallback for reliable academic demonstration.
"""

import os
import sqlite3
import pymysql
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "coop_bank_screening")

SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "coop_bank.db")

class DatabaseManager:
    """Manages relational database connections and query execution with dual MySQL/SQLite support."""

    _active_engine = None

    @classmethod
    def get_engine_name(cls) -> str:
        """Returns the currently active database engine name ('MySQL' or 'SQLite')."""
        if cls._active_engine is None:
            cls.test_connection()
        return cls._active_engine or "SQLite"

    @classmethod
    def get_connection(cls):
        """Creates and returns an active database connection object."""
        if DB_TYPE == "mysql":
            try:
                conn = pymysql.connect(
                    host=DB_HOST,
                    port=DB_PORT,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME,
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=False
                )
                cls._active_engine = "MySQL"
                return conn
            except Exception as e:
                # Graceful fallback to SQLite for portable presentation
                cls._active_engine = "SQLite (Fallback)"
                return sqlite3.connect(SQLITE_DB_PATH)
        else:
            cls._active_engine = "SQLite"
            conn = sqlite3.connect(SQLITE_DB_PATH)
            conn.row_factory = sqlite3.Row
            return conn

    @classmethod
    def test_connection(cls) -> dict:
        """Tests the database connection and returns status dictionary."""
        status = {"engine": "Unknown", "connected": False, "message": ""}
        try:
            conn = cls.get_connection()
            status["engine"] = cls._active_engine
            status["connected"] = True
            status["message"] = f"Successfully connected to {cls._active_engine} database."
            conn.close()
        except Exception as ex:
            status["connected"] = False
            status["message"] = f"Connection error: {str(ex)}"
        return status

    @classmethod
    def execute_query(cls, query: str, params=None, commit: bool = False):
        """
        Executes a SQL query safely with parameterized inputs.
        
        Args:
            query: SQL query string (uses %s for MySQL or ? for SQLite)
            params: Tuple or list of parameters
            commit: Whether to commit transaction (for INSERT, UPDATE, DELETE)
            
        Returns:
            DataFrame for SELECT queries, or lastrowid for INSERT queries.
        """
        conn = cls.get_connection()
        engine = cls._active_engine
        
        # Adapt parameter placeholder syntax (%s vs ?)
        is_sqlite = "SQLite" in (engine or "")
        adapted_query = query
        if is_sqlite:
            # Replace %s with ? for SQLite compatibility
            adapted_query = adapted_query.replace("%s", "?")
            # Replace unquoted TRANSACTION table with "TRANSACTION" for SQLite
            import re
            adapted_query = re.sub(r'\bINTO\s+TRANSACTION\b', 'INTO "TRANSACTION"', adapted_query, flags=re.IGNORECASE)
            adapted_query = re.sub(r'\bFROM\s+TRANSACTION\b', 'FROM "TRANSACTION"', adapted_query, flags=re.IGNORECASE)
            adapted_query = re.sub(r'\bJOIN\s+TRANSACTION\b', 'JOIN "TRANSACTION"', adapted_query, flags=re.IGNORECASE)
            adapted_query = re.sub(r'\bUPDATE\s+TRANSACTION\b', 'UPDATE "TRANSACTION"', adapted_query, flags=re.IGNORECASE)
            adapted_query = re.sub(r'\bDELETE\s+FROM\s+TRANSACTION\b', 'DELETE FROM "TRANSACTION"', adapted_query, flags=re.IGNORECASE)
            # Convert MySQL DATE_ADD syntax if present
            adapted_query = adapted_query.replace("DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 5 MINUTE)", "datetime('now', '+5 minutes')")
        
        try:
            if commit:
                cursor = conn.cursor()
                if params:
                    cursor.execute(adapted_query, params)
                else:
                    cursor.execute(adapted_query)
                conn.commit()
                last_id = cursor.lastrowid
                cursor.close()
                return last_id
            else:
                # Read query returning Pandas DataFrame
                if params:
                    df = pd.read_sql_query(adapted_query, conn, params=params)
                else:
                    df = pd.read_sql_query(adapted_query, conn)
                return df
        finally:
            conn.close()

    @classmethod
    def execute_raw(cls, sql_script: str):
        """Executes a multi-statement SQL script."""
        conn = cls.get_connection()
        is_sqlite = "SQLite" in (cls._active_engine or "")
        try:
            cursor = conn.cursor()
            if is_sqlite:
                cursor.executescript(sql_script)
            else:
                for statement in sql_script.split(";"):
                    stmt = statement.strip()
                    if stmt:
                        cursor.execute(stmt)
            conn.commit()
            cursor.close()
        finally:
            conn.close()
