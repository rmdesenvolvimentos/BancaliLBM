import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_file="bancali.db"):
        self.db_file = db_file
        # Verifica se il database esiste già
        db_exists = os.path.exists(db_file)
        self.create_tables()
        
        # Se il database è appena stato creato, inizializza le tabelle
        if not db_exists:
            print("Database appena creato, inizializzazione tabelle...")
    
    def _connect(self):
        """Crea una connessione al database"""
        return sqlite3.connect(self.db_file)
    
    def create_tables(self):
        """Crea le tabelle necessarie se non esistono"""
        conn = self._connect()
        cursor = conn.cursor()
        
        # Tabella bancali
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bancali (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codice TEXT UNIQUE NOT NULL,
            stato TEXT DEFAULT 'magazzino',
            note TEXT
        )
        ''')
        
        # Tabella fornitori
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fornitori (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            indirizzo TEXT,
            telefono TEXT,
            email TEXT
        )
        ''')
        
        # Tabella movimenti
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bancale_id INTEGER,
            fornitore_id INTEGER,
            tipo_movimento TEXT NOT NULL,
            data TEXT NOT NULL,
            note TEXT,
            FOREIGN KEY (bancale_id) REFERENCES bancali (id),
            FOREIGN KEY (fornitore_id) REFERENCES fornitori (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def inizializza_bancali(self, prefisso="PZ00-", inizio=1, fine=2000):
        """Inizializza il database con i bancali dal numero inizio a fine, gestendo due formati"""
        conn = self._connect()
        cursor = conn.cursor()
        
        # Verifica se ci sono già bancali nel database
        cursor.execute("SELECT COUNT(*) FROM bancali")
        count = cursor.fetchone()[0]
        
        if count == 0:
            bancali = []
            for i in range(inizio, fine + 1):
                if i < 1000:
                    # Formato a 5 cifre (es. PZ00-00001)
                    codice = f"{prefisso}{str(i).zfill(5)}"
                else:
                    # Formato a 4 cifre (es. PZ00-1000)
                    codice = f"{prefisso}{str(i).zfill(4)}"
                bancali.append((codice, "magazzino", ""))
            
            cursor.executemany(
                "INSERT INTO bancali (codice, stato, note) VALUES (?, ?, ?)", 
                bancali
            )
            conn.commit()
            result = True
        else:
            result = False
        
        conn.close()
        return result
    
    def aggiungi_fornitore(self, nome, indirizzo="", telefono="", email=""):
        """Aggiunge un nuovo fornitore al database"""
        conn = self._connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO fornitori (nome, indirizzo, telefono, email) VALUES (?, ?, ?, ?)",
            (nome, indirizzo, telefono, email)
        )
        
        conn.commit()
        fornitore_id = cursor.lastrowid
        conn.close()
        
        return fornitore_id
    
    def get_fornitori(self):
        """Restituisce la lista di tutti i fornitori"""
        conn = self._connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id, nome FROM fornitori ORDER BY nome")
            fornitori = cursor.fetchall()
        except sqlite3.OperationalError:
            # Se la tabella non esiste o ha una struttura diversa, ritorna una lista vuota
            fornitori = []
        finally:
            conn.close()
        
        return fornitori
    
    def get_bancali_disponibili(self):
        """Restituisce la lista dei bancali disponibili in magazzino"""
        conn = self._connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id, codice FROM bancali WHERE stato = 'magazzino' ORDER BY codice")
            bancali = cursor.fetchall()
        except sqlite3.OperationalError:
            bancali = []
        finally:
            conn.close()
        
        return bancali
    
    def get_bancali_fornitore(self, fornitore_id):
        """Restituisce la lista dei bancali presso un fornitore"""
        conn = self._connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT b.id, b.codice 
                FROM bancali b 
                WHERE b.stato = 'fornitore' AND b.id IN (
                    SELECT bancale_id 
                    FROM movimenti 
                    WHERE fornitore_id = ? AND tipo_movimento = 'uscita'
                    AND bancale_id NOT IN (
                        SELECT bancale_id 
                        FROM movimenti 
                        WHERE fornitore_id = ? AND tipo_movimento = 'rientro'
                    )
                )
                ORDER BY b.codice
            """, (fornitore_id, fornitore_id))
            bancali = cursor.fetchall()
        except sqlite3.OperationalError:
            bancali = []
        finally:
            conn.close()
        
        return bancali
    
    def spedisci_bancali(self, bancali_ids, fornitore_id, note=""):
        """Registra la spedizione dei bancali al fornitore"""
        conn = self._connect()
        cursor = conn.cursor()
        
        data_ora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            for bancale_id in bancali_ids:
                # Aggiorna lo stato del bancale
                cursor.execute(
                    "UPDATE bancali SET stato = 'fornitore' WHERE id = ?",
                    (bancale_id,)
                )
                
                # Registra il movimento
                cursor.execute(
                    "INSERT INTO movimenti (bancale_id, fornitore_id, tipo_movimento, data, note) VALUES (?, ?, ?, ?, ?)",
                    (bancale_id, fornitore_id, "uscita", data_ora, note)
                )
            
            conn.commit()
            success = True
        except:
            conn.rollback()
            success = False
        finally:
            conn.close()
        
        return success
    
    def rientra_bancali(self, bancali_ids, fornitore_id, note=""):
        """Registra il rientro dei bancali dal fornitore"""
        conn = self._connect()
        cursor = conn.cursor()
        
        data_ora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            for bancale_id in bancali_ids:
                # Aggiorna lo stato del bancale
                cursor.execute(
                    "UPDATE bancali SET stato = 'magazzino' WHERE id = ?",
                    (bancale_id,)
                )
                
                # Registra il movimento
                cursor.execute(
                    "INSERT INTO movimenti (bancale_id, fornitore_id, tipo_movimento, data, note) VALUES (?, ?, ?, ?, ?)",
                    (bancale_id, fornitore_id, "rientro", data_ora, note)
                )
            
            conn.commit()
            success = True
        except:
            conn.rollback()
            success = False
        finally:
            conn.close()
        
        return success
    
    def get_statistiche_fornitori(self):
        """Restituisce statistiche sul numero di bancali presso ogni fornitore"""
        conn = self._connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    f.id, 
                    f.nome, 
                    (SELECT COUNT(*) FROM bancali 
                     WHERE stato = 'fornitore' AND id IN 
                        (SELECT bancale_id FROM movimenti 
                         WHERE fornitore_id = f.id AND tipo_movimento = 'uscita'
                         AND bancale_id NOT IN 
                            (SELECT bancale_id FROM movimenti 
                             WHERE fornitore_id = f.id AND tipo_movimento = 'rientro')
                        )
                    ) AS num_bancali
                FROM 
                    fornitori f
                ORDER BY 
                    f.nome
            """)
            
            statistiche = [(row[0], row[1], row[2]) for row in cursor.fetchall()]
        except sqlite3.Error:
            statistiche = []
        finally:
            conn.close()
        
        return statistiche