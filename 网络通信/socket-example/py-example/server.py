# server.py
import socket
import struct


def recv_n(socket, n):
    """Receive n bytes from the socket."""
    data = bytearray()
    while len(data) < n:
        chunk = socket.recv(n - len(data))
        if not chunk:
            return None
        data.extend(chunk)
    return bytes(data)


def send_message(socket, msg: str):
    msg_bytes = msg.encode("utf-8")
    socket.sendall(struct.pack(">I", len(msg_bytes)) + msg_bytes)


def handle_client(conn):
    try:
        while True:
            # 先读 4 个字节，表示消息长度
            raw_len = recv_n(conn, 4)
            if not raw_len:
                print("Client disconnected")
                break

            # 解码长度
            msg_len = struct.unpack(">I", raw_len)[0]  # 网络字节序 unsigned int
            msg = recv_n(conn, msg_len)
            if not msg:
                break
            print(f"Received message: {msg.decode('utf-8')}")

            # 发送响应
            response = f"Echo from Python server: {msg.decode('utf-8')}"
            send_message(conn, response)
    finally:
        conn.close()


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        # bind the socket to a host and port
        server_socket.bind(("localhost", 12345))

        # listen for incoming connections
        server_socket.listen(1)
        print("Server is listening on port 12345...")

        while True:
            # accept incoming connections
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")
            handle_client(client_socket)


if __name__ == "__main__":
    start_server()
