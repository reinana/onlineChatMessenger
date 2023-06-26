import socket
import pickle
import threading
import sys

# サーバのアドレスとポート
SERVER_ADDRESS = "127.0.0.1"
SERVER_PORT = 49152

# クライアントのアドレスとポート
CLIENT_ADDRESS = 'localhost'
CLIENT_PORT = 54321

# サーバへの接続
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    tcp_socket.connect((SERVER_ADDRESS, SERVER_PORT))
except socket.error as err:
    print(err)
    sys.exit(1)

print('Connected to the server.')

# クライアントのアドレス返信を受信
result = tcp_socket.recv(1024).decode('utf-8')
cl_address, cl_port = result.split(":",1)
cl_port = int(cl_port)
print(cl_address,cl_port)

# チャットルームの作成
data = tcp_socket.recv(1024)
available_room = pickle.loads(data)
print(available_room)
room_name = input('Select room or Input new room: ')
if room_name not in available_room:
    max_participants = input('Input max participants: ')
    newChatroom = f'{room_name}:{max_participants}'
    tcp_socket.send(newChatroom.encode("utf-8"))

else:
    joinroom = f'{room_name}:join'
    tcp_socket.send(joinroom.encode("utf-8"))

# udp_socket データ受信無限ループ
def recv_data(sock):
    sock.bind((cl_address, cl_port))
    while True:
        try:
            # ソケットから byte 形式でデータ受信
            data, address = sock.recvfrom(1024)

            if data:
                data = data.decode("utf-8")
                print(f'\n{data}') 
            else:
                break
        except ConnectionResetError:
            break
thread = threading.Thread(target=recv_data, args=(udp_socket,)).start()


# メッセージの送信
while True:
    message = input('Enter a message (or "quit" to exit): ')
    if message == 'quit':
        break

    formatted_message = f'message: {room_name}: {len(message)}: {message}'
    print(udp_socket.sendto(formatted_message.encode("utf-8"), (SERVER_ADDRESS, SERVER_PORT)))
    print(formatted_message)




# 接続を終了
tcp_socket.close()
udp_socket.close()
print('Disconnected from the server.')




