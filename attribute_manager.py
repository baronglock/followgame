#!/usr/bin/env python3
"""
Attribute Manager - Gerenciador de Atributos para Fight Club
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import json

class AttributeManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Fight Club - Gerenciador de Atributos")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        # Database connection
        self.conn = sqlite3.connect('game_stats.db')
        self.cursor = self.conn.cursor()
        self.ensure_tables()
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#1a1a1a', foreground='white')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#1a1a1a', foreground='white')
        style.configure('Info.TLabel', font=('Arial', 10), background='#1a1a1a', foreground='#cccccc')
        
        self.setup_ui()
        self.load_users()
        
    def ensure_tables(self):
        """Ensure the player_attributes table exists"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_attributes (
                username TEXT PRIMARY KEY,
                bonus_hp INTEGER DEFAULT 0,
                bonus_strength INTEGER DEFAULT 0,
                bonus_armor INTEGER DEFAULT 0,
                bonus_luck INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()
    
    def setup_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg='#1a1a1a')
        title_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(title_frame, text="⚔️ FIGHT CLUB - GERENCIADOR DE ATRIBUTOS ⚔️", 
                 style='Title.TLabel').pack()
        
        # User selection frame
        select_frame = tk.Frame(self.root, bg='#2a2a2a')
        select_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(select_frame, text="Usuário:", font=('Arial', 11), 
                bg='#2a2a2a', fg='white').pack(side='left', padx=10, pady=10)
        
        self.user_var = tk.StringVar()
        self.user_combo = ttk.Combobox(select_frame, textvariable=self.user_var, 
                                       width=30, font=('Arial', 10))
        self.user_combo.pack(side='left', padx=10, pady=10)
        self.user_combo.bind('<<ComboboxSelected>>', self.load_user_attributes)
        
        tk.Button(select_frame, text="Carregar", command=self.load_user_attributes,
                 bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                 padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(select_frame, text="Atualizar Lista", command=self.load_users,
                 bg='#2196F3', fg='white', font=('Arial', 10),
                 padx=15, pady=5).pack(side='left', padx=5)
        
        # Attributes frame
        attr_frame = tk.Frame(self.root, bg='#2a2a2a')
        attr_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Current values display
        current_frame = tk.LabelFrame(attr_frame, text="Valores Atuais", 
                                     font=('Arial', 11, 'bold'),
                                     bg='#2a2a2a', fg='white')
        current_frame.grid(row=0, column=0, columnspan=2, sticky='ew', padx=10, pady=10)
        
        self.current_labels = {}
        attrs = [
            ('HP', '❤️', 'bonus_hp'),
            ('Força', '⚔️', 'bonus_strength'),
            ('Armadura', '🛡️', 'bonus_armor'),
            ('Sorte', '🍀', 'bonus_luck')
        ]
        
        for i, (name, icon, key) in enumerate(attrs):
            label = tk.Label(current_frame, text=f"{icon} {name}: 0", 
                           font=('Arial', 10), bg='#2a2a2a', fg='#ffffff')
            label.grid(row=0, column=i, padx=15, pady=10)
            self.current_labels[key] = label
        
        # Edit attributes
        edit_frame = tk.LabelFrame(attr_frame, text="Editar Atributos", 
                                  font=('Arial', 11, 'bold'),
                                  bg='#2a2a2a', fg='white')
        edit_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=10, pady=10)
        
        self.spinboxes = {}
        
        for i, (name, icon, key) in enumerate(attrs):
            frame = tk.Frame(edit_frame, bg='#2a2a2a')
            frame.grid(row=i//2, column=i%2, padx=20, pady=15, sticky='w')
            
            tk.Label(frame, text=f"{icon} {name}:", font=('Arial', 10),
                    bg='#2a2a2a', fg='white', width=12).pack(side='left')
            
            spinbox = tk.Spinbox(frame, from_=0, to=999, width=10,
                                font=('Arial', 10), increment=1)
            spinbox.pack(side='left', padx=5)
            self.spinboxes[key] = spinbox
        
        # Buttons
        button_frame = tk.Frame(self.root, bg='#1a1a1a')
        button_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Button(button_frame, text="💾 Salvar Atributos", 
                 command=self.save_attributes,
                 bg='#4CAF50', fg='white', font=('Arial', 11, 'bold'),
                 padx=20, pady=10).pack(side='left', padx=10)
        
        tk.Button(button_frame, text="🔄 Resetar para 0", 
                 command=self.reset_attributes,
                 bg='#FF9800', fg='white', font=('Arial', 11, 'bold'),
                 padx=20, pady=10).pack(side='left', padx=10)
        
        tk.Button(button_frame, text="📊 Ver Todos", 
                 command=self.show_all_users,
                 bg='#9C27B0', fg='white', font=('Arial', 11, 'bold'),
                 padx=20, pady=10).pack(side='left', padx=10)
        
        # Info frame
        info_frame = tk.Frame(self.root, bg='#1a1a1a')
        info_frame.pack(fill='x', padx=20, pady=5)
        
        info_text = """
        Ícones no jogo: ❤️ HP (coração) | ⚔️ Força (espada) | 🛡️ Armadura (escudo) | 🍀 Sorte (trevo)
        """
        tk.Label(info_frame, text=info_text, font=('Arial', 9),
                bg='#1a1a1a', fg='#888888').pack()
    
    def load_users(self):
        """Load all users from scraped_users database"""
        try:
            # Try to get users from scraped_users.db
            scraped_conn = sqlite3.connect('scraped_users.db')
            scraped_cursor = scraped_conn.cursor()
            scraped_cursor.execute('SELECT username FROM users ORDER BY username')
            users = [row[0] for row in scraped_cursor.fetchall()]
            scraped_conn.close()
            
            if users:
                self.user_combo['values'] = users
                print(f"Loaded {len(users)} users")
            else:
                messagebox.showwarning("Aviso", "Nenhum usuário encontrado. Execute o scraper primeiro.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar usuários: {e}")
    
    def load_user_attributes(self, event=None):
        """Load attributes for selected user"""
        username = self.user_var.get()
        if not username:
            return
        
        # Get or create user attributes
        self.cursor.execute('''
            SELECT bonus_hp, bonus_strength, bonus_armor, bonus_luck 
            FROM player_attributes WHERE username = ?
        ''', (username,))
        
        result = self.cursor.fetchone()
        if result:
            hp, strength, armor, luck = result
        else:
            # Create default entry
            self.cursor.execute('''
                INSERT INTO player_attributes (username, bonus_hp, bonus_strength, bonus_armor, bonus_luck)
                VALUES (?, 0, 0, 0, 0)
            ''', (username,))
            self.conn.commit()
            hp = strength = armor = luck = 0
        
        # Update displays
        self.current_labels['bonus_hp'].config(text=f"❤️ HP: {hp}")
        self.current_labels['bonus_strength'].config(text=f"⚔️ Força: {strength}")
        self.current_labels['bonus_armor'].config(text=f"🛡️ Armadura: {armor}")
        self.current_labels['bonus_luck'].config(text=f"🍀 Sorte: {luck}")
        
        # Update spinboxes
        self.spinboxes['bonus_hp'].delete(0, 'end')
        self.spinboxes['bonus_hp'].insert(0, str(hp))
        self.spinboxes['bonus_strength'].delete(0, 'end')
        self.spinboxes['bonus_strength'].insert(0, str(strength))
        self.spinboxes['bonus_armor'].delete(0, 'end')
        self.spinboxes['bonus_armor'].insert(0, str(armor))
        self.spinboxes['bonus_luck'].delete(0, 'end')
        self.spinboxes['bonus_luck'].insert(0, str(luck))
    
    def save_attributes(self):
        """Save attributes for selected user"""
        username = self.user_var.get()
        if not username:
            messagebox.showwarning("Aviso", "Selecione um usuário primeiro!")
            return
        
        try:
            hp = int(self.spinboxes['bonus_hp'].get())
            strength = int(self.spinboxes['bonus_strength'].get())
            armor = int(self.spinboxes['bonus_armor'].get())
            luck = int(self.spinboxes['bonus_luck'].get())
            
            self.cursor.execute('''
                INSERT OR REPLACE INTO player_attributes 
                (username, bonus_hp, bonus_strength, bonus_armor, bonus_luck)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, hp, strength, armor, luck))
            self.conn.commit()
            
            # Update display
            self.load_user_attributes()
            
            messagebox.showinfo("Sucesso", 
                f"Atributos salvos para @{username}!\n"
                f"HP: +{hp} | Força: +{strength} | Armadura: +{armor} | Sorte: +{luck}")
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira apenas números!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    def reset_attributes(self):
        """Reset attributes to 0"""
        username = self.user_var.get()
        if not username:
            messagebox.showwarning("Aviso", "Selecione um usuário primeiro!")
            return
        
        if messagebox.askyesno("Confirmar", f"Resetar todos os atributos de @{username} para 0?"):
            self.cursor.execute('''
                UPDATE player_attributes 
                SET bonus_hp = 0, bonus_strength = 0, bonus_armor = 0, bonus_luck = 0
                WHERE username = ?
            ''', (username,))
            self.conn.commit()
            self.load_user_attributes()
            messagebox.showinfo("Sucesso", f"Atributos de @{username} resetados!")
    
    def show_all_users(self):
        """Show all users with attributes"""
        window = tk.Toplevel(self.root)
        window.title("Todos os Usuários com Atributos")
        window.geometry("600x400")
        window.configure(bg='#1a1a1a')
        
        # Create treeview
        tree = ttk.Treeview(window, columns=('HP', 'Força', 'Armadura', 'Sorte'), 
                           show='tree headings', height=15)
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        tree.heading('#0', text='Usuário')
        tree.heading('HP', text='❤️ HP')
        tree.heading('Força', text='⚔️ Força')
        tree.heading('Armadura', text='🛡️ Armadura')
        tree.heading('Sorte', text='🍀 Sorte')
        
        tree.column('#0', width=200)
        tree.column('HP', width=80, anchor='center')
        tree.column('Força', width=80, anchor='center')
        tree.column('Armadura', width=80, anchor='center')
        tree.column('Sorte', width=80, anchor='center')
        
        # Load data
        self.cursor.execute('''
            SELECT username, bonus_hp, bonus_strength, bonus_armor, bonus_luck
            FROM player_attributes
            WHERE bonus_hp > 0 OR bonus_strength > 0 OR bonus_armor > 0 OR bonus_luck > 0
            ORDER BY username
        ''')
        
        for row in self.cursor.fetchall():
            username, hp, strength, armor, luck = row
            tree.insert('', 'end', text=f"@{username}", 
                       values=(hp, strength, armor, luck))
    
    def run(self):
        self.root.mainloop()
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    app = AttributeManager()
    app.run()