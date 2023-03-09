import paramiko
import sys





def main(ip, user, cmd):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.connect(username=user, hostname=ip)
    _, stdout, stderr = client.exec_command(cmd)
    
    if stdout:
        for line in stdout:
            print(line.strip())
    if stderr:
        for line in stderr:
            print(line.strip())
    #else:
    #   print('无响应')

if __name__ == '__main__': 
    # 注意：sys.argv[0]是程序的名称'ssh_client.py'!!
    if len(sys.argv[1:]) != 3:
        print('Usage: python ssh_client.py [ip] [user] [cmd]')
    else:
        ip = sys.argv[1]
        user = sys.argv[2]
        cmd = sys.argv[3]
        main(ip, user, cmd)
