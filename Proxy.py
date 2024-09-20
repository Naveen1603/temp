from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import os

# Define the enterprise proxy
ENTERPRISE_PROXY = "http://enterprise.proxy:port"  # Change to your enterprise proxy URL

class ProxyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Log the incoming request details
        print(f"Captured GET request to URL: {self.path}")
        print(f"Headers: {self.headers}")

        # Forward the request to the enterprise proxy
        proxy_support = urllib.request.ProxyHandler({'http': ENTERPRISE_PROXY, 'https': ENTERPRISE_PROXY})
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)

        req = urllib.request.Request(self.path, headers=self.headers)
        response = urllib.request.urlopen(req)

        # Send response back to the client
        self.send_response(response.status)
        for header in response.headers.items():
            self.send_header(*header)
        self.end_headers()
        self.wfile.write(response.read())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Log the incoming request details
        print(f"Captured POST request to URL: {self.path}")
        print(f"Headers: {self.headers}")
        print(f"Payload: {post_data.decode('utf-8')}")
        
        # Forward the request to the enterprise proxy
        proxy_support = urllib.request.ProxyHandler({'http': ENTERPRISE_PROXY, 'https': ENTERPRISE_PROXY})
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)

        req = urllib.request.Request(self.path, data=post_data, headers=self.headers, method='POST')
        response = urllib.request.urlopen(req)

        # Send response back to the client
        self.send_response(response.status)
        for header in response.headers.items():
            self.send_header(*header)
        self.end_headers()
        self.wfile.write(response.read())

def run_proxy():
    # Set the proxy to run locally (e.g., on port 8080)
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, ProxyHandler)
    print("Local proxy server running on port 8080...")
    httpd.serve_forever()

if __name__ == "__main__":
    run_proxy()
