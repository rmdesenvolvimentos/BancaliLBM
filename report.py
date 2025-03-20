# report.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import sqlite3
import pandas as pd

class ReportFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.selected_fornitore = None
        self.init_ui()

    def init_ui(self):
        """Inizializza l'interfaccia semplificata"""
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Filtri di ricerca
        filter_frame = ttk.LabelFrame(main_frame, text="Filtri", padding=10)
        filter_frame.pack(fill=tk.X, pady=5)

        # Selezione fornitore
        ttk.Label(filter_frame, text="Fornitore:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.fornitore_combo = ttk.Combobox(filter_frame, state="readonly")
        self.fornitore_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Tipo movimento
        ttk.Label(filter_frame, text="Tipo Movimento:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.tipo_movimento = ttk.Combobox(filter_frame, values=["Uscita", "Rientro"])
        self.tipo_movimento.current(0)
        self.tipo_movimento.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        # Date
        ttk.Label(filter_frame, text="Da:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.data_inizio = ttk.Entry(filter_frame, width=12)
        self.data_inizio.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(filter_frame, text="A:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.data_fine = ttk.Entry(filter_frame, width=12)
        self.data_fine.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)

        # Pulsanti
        btn_frame = ttk.Frame(filter_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=5)
        
        ttk.Button(btn_frame, text="Cerca", command=self.cerca).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Pulisci", command=self.pulisci).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Excel", command=self.export_excel).pack(side=tk.LEFT, padx=2)

        # Panello informazioni
        info_frame = ttk.LabelFrame(main_frame, text="Informazioni Fornitore", padding=10)
        info_frame.pack(fill=tk.X, pady=5)

        self.info_nome = ttk.Label(info_frame, text="Nome Fornitore: -")
        self.info_nome.pack(anchor=tk.W)
        
        self.info_quantita = ttk.Label(info_frame, text="Bancali Presso Fornitore: -")
        self.info_quantita.pack(anchor=tk.W)

        # Anteprima barcode
        self.barcode_frame = ttk.LabelFrame(main_frame, text="Anteprima Barcode", padding=10)
        self.barcode_text = tk.Text(self.barcode_frame, height=10, width=50)
        scrollbar = ttk.Scrollbar(self.barcode_frame, command=self.barcode_text.yview)
        self.barcode_text.configure(yscrollcommand=scrollbar.set)
        
        self.barcode_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.aggiorna_fornitori()

    def aggiorna_fornitori(self):
        """Carica la lista dei fornitori"""
        fornitori = self.db.get_fornitori()
        self.fornitore_combo['values'] = [f"{f[0]} - {f[1]}" for f in fornitori]

    def cerca(self):
        """Cerca i bancali secondo i filtri"""
        try:
            # Recupera ID fornitore
            fornitore_id = self.fornitore_combo.get().split(" - ")[0]
            
            conn = sqlite3.connect(self.db.db_file)
            cursor = conn.cursor()
            
            # Query per informazioni fornitore
            cursor.execute("SELECT nome FROM fornitori WHERE id = ?", (fornitore_id,))
            nome_fornitore = cursor.fetchone()[0]
            
            # Query per bancali attualmente presso il fornitore
            cursor.execute("""
                SELECT COUNT(*) 
                FROM bancali 
                WHERE stato = 'fornitore' 
                AND id IN (
                    SELECT bancale_id FROM movimenti 
                    WHERE fornitore_id = ? AND tipo_movimento = 'uscita'
                    EXCEPT
                    SELECT bancale_id FROM movimenti 
                    WHERE fornitore_id = ? AND tipo_movimento = 'rientro'
                )
            """, (fornitore_id, fornitore_id))
            
            quantita = cursor.fetchone()[0]
            
            # Query per lista barcode
            cursor.execute("""
                SELECT b.codice 
                FROM bancali b
                JOIN movimenti m ON b.id = m.bancale_id
                WHERE m.fornitore_id = ? 
                AND m.tipo_movimento = 'uscita'
                AND b.id NOT IN (
                    SELECT bancale_id FROM movimenti 
                    WHERE tipo_movimento = 'rientro' 
                    AND fornitore_id = ?
                )
            """, (fornitore_id, fornitore_id))
            
            barcodes = [row[0] for row in cursor.fetchall()]
            conn.close()

            # Aggiorna UI
            self.info_nome.config(text=f"Nome Fornitore: {nome_fornitore}")
            self.info_quantita.config(text=f"Bancali Presso Fornitore: {quantita}")
            
            self.barcode_text.delete(1.0, tk.END)
            self.barcode_text.insert(tk.END, "\n".join(barcodes))
            self.barcode_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella ricerca:\n{str(e)}")

    def pulisci(self):
        """Resetta tutti i campi"""
        self.fornitore_combo.set('')
        self.tipo_movimento.current(0)
        self.data_inizio.delete(0, tk.END)
        self.data_fine.delete(0, tk.END)
        self.info_nome.config(text="Nome Fornitore: -")
        self.info_quantita.config(text="Bancali Presso Fornitore: -")
        self.barcode_text.delete(1.0, tk.END)
        self.barcode_frame.pack_forget()

    def export_excel(self):
        """Esporta i barcode in Excel"""
        barcodes = self.barcode_text.get(1.0, tk.END).split("\n")
        if len(barcodes) == 0 or barcodes[0] == "":
            messagebox.showwarning("Attenzione", "Nessun barcode da esportare")
            return

        df = pd.DataFrame({"Barcode": [b for b in barcodes if b]})
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )

        if file_path:
            try:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Successo", "Esportazione completata!")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nell'esportazione:\n{str(e)}")