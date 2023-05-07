import paramiko
import threading
import socket
import sys
import os






current_module_dirname = os.path.dirname(os.path.realpath(__file__))
#HOSTKEY填私钥
#使用ssh-keygen -m PEM -t rsa创建公私钥，-m PEM制定密钥格式为PEM，-t rsa制定要创建的密钥类型为rsa
HOSTKEY = paramiko.RSAKey(filename=os.path.join(current_module_dirname, 'kgkey'))

IP = '10.128.248.20'
PORT = 2222


#ServerInterface需要写的特殊代码
class Server(paramiko.ServerInterface):
    def __init__(self) -> None:
        self.event = threading.Event()

    #身份认证完成后，当客户端请求通道时，会检查通道类型kind，并决定服务器是否与该通道连接
    def check_channel_request(self, kind: str, chanid: int) :
        if kind == 'session': 
            print('return paramiko.OPEN_SUCCEEDED')
            return paramiko.OPEN_SUCCEEDED
        print('return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED')
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    def check_auth_password(self, username: str, password: str) -> int:
        if (username == 'icarus') and (password == 'icarus'):
            return paramiko.AUTH_SUCCESSFUL



if __name__ == '__main__':
    #先建立socket
    lsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsocket.bind((IP, PORT))
    print('----开始监听----')
    lsocket.listen(100)
    ing_socket, address = lsocket.accept()
    print('----socket已连接----')

    #通过已建立的socket，用Transport()建立channel
    server_transport = paramiko.Transport(ing_socket)
    print('----已创建transport----')
    server_transport.add_server_key(HOSTKEY)
    print('----已为trangsport添加HOSTKEY----')
    server = Server()
    server_transport.start_server(server=server)
    mychannel = server_transport.accept(20)
    #如果超时
    if mychannel is None:
        print('----超时----')
        sys.exit()
    else:
        print('----已创建channel----')

    while True:
        try:
            print(mychannel.recv(4096).decode())
            i = input('>> ')
            mychannel.send(i.encode())
            print('----已发送数据----')
        except KeyboardInterrupt:
            print('----再见----')
            sys.exit()

