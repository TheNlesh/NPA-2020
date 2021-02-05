class Router:

	def __init__(self, brand, model, os, hostname):
		self.__brand = brand
		self.__model = model
		self.__os = os
		self.__hostname = hostname
		self.__interfaces = []
		self.connection = {}

	# Hostname
	def setHostname(self, hostname):
		self.__hostname = hostname

	def getHostname(self):
		return self.__hostname

	# Interface
	def addInterface(self, interfaceName):
		self.__interfaces.append(str(interfaceName))

	def removeInterface(self, interfaceName):
		if interfaceName in self.__interfaces:
			int_index = self.__interfaces.index(str(interfaceName))
			del self.__interfaces[int_index]

	def getInterfaces(self):
		return self.__interfaces

	# Connectivity
	def connect(self, local_int, remote_host, remote_int):
		self.connection[local_int] = [remote_host.getHostname(), remote_int]
		remote_host.connection[remote_int] = [self.getHostname(), local_int]

def show_interface(device):
	""" print Device's interface(s)"""
	device_hostname = device.getHostname()
	device_int = device.getInterfaces()
	print("Show interface(s) of {}".format(device_hostname))
	print("{} has {} interface(s)".format(device_hostname, len(device_int)))
	print(*device_int, sep="\n")
	print()

def show_cdp(device):
	""" Show Device's connection"""
	device_hostname = device.getHostname()
	print("Show cdp of {}".format(device_hostname))
	for iface in device.connection:
		remotehost_info = device.connection[iface]
		print("{} interface {} connect to {} on {}".format(device_hostname, iface, remotehost_info[0], remotehost_info[1]))
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
rt3.removeInterface("G0/6") # Try to remove interface on R3

show_interface(rt1)
show_interface(rt2)
show_interface(rt3)

rt1.connect("G0/1", rt2, "G0/2")
rt2.connect("G0/3", rt3, "G0/4")
rt3.connect("G0/5", rt1, "G0/0")

show_cdp(rt1)
show_cdp(rt2)
show_cdp(rt3)


