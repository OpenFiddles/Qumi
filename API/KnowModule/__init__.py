import sqlite3
import random
import os

class Know:
    def __init__(self, db_path="QumiData/brain.db"):
        self.db_path = db_path
        # Ensure the data directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """
        Neurons: Represent individual characters/signals.
        Synapses: Represent the learned associations between those signals.
        """
        # Every character is a point in 3D manifold space
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS neurons (
                token TEXT PRIMARY KEY,
                x REAL, y REAL, z REAL,
                voltage REAL DEFAULT 0.5
            )
        ''')
        # Synapses store how likely one character follows another
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS synapses (
                source TEXT,
                target TEXT,
                weight REAL,
                PRIMARY KEY (source, target)
            )
        ''')
        self.conn.commit()

    def get_manifold_state(self, char):
        """
        Finds the (x, y, z) of a character. 
        If it's a new sound/letter, Qumi 'discovers' it at a random coordinate.
        """
        self.cursor.execute("SELECT x, y, z FROM neurons WHERE token = ?", (char,))
        result = self.cursor.fetchone()
        
        if result:
            return {'x': result[0], 'y': result[1], 'z': result[2]}
        else:
            # DISCOVERY: The 'baby' brain creates a new neuron for a new signal
            nx, ny, nz = [random.uniform(-1, 1) for _ in range(3)]
            self.cursor.execute(
                "INSERT INTO neurons (token, x, y, z) VALUES (?, ?, ?, ?)",
                (char, nx, ny, nz)
            )
            self.conn.commit()
            return {'x': nx, 'y': ny, 'z': nz}

    def get_synapses_for(self, char):
        """
        Retrieves the strongest learned connections for a given character.
        Used by Thinker.py to 'babble' and form words.
        """
        self.cursor.execute(
            "SELECT target FROM synapses WHERE source = ? ORDER BY weight DESC LIMIT 5", 
            (char,)
        )
        results = self.cursor.fetchall()
        return [r[0] for r in results]

    def reinforce(self, source, target, strength=0.1):
        """
        Synaptic Plasticity: 'Neurons that fire together, wire together.'
        Strengthens the bond between two characters.
        """
        self.cursor.execute('''
            INSERT OR REPLACE INTO synapses (source, target, weight) 
            VALUES (?, ?, COALESCE((SELECT weight FROM synapses WHERE source = ? AND target = ?) + ?, ?))
        ''', (source, target, source, target, strength, strength))
        self.conn.commit()

    def update_voltage(self, char, delta):
        """Updates the 'emotional' intensity of a specific neuron."""
        self.cursor.execute(
            "UPDATE neurons SET voltage = voltage + ? WHERE token = ?",
            (delta, char)
        )
        self.conn.commit()

    def close_connection(self):
        self.conn.close()

Instance = Know()