import socket
import json
import threading
import time
from queue import Queue
import select

class TCPServer:
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}  # {client_address: socket}
        self.running = False
        self.lock = threading.Lock()
        self.result_queue = Queue()
        
    def start(self):
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        # Start the main server thread
        server_thread = threading.Thread(target=self._accept_connections)
        server_thread.daemon = True
        server_thread.start()
        
        # # Start the client monitor thread
        # monitor_thread = threading.Thread(target=self._monitor_clients)
        # monitor_thread.daemon = True
        # monitor_thread.start()
        
    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        with self.lock:
            for client in self.clients.values():
                try:
                    client.close()
                except:
                    pass
            self.clients.clear()
            
    def _accept_connections(self):
        while self.running:
            try:
                readable, _, _ = select.select([self.server_socket], [], [], 1.0)
                if self.server_socket in readable:
                    client_socket, client_address = self.server_socket.accept()
                    client_socket.settimeout(60)  # Set timeout for client operations
                    with self.lock:
                        self.clients[client_address] = client_socket
                    
                    # Start a new thread to handle this client
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
            except Exception as e:
                print(f"Error in accept_connections: {e}")
                time.sleep(1)
                
    def _handle_client(self, client_socket, client_address):
        while self.running:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                    
                command = data.decode('utf-8').strip()
                
                # Handle the test command
                if command == "TEST":
                    # Get the latest result from the result queue
                    try:
                        result = self.result_queue.get()#会在这阻塞 直到有数据
                    except Queue.Empty:
                        result = {'code': 0, 'message': 'No result available'}
                    
                    # Send the response back to the client
                    response = json.dumps(result).encode('utf-8')
                    client_socket.send(response)
                    
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error handling client {client_address}: {e}")
                break
                
        # Clean up the client connection
        with self.lock:
            if client_address in self.clients:
                del self.clients[client_address]
        try:
            client_socket.close()
        except:
            pass
            
    def _monitor_clients(self):
        while self.running:
            with self.lock:
                # Create a copy of clients to avoid modification during iteration
                clients = list(self.clients.items())
                
            for client_address, client_socket in clients:
                try:
                    # Try to send a heartbeat
                    client_socket.send(b'ping')
                except:
                    # If failed, remove the client and close the socket
                    with self.lock:
                        if client_address in self.clients:
                            del self.clients[client_address]
                    try:
                        client_socket.close()
                    except:
                        pass
                        
            time.sleep(5)  # Check every 5 seconds
            
    def update_result(self, result):
        """Update the latest test result"""
        # Clear the queue and put the new result
        while not self.result_queue.empty():
            try:
                self.result_queue.get_nowait()
            except Queue.Empty:
                break
        self.result_queue.put(result)

# Create a global TCP server instance
tcp_server = None