import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use("TkAgg")

class DashboardFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.colori = ["#3498db", "#2ecc71", "#e74c3c", "#f39c12", "#9b59b6", "#1abc9c", "#34495e", "#e67e22"]
        
        self.style = ttk.Style()
        self.style.configure("Dashboard.TFrame", background="#f5f5f5")
        self.style.configure("Card.TFrame", background="white", relief="flat")
        self.style.configure("CardTitle.TLabel", background="white", font=("Arial", 12, "bold"))
        self.style.configure("CardValue.TLabel", background="white", font=("Arial", 24, "bold"))
        
        self.config(style="Dashboard.TFrame", padding=20)
        
        self.init_ui()
    
    def init_ui(self):
        """Inizializza l'interfaccia della dashboard"""
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        header_label = ttk.Label(header_frame, text="Dashboard - Situazione Bancali", 
                               font=("Arial", 18, "bold"))
        header_label.pack(side=tk.LEFT)
        
        refresh_btn = ttk.Button(header_frame, text="🔄 Aggiorna", command=self.aggiorna_dashboard)
        refresh_btn.pack(side=tk.RIGHT)
        
        # Contenitore principale con due colonne
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Colonna sinistra (tabella)
        left_column = ttk.Frame(main_container, padding=10)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        table_frame = ttk.LabelFrame(left_column, text="Dettaglio per Fornitore", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crea il treeview per visualizzare le statistiche
        columns = ("ID", "Fornitore", "Numero Bancali")
        self.dashboard_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        # Configura le colonne
        self.dashboard_tree.heading("ID", text="ID")
        self.dashboard_tree.heading("Fornitore", text="Fornitore")
        self.dashboard_tree.heading("Numero Bancali", text="Numero Bancali")
        
        self.dashboard_tree.column("ID", width=50)
        self.dashboard_tree.column("Fornitore", width=200)
        self.dashboard_tree.column("Numero Bancali", width=120)
        
        # Personalizza l'aspetto del treeview
        self.style.configure("Treeview", 
                            background="white",
                            foreground="black",
                            rowheight=25,
                            fieldbackground="white")
        self.style.map('Treeview', background=[('selected', '#0078d7')])
        self.style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        
        # Aggiunge scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.dashboard_tree.yview)
        self.dashboard_tree.configure(yscroll=scrollbar.set)
        
        # Layout
        self.dashboard_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Colonna destra (grafici)
        right_column = ttk.Frame(main_container, padding=10)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Grafico a barre
        bar_frame = ttk.LabelFrame(right_column, text="Distribuzione Bancali", padding=10)
        bar_frame.pack(fill=tk.BOTH, expand=True)
        
        self.figure1 = plt.Figure(figsize=(5, 4), dpi=100)
        self.bar_subplot = self.figure1.add_subplot(111)
        self.bar_canvas = FigureCanvasTkAgg(self.figure1, bar_frame)
        self.bar_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Cards per statistiche riassuntive
        stats_frame = ttk.Frame(left_column, padding=(0, 10, 0, 0))
        stats_frame.pack(fill=tk.X)
        
        # Card: Totale bancali presso fornitori
        self.bancali_esterni_card = self._create_card(stats_frame, "Bancali presso fornitori", "0")
        self.bancali_esterni_card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Card: Totale bancali in magazzino
        self.bancali_magazzino_card = self._create_card(stats_frame, "Bancali in magazzino", "0")
        self.bancali_magazzino_card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Riempie la dashboard con i dati iniziali
        self.aggiorna_dashboard()
    
    def _create_card(self, parent, title, value):
        """Crea una card con titolo e valore"""
        card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        card.configure(relief="raised", borderwidth=1)
        
        ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor=tk.W)
        
        self.value_label = ttk.Label(card, text=value, style="CardValue.TLabel")
        self.value_label.pack(anchor=tk.CENTER, pady=10)
        
        return card
    
    def aggiorna_dashboard(self):
        """Aggiorna i dati nella dashboard"""
        # Ottieni statistiche
        statistiche = self.db.get_statistiche_fornitori()
        
        # Conteggio bancali in magazzino
        conn = self.db._connect()
        cursor = conn.cursor()
        
        # Prima verifica la struttura della tabella per determinare il nome della colonna stato
        cursor.execute("PRAGMA table_info(bancali)")
        columns = [column[1] for column in cursor.fetchall()]  # ottieni i nomi delle colonne
        
        # Determina quale colonna contiene lo stato (magazzino/fornitore)
        stato_column = None
        for possible_name in ['stato', 'status', 'location', 'posizione']:
            if possible_name in columns:
                stato_column = possible_name
                break
        
        if stato_column is None:
            # Se nessuna colonna stato viene trovata, usa valori di default
            bancali_magazzino = 0
            bancali_fornitori = 0
        else:
            # Usa la colonna trovata
            cursor.execute(f"SELECT COUNT(*) FROM bancali WHERE {stato_column} = 'magazzino'")
            bancali_magazzino = cursor.fetchone()[0]
            
            cursor.execute(f"SELECT COUNT(*) FROM bancali WHERE {stato_column} = 'fornitore'")
            bancali_fornitori = cursor.fetchone()[0]
        
        conn.close()
        
        # Aggiorna i valori delle cards
        self.bancali_magazzino_card.children["!label2"].configure(text=str(bancali_magazzino))
        self.bancali_esterni_card.children["!label2"].configure(text=str(bancali_fornitori))
        
        # Pulisci la vista
        for item in self.dashboard_tree.get_children():
            self.dashboard_tree.delete(item)
        
        # Riempie con i dati aggiornati e applica righe alternate
        for i, stat in enumerate(statistiche):
            tag = "even" if i % 2 == 0 else "odd"
            self.dashboard_tree.insert("", tk.END, values=stat, tags=(tag,))
            
        # Configura le righe alternate per maggiore leggibilità
        self.style.configure("Treeview", background="white")
        self.dashboard_tree.tag_configure("odd", background="#f0f0f0")
        self.dashboard_tree.tag_configure("even", background="white")
        
        # Aggiorna il grafico a barre
        self.bar_subplot.clear()
        
        # Prepara i dati per il grafico a barre
        labels = []
        sizes = []
        for stat in statistiche:
            if stat[2] > 0:  # Solo fornitori con bancali
                labels.append(stat[1])
                sizes.append(stat[2])
        
        # Aggiungi i bancali in magazzino
        labels.append("In magazzino")
        sizes.append(bancali_magazzino)
        
        # Crea il grafico a barre
        self.bar_subplot.bar(labels, sizes, color=self.colori[:len(labels)])
        self.bar_subplot.set_ylabel("Numero Bancali")
        self.bar_subplot.set_title("Distribuzione Bancali")
        
        self.bar_canvas.draw()