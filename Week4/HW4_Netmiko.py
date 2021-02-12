from netmiko import NetMikoAuthenticationException, NetmikoAuthError, NetmikoTimeoutError, NetMikoTimeoutException
from netmiko import ConnectHandler
import getpass

class Manager:
    def __init__(self, ip, username, password, device_type):
        self.__ip = ip
        self.__username = username
        self.__password = password
        self.__device_type = device_type

    def create_connection(self):
        """ Create connection to device """
        device = {
            'ip' : self.__ip,
            'username' : self.__username,
            'password' : self.__password,
            'device_type' : self.__device_type
        }
        try:
            connection = ConnectHandler(**device)
        except (NetMikoTimeoutException, NetmikoTimeoutError):
            print("error: connection timeout to device = " + device['ip'])
            return False
        except (NetmikoAuthError, NetMikoAuthenticationException):
            print("error: Authentication failed to device = " + device['ip'])
            return False
        return connection

    def save_config(self):
        """ Save configuration into flash """
        connection = self.create_connection()
        if not connection:
            return False
        try:
            wr = connection.send_command(command_string="write mem", expect_string=r"#")
        except Exception as e:
            return False
        else:
            return True
        finally:
            connection.disconnect()


    def backup_config(self, filename="config"):
        """ Backup recent configuration into filename.old """
        connection = self.create_connection()
        if not connection:
            return False
        try:
            wr = connection.send_command(command_string="copy run flash:{}.old".format(filename), expect_string=r"Destination filename")
            wr = connection.send_command(command_string="\n")
        except Exception as e:
            return False
        else:
            return True
        finally:
            connection.disconnect()

    def rollback_config(self, interval=2):
        """ Rollback config to backup config """
        connection = self.create_connection()
        if not connection:
            return False
        try:
            connection.send_command("term len 0", expect_string=r"#")
            connection.send_command("conf t", expect_string=r"#")

            rollbackScriptPolicy = ["kron policy-list ROLLBACK", "cli copy config.old running", "exit"]
            for cmd in rollbackScriptPolicy:
                connection.send_command(cmd, expect_string=r"#")

            rollbackScriptScheduler = ["kron occur ROLLBACK-CFG in {} oneshot".format(str(interval).zfill(3)), "policy-list rollback-backup", "end"]
            for cmd in rollbackScriptScheduler:
                connection.send_command(cmd, expect_string=r"#")
        except Exception as e:
            return False
        else:
            return True
        finally:
            connection.disconnect()


if __name__ == '__main__':
    # Test method
    host = "172.31.179.1"
    username = input("Username: ")
    password = getpass.getpass()
    device_type = "cisco_ios"

    manageObj = Manager(host, username, password, device_type)
    print(manageObj.backup_config(filename="OLDCONFIG"))
    print(manageObj.save_config())
    print(manageObj.rollback_config(interval=5))














