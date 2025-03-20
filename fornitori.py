import tkinter as tk
from tkinter import ttk, messagebox

class FornitoriFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.callback = None
        self.init_ui()
    
    def set_callbacks(self, callback):
        """Imposta la funzione callback da chiamare quando i fornitori cambiano"""
        self.callback = callback
    
    def init_ui(self):
        """Inizializza l'interfaccia per la gestione dei fornitori"""
        # Header frame
        header_frame = ttk.Frame(self, padding=10)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Gestione Fornitori", 
                font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Frame principale con due colonne
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Colonna sinistra (aggiungi fornitore)
        left_frame = ttk.Frame(main_frame, padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10), expand=True)
        
        # Frame per aggiungere un nuovo fornitore
        add_frame = ttk.LabelFrame(left_frame, text="Aggiungi Nuovo Fornitore", padding=15)
        add_frame.pack(fill=tk.BOTH, expand=True)
        
        # Stile moderno per il form
        form_frame = ttk.Frame(add_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Form per aggiungere un fornitore
        ttk.Label(form_frame, text="Nome:").grid(row=0, column=0, padx=5, pady=10, sticky=tk.W)
        self.nome_fornitore = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.nome_fornitore.grid(row=0, column=1, padx=5, pady=10, sticky=tk.W)
        
        ttk.Label(form_frame, text="Indirizzo:").grid(row=1, column=0, padx=5, pady=10, sticky=tk.W)
        self.indirizzo_fornitore = ttk.Entry(form_frame, width=40, font=("Arial", 10))
        self.indirizzo_fornitore.grid(row=1, column=1, padx=5, pady=10, sticky=tk.W)
        
        ttk.Label(form_frame, text="Telefono:").grid(row=2, column=0, padx=5, pady=10, sticky=tk.W)
        self.telefono_fornitore = ttk.Entry(form_frame, width=20, font=("Arial", 10))
        self.telefono_fornitore.grid(row=2, column=1, padx=5, pady=10, sticky=tk.W)
        
        ttk.Label(form_frame, text="Email:").grid(row=3, column=0, padx=5, pady=10, sticky=tk.W)
        self.email_fornitore = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.email_fornitore.grid(row=3, column=1, padx=5, pady=10, sticky=tk.W)
        
        # Pulsante per aggiungere
        buttons_frame = ttk.Frame(add_frame)
        buttons_frame.pack(fill=tk.X, pady=15)
        
        add_button = ttk.Button(buttons_frame, text="Aggiungi Fornitore", command=self.aggiungi_fornitore, 
                                width=20)
        add_button.pack(pady=5)
        
        clear_button = ttk.Button(buttons_frame, text="Pulisci Form", command=self.pulisci_form, 
                                width=20)
        clear_button.pack(pady=5)
        
        # Colonna destra (lista fornitori)
        right_frame = ttk.Frame(main_frame, padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Lista fornitori
        list_frame = ttk.LabelFrame(right_frame, text="Elenco Fornitori", padding=15)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Barra di ricerca
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Cerca:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.search_var.trace("w", self.filter_fornitori)
        
        # Crea la Treeview con stile moderno
        columns = ("ID", "Nome", "Telefono", "Email")
        self.fornitori_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        self.fornitori_tree.heading("ID", text="ID")
        self.fornitori_tree.heading("Nome", text="Nome Fornitore")
        self.fornitori_tree.heading("Telefono", text="Telefono")
        self.fornitori_tree.heading("Email", text="Email")
        
        self.fornitori_tree.column("ID", width=50)
        self.fornitori_tree.column("Nome", width=200)
        self.fornitori_tree.column("Telefono", width=120)
        self.fornitori_tree.column("Email", width=180)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.fornitori_tree.yview)
        self.fornitori_tree.configure(yscroll=scrollbar.set)
        
        # Layout
        self.fornitori_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Pulsante aggiorna
        update_button = ttk.Button(right_frame, text="Aggiorna Lista", command=self.aggiorna_lista_fornitori)
        update_button.pack(pady=10)
        
        # Pulsanti per operazioni sui fornitori selezionati
        buttons_frame = ttk.Frame(right_frame)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        delete_button = ttk.Button(buttons_frame, text="Elimina Selezionato", command=self.elimina_fornitore)
        delete_button.pack(side=tk.LEFT, padx=5)
        
        view_button = ttk.Button(buttons_frame, text="Visualizza Dettagli", command=self.visualizza_dettagli)
        view_button.pack(side=tk.LEFT, padx=5)
        
        # Carica i fornitori iniziali
        self.aggiorna_lista_fornitori()
    
    def pulisci_form(self):
        """Pulisce il form di inserimento"""
        self.nome_fornitore.delete(0, tk.END)
        self.indirizzo_fornitore.delete(0, tk.END)
        self.telefono_fornitore.delete(0, tk.END)
        self.email_fornitore.delete(0, tk.END)
    
    def filter_fornitori(self, *args):
        """Filtra la lista dei fornitori in base al testo di ricerca"""
        search_text = self.search_var.get().lower()
        
        # Ottieni tutti i fornitori
        conn = self.db._connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, nome, telefono, email 
                FROM fornitori 
                WHERE LOWER(nome) LIKE ? OR LOWER(telefono) LIKE ? OR LOWER(email) LIKE ?
                ORDER BY nome
            """, (f'%{search_text}%', f'%{search_text}%', f'%{search_text}%'))
            fornitori = cursor.fetchall()
        except:
            fornitori = []
        
        conn.close()
        
        # Pulisci la lista
        for item in self.fornitori_tree.get_children():
            self.fornitori_tree.delete(item)
        
        # Riempi con i risultati filtrati
        for i, fornitore in enumerate(fornitori):
            tag = "even" if i % 2 == 0 else "odd"
            self.fornitori_tree.insert("", tk.END, values=fornitore, tags=(tag,))
        
        # Configura le righe alternate
        self.fornitori_tree.tag_configure("odd", background="#f5f5f5")
        self.fornitori_tree.tag_configure("even", background="white")
    
    def aggiorna_lista_fornitori(self):
        """Aggiorna la lista dei fornitori"""
        # Ottieni tutti i fornitori con info aggiuntive
        conn = self.db._connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id, nome, telefono, email FROM fornitori ORDER BY nome")
            fornitori = cursor.fetchall()
        except:
            fornitori = []
        
        conn.close()
        
        # Aggiorna la lista
        for item in self.fornitori_tree.get_children():
            self.fornitori_tree.delete(item)
        
        for i, fornitore in enumerate(fornitori):
            tag = "even" if i % 2 == 0 else "odd"
            self.fornitori_tree.insert("", tk.END, values=fornitore, tags=(tag,))
        
        # Configura le righe alternate
        self.fornitori_tree.tag_configure("odd", background="#f5f5f5")
        self.fornitori_tree.tag_configure("even", background="white")
    
    def aggiungi_fornitore(self):
        """Aggiunge un nuovo fornitore al database"""
        nome = self.nome_fornitore.get().strip()
        indirizzo = self.indirizzo_fornitore.get().strip()
        telefono = self.telefono_fornitore.get().strip()
        email = self.email_fornitore.get().strip()
        
        if not nome:
            messagebox.showwarning("Attenzione", "Il nome del fornitore è obbligatorio")
            return
        
        try:
            # Aggiungi fornitore al database
            fornitore_id = self.db.aggiungi_fornitore(nome, indirizzo, telefono, email)
            
            if fornitore_id:
                messagebox.showinfo("Successo", f"Fornitore '{nome}' aggiunto con successo!")
                self.pulisci_form()
                
                # Aggiorna la lista
                self.aggiorna_lista_fornitori()
                
                # Notifica altri componenti del cambiamento
                if self.callback:
                    self.callback()
                    
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'aggiunta del fornitore: {str(e)}")
    
    def elimina_fornitore(self):
        """Elimina il fornitore selezionato"""
        selected = self.fornitori_tree.selection()
        
        if not selected:
            messagebox.showinfo("Informazione", "Seleziona un fornitore da eliminare")
            return
            
        fornitore_id = self.fornitori_tree.item(selected[0], "values")[0]
        fornitore_nome = self.fornitori_tree.item(selected[0], "values")[1]
        
        # Verifica se ci sono bancali presso questo fornitore
        conn = self.db._connect()
        cursor = conn.cursor()
        
        try:
            # Controlla se ci sono bancali presso questo fornitore
            cursor.execute("""
                SELECT COUNT(*) FROM bancali
                WHERE stato = 'fornitore' AND id IN (
                    SELECT bancale_id FROM movimenti
                    WHERE fornitore_id = ? AND tipo_movimento = 'uscita'
                    AND bancale_id NOT IN (
                        SELECT bancale_id FROM movimenti
                        WHERE fornitore_id = ? AND tipo_movimento = 'rientro'
                    )
                )
            """, (fornitore_id, fornitore_id))
            
            num_bancali = cursor.fetchone()[0]
            
            if num_bancali > 0:
                # Ci sono bancali presso questo fornitore
                messagebox.showwarning(
                    "Impossibile eliminare", 
                    f"Ci sono ancora {num_bancali} bancali presso questo fornitore. "
                    "Fai rientrare tutti i bancali prima di eliminare il fornitore."
                )
                conn.close()
                return
                
            # Chiedi conferma
            conferma = messagebox.askyesno(
                "Conferma eliminazione", 
                f"Sei sicuro di voler eliminare il fornitore '{fornitore_nome}'?"
            )
            
            if not conferma:
                conn.close()
                return
                
            # Elimina il fornitore
            cursor.execute("DELETE FROM fornitori WHERE id = ?", (fornitore_id,))
            conn.commit()
            
            messagebox.showinfo("Successo", f"Fornitore '{fornitore_nome}' eliminato con successo!")
            
            # Aggiorna la lista
            self.aggiorna_lista_fornitori()
            
            # Notifica altri componenti del cambiamento
            if self.callback:
                self.callback()
                
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'eliminazione del fornitore: {str(e)}")
        finally:
            conn.close()
    
    def visualizza_dettagli(self):
        """Visualizza i dettagli del fornitore selezionato"""
        selected = self.fornitori_tree.selection()
        
        if not selected:
            messagebox.showinfo("Informazione", "Seleziona un fornitore per visualizzarne i dettagli")
            return
            
        fornitore_id = self.fornitori_tree.item(selected[0], "values")[0]
        
        # Ottieni dettagli del fornitore
        conn = self.db._connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT nome, indirizzo, telefono, email
                FROM fornitori
                WHERE id = ?
            """, (fornitore_id,))
            
            fornitore = cursor.fetchone()
            
            if not fornitore:
                messagebox.showinfo("Informazione", "Fornitore non trovato")
                conn.close()
                return
                
            # Ottieni numero di bancali attualmente presso il fornitore
            cursor.execute("""
                SELECT COUNT(*) FROM bancali
                WHERE stato = 'fornitore' AND id IN (
                    SELECT bancale_id FROM movimenti
                    WHERE fornitore_id = ? AND tipo_movimento = 'uscita'
                    AND bancale_id NOT IN (
                        SELECT bancale_id FROM movimenti
                        WHERE fornitore_id = ? AND tipo_movimento = 'rientro'
                    )
                )
            """, (fornitore_id, fornitore_id))
            
            num_bancali = cursor.fetchone()[0]
            
            # Crea finestra di dettaglio
            dettagli = tk.Toplevel(self)
            dettagli.title(f"Dettagli Fornitore: {fornitore[0]}")
            dettagli.geometry("500x400")
            dettagli.resizable(False, False)
            
            # Stile per la finestra di dettaglio
            dettagli_frame = ttk.Frame(dettagli, padding=20)
            dettagli_frame.pack(fill=tk.BOTH, expand=True)
            
            # Intestazione
            ttk.Label(dettagli_frame, 
                    text=f"Dettagli Fornitore: {fornitore[0]}", 
                    font=("Arial", 16, "bold")).pack(anchor=tk.W, pady=(0, 20))
            
            # Informazioni generali
            info_frame = ttk.LabelFrame(dettagli_frame, text="Informazioni Generali", padding=15)
            info_frame.pack(fill=tk.X, pady=10)
            
            ttk.Label(info_frame, text=f"ID: {fornitore_id}").grid(row=0, column=0, sticky=tk.W, pady=5)
            ttk.Label(info_frame, text=f"Nome: {fornitore[0]}").grid(row=1, column=0, sticky=tk.W, pady=5)
            ttk.Label(info_frame, text=f"Indirizzo: {fornitore[1] or 'Non specificato'}").grid(row=2, column=0, sticky=tk.W, pady=5)
            ttk.Label(info_frame, text=f"Telefono: {fornitore[2] or 'Non specificato'}").grid(row=3, column=0, sticky=tk.W, pady=5)
            ttk.Label(info_frame, text=f"Email: {fornitore[3] or 'Non specificato'}").grid(row=4, column=0, sticky=tk.W, pady=5)
            
            # Informazioni sui bancali
            bancali_frame = ttk.LabelFrame(dettagli_frame, text="Situazione Bancali", padding=15)
            bancali_frame.pack(fill=tk.X, pady=10)
            
            ttk.Label(bancali_frame, 
                    text=f"Bancali attualmente presso il fornitore: {num_bancali}",
                    font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)
            
            # Bottoni di azione
            buttons_frame = ttk.Frame(dettagli_frame)
            buttons_frame.pack(fill=tk.X, pady=20)
            
            ttk.Button(buttons_frame, 
                        text="Chiudi", 
                        command=dettagli.destroy).pack(side=tk.RIGHT)
                        
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel caricamento dei dettagli: {str(e)}")
        finally:
            conn.close()