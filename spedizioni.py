import tkinter as tk
from tkinter import ttk, messagebox
import time
import sqlite3

class SpedizioniFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.barcode_buffer = ""
        self.last_scan_time = 0
        self.bancali_selezionati = []  # Lista per tenere traccia dei bancali scansionati
        self.init_ui()
    
    def init_ui(self):
        """Inizializza l'interfaccia per la spedizione di bancali"""
        # Frame per la selezione del fornitore
        fornitore_frame = ttk.LabelFrame(self, text="Seleziona Fornitore")
        fornitore_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(fornitore_frame, text="Fornitore:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.fornitore_var = tk.StringVar()
        self.fornitore_combo = ttk.Combobox(fornitore_frame, textvariable=self.fornitore_var)
        self.fornitore_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Note di spedizione
        ttk.Label(fornitore_frame, text="Note:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.note_spedizione = ttk.Entry(fornitore_frame, width=40)
        self.note_spedizione.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
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
        bancali_frame = ttk.LabelFrame(self, text="Bancali Scansionati")
        bancali_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pulsanti per gestire la lista - CORREZIONE: posizionato prima della creazione del Treeview
        btn_frame = ttk.Frame(bancali_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.remove_btn = ttk.Button(btn_frame, text="Rimuovi Selezionati", command=self.rimuovi_selezionati)
        self.remove_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(btn_frame, text="Svuota Lista", command=self.svuota_lista)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Crea la Treeview per i bancali scansionati
        columns = ("ID", "Codice")
        self.bancali_tree = ttk.Treeview(bancali_frame, columns=columns, show='headings', selectmode="extended")
        
        self.bancali_tree.heading("ID", text="ID")
        self.bancali_tree.heading("Codice", text="Codice Bancale")
        
        self.bancali_tree.column("ID", width=50)
        self.bancali_tree.column("Codice", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(bancali_frame, orient=tk.VERTICAL, command=self.bancali_tree.yview)
        self.bancali_tree.configure(yscroll=scrollbar.set)
        
        # Layout
        self.bancali_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Contatore bancali
        self.counter_var = tk.StringVar(value="Bancali: 0")
        ttk.Label(self, textvariable=self.counter_var).pack(anchor=tk.W, padx=10)
        
        # Pulsante spedisci
        spedisci_button = ttk.Button(self, text="Spedisci Bancali", command=self.spedisci_bancali)
        spedisci_button.pack(pady=10)
        
        # Metti subito il focus sul campo di scansione
        self.barcode_entry.focus_set()
        
        # Aggiorna le liste
        self.aggiorna_lista_fornitori()
    
    def on_barcode_keypress(self, event):
        """Gestisce l'input dal lettore di codici a barre"""
        # Reset buffer se è passato troppo tempo dall'ultimo carattere
        current_time = time.time()
        if current_time - self.last_scan_time > 0.5:  # timeout di 500ms
            self.barcode_buffer = ""
        
        self.last_scan_time = current_time
        
        # Non fare nulla qui, lasciamo che il campo di input raccolga i caratteri
        # Il processing avverrà quando viene premuto invio (dal lettore)
    
    def process_barcode(self, event):
        """Processa il codice a barre quando viene completato (invio)"""
        barcode = self.barcode_entry.get().strip()
        if not barcode:
            return
        
        # Cerca il bancale nel database
        conn = sqlite3.connect(self.db.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT id, codice FROM bancali WHERE codice = ? AND stato = 'magazzino'", (barcode,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            bancale_id, bancale_code = result
            
            # Verifica se il bancale è già stato scansionato
            for item in self.bancali_tree.get_children():
                if self.bancali_tree.item(item, "values")[0] == bancale_id:
                    self.scan_status_var.set("Bancale già scansionato!")
                    self.flash_status_color("red")
                    self.barcode_entry.delete(0, tk.END)
                    return
            
            # Aggiungi il bancale alla lista
            self.bancali_tree.insert("", tk.END, values=(bancale_id, bancale_code))
            self.bancali_selezionati.append(bancale_id)
            
            # Aggiorna il contatore
            self.counter_var.set(f"Bancali: {len(self.bancali_selezionati)}")
            
            # Mostra conferma
            self.scan_status_var.set(f"Bancale {bancale_code} aggiunto!")
            self.flash_status_color("green")
        else:
            # Bancale non trovato o non disponibile
            self.scan_status_var.set("Bancale non trovato o già spedito!")
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
    
    def aggiorna_lista_fornitori(self):
        """Aggiorna la lista dei fornitori nel combobox"""
        fornitori = self.db.get_fornitori()
        fornitore_values = [f"{f[0]} - {f[1]}" for f in fornitori]
        self.fornitore_combo['values'] = fornitore_values
    
    def spedisci_bancali(self):
        """Gestisce la spedizione dei bancali al fornitore"""
        # Ottieni il fornitore selezionato
        selezione = self.fornitore_var.get()
        if not selezione:
            messagebox.showwarning("Attenzione", "Seleziona un fornitore")
            return
        
        # Verifica se ci sono bancali da spedire
        if not self.bancali_selezionati:
            messagebox.showwarning("Attenzione", "Nessun bancale da spedire")
            return
        
        try:
            fornitore_id = int(selezione.split(" - ")[0])
            note = self.note_spedizione.get()
            
            # Registra la spedizione
            success = self.db.spedisci_bancali(self.bancali_selezionati, fornitore_id, note)
            
            if success:
                messagebox.showinfo("Successo", f"{len(self.bancali_selezionati)} bancali spediti correttamente al fornitore")
                # Pulisci la nota e la lista
                self.note_spedizione.delete(0, tk.END)
                self.svuota_lista()
                self.scan_status_var.set("Pronto per la scansione")
            
        except (ValueError, IndexError) as e:
            messagebox.showerror("Errore", f"Errore durante la spedizione: {str(e)}")
        
        # Rimetti il focus sul campo di scansione
        self.barcode_entry.focus_set()