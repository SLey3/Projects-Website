# ------------------ Imports ------------------
import socket

# ------------------ Socket Config ------------------
socket_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_conn.bind((socket.gethostname(), 1234))
socket_conn.listen(5)

# ------------------ Server Code ------------------
while True:
    client_conn, addr = socket_conn.accept()
    print(f"[SERVER_LOG] {addr[0]} has connected to the server")
    client_conn.send(bytes("Hello", "utf-8"))
    