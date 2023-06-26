import threading
import pickle
# ソケットライブラリ取り込み
import socket

# チャットルームを管理するクラス
class ChatRoom:
    def __init__(self, title, max_participants):
        self.title = title
        self.max_participants = max_participants
        self.participants = {}  # 参加者を管理するハッシュマップ

    # クライアントを追加
    def add_participant(self, client_key, client):
        self.participants[client_key] = client
    # クライアントを削除
    def remove_participant(self, client_key):
        del self.participants[client_key]
    # ブロードキャスト（ルームの参加者全員に送信）
    def broadcast_message(self, sender_key, message):
        for key, client in self.participants.items():
            if key != sender_key:
                client.send_message(message)


# クライアントを管理するクラス
class Client:
    def __init__(self, connection, address, port):
        self.connection = connection
        self.address = address
        self.port = port

    def send_message(self, message):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.sendto(message.encode(), (self.address, self.port))
        udp_socket.close()

# サーバーIPとポート番号
SERVER_ADDRESS = "127.0.0.1"
SERVER_PORT = 49152

# チャットルームのハッシュマップ
chat_rooms = {}

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((SERVER_ADDRESS, SERVER_PORT))
# TCPでクライアントの接続を待機するスレッド
def wait_for_clients():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((SERVER_ADDRESS, SERVER_PORT))
    tcp_socket.listen()
    print('Server started and listening for incoming connections...')

    while True:
        connection, client_address = tcp_socket.accept()
        address, port = client_address
        # クライアントインスタンスの生成
        # print(client_address)
        client = Client(connection, address, port)

        # クライアントのアドレスを返信
        connection.send(f'{address}:{port}'.encode('utf-8'))
        threading.Thread(target=handle_client, args=(client,)).start()


# クライアントの処理を行う関数
def handle_client(client):

    client_key = f'{client.address}:{client.port}'
    # print(client_key)

    # 入室できるルームを取得
    available_rooms = [k for k, v in chat_rooms.items() if v.max_participants > len(v.participants)]
    # pickleでバイナリー化
    keys = pickle.dumps(available_rooms)
    # print(available_rooms)
    # 入室できるルーム名のリストを送信 TCPで
    client.connection.send(keys)
    roomname = ""
    # ルームを受信
    data = client.connection.recv(1024)
    data = data.decode("utf-8")
    print(f'{data} {client_key}')
    
    pre, suf = data.split(':', 1)
    roomname = pre
    # 既存の名前:joinだったら既存の名前に追加
    if suf == "join":
        chat_rooms[pre].add_participant(client_key, client)
    # dataが 新しい名前: 人数 の形式だったら新しくルームを作る
    else:    
        newroom = ChatRoom(pre, int(suf))
        chat_rooms[roomname] = newroom
        newroom.add_participant(client_key, client)

    # メッセージ受信ループ ブロードキャスト
    while True:

        data, address = udp_socket.recvfrom(1024)
        add, port = address
        senderkey = f'{add}:{port}'
        recvmsg = f'{senderkey}> {data.decode()}'
        chat_rooms[pre].broadcast_message(senderkey, recvmsg)
        print(recvmsg)


        if data is None:
            break
    
    client.connection.close()


# メイン関数
def main():
    threading.Thread(target=wait_for_clients, args=()).start()

if __name__ == '__main__':
    main()

