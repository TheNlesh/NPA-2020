import pexpect

prompt = '#'
ip = '172.31.179.5'
show_ip = 'sh ip int br'
username = 'admin'
password = 'cisco'

conn = pexpect.spawn('telnet ' + ip)

conn.expect('Username')
conn.sendline(username)
conn.expect('Password')
conn.sendline(password)

conn.expect(prompt)
set_loopback_cmd = ['conf t', 'int lo0', 'ip add 172.20.179.5 255.255.255.255', 'end', 'wr']

for cmd in set_loopback_cmd:
	conn.sendline(cmd)
	conn.expect(prompt)

conn.sendline(show_ip)
conn.expect(prompt)
result = conn.before.decode()
print(result)
conn.sendline('exit')
conn.close()