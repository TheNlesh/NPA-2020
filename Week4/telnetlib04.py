import getpass
import telnetlib
import time

host_template = "172.31.179."
username = input("Enter username: ")
password = getpass.getpass()

for number in range(1, 10):
	number = str(number)
	tn = telnetlib.Telnet(host=host_template + number, port=23, timeout=5)

	tn.read_until(b"Username:")
	tn.write(username.encode('ascii') + b"\n")
	time.sleep(1)

	tn.read_until(b"Password:")
	tn.write(password.encode('ascii') + b"\n")
	time.sleep(1)

	tn.write(b"conf t\n")
	time.sleep(1)

	tn.read_until(b"(config)#")
	tn.write(b"int lo0\n")

	tn.read_until(b"(config-if)#")

	tn.write(b"ip add 172.20.179.%b 255.255.255.255\n" %(number.encode('utf8')))
	tn.write(b"end\n")

	tn.read_until(b"#")
	tn.write(b"sh ip int br\n")
	time.sleep(2)
	tn.write(b"exit\n")
	time.sleep(1)

	output = tn.read_all()
	print(output.decode('ascii'))

	tn.close()
	time.sleep(1)