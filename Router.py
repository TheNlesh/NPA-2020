class Router:

	def __init__(self, brand, model, os, hostname):
		self.__brand = brand
		self.__model = model
		self.__os = os
		self.__hostname = hostname
		self.__interfaces = {}
		self.connection = {}
		self.__routing = {"default" : "not set"}

	# Hostname
	def setHostname(self, hostname):
		self.__hostname = hostname

	def getHostname(self):
		return self.__hostname

	# Interface
	def addInterface(self, interfaceName):
		self.__interfaces[interfaceName] = "unassigned IP"

	def removeInterface(self, interfaceName):
		if interfaceName in self.__interfaces:
			del self.__interfaces[interfaceName]

	def getInterfaces(self):
		return self.__interfaces

	# Connectivity
	def connect(self, local_int, remote_host, remote_int):
		self.connection[local_int] = [remote_host.getHostname(), remote_int]
		remote_host.connection[remote_int] = [self.getHostname(), local_int]

	def disconnect(self, local_int, remote_host, remote_int):
		del self.connection[local_int]
		del remote_host.connection[remote_int]

	# Addressing
	def setIP(self, interfaceName, ip):
		self.__interfaces[interfaceName] = ip

def show_interface(device):
	""" print Device's interface(s)"""
	device_hostname = device.getHostname()
	device_int = device.getInterfaces()
	print("Show interface(s) of {}".format(device_hostname))
	print("{} has {} interface(s)".format(device_hostname, len(device_int)))
	for iface in device_int:
		print(iface, device_int[iface])
	print()

def show_cdp(device):
	""" Show Device's connection"""
	device_hostname = device.getHostname()
	print("Show cdp of {}".format(device_hostname))
	print("{} has {} neighbor(s)".format(device_hostname, len(device.connection)))
	for iface in device.connection:
		remotehost_info = device.connection[iface]
		print("interface {} connect to {} on {}".format(iface, remotehost_info[0], remotehost_info[1]))
	print()

rt1 = Router("Cisco", "c7200", "IOS", "R1")
rt2 = Router("Cisco", "Nexus", "NXOS", "R2")
rt3 = Router("Cisco", "csr1000v", "IOSXE", "R3")

# rt1_hostname = rt1.getHostname()
# print(rt1_hostname)

# rt2_hostname = rt2.getHostname()
# print(rt2_hostname)

# rt3_hostname = rt3.getHostname()
# print(rt3_hostname)

rt1.addInterface("G0/0")
rt1.addInterface("G0/1")

rt2.addInterface("G0/2")
rt2.addInterface("G0/3")

rt3.addInterface("G0/4")
rt3.addInterface("G0/5")
rt3.addInterface("G0/6")

show_interface(rt1)
show_interface(rt2)
show_interface(rt3)

print("Remove interface G0/6 on R3...\n")
rt3.removeInterface("G0/6")
show_interface(rt3)

rt1.connect("G0/1", rt2, "G0/2")
rt2.connect("G0/3", rt3, "G0/4")
rt3.connect("G0/5", rt1, "G0/0")

show_cdp(rt1)
show_cdp(rt2)
show_cdp(rt3)

print("Disconnect from R3 interface G0/5 to R1 interface G0/0...\n")
rt3.disconnect("G0/5", rt1, "G0/0")

show_cdp(rt1)
show_cdp(rt2)
show_cdp(rt3)

print("Set IP Address to interface G0/0 on R1")
rt1.setIP("G0/0", "192.168.1.1")
show_interface(rt1)