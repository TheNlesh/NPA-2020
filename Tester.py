from Router import *
import unittest

class TestRouter(unittest.TestCase):

	def testRouterATR(self):
		rt1 = Router("Cisco", "c7200", "IOS", "R1")
		self.assertEqual(rt1.getBrand(), "Cisco")
		self.assertEqual(rt1.getModel(), "c7200")
		self.assertEqual(rt1.getHostname(), "R1")
		self.assertEqual(rt1.getOS(), "IOS")

	def testInterface(self):
		rt1 = Router("Cisco", "c7200", "IOS", "R1")
		self.assertTrue(rt1.addInterface("G0/0"))

		self.assertFalse(rt1.addInterface("G0/0"))

unittest.main()