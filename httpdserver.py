import http.server
#import socketserver
from http.server import HTTPServer, CGIHTTPRequestHandler
PORT = 1234

Handler = http.server.SimpleHTTPRequestHandler

httpd = HTTPServer(('',PORT), CGIHTTPRequestHandler)
print("Starting simple_httpd on port: " + str(httpd.server_port))
httpd.serve_forever()
# with socketserver.TCPServer(("", PORT), Handler) as httpd:
#     print("serving at port", PORT)
#     httpd.serve_forever()
