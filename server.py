import http.server
import socketserver
import sys
import os

DEFAULT_PORT = 8000
DEFAULT_DIRECTORY = "site"

def run_server(port, directory):
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving HTTP on port {port} from directory '{directory}'")
        print("Press Ctrl+C to stop the server")
        httpd.serve_forever()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    directory = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DIRECTORY
    run_server(port, directory)
