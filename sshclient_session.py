from paramiko import SSHClient, Transport


class SSHClientSession(SSHClient):
    """
    A hack way to remember current path after a series of commands like "cd xx".
    use like this:
        trans = Transport(("192.168.1.2", 22))
        trans.connect(username="root", password="password")
        client = SSHClientSession()
        client._transport = trans

        client.exec_command('pwd')               # path: /root
        client.exec_command('cd /home')
        client.exec_command('pwd')               # path: /home
        client.close()
    """

    def __init__(self):
        super().__init__()
        self.cd_list = []
        self.and_str = " && "

    def cd_add(self, line: str):
        """
        store command with 'cd'
        :param line: single command without '&&'
        :return:
        """
        t = line.strip()
        if (len(t) >= 2) and (t[:2] == "cd"):
            self.cd_list.append(t)

    def exec_command(
            self,
            command,
            bufsize=-1,
            timeout=None,
            get_pty=False,
            environment=None,):
        """
        rewrite exec_command, args is the same with SSHClient()
        """
        t = self.and_str

        if len(self.cd_list) == 0:
            arr_cmd = []
        else:
            arr_cmd = [t.join(self.cd_list)]

        if t in command:
            cmd_list = command.split(t.strip())
            for item in cmd_list:
                self.cd_add(item)
        else:
            self.cd_add(command)

        arr_cmd.append(command)
        final = t.join(arr_cmd)
        return super().exec_command(final, bufsize, timeout, get_pty, environment)


def test_simple():
    sock = ("192.168.1.2", 22)
    trans = Transport(sock)
    trans.connect(username="root", password="root")
    client = SSHClientSession()
    client._transport = trans
    stdout = client.exec_command('pwd')[1]
    print("output:", stdout.read().decode())
    client.exec_command('cd /home')
    stdout2 = client.exec_command('pwd')[1]
    print("output:", stdout2.read().decode())
    client.close()


def main():
    test_simple()


if __name__ == '__main__':
    main()
