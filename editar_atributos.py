#!/usr/bin/env python3
"""
Editor Simples de Atributos - Fight Club
"""

import sqlite3
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def ensure_database():
    conn = sqlite3.connect('game_stats.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_attributes (
            username TEXT PRIMARY KEY,
            bonus_hp INTEGER DEFAULT 0,
            bonus_strength INTEGER DEFAULT 0,
            bonus_armor INTEGER DEFAULT 0,
            bonus_luck INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    return conn, cursor

def show_header():
    print("=" * 50)
    print("     FIGHT CLUB - EDITOR DE ATRIBUTOS")
    print("=" * 50)
    print()
    print("ICONOS NO JOGO:")
    print("  [CORAÇÃO]  HP+ (Vida extra)")
    print("  [ESPADA]   STR+ (Força extra)")
    print("  [ESCUDO]   ARM+ (Armadura)")
    print("  [TREVO]    LUCK+ (Sorte para crítico)")
    print("=" * 50)
    print()

def get_user_attributes(cursor, username):
    cursor.execute('''
        SELECT bonus_hp, bonus_strength, bonus_armor, bonus_luck 
        FROM player_attributes WHERE username = ?
    ''', (username,))
    result = cursor.fetchone()
    if result:
        return list(result)
    return [0, 0, 0, 0]

def save_attributes(conn, cursor, username, hp, strength, armor, luck):
    cursor.execute('''
        INSERT OR REPLACE INTO player_attributes 
        (username, bonus_hp, bonus_strength, bonus_armor, bonus_luck)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, hp, strength, armor, luck))
    conn.commit()

def edit_user():
    conn, cursor = ensure_database()
    
    while True:
        clear_screen()
        show_header()
        
        print("Digite o nome do usuário (sem @) ou 'sair' para voltar:")
        username = input("> ").strip().lower()
        
        if username == 'sair':
            break
        
        if not username:
            continue
        
        # Remove @ if present
        username = username.replace('@', '')
        
        # Get current attributes
        hp, strength, armor, luck = get_user_attributes(cursor, username)
        
        while True:
            clear_screen()
            show_header()
            print(f"EDITANDO: @{username}")
            print("-" * 30)
            print(f"1. HP:       {hp:3d} pontos")
            print(f"2. Força:    {strength:3d} pontos")
            print(f"3. Armadura: {armor:3d} pontos")
            print(f"4. Sorte:    {luck:3d} pontos")
            print("-" * 30)
            print("5. SALVAR e voltar")
            print("6. Cancelar (não salvar)")
            print()
            print("Escolha o atributo (1-4) ou opção (5-6):")
            
            choice = input("> ").strip()
            
            if choice == '5':
                save_attributes(conn, cursor, username, hp, strength, armor, luck)
                print(f"\n✓ Atributos de @{username} salvos!")
                input("Pressione ENTER...")
                break
            elif choice == '6':
                print("\n✗ Alterações canceladas")
                input("Pressione ENTER...")
                break
            elif choice in ['1', '2', '3', '4']:
                attr_names = ['HP', 'Força', 'Armadura', 'Sorte']
                attr_idx = int(choice) - 1
                current_values = [hp, strength, armor, luck]
                
                print(f"\n{attr_names[attr_idx]} atual: {current_values[attr_idx]}")
                print("Digite o novo valor (0-999):")
                
                try:
                    new_value = int(input("> "))
                    if 0 <= new_value <= 999:
                        if attr_idx == 0:
                            hp = new_value
                        elif attr_idx == 1:
                            strength = new_value
                        elif attr_idx == 2:
                            armor = new_value
                        elif attr_idx == 3:
                            luck = new_value
                        print(f"✓ {attr_names[attr_idx]} alterado para {new_value}")
                    else:
                        print("✗ Valor deve ser entre 0 e 999")
                except ValueError:
                    print("✗ Digite apenas números")
                
                input("Pressione ENTER...")
    
    conn.close()

def list_all_users():
    conn, cursor = ensure_database()
    clear_screen()
    show_header()
    
    print("USUÁRIOS COM ATRIBUTOS:")
    print("-" * 50)
    
    cursor.execute('''
        SELECT username, bonus_hp, bonus_strength, bonus_armor, bonus_luck
        FROM player_attributes
        WHERE bonus_hp > 0 OR bonus_strength > 0 OR bonus_armor > 0 OR bonus_luck > 0
        ORDER BY username
    ''')
    
    users = cursor.fetchall()
    if users:
        for user in users:
            username, hp, strength, armor, luck = user
            attrs = []
            if hp > 0: attrs.append(f"HP+{hp}")
            if strength > 0: attrs.append(f"STR+{strength}")
            if armor > 0: attrs.append(f"ARM+{armor}")
            if luck > 0: attrs.append(f"LUCK+{luck}")
            print(f"@{username:20s} | {' | '.join(attrs)}")
    else:
        print("Nenhum usuário com atributos ainda.")
    
    print("-" * 50)
    input("\nPressione ENTER para voltar...")
    conn.close()

def main():
    while True:
        clear_screen()
        show_header()
        
        print("MENU PRINCIPAL:")
        print("1. Editar atributos de um usuário")
        print("2. Ver todos os usuários com atributos")
        print("3. Sair")
        print()
        print("Escolha uma opção:")
        
        choice = input("> ").strip()
        
        if choice == '1':
            edit_user()
        elif choice == '2':
            list_all_users()
        elif choice == '3':
            print("\nSaindo...")
            break
        else:
            print("Opção inválida!")
            input("Pressione ENTER...")

if __name__ == "__main__":
    main()