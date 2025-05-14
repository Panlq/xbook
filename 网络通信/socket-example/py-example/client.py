import socket
import struct
import time


from server import recv_n, send_message


def recv_msg(socket):
    """Receive a message from the socket."""
    # 先读 4 个字节，表示消息长度
    raw_len = recv_n(socket, 4)
    if not raw_len:
        return None

    # 解码长度
    msg_len = struct.unpack(">I", raw_len)[0]  # 网络字节序 unsigned int
    msg = recv_n(socket, msg_len)
    if not msg:
        return None
    return msg.decode("utf-8")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        # connect to the server
        s.connect(("localhost", 12345))

        for i in range(3):
            msg = f"Hello from py client {i}!"
            send_message(s, msg)

            response = recv_msg(s)
            print(f"Received message: {response}")

            time.sleep(1)


if __name__ == "__main__":
    main()
