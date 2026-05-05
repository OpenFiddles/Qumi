import sqlite3
import os

# THE MASTER UNIQUE ID
# Ensures Qumi only loads her own 'Blank Slate' memories
QUMO_SIGNATURE = "QUMIO-CODECS"

def verify_vault(db_path):
    """Checks if a database is Qumi-branded."""
    if not os.path.exists(db_path):
        return False
        
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check for Qumi identity stamp
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='qumo_metadata'")
        if not cursor.fetchone():
            conn.close()
            return False
            
        cursor.execute("SELECT sig_value FROM qumo_metadata WHERE sig_key='id'")
        row = cursor.fetchone()
        conn.close()
        
        return row and row[0] == QUMO_SIGNATURE
    except:
        if conn: conn.close()
        return False

def inject_vault_signature(cursor):
    """Stamps the Qumi Identity into a brand new baby brain."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS qumo_metadata 
        (sig_key TEXT, sig_value TEXT)
    """)
    
    cursor.execute("SELECT sig_value FROM qumo_metadata WHERE sig_key='id'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO qumo_metadata (sig_key, sig_value) VALUES ('id', ?)", 
                       (QUMO_SIGNATURE,))