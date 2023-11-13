import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 12345))
server_socket.listen(1)
client_socket, addr = server_socket.accept()

data = "Hello from Python"
client_socket.send(data.encode())
client_socket.close()
