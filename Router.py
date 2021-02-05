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

rt1 = Router("Cisco", "c7200", "IOS", "R1")
rt2 = Router("Cisco", "Nexus", "NXOS", "R2")
rt3 = Router("Cisco", "csr1000v", "IOSXE", "R3")

rt1_hostname = rt1.getHostname()
# print(rt1_hostname)

rt2_hostname = rt2.getHostname()
# print(rt2_hostname)

rt3_hostname = rt3.getHostname()
# print(rt3_hostname)

rt1.addInterface("G0/0")
rt1.addInterface("G0/1")

rt2.addInterface("G0/2")
rt2.addInterface("G0/3")

rt3.addInterface("G0/4")
rt3.addInterface("G0/5")
rt3.addInterface("G0/6")
rt3.removeInterface("G0/6") # Try to remove interface on R3

rt1_int = rt1.getInterfaces()
print("{} has {} interface(s)".format(rt1_hostname, len(rt1_int)))
print(*rt1_int, sep="\n")

rt2_int = rt2.getInterfaces()
print("{} has {} interface(s)".format(rt2_hostname, len(rt2_int)))
print(*rt2_int, sep="\n")

rt3_int = rt3.getInterfaces()
print("{} has {} interface(s)".format(rt3_hostname, len(rt3_int)))
print(*rt3_int, sep="\n")



