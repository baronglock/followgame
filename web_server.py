#!/usr/bin/env python3
"""
Simple Web Server for Fight Club Rankings
"""

import http.server
import socketserver
import json
import os
from game_logger import game_logger

PORT = 8080

class FightClubHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="web", **kwargs)
    
    def do_GET(self):
        if self.path == '/api/stats':
            # Export fresh stats
            game_logger.export_to_json()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            with open('web/game_stats.json', 'rb') as f:
                self.wfile.write(f.read())
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/payment':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            # Create payment
            result = game_logger.create_payment(
                data['username'],
                data['type'],
                data['amount'],
                data['price']
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

def start_server():
    os.makedirs('web', exist_ok=True)
    
    with socketserver.TCPServer(("", PORT), FightClubHandler) as httpd:
        print(f"🌐 Server running at http://localhost:{PORT}")
        print(f"📊 View rankings at http://localhost:{PORT}/index.html")
        print("Press Ctrl+C to stop")
        httpd.serve_forever()

if __name__ == "__main__":
    start_server()