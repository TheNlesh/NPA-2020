from ncclient import manager
import xmltodict
from pprint import pprint

m = manager.connect(
    host = "10.0.15.177",
    port = 830,
    username = "admin",
    password = "cisco",
    hostkey_verify = False
)

def getcapabilities():
    print("#Supported Capabilities (YANG modles): ")
    for capability in m.server_capabilities:
        print(capability)

# getcapabilities()

def get_running_cfg():
    netconf_filter = """
        <filter>
        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native" />
        </filter>
    """

    netconf_reply = m.get_config(source="running", filter=netconf_filter)
    pprint(xmltodict.parse(str(netconf_reply)), indent=2)

# get_running_cfg()

def set_hostname(name):
    netconf_hostname_config = """
    <config>
     <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
     <hostname>{}</hostname>
     </native>
    </config>
    """.format(name)


    netconf_reply = m.edit_config(target="running", config=netconf_hostname_config)
    data_json = xmltodict.parse(str(netconf_reply))
    pprint(data_json)

# set_hostname("CSR-Net")

def create_loopback(ip, mask, loopback_number=0, description="Config from Netconf"):
    netconf_loopback = """
                <config>
                    <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                        <interface>
                            <Loopback>
                                <name>{}</name>
                                <description>{}</description>
                                <ip>
                                    <address>
                                        <primary>
                                            <address>{}</address>
                                            <mask>{}</mask>
                                        </primary>
                                    </address>
                                </ip>
                            </Loopback>
                        </interface>
                    </native>
                </config>
                """.format(loopback_number, description, ip, mask)

    netconf_reply = m.edit_config(target="running", config=netconf_loopback)
    data_json = xmltodict.parse(str(netconf_reply))
    pprint(data_json)

# create_loopback(loopback_number=77, ip="77.77.77.77", mask="255.255.255.255", description="Test")

def delete_loopback(loopback_number):
    del_loopback = """
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface operation="delete">
                <name>Loopback{}</name>
            </interface>
        </interfaces>
    </config>""".format(loopback_number)

    netconf_reply = m.edit_config(target="running", config=del_loopback)
    data_json = xmltodict.parse(str(netconf_reply))
    pprint(data_json)
# delete_loopback(77)

def get_interfaces_state(int_name):
    netconf_filter = """
        <filter>
            <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                <interface>
                    <name>{}</name>
                </interface>
            </interfaces-state>
        </filter>
    """.format(int_name)
    netconf_reply = m.get(filter=netconf_filter)
    resp_dict = xmltodict.parse(str(netconf_reply), dict_constructor=dict)['rpc-reply']['data']

    GE1_status = resp_dict['interfaces-state']['interface']
    for i in GE1_status:
        print("{} : {}".format(i, GE1_status[i]))
# get_interfaces_state("GigabitEthernet1")

def show_ip_int_oper(intName):
    netconf_filter = """
    <filter>
            <interfaces xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-interfaces-oper">
                <interface>
                    <name>{}</name>
                </interface>
            </interfaces>
        </filter>
    """.format(intName)
    netconf_reply = m.get(filter=netconf_filter)
    resp_dict = xmltodict.parse(str(netconf_reply), dict_constructor=dict)['rpc-reply']['data']
    int_status = resp_dict['interfaces']['interface']
    for i in int_status:
        print("{} : {}".format(i, int_status[i]))
# show_ip_int_oper("GigabitEthernet2")

def show_arp():
    netconf_filter = """
    <filter>
        <arp-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-arp-oper">
        </arp-data>
    </filter>
    """
    netconf_reply = m.get(filter=netconf_filter)
    resp_dict = xmltodict.parse(str(netconf_reply), dict_constructor=dict)['rpc-reply']['data']
    arp_data = resp_dict['arp-data']['arp-vrf']['arp-oper']
    for i in arp_data:
        for j in i:
            print(j, i[j], sep=" : ")
        print("-"*20)
    # print(netconf_reply)
# show_arp()

def noshut_int():
    noshut_cmd = """ <config>
            <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                <interface>
                    <name>GigabitEthernet4</name>
                    <enabled>true</enabled>
                </interface>
            </interfaces>
        </config> """
    netconf_reply = m.edit_config(target="running", config=noshut_cmd)
    data_json = xmltodict.parse(str(netconf_reply))
    pprint(data_json)
# noshut_int()

def get_all_cfg():

    netconf_reply = m.get_config(source="running")
    print(netconf_reply)
    # pprint(xmltodict.parse(str(netconf_reply)), indent=2)
get_all_cfg()






