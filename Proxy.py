import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import threading

ENTERPRISE_PROXY = "enterprise.proxy.com:8080"  # Replace with actual enterprise proxy

class ProxyHandler(BaseHTTPRequestHandler):

    def do_CONNECT(self):
        # Handle HTTPS CONNECT method
        print(f"Handling CONNECT to {self.path}")
        
        try:
            # Create a socket to the enterprise proxy
            proxy_socket = socket.create_connection((ENTERPRISE_PROXY.split(':')[0], int(ENTERPRISE_PROXY.split(':')[1])))
            
            # Tell the client to continue
            self.send_response(200, 'Connection Established')
            self.end_headers()

            # Now, tunnel data between the client and the enterprise proxy
            self._tunnel(self.connection, proxy_socket)
        except Exception as e:
            self.send_error(502, 'Bad Gateway')
            print(f"Error handling CONNECT: {e}")

    def _tunnel(self, client_socket, proxy_socket):
        """Tunnel data between the client and the proxy socket."""
        client_socket.setblocking(0)
        proxy_socket.setblocking(0)

        while True:
            try:
                data_from_client = client_socket.recv(8192)
                if data_from_client:
                    proxy_socket.sendall(data_from_client)
            except socket.error:
                pass

            try:
                data_from_proxy = proxy_socket.recv(8192)
                if data_from_proxy:
                    client_socket.sendall(data_from_proxy)
            except socket.error:
                pass

    def do_GET(self):
        # Forward GET request to enterprise proxy
        self._forward_request()

    def do_POST(self):
        # Forward POST request to enterprise proxy
        self._forward_request()

    def _forward_request(self):
        # Forward HTTP(S) requests via enterprise proxy
        try:
            proxy_support = urllib.request.ProxyHandler({'http': f'http://{ENTERPRISE_PROXY}', 'https': f'https://{ENTERPRISE_PROXY}'})
            opener = urllib.request.build_opener(proxy_support)
            urllib.request.install_opener(opener)

            # Prepare request
            req = urllib.request.Request(self.path, headers=self.headers)
            response = urllib.request.urlopen(req)

            # Send response back to the client
            self.send_response(response.status)
            for header in response.headers.items():
                self.send_header(*header)
            self.end_headers()
            self.wfile.write(response.read())
        except Exception as e:
            self.send_error(502, 'Bad Gateway')
            print(f"Error forwarding request: {e}")

def run_proxy():
    # Set up a local proxy server on port 8080
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, ProxyHandler)
    print("Local proxy server running on port 8080...")
    httpd.serve_forever()

if __name__ == "__main__":
    run_proxy()
