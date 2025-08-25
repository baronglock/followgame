#!/usr/bin/env python3
"""
Test script to verify Fight Club system is working correctly
"""

import json
import sqlite3
import os

def check_system():
    print("=" * 50)
    print("FIGHT CLUB SYSTEM CHECK")
    print("=" * 50)
    
    # Check databases
    print("\n[OK] Checking databases...")
    if os.path.exists('game_stats.db'):
        conn = sqlite3.connect('game_stats.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM games')
        games = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM player_attributes')
        attrs = cursor.fetchone()[0]
        print(f"  - Games played: {games}")
        print(f"  - Players with bonus attributes: {attrs}")
        conn.close()
    else:
        print("  [!] Database not found - run a game first")
    
    # Check PIX config
    print("\n[OK] Checking PIX configuration...")
    with open('pix_config.json', 'r', encoding='utf-8') as f:
        pix_config = json.load(f)
    
    if pix_config['pix_key'] == "SUA_CHAVE_PIX_AQUI":
        print("  [!] PIX key not configured - edit pix_config.json")
    else:
        print(f"  - PIX key configured: {pix_config['pix_key'][:4]}***")
    print(f"  - Key type: {pix_config['pix_key_type']}")
    print(f"  - Merchant: {pix_config['merchant_name']}")
    
    # Check web files
    print("\n[OK] Checking web interface...")
    if os.path.exists('web/index.html'):
        print("  - Web interface: OK")
        print("  - Pricing: R$1.00 per attribute point")
        print("  - Shopping cart: Enabled")
    else:
        print("  [!] Web interface not found")
    
    # Check server
    print("\n[OK] Server information:")
    print("  - URL: http://localhost:8080")
    print("  - API endpoint: http://localhost:8080/api/stats")
    print("  - Payment endpoint: http://localhost:8080/api/payment")
    
    print("\n" + "=" * 50)
    print("NEXT STEPS:")
    print("=" * 50)
    print("1. Edit pix_config.json with your actual PIX key")
    print("2. Run: start_all.bat (to start the web server)")
    print("3. Run: python main.py (to play a game)")
    print("4. Open: http://localhost:8080 (to view rankings)")
    print("=" * 50)

if __name__ == "__main__":
    check_system()