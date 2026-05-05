import sqlite3

# This must be the SAME ID used in vault.py and the API
QUMO_SIGNATURE = "QUMIO-CODECS"

def is_qumo_db(db_path):
    """Verifies the database is a valid Qumi Manifold."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT sig_value FROM qumo_metadata WHERE sig_key='id'")
        row = cursor.fetchone()
        conn.close()
        return row and row[0] == QUMO_SIGNATURE
    except:
        return False