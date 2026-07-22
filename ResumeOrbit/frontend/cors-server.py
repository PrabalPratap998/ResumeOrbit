#!/usr/bin/env python3
"""
CORS-enabled HTTP server with proxy for ResumeOrbit frontend
"""
import http.server
import socketserver
import os
import urllib.request
import json
import sys
from urllib.parse import urljoin

# Add CORS headers and proxy API requests
class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        # Check if this is an API request
        if self.path.startswith('/api'):
            self.proxy_request()
        else:
            super().do_POST()

    def do_GET(self):
        # Check if this is an API request
        if self.path.startswith('/api'):
            self.proxy_request()
        else:
            super().do_GET()

    def proxy_request(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b''

            # Forward request to Node backend
            backend_url = f"http://localhost:3001{self.path}"
            req = urllib.request.Request(backend_url, data=body, method=self.command)
            
            # Copy headers
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'connection']:
                    req.add_header(header, value)

            with urllib.request.urlopen(req) as response:
                status = response.status
                response_body = response.read()
                content_type = response.headers.get('Content-Type', 'application/json')

                self.send_response(status)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', len(response_body))
                self.end_headers()
                self.wfile.write(response_body)

        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({'error': str(e)}).encode()
            self.wfile.write(error_response)
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({'error': f'Proxy error: {str(e)}'}).encode()
            self.wfile.write(error_response)

PORT = 8000
os.chdir(os.path.dirname(os.path.abspath(__file__)))

with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
    print(f"🚀 Frontend server running on http://localhost:{PORT}")
    print(f"📡 Proxying /api to http://localhost:3001")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✋ Server stopped")
