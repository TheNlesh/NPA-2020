from termcolor import cprint
import re

class Router:

	def __init__(self, brand, model, os, hostname):
		self.__brand = brand
		self.__model = model
		self.__os = os
		self.__hostname = hostname
		self.__interfaces = {}
		self.connection = {}
		self.__routing = {"default" : "not set"}

	def __find_network_address(self, ip):
		address, mask = ip.split("/")
		mask = int(mask)
		binary = ""

		decimal_address = [int(octet) for octet in address.split(".")]
		
		# Change decimal address to binary address
		for number in decimal_address:
			binary += bin(number)[2:].zfill(8)

		# find the network address on binary address using subnet mask
		bin_dst = binary[:mask]
		remainder = 32 - len(bin_dst)
		bin_dst += '0' * remainder

		# Slice binary address every 8 indices for group and convert into decimal
		dec_dst = re.findall('.'*8, bin_dst)

		# Convert binary address to decimal
		dst = [str(int(dec, 2)) for dec in dec_dst]
		
		# Join list into network address by "."
		dst = ".".join(dst) + "/" + str(32 - remainder)
		return dst

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
			ip = self.__interfaces[interfaceName]
			if ip != "unassigned IP":
				self.deleteRoute(ip)
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
		
		# Add directly connected

		dst = self.__find_network_address(ip)
		self.addRoute(dst, "directly connected", interfaceName)

	def deleteIP(self, interfaceName):

		# Delete directly connected
		ip = self.__interfaces[interfaceName]
		self.deleteRoute(ip)

		# Delete IP address
		self.__interfaces[interfaceName] = "unassigned IP"

	# Routing
	def addRoute(self, dst, nexthop, iface=""):
		if dst == "0.0.0.0/0":
			dst = "default"
			iface = ""
		self.__routing[dst] = nexthop + " " + iface

	def deleteRoute(self, dst, iface=""):
		if dst == "0.0.0.0/0":
			self.__routing["default"] = "not set"
		else:
			dst = self.__find_network_address(dst)
			del self.__routing[dst]

	def getRoute(self):
		return self.__routing

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

def show_routing(device):
	""" Show ip routing """
	device_hostname = device.getHostname()
	routing = device.getRoute()
	print("Show routing table of {}".format(device_hostname))
	print("Gateway of last resort is {}".format(routing["default"]))
	for dst in routing:
		if dst != "default":
			nexthop = routing[dst]
			print("{} via {}".format(dst, nexthop))
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

cprint("Remove interface G0/6 on R3...\n", color="red")
rt3.removeInterface("G0/6")
show_interface(rt3)

rt1.connect("G0/1", rt2, "G0/2")
rt2.connect("G0/3", rt3, "G0/4")
rt3.connect("G0/5", rt1, "G0/0")

show_cdp(rt1)
show_cdp(rt2)
show_cdp(rt3)

cprint("Disconnect from R3 interface G0/5 to R1 interface G0/0...\n", color="red")
rt3.disconnect("G0/5", rt1, "G0/0")

show_cdp(rt1)
show_cdp(rt2)
show_cdp(rt3)

cprint("Assign IP Address to interface G0/0 on R1...\n", color="green")
rt1.setIP("G0/0", "192.168.1.199/25")
show_interface(rt1)

rt1.addRoute("192.168.2.0/24", "192.168.1.2", "G0/0")
rt1.addRoute("172.16.0.0/16", "172.16.1.1")
rt1.addRoute("0.0.0.0/0", "8.8.8.8")
show_routing(rt1)

cprint("Delete IP Address of interface G0/0 on R1...\n", color="red")

rt1.deleteIP("G0/0")
show_interface(rt1)
show_routing(rt1)

cprint("Try to delete some route on R1...\n", color="red")
rt1.deleteRoute("172.16.0.0/16")
show_routing(rt1)

cprint("Try to delete default route on R1...\n", color="red")
rt1.deleteRoute("0.0.0.0/0")
show_routing(rt1)