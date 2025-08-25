#!/usr/bin/env python3
"""
Quick test script to add attributes to some users
"""

import sqlite3
import random

def add_test_attributes():
    conn = sqlite3.connect('game_stats.db')
    cursor = conn.cursor()
    
    # Ensure table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_attributes (
            username TEXT PRIMARY KEY,
            bonus_hp INTEGER DEFAULT 0,
            bonus_strength INTEGER DEFAULT 0,
            bonus_armor INTEGER DEFAULT 0,
            bonus_luck INTEGER DEFAULT 0
        )
    ''')
    
    # Get some users from scraped_users
    scraped_conn = sqlite3.connect('scraped_users.db')
    scraped_cursor = scraped_conn.cursor()
    scraped_cursor.execute('SELECT username FROM users LIMIT 5')
    users = [row[0] for row in scraped_cursor.fetchall()]
    scraped_conn.close()
    
    if not users:
        print("No users found. Run the scraper first!")
        return
    
    print("Adding test attributes to users:")
    print("-" * 40)
    
    # Add different attributes to each user for testing
    test_configs = [
        (10, 5, 0, 0),   # HP and Strength
        (0, 0, 10, 5),   # Armor and Luck
        (20, 0, 0, 0),   # Only HP
        (0, 10, 5, 0),   # Strength and Armor
        (5, 5, 5, 5),    # Balanced
    ]
    
    for i, username in enumerate(users):
        if i < len(test_configs):
            hp, strength, armor, luck = test_configs[i]
        else:
            hp = strength = armor = luck = 0
        
        cursor.execute('''
            INSERT OR REPLACE INTO player_attributes 
            (username, bonus_hp, bonus_strength, bonus_armor, bonus_luck)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, hp, strength, armor, luck))
        
        icons = []
        if hp > 0: icons.append(f"HP+{hp}")
        if strength > 0: icons.append(f"STR+{strength}")
        if armor > 0: icons.append(f"ARM+{armor}")
        if luck > 0: icons.append(f"LUCK+{luck}")
        
        print(f"@{username}: {' | '.join(icons) if icons else 'No bonuses'}")
    
    conn.commit()
    conn.close()
    
    print("-" * 40)
    print("Test attributes added!")
    print("\nNow you can:")
    print("1. Run: python main.py (to see icons in game)")
    print("2. Run: python attribute_manager.py (to manage attributes)")

if __name__ == "__main__":
    add_test_attributes()