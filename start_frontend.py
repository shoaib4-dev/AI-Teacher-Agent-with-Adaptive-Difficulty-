#!/usr/bin/env python3
"""Simple HTTP server to serve the UI from the ui directory"""
import http.server
import socketserver
import os
import sys

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
ui_dir = os.path.join(script_dir, 'ui')

# Verify ui directory exists
if not os.path.exists(ui_dir):
    print(f"Error: UI directory not found at {ui_dir}")
    sys.exit(1)

# Change to the ui directory
os.chdir(ui_dir)
print(f"Changed to directory: {os.getcwd()}")
print(f"Index.html exists: {os.path.exists('index.html')}")

PORT = 3000

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server running at http://localhost:{PORT}/")
    print(f"Serving from: {os.getcwd()}")
    httpd.serve_forever()

