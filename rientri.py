import tkinter as tk
from tkinter import ttk, messagebox
import time
import sqlite3

class RientriFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.barcode_buffer = ""
        self.last_scan_time = 0
        self.bancali_selezionati = []# Lista per tenere traccia degli ID dei bancali scansionati
        self.bancali_info = {} # Dizionario per tenere traccia di ID e fornitore del bancale
        self.init_ui()

    def aggiorna_lista_fornitori(self):
        """Metodo necessario per il callback di aggiornamento fornitori"""
        pass

    def init_ui(self):
        """Inizializza l'interfaccia per il rientro dei bancali"""
        # Frame per il lettore di codici a barre
        barcode_frame = ttk.LabelFrame(self, text="Scansione Codici a Barre")
        barcode_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(barcode_frame, text="Scansiona codice:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.barcode_entry = ttk.Entry(barcode_frame, width=30)
        self.barcode_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.barcode_entry.bind("<KeyPress>", self.on_barcode_keypress)
        self.barcode_entry.bind("<Return>", self.process_barcode)

        # Stato scansione
        self.scan_status_var = tk.StringVar(value="Pronto per la scansione")
        ttk.Label(barcode_frame, textvariable=self.scan_status_var).grid(row=0, column=2, padx=10, pady=5)

        # Frame per la lista dei bancali scansionati
        bancali_frame = ttk.LabelFrame(self, text="Bancali Scansionati per Rientro")
        bancali_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Pulsanti per gestire la lista
        btn_frame = ttk.Frame(bancali_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        self.remove_btn = ttk.Button(btn_frame, text="Rimuovi Selezionati", command=self.rimuovi_selezionati)
        self.remove_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(btn_frame, text="Svuota Lista", command=self.svuota_lista)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Crea la Treeview per i bancali scansionati
        columns = ("ID", "Codice", "Fornitore", "Fornitore ID") # Aggiungiamo una colonna nascosta per l'ID fornitore
        self.bancali_tree = ttk.Treeview(bancali_frame, columns=columns, show='headings', selectmode="extended")

        self.bancali_tree.heading("ID", text="ID")
        self.bancali_tree.heading("Codice", text="Codice Bancale")
        self.bancali_tree.heading("Fornitore", text="Fornitore")
        self.bancali_tree.heading("Fornitore ID", text="Fornitore ID") # Intestazione per la colonna nascosta
        self.bancali_tree.column("Fornitore ID", width=0, stretch=tk.NO) # Nascondi la colonna dell'ID fornitore

        self.bancali_tree.column("ID", width=50)
        self.bancali_tree.column("Codice", width=150)
        self.bancali_tree.column("Fornitore", width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(bancali_frame, orient=tk.VERTICAL, command=self.bancali_tree.yview)
        self.bancali_tree.configure(yscroll=scrollbar.set)

        # Layout
        self.bancali_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Contatore bancali
        self.counter_var = tk.StringVar(value="Bancali: 0")
        ttk.Label(self, textvariable=self.counter_var).pack(anchor=tk.W, padx=10)

        # Pulsante rientra
        rientra_button = ttk.Button(self, text="Registra Rientro Bancali", command=self.rientra_bancali)
        rientra_button.pack(pady=10)

        # Metti subito il focus sul campo di scansione
        self.barcode_entry.focus_set()

    def on_barcode_keypress(self, event):
        """Gestisce l'input dal lettore di codici a barre"""
        # Reset buffer se è passato troppo tempo dall'ultimo carattere
        current_time = time.time()
        if current_time - self.last_scan_time > 0.5:  # timeout di 500ms
            self.barcode_buffer = ""

        self.last_scan_time = current_time

    def process_barcode(self, event):
        """Processa il codice a barre quando viene completato (invio)"""
        barcode = self.barcode_entry.get().strip()
        if not barcode:
            return

        # Verifica se il bancale è presso un fornitore
        conn = sqlite3.connect(self.db.db_file)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT b.id, b.codice, f.nome, f.id
            FROM bancali b
            JOIN movimenti m ON b.id = m.bancale_id
            JOIN fornitori f ON m.fornitore_id = f.id
            WHERE b.codice = ? AND m.tipo_movimento = 'uscita'
            AND b.id NOT IN (
                SELECT bancale_id FROM movimenti
                WHERE tipo_movimento = 'rientro' AND bancale_id = b.id
            )
            ORDER BY m.data DESC
            LIMIT 1
        """, (barcode,))
        result = cursor.fetchone()
        conn.close()

        if result:
            bancale_id, bancale_code, fornitore_nome, fornitore_id = result

            # Verifica se il bancale è già stato scansionato
            for item in self.bancali_tree.get_children():
                if int(self.bancali_tree.item(item, "values")[0]) == bancale_id:
                    self.scan_status_var.set("Bancale già scansionato!")
                    self.flash_status_color("red")
                    self.barcode_entry.delete(0, tk.END)
                    return

            # Aggiungi il bancale alla lista
            self.bancali_tree.insert("", tk.END, values=(bancale_id, bancale_code, fornitore_nome, fornitore_id))
            self.bancali_selezionati.append(bancale_id)

            # Aggiorna il contatore
            self.counter_var.set(f"Bancali: {len(self.bancali_selezionati)}")

            # Mostra conferma
            self.scan_status_var.set(f"Bancale {bancale_code} aggiunto!")
            self.flash_status_color("green")
        else:
            # Bancale non trovato o non disponibile
            self.scan_status_var.set("Bancale non trovato presso un fornitore o già rientrato!")
            self.flash_status_color("red")

        # Pulisci il campo e mantieni il focus per la prossima scansione
        self.barcode_entry.delete(0, tk.END)
        self.barcode_entry.focus_set()

    def flash_status_color(self, color):
        """Cambia temporaneamente il colore dello stato per dare feedback visivo"""
        # Questa è una versione semplificata, si potrebbe implementare un effetto più elaborato
        self.scan_status_var.set_bg = color
        self.after(1000, lambda: setattr(self.scan_status_var, 'set_bg', 'default'))

    def rimuovi_selezionati(self):
        """Rimuove i bancali selezionati dalla lista"""
        selected_items = self.bancali_tree.selection()
        if not selected_items:
            return

        for item in selected_items:
            bancale_id = self.bancali_tree.item(item, "values")[0]
            if int(bancale_id) in self.bancali_selezionati:
                self.bancali_selezionati.remove(int(bancale_id))
            self.bancali_tree.delete(item)

        # Aggiorna il contatore
        self.counter_var.set(f"Bancali: {len(self.bancali_selezionati)}")

    def svuota_lista(self):
        """Svuota completamente la lista dei bancali scansionati"""
        for item in self.bancali_tree.get_children():
            self.bancali_tree.delete(item)

        self.bancali_selezionati = []
        self.counter_var.set("Bancali: 0")

    def rientra_bancali(self):
        """Gestisce il rientro dei bancali dal fornitore"""
        # Verifica se ci sono bancali da far rientrare
        if not self.bancali_selezionati:
            messagebox.showwarning("Attenzione", "Nessun bancale scansionato per il rientro")
            return

        conn = sqlite3.connect(self.db.db_file)
        cursor = conn.cursor()

        data_ora = time.strftime("%Y-%m-%d %H:%M:%S")

        try:
            for item_id in self.bancali_tree.get_children():
                values = self.bancali_tree.item(item_id, 'values')
                bancale_id = int(values[0])
                fornitore_id = int(values[3]) # Recupera l'ID fornitore dalla Treeview

                # Aggiorna lo stato del bancale
                cursor.execute(
                    "UPDATE bancali SET stato = 'magazzino' WHERE id = ?",
                    (bancale_id,)
                )

                # Registra il movimento di rientro CON l'ID del fornitore
                cursor.execute(
                    "INSERT INTO movimenti (bancale_id, fornitore_id, tipo_movimento, data_movimento) VALUES (?, ?, ?, ?)",
                    (bancale_id, fornitore_id, "rientro", data_ora)
                )

            conn.commit()
            messagebox.showinfo("Successo", f"{len(self.bancali_selezionati)} bancali sono rientrati correttamente")

            # Pulisci la lista
            self.svuota_lista()
            self.scan_status_var.set("Pronto per la scansione")

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Errore", f"Errore durante il rientro: {str(e)}")

        finally:
            conn.close()

        # Rimetti il focus sul campo di scansione
        self.barcode_entry.focus_set()
