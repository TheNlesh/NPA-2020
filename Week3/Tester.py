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

    def testAddressing(self):
        rt1 = Router("Cisco", "c7200", "IOS", "R1")
        rt1.addInterface("G0/0")
        rt1.addInterface("G0/1")

        # Normally IP addressing
        self.assertTrue(rt1.setIP("G0/0", "192.168.1.1/24"))
        self.assertEqual(rt1.getInterfaces()["G0/0"], "192.168.1.1/24")

        # Addressing with Broadcast or Network address
        self.assertFalse(rt1.setIP("G0/0", "192.168.1.0/24"))
        self.assertFalse(rt1.setIP("G0/0", "192.168.1.255/24"))

        # Addressing with invalid IP address or Subnet mask
        self.assertFalse(rt1.setIP("G0/0", "999.999.999.999/24"))
        self.assertFalse(rt1.setIP("G0/0", "192.168.1.1/999"))

        # Addressing to the interface that doesn't exist
        self.assertFalse(rt1.setIP("G0/5", "192.168.1.1/24"))

        # check routing (Directly connected)
        self.assertIn("192.168.1.0/24", rt1.getRoute())

        # Addressing to interface that already has IP (Change IP Address)
        self.assertTrue(rt1.setIP("G0/0", "192.168.1.10/24"))

        # Check that IP was changed
        self.assertEqual(rt1.getInterfaces()["G0/0"], "192.168.1.10/24")

        # Normally delete IP address
        self.assertTrue(rt1.deleteIP("G0/0"))
        self.assertEqual(rt1.getInterfaces()["G0/0"], "unassigned IP")
        self.assertNotIn("192.168.1.0/24", rt1.getRoute())

        # delete IP address in the interface that doesn't have IP or doesn't exist
        self.assertFalse(rt1.deleteIP("G0/1"))
        self.assertFalse(rt1.deleteIP("G0/10"))

        # check routing (Directly connected)
        self.assertNotIn("192.168.1.0/24", rt1.getRoute())

        del rt1

    def testRouting(self):
        rt1 = Router("Cisco", "c7200", "IOS", "R1")
        rt1.addInterface("G0/0")
        rt1.addInterface("G0/1")

        # Normally add route
        self.assertTrue(rt1.addRoute("192.168.2.0/24", "192.168.1.2", "G0/0"))
        self.assertTrue(rt1.addRoute("172.16.0.0/16", "172.16.1.1"))
        self.assertTrue(rt1.addRoute("0.0.0.0/0", "8.8.8.8"))

        # Invalid destination routing or nexthop
        self.assertFalse(rt1.addRoute("999.999.999.999/24", "192.168.1.2"))
        self.assertFalse(rt1.addRoute("10.10.1.0/24", "999.99.999.99"))
        self.assertFalse(rt1.addRoute("172.16.0.0/99", "172.16.1.1"))

        # Invalid nexthop interface
        self.assertFalse(rt1.addRoute("172.16.0.0/16", "172.16.1.1", "G0/10"))

        # Validate routing table
        routingtable = rt1.getRoute()
        self.assertIn("192.168.2.0/24", routingtable)
        self.assertIn("172.16.0.0/16", routingtable)
        self.assertIn("8.8.8.8", routingtable['default'])

        # Delete route normally
        self.assertTrue(rt1.deleteRoute("172.16.0.0/16"))

        # Delete route that invalid or doesn't exist
        self.assertFalse(rt1.deleteRoute("999.999.999.999/999"))
        self.assertFalse(rt1.deleteRoute("10.1.1.0/24"))

        # Verify that the route was deleted
        self.assertNotIn("172.16.0.0/16", routingtable)

        del rt1

if __name__ == '__main__':
    unittest.main()