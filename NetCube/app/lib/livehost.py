import nmap
from scapy.all import *
import mysql.connector
from time import time
from lib.snmp import snmp_device_scan


def arp_scan(network):
    print("Escaneo de dispositivos".center(50,"|"))
    scanner = nmap.PortScanner()
    scanner.scan(hosts=network, arguments='-sS')
    conn=mysql.connector.connect(host="localhost", user="root", password="", db="net_cube") 
    print("resultados",scanner.all_hosts())
    for host in scanner.all_hosts():
        print(">"+host)
        if host != "192.168.0.1":          
            cur = conn.cursor()
            cur.execute("DELETE FROM DISPOSITIVOS where IP='" + host + "'")
            varBinds = snmp_device_scan(comnty='public', hostip=host)
            if varBinds is not None:
                cur.execute("INSERT INTO DISPOSITIVOS (IP, HOSTNAME) VALUES (%s, %s)", (host, str(varBinds[4][1])))
                conn.commit()
    cur = conn.cursor()
    cur.execute("SELECT * FROM dispositivos")
    usuarios = cur.fetchall()
    conn.close()
    return usuarios
