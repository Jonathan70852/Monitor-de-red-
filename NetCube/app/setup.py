import os

#Install libraries
os.system('pip install -r librerias.txt')

#Run pyinstaller
os.system('pyinstaller --hidden-import python-nmap --hidden-import scapy --hidden-import scapy-http --hidden-import scapy-python3 --hidden-import mysql-connector-python --hidden-import mysqlclient --hidden-import PyMySQL --hidden-import Flask-MySQLdb --hidden-import pysnmp --hidden-import netaddr --hidden-import Flask --hidden-import Flask-WTF --hidden-import WTForms --hidden-import fpdf2 app.py')
