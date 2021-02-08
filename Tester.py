from Router import *
import unittest

class TestRouter(unittest.TestCase):

	def testRouterATR(self):
		rt1 = Router("Cisco", "c7200", "IOS", "R1")
		self.assertEqual(rt1.getBrand(), "Cisco")
		self.assertEqual(rt1.getModel(), "c7200")
		self.assertEqual(rt1.getHostname(), "R1")
		self.assertEqual(rt1.getOS(), "IOS")

		# Change the router's name
		rt1.setHostname("RT1")
		self.assertEqual(rt1.getHostname(), "RT1")
		
		del rt1

	def testInterface(self):
		rt1 = Router("Cisco", "c7200", "IOS", "R1")
		self.assertTrue(rt1.addInterface("G0/0"))

		# Add duplicate interface
		self.assertFalse(rt1.addInterface("G0/0"))

		# Add new interface
		self.assertTrue(rt1.addInterface("G0/1"))
		self.assertTrue(rt1.addInterface("G0/3"))

		# Check that the interface successfully added
		self.assertIn("G0/0", rt1.getInterfaces())
		self.assertIn("G0/1", rt1.getInterfaces())
		self.assertIn("G0/3", rt1.getInterfaces())

		# Show interface that the router have
		self.assertDictEqual(rt1.getInterfaces(), {'G0/0': 'unassigned IP', 'G0/1': 'unassigned IP', 'G0/3': 'unassigned IP'})

		# Delete interface and check
		self.assertTrue(rt1.deleteInterface("G0/3"))
		self.assertNotIn("G0/3", rt1.getInterfaces())

		# Delete interface doesn't exist
		self.assertFalse(rt1.deleteInterface("G0/3"))

		# Show interface that router have
		self.assertDictEqual(rt1.getInterfaces(), {'G0/0': 'unassigned IP', 'G0/1': 'unassigned IP'})

		del rt1

	def testConnectivity(self):
		rt1 = Router("Cisco", "c7200", "IOS", "R1")
		rt2 = Router("Cisco", "Nexus", "NXOS", "R2")
		rt3 = Router("Cisco", "csr1000v", "IOSXE", "R3")
		
		rt1.addInterface("G0/0")
		rt1.addInterface("G0/1")

		rt2.addInterface("G0/2")
		rt2.addInterface("G0/3")

		rt3.addInterface("G0/4")
		rt3.addInterface("G0/5")

		# Normal connect
		self.assertTrue(rt1.connect("G0/1", rt2, "G0/2"))
		self.assertTrue(rt2.connect("G0/3", rt3, "G0/4"))
		self.assertTrue(rt3.connect("G0/5", rt1, "G0/0"))

		#              Topology
		#
		# R1 -- (G0/1) ------- (G0/2) -- R2
		#    \                          /
		#   (G0/0)                 (G0/3)
		#      \                      /
		#       \                    /
		#        \                  /
		#         \                /
		#          \              /
		#           \            /
		#            \          /
		#             \        /
		#              \      /
		#           (G0/5)  (G0/4)
		#                \  /
		#                 R3

		self.assertIn("G0/0", rt1.connection)
		self.assertIn("G0/1", rt1.connection)

		self.assertIn("G0/2", rt2.connection)
		self.assertIn("G0/3", rt2.connection)

		self.assertIn("G0/4", rt3.connection)
		self.assertIn("G0/5", rt3.connection)

		self.assertDictEqual(rt1.connection, {'G0/1': ['R2', 'G0/2'], 'G0/0': ['R3', 'G0/5']})
		self.assertDictEqual(rt2.connection, {'G0/2': ['R1', 'G0/1'], 'G0/3': ['R3', 'G0/4']})
		self.assertDictEqual(rt3.connection, {'G0/4': ['R2', 'G0/3'], 'G0/5': ['R1', 'G0/0']})

		# Connect to interface that was connected or not exist
		self.assertFalse(rt1.connect("G0/1", rt3, "G0/4"))
		self.assertFalse(rt1.connect("G0/10", rt3, "G0/20"))

		# Disconnect interface
		self.assertTrue(rt1.disconnect("G0/0", rt3, "G0/5"))
		self.assertNotIn("G0/0", rt1.connection)
		self.assertNotIn("G0/5", rt3.connection)

		self.assertDictEqual(rt1.connection, {'G0/1': ['R2', 'G0/2']})
		self.assertDictEqual(rt3.connection, {'G0/4': ['R2', 'G0/3']})

		# Disconnect the interface that not exist or not connected
		self.assertFalse(rt1.disconnect("G0/10", rt2, "G0/2"))
		self.assertFalse(rt3.disconnect("G0/5", rt1, "G0/0"))

		del rt1, rt2, rt3


if __name__ == '__main__':
	unittest.main()