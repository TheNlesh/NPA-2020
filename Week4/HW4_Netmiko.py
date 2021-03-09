from netmiko import NetMikoAuthenticationException, NetmikoAuthError, NetmikoTimeoutError, NetMikoTimeoutException
from netmiko import ConnectHandler
import getpass
import threading

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

    def show_hostname(self):
        connection = self.create_connection()
        if not connection:
            return False
        try:
            hostname = connection.send_command("sh run | in hostname")
        except Exception as e:
            return False
        else:
            return hostname.split()[1]
        finally:
            connection.disconnect()

    def create_vrf(self, vrf_name, as_number, vrf_number):
        connection = self.create_connection()
        if not connection:
            return False
        try:
            vrf_cmd = ["conf t", "ip vrf {}".format(vrf_name), "rd {}:{}".format(str(as_number), str(vrf_number)), "end"]
            for cmd in vrf_cmd:
                connection.send_command(cmd, expect_string=r"#")

        except Exception as e:
            return False
        else:
            return True
        finally:
            connection.disconnect()

    def show_vrf(self):
        connection = self.create_connection()
        if not connection:
            return False

        try:
            vrf_list = connection.send_command("sh vrf", expect_string=r"#")
        except Exception as e:
            return False
        else:
            return vrf_list
        finally:
            connection.disconnect()

    def create_loopback(self, number, ip, mask, vrf_name):
        """ Create loopback from loopback number, ip, and subnet mask """
        connection = self.create_connection()
        if not connection:
            return False
        try:
            loopbackcmd = ["conf t", "int lo{}".format(str(number)), "ip vrf forward {}".format(vrf_name), "ip add {} {}".format(ip, mask), "end"]
            for cmd in loopbackcmd:
                connection.send_command(cmd, expect_string=r"#")
        except Exception as e:
            return False
        else:
            return True
        finally:
            connection.disconnect()

    def create_subinterface(self, interface, subif_number, ip, mask, vlan, vrf_name):
        connection = self.create_connection()
        if not connection:
            return False

        try:
            interface_command = ["conf t", "int {}.{}".format(interface, subif_number), "encap dot1Q {}".format(vlan),\
            "ip vrf forward {}".format(vrf_name), "ip add {} {}".format(ip, mask), "int {}".format(interface), "no shut", "end"]

            for cmd in interface_command:
                connection.send_command(cmd, expect_string=r"#")

        except Exception as e:
            return False
        else:
            return True
        finally:
            connection.disconnect()

    def show_interface(self):
        connection = self.create_connection()
        if not connection:
            return False

        try:
            interfaces = connection.send_command("sh ip int br", expect_string=r"#")
        except Exception as e:
            return False
        else:
            return interfaces
        finally:
            connection.disconnect()

def task_1(host_template, loopback_template, last_octet):
    """ Create loopback for all device """
    host = host_template + str(last_octet)
    loopback_ip = loopback_template + str(last_octet)

    manageObj = Manager(ip=host, username=username, password=password, device_type=device_type)
    manageObj.create_vrf(vrf_name="Net", as_number=300, vrf_number=100)
    manageObj.create_loopback(number=100, ip=loopback_ip, mask="255.255.255.0", vrf_name="Net")

    hostname = manageObj.show_hostname()
    interfaces = manageObj.show_interface()
    print(hostname, interfaces, sep="\n")
    print("-"*50)

def task_3(host, interface_info, subif_number, vlan, vrf_name):
    """ Apply vrf to the interface for sepertate management and data traffic """
    manageObj = Manager(ip=host, username=username, password=password, device_type=device_type)
    for iface in interface_info:
        interface = iface.split()
        interfaceName = interface[0]
        interface_ip = interface[1]
        interface_subnetmask = interface[2]

        manageObj.create_subinterface(interface=interfaceName, subif_number=subif_number, ip=interface_ip, mask=interface_subnetmask, vlan=vlan, vrf_name=vrf_name)

    hostname = manageObj.show_hostname()
    interfaces = manageObj.show_interface()
    print(hostname, interfaces, sep="\n")
    print("-"*50)

if __name__ == '__main__':
    # Test method
    host_template = "172.31.179."
    loopback_template = "172.20.179."
    username = input("Username: ")
    password = getpass.getpass()
    device_type = "cisco_ios"

    # print(manageObj.backup_config(filename="OLDCONFIG"))
    # print(manageObj.save_config())
    # print(manageObj.rollback_config(interval=5))

    # Task1 add loopback
    task1_threads = []
    for number in range(1, 10):
        thread_arg = [host_template, loopback_template, number]
        task1_threads.append(threading.Thread(target=task_1, args=thread_arg))
        # task_1(host_template, loopback_template, number, username, password, device_type)
    for t in task1_threads:
        t.start()

    # Task2 completed by manual

    # Task3 add vrf
    task3_threads = []
    Routers = { "172.31.179.4" : ["G0/1 172.31.179.17 255.255.255.240", "G0/2 172.31.179.33 255.255.255.240"],
               "172.31.179.5" : ["G0/1 172.31.179.18 255.255.255.240", "G0/2 172.31.179.149 255.255.255.240"],
               "172.31.179.6" : ["G0/1 172.31.179.34 255.255.255.240", "G0/2 172.31.179.50 255.255.255.240", "G0/3 172.31.179.65 255.255.255.240"],
               "172.31.179.7" : ["G0/1 172.31.179.66 255.255.255.240"],
               "172.31.179.9" : ["G0/1 172.31.179.67 255.255.255.240"]
    }
    for router in Routers:
        thread_arg = [router, Routers[router], 100, 100, "Net"]
        task3_threads.append(threading.Thread(target=task_3, args=thread_arg))
    for t in task3_threads:
        t.start()












