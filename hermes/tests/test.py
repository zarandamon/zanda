from http.server import SimpleHTTPRequestHandler, HTTPServer

HTTPServer(("127.0.0.1", 8000), SimpleHTTPRequestHandler).serve_forever()
