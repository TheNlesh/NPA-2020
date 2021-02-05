class Router:

	# Private Attribute
	__brand = "Null"
	__model = "Null"
	__os = "Null"
	__hostname = "Null"
	__interfaces = []

	# Public Attribute
	connection = {}

	def __init__(self, brand, model, os, hostname):
		self.__brand = brand
		self.__model = model
		self.__os = os
		self.__hostname = hostname

	# Hostname
	def setHostname(self, hostname):
		self.__hostname = hostname

	def getHostname(self):
		return self.__hostname

rt1 = Router("Cisco", "c7200", "IOS", "R1")
rt2 = Router("Cisco", "Nexus", "NXOS", "R2")
rt3 = Router("Cisco", "csr1000v", "IOSXE", "R3")

rt1_hostname = rt1.getHostname()
print(rt1_hostname)









