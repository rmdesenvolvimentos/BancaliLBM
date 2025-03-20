# report.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import sqlite3
import pandas as pd
from tkcalendar import Calendar  # Importa il modulo Calendar

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
        self.data_inizio.bind("<Button-1>", self.scegli_data_da)  # Associa la funzione all'evento di click

        ttk.Label(filter_frame, text="A:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.data_fine = ttk.Entry(filter_frame, width=12)
        self.data_fine.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        self.data_fine.bind("<Button-1>", self.scegli_data_a)  # Associa la funzione all'evento di click

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

    def scegli_data_da(self, event=None):
        def set_data():
            data_selezionata = cal.get_date()
            self.data_inizio.delete(0, tk.END)
            self.data_inizio.insert(0, data_selezionata)
            top.destroy()

        top = tk.Toplevel(self)
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=10)
        ttk.Button(top, text="Seleziona", command=set_data).pack(pady=5)

        # Posiziona la finestra del calendario vicino al campo di input
        x = self.data_inizio.winfo_rootx()
        y = self.data_inizio.winfo_rooty() + self.data_inizio.winfo_height()
        top.geometry(f"+{x}+{y}")

        # Fai in modo che la finestra si chiuda quando perde il focus (opzionale)
        top.transient(self)
        top.grab_set()
        self.wait_window(top)

    def scegli_data_a(self, event=None):
        def set_data():
            data_selezionata = cal.get_date()
            self.data_fine.delete(0, tk.END)
            self.data_fine.insert(0, data_selezionata)
            top.destroy()

        top = tk.Toplevel(self)
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=10)
        ttk.Button(top, text="Seleziona", command=set_data).pack(pady=5)

        # Posiziona la finestra del calendario vicino al campo di input
        x = self.data_fine.winfo_rootx()
        y = self.data_fine.winfo_rooty() + self.data_fine.winfo_height()
        top.geometry(f"+{x}+{y}")

        # Fai in modo che la finestra si chiuda quando perde il focus (opzionale)
        top.transient(self)
        top.grab_set()
        self.wait_window(top)

    def aggiorna_fornitori(self):
        """Carica la lista dei fornitori"""
        fornitori = self.db.get_fornitori()
        self.fornitore_combo['values'] = [f"{f[0]} - {f[1]}" for f in fornitori]

    def cerca(self):
        """Cerca i bancali secondo i filtri"""
        try:
            # Recupera ID fornitore
            fornitore_id = self.fornitore_combo.get().split(" - ")[0]
            # tipo_movimento_selezionato = self.tipo_movimento.get() # Non lo usiamo direttamente in questa query

            conn = sqlite3.connect(self.db.db_file)
            cursor = conn.cursor()

            # Query per informazioni fornitore
            cursor.execute("SELECT nome FROM fornitori WHERE id = ?", (fornitore_id,))
            nome_fornitore_tuple = cursor.fetchone()

            if nome_fornitore_tuple:
                nome_fornitore = nome_fornitore_tuple[0]

                # Query per bancali attualmente presso il fornitore (questa parte rimane simile)
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

                # Query per lista barcode dei bancali ATTUALMENTE presso il fornitore selezionato
                # Modifichiamo questa query per considerare l'ultimo movimento
                cursor.execute("""
                    SELECT b.codice
                    FROM bancali b
                    JOIN movimenti m ON b.id = m.bancale_id
                    WHERE m.fornitore_id = ?
                    GROUP BY b.id
                    HAVING MAX(m.data_movimento) AND MAX(CASE WHEN m.tipo_movimento = 'uscita' THEN 1 ELSE 0 END) = 1
                    AND NOT EXISTS (
                        SELECT 1
                        FROM movimenti m2
                        WHERE m2.bancale_id = b.id
                        AND m2.fornitore_id = ?
                        AND m2.tipo_movimento = 'rientro'
                        AND m2.data_movimento > (SELECT MAX(data_movimento) FROM movimenti WHERE bancale_id = b.id AND fornitore_id = ? AND tipo_movimento = 'uscita')
                    )
                """, (fornitore_id, fornitore_id, fornitore_id))

                barcodes = [row[0] for row in cursor.fetchall()]
                conn.close()

                # Aggiorna UI
                self.info_nome.config(text=f"Nome Fornitore: {nome_fornitore}", font=("Arial", 14))
                self.info_quantita.config(text=f"Bancali Presso Fornitore: {quantita}", font=("Arial", 14))

                self.barcode_text.delete(1.0, tk.END)
                self.barcode_text.insert(tk.END, "\n".join(barcodes))
                self.barcode_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            else:
                conn.close()
                messagebox.showerror("Errore nella ricerca", "Nessun fornitore trovato con l'ID selezionato.")
                self.info_nome.config(text=f"Nome Fornitore: ", font=("Arial", 14))
                self.info_quantita.config(text=f"Bancali Presso Fornitore: ", font=("Arial", 14))
                self.barcode_text.delete(1.0, tk.END)
                self.barcode_text.insert(tk.END, "")
                self.barcode_frame.pack(fill=tk.BOTH, expand=True, pady=5)
                return

        except Exception as e:
            messagebox.showerror("Errore generico nella ricerca", f"Si è verificato un errore durante la ricerca:\n{str(e)}")
            if 'conn' in locals():
                conn.close()

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