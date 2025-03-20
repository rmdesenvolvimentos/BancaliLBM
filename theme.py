import tkinter as tk
from tkinter import ttk

class ModernTheme:
    """Classe per applicare un tema moderno all'interfaccia"""
    
    def __init__(self):
        # Colori principali
        self.bg_color = "#f5f5f5"           # Sfondo principale
        self.panel_bg = "white"             # Sfondo pannelli
        self.accent_color = "#0078d7"       # Colore di accento (azzurro Microsoft)
        self.text_color = "#333333"         # Colore testo
        self.success_color = "#2ecc71"      # Verde successo
        self.warning_color = "#f39c12"      # Giallo warning
        self.danger_color = "#e74c3c"       # Rosso errore
        
        # Font
        self.font_family = "Arial"
        self.header_font = (self.font_family, 18, "bold")
        self.subheader_font = (self.font_family, 14, "bold")
        self.normal_font = (self.font_family, 10)
        self.small_font = (self.font_family, 9)
        self.stats_font = (self.font_family, 12, "bold")
        
    def apply_theme(self, root):
        """Applica il tema all'applicazione"""
        style = ttk.Style(root)
        
        # Configura il tema generale
        if 'vista' in style.theme_names():  # Vista è un tema base moderno
            style.theme_use('vista')
        elif 'winnative' in style.theme_names():
            style.theme_use('winnative')
        
        # Configura il tema per le statistiche
        self.stats_header_font = (self.font_family, 10)  # Testo descrittivo
        self.stats_value_font = (self.font_family, 14, "bold")  # Valori numerici
        
        # Personalizza i widget principali
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.text_color)
        style.configure("TButton", font=self.normal_font)
        style.configure("TEntry", font=self.normal_font)
        style.configure("TCombobox", font=self.normal_font)
        style.configure("Stats.TLabel", font=self.stats_font, background=self.bg_color,foreground=self.text_color)
        style.configure("StatsHeader.TLabel", font=self.stats_header_font)
        style.configure("StatsValue.TLabel", font=self.stats_value_font)
        
        # Stili specifici
        style.configure("Header.TLabel", 
                        font=self.header_font, 
                        background=self.bg_color, 
                        foreground=self.text_color)
        
        style.configure("Subheader.TLabel", 
                        font=self.subheader_font, 
                        background=self.bg_color, 
                        foreground=self.text_color)
        
        # Panel style (per i frame con sfondo bianco)
        style.configure("Panel.TFrame", 
                        background=self.panel_bg,
                        relief="raised",
                        borderwidth=1)
        
        style.configure("Panel.TLabel", 
                        background=self.panel_bg, 
                        foreground=self.text_color)
        
        style.configure("StatsValue.TLabel", 
                        font=self.stats_value_font,
                        foreground="#0078d7")  # Colore blu accento
        
        # Tabelle
        style.configure("Treeview", 
                        background=self.panel_bg,
                        foreground=self.text_color,
                        rowheight=25,
                        fieldbackground=self.panel_bg)
        
        style.map('Treeview', background=[('selected', self.accent_color)])
        
        style.configure("Treeview.Heading", 
                        font=(self.font_family, 10, 'bold'),
                        background=self.bg_color,
                        foreground=self.text_color)
        
        # Schede del notebook
        style.configure("TNotebook", background=self.bg_color)
        style.configure("TNotebook.Tab", 
                        background=self.bg_color,
                        foreground=self.text_color,
                        padding=[12, 6])
        
        style.map("TNotebook.Tab",
                background=[("selected", self.panel_bg)],
                foreground=[("selected", self.accent_color)])
        
        # LabelFrame
        style.configure("TLabelframe", 
                        background=self.panel_bg, 
                        foreground=self.text_color)
        
        style.configure("TLabelframe.Label", 
                        background=self.bg_color, 
                        foreground=self.text_color,
                        font=(self.font_family, 10, 'bold'))
        
        # Button states
        style.map("TButton",
                background=[("active", self.accent_color)],
                foreground=[("active", "white")])
                
        # Status colors
        style.configure("Success.TLabel", foreground=self.success_color)
        style.configure("Warning.TLabel", foreground=self.warning_color)
        style.configure("Danger.TLabel", foreground=self.danger_color)

        return style