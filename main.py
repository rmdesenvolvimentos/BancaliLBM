import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from dashboard import DashboardFrame
from spedizioni import SpedizioniFrame
from rientri import RientriFrame
from fornitori import FornitoriFrame
from theme import ModernTheme
from report import ReportFrame
from PIL  import ImageTk,Image

class GestionaleBancali:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestionale Bancali")
        self.root.geometry("1280x800")
        
        # Applica il tema moderno
        self.theme = ModernTheme()
        self.style = self.theme.apply_theme(root)
        
        # Inizializza il database
        self.db = Database()
        
        # Crea l'header dell'applicazione
        self.create_header()
        
        # Crea il notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Crea i frame per le diverse funzionalità
        self.dashboard = DashboardFrame(self.notebook, self.db)
        self.spedizioni = SpedizioniFrame(self.notebook, self.db)
        self.rientri = RientriFrame(self.notebook, self.db)
        self.fornitori = FornitoriFrame(self.notebook, self.db)
        self.report = ReportFrame(self.notebook, self.db)

        # Aggiungi i frame al notebook
        self.notebook.add(self.dashboard, text="Dashboard")
        self.notebook.add(self.spedizioni, text="Spedizione Bancali")
        self.notebook.add(self.rientri, text="Rientro Bancali")
        self.notebook.add(self.fornitori, text="Gestione Fornitori")
        self.notebook.add(self.report, text="Genera Report")
        
        # Crea la barra di menu
        # Configura il collegamento tra i moduli
        self.fornitori.set_callbacks(self.on_fornitori_changed)
        
        # Controlla se ci sono bancali nel database
        self.check_bancali_iniziali()
        
        # Crea la statusbar
        self.create_statusbar()
    
    def create_header(self):
        """Crea l'header dell'applicazione"""
        header = ttk.Frame(self.root, style="Panel.TFrame", padding=(15, 10))
        header.pack(fill=tk.X, padx=20, pady=20)
        
        title_label = ttk.Label(header, 
                                text="Gestione Bancali", 
                                style="Header.TLabel",
                                font=("Arial", 20, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Bottoni di utilità nell'header
        #help_btn = ttk.Button(header, text="Aiuto", width=10)
        #help_btn.pack(side=tk.RIGHT, padx=5)
        
        #about_btn = ttk.Button(header, text="Info", width=10)
        #about_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_statusbar(self):
        """Crea la barra di stato in fondo all'applicazione"""
        statusbar = ttk.Frame(self.root)
        statusbar.pack(fill=tk.X, pady=(0, 10), padx=20)
        
        self.status_text = tk.StringVar(value="Pronto")
        status_label = ttk.Label(statusbar, textvariable=self.status_text)
        status_label.pack(side=tk.LEFT)
        
        # Versione del software
        version_label = ttk.Label(statusbar, text="v1.0.0")
        version_label.pack(side=tk.RIGHT)
    
    def check_bancali_iniziali(self):
        """Controlla se ci sono bancali inizializzati, altrimenti chiede se crearli"""
        # Ottieni bancali disponibili
        bancali = self.db.get_bancali_disponibili()
        
        if not bancali:
            risposta = messagebox.askyesno(
                "Inizializzazione Database",
                "Non ci sono bancali nel database. Vuoi creare i bancali da PZ00-00001 a PZ00-10000?"
            )
            
            if risposta:
                if self.db.inizializza_bancali():
                    messagebox.showinfo("Successo", "Bancali inizializzati con successo!")
                    self.status_text.set("Database inizializzato con successo")
                else:
                    messagebox.showwarning("Attenzione", "I bancali sono già presenti nel database.")
                    self.status_text.set("Database già inizializzato")
    
    def on_fornitori_changed(self):
        """Callback chiamato quando i fornitori cambiano"""
        self.spedizioni.aggiorna_lista_fornitori()
        self.rientri.aggiorna_lista_fornitori()
        self.dashboard.aggiorna_dashboard()
        self.status_text.set("Lista fornitori aggiornata")

if __name__ == "__main__":
    root = tk.Tk()
    root.iconphoto(False, ImageTk.PhotoImage(Image.open("c:/Users/Rafael/Pictures/bancale.png")))
    app = GestionaleBancali(root)
    root.mainloop()