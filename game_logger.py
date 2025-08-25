"""
Game Statistics Logger
Logs all battle statistics to database for web display
"""

import json
import sqlite3
from datetime import datetime
import os

class GameLogger:
    def __init__(self):
        self.init_database()
        self.current_game_id = None
        self.game_stats = {}
        
    def init_database(self):
        """Initialize SQLite database for game statistics"""
        self.conn = sqlite3.connect('game_stats.db')
        self.cursor = self.conn.cursor()
        
        # Games table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TIMESTAMP,
                ended_at TIMESTAMP,
                total_players INTEGER,
                winner TEXT,
                duration_seconds REAL
            )
        ''')
        
        # Player stats table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER,
                username TEXT,
                kills INTEGER DEFAULT 0,
                damage_dealt INTEGER DEFAULT 0,
                damage_taken INTEGER DEFAULT 0,
                survived_seconds REAL DEFAULT 0,
                final_position INTEGER,
                hp_start INTEGER,
                strength INTEGER DEFAULT 5,
                armor INTEGER DEFAULT 0,
                luck INTEGER DEFAULT 0,
                FOREIGN KEY (game_id) REFERENCES games(id)
            )
        ''')
        
        # Kills log table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS kill_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER,
                killer TEXT,
                victim TEXT,
                damage INTEGER,
                timestamp TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES games(id)
            )
        ''')
        
        # Player attributes table (for paid upgrades)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_attributes (
                username TEXT PRIMARY KEY,
                bonus_hp INTEGER DEFAULT 0,
                bonus_strength INTEGER DEFAULT 0,
                bonus_armor INTEGER DEFAULT 0,
                bonus_luck INTEGER DEFAULT 0,
                total_spent REAL DEFAULT 0,
                last_payment TIMESTAMP
            )
        ''')
        
        # Payment queue table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                attribute_type TEXT,
                amount INTEGER,
                price REAL,
                pix_code TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP,
                confirmed_at TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def start_game(self, players):
        """Start logging a new game"""
        self.cursor.execute('''
            INSERT INTO games (started_at, total_players)
            VALUES (?, ?)
        ''', (datetime.now(), len(players)))
        
        self.current_game_id = self.cursor.lastrowid
        self.game_stats = {
            'start_time': datetime.now(),
            'players': {},
            'alive_count': len(players)
        }
        
        # Initialize player stats
        for player in players:
            username = player.get('instagram_username', 'Unknown')
            stats = player.get('stats', {})
            
            self.cursor.execute('''
                INSERT INTO player_stats 
                (game_id, username, hp_start, strength, armor, luck)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                self.current_game_id,
                username,
                stats.get('hp', 100),
                stats.get('strength', 5),
                stats.get('armor', 0),
                stats.get('luck', 0)
            ))
            
            self.game_stats['players'][username] = {
                'kills': 0,
                'damage_dealt': 0,
                'damage_taken': 0,
                'alive': True
            }
        
        self.conn.commit()
        return self.current_game_id
    
    def log_damage(self, attacker, victim, damage):
        """Log damage dealt"""
        if not self.current_game_id:
            return
            
        # Update damage stats
        if attacker in self.game_stats['players']:
            self.game_stats['players'][attacker]['damage_dealt'] += damage
        if victim in self.game_stats['players']:
            self.game_stats['players'][victim]['damage_taken'] += damage
    
    def log_kill(self, killer, victim):
        """Log a kill"""
        if not self.current_game_id:
            return
            
        # Log the kill
        self.cursor.execute('''
            INSERT INTO kill_log (game_id, killer, victim, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (self.current_game_id, killer, victim, datetime.now()))
        
        # Update kill count
        if killer in self.game_stats['players']:
            self.game_stats['players'][killer]['kills'] += 1
        
        # Mark victim as dead
        if victim in self.game_stats['players']:
            self.game_stats['players'][victim]['alive'] = False
            self.game_stats['alive_count'] -= 1
            
            # Update final position
            self.cursor.execute('''
                UPDATE player_stats 
                SET final_position = ?
                WHERE game_id = ? AND username = ?
            ''', (self.game_stats['alive_count'] + 1, self.current_game_id, victim))
        
        self.conn.commit()
    
    def end_game(self, winner):
        """End the game and finalize stats"""
        if not self.current_game_id:
            return
            
        end_time = datetime.now()
        duration = (end_time - self.game_stats['start_time']).total_seconds()
        
        # Update game record
        self.cursor.execute('''
            UPDATE games 
            SET ended_at = ?, winner = ?, duration_seconds = ?
            WHERE id = ?
        ''', (end_time, winner, duration, self.current_game_id))
        
        # Update winner position
        self.cursor.execute('''
            UPDATE player_stats 
            SET final_position = 1
            WHERE game_id = ? AND username = ?
        ''', (self.current_game_id, winner))
        
        # Update all player stats
        for username, stats in self.game_stats['players'].items():
            self.cursor.execute('''
                UPDATE player_stats 
                SET kills = ?, damage_dealt = ?, damage_taken = ?
                WHERE game_id = ? AND username = ?
            ''', (
                stats['kills'],
                stats['damage_dealt'],
                stats['damage_taken'],
                self.current_game_id,
                username
            ))
        
        self.conn.commit()
        
        # Export to JSON for web
        self.export_to_json()
        
        print(f"\n📊 Game #{self.current_game_id} ended!")
        print(f"Winner: {winner}")
        print(f"Duration: {duration:.1f} seconds")
    
    def export_to_json(self):
        """Export current stats to JSON for web display"""
        # Get overall rankings
        self.cursor.execute('''
            SELECT 
                username,
                COUNT(*) as games_played,
                SUM(CASE WHEN final_position = 1 THEN 1 ELSE 0 END) as wins,
                SUM(kills) as total_kills,
                SUM(damage_dealt) as total_damage,
                AVG(final_position) as avg_position
            FROM player_stats
            GROUP BY username
            ORDER BY wins DESC, total_kills DESC
            LIMIT 50
        ''')
        
        rankings = []
        for row in self.cursor.fetchall():
            rankings.append({
                'username': row[0],
                'games': row[1],
                'wins': row[2],
                'kills': row[3],
                'damage': row[4],
                'avg_position': round(row[5], 1) if row[5] else 0
            })
        
        # Get recent games
        self.cursor.execute('''
            SELECT id, winner, total_players, duration_seconds, ended_at
            FROM games
            WHERE ended_at IS NOT NULL
            ORDER BY id DESC
            LIMIT 10
        ''')
        
        recent_games = []
        for row in self.cursor.fetchall():
            game_id = row[0]
            
            # Get top damage dealer for this game
            self.cursor.execute('''
                SELECT attacker, SUM(damage) as total_damage
                FROM damage_log
                WHERE game_id = ?
                GROUP BY attacker
                ORDER BY total_damage DESC
                LIMIT 1
            ''', (game_id,))
            
            top_damage_result = self.cursor.fetchone()
            top_damage_player = top_damage_result[0] if top_damage_result else None
            top_damage_amount = top_damage_result[1] if top_damage_result else 0
            
            recent_games.append({
                'id': game_id,
                'winner': row[1],
                'players': row[2],
                'duration': row[3],
                'date': row[4],
                'top_damage': {
                    'player': top_damage_player,
                    'amount': top_damage_amount
                }
            })
        
        # Export to JSON
        export_data = {
            'last_updated': datetime.now().isoformat(),
            'rankings': rankings,
            'recent_games': recent_games
        }
        
        with open('web/game_stats.json', 'w') as f:
            json.dump(export_data, f, indent=2)
    
    def get_player_attributes(self, username):
        """Get paid attributes for a player"""
        self.cursor.execute('''
            SELECT bonus_hp, bonus_strength, bonus_armor, bonus_luck
            FROM player_attributes
            WHERE username = ?
        ''', (username,))
        
        result = self.cursor.fetchone()
        if result:
            return {
                'bonus_hp': result[0],
                'bonus_strength': result[1],
                'bonus_armor': result[2],
                'bonus_luck': result[3]
            }
        return {
            'bonus_hp': 0,
            'bonus_strength': 0,
            'bonus_armor': 0,
            'bonus_luck': 0
        }
    
    def create_payment(self, username, attribute_type, amount, price):
        """Create a payment request for attribute upgrade"""
        import uuid
        
        # Generate unique PIX code
        pix_code = f"PIX{uuid.uuid4().hex[:8].upper()}"
        
        self.cursor.execute('''
            INSERT INTO payment_queue 
            (username, attribute_type, amount, price, pix_code, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, attribute_type, amount, price, pix_code, datetime.now()))
        
        self.conn.commit()
        
        return {
            'pix_code': pix_code,
            'pix_key': '11999999999',  # Your PIX key here
            'amount': price,
            'description': f'+{amount} {attribute_type} for {username}'
        }
    
    def confirm_payment(self, pix_code):
        """Confirm a payment and apply attributes"""
        self.cursor.execute('''
            SELECT username, attribute_type, amount
            FROM payment_queue
            WHERE pix_code = ? AND status = 'pending'
        ''', (pix_code,))
        
        result = self.cursor.fetchone()
        if not result:
            return False
        
        username, attr_type, amount = result
        
        # Update payment status
        self.cursor.execute('''
            UPDATE payment_queue
            SET status = 'confirmed', confirmed_at = ?
            WHERE pix_code = ?
        ''', (datetime.now(), pix_code))
        
        # Apply attribute bonus
        column_map = {
            'hp': 'bonus_hp',
            'strength': 'bonus_strength',
            'armor': 'bonus_armor',
            'luck': 'bonus_luck'
        }
        
        if attr_type in column_map:
            column = column_map[attr_type]
            
            # Insert or update player attributes
            self.cursor.execute(f'''
                INSERT INTO player_attributes (username, {column})
                VALUES (?, ?)
                ON CONFLICT(username) DO UPDATE SET
                {column} = {column} + ?
            ''', (username, amount, amount))
        
        self.conn.commit()
        return True

# Singleton instance
game_logger = GameLogger()