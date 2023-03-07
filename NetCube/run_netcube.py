import os

# Obtener la ruta absoluta de la carpeta 'datos'
dir_path = os.path.abspath('app')

# Cambiar el directorio de trabajo actual al directorio 'datos'
os.chdir(dir_path)

#os.chdir('C:/Users/Jonathan/Desktop/Nueva carpeta/Monitor de red/Flask/app')

#Install libraries
os.system('pip install -r librerias.txt')

#Run pyinstaller
#os.system('pyinstaller --hidden-import python-nmap --hidden-import scapy --hidden-import scapy-http --hidden-import scapy-python3 --hidden-import mysql-connector-python --hidden-import mysqlclient --hidden-import PyMySQL --hidden-import Flask-MySQLdb --hidden-import pysnmp --hidden-import netaddr --hidden-import Flask --hidden-import Flask-WTF --hidden-import WTForms --hidden-import fpdf2 app.py')

os.system('python app.py')





