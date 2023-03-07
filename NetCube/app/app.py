
from flask import Flask, request, render_template, make_response, redirect, flash, session 
from flask_mysqldb import MySQL
from lib.livehost import arp_scan
from lib.snmp import create_list, snmp_device_scan
from send_emails import send_email
from create_pdf import create_pdf
from datetime import datetime
from alerts_thread import RepeatTimer
from flask_wtf import FlaskForm
from wtforms.fields import DateField
from wtforms.validators import DataRequired
from wtforms import validators, SubmitField

app = Flask(__name__)
app.title = 'Netcube'
#Conexión a MySQL
#app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'net_cube'

conexion = MySQL(app)

hardDisk_alert = ""
wifi_alert = ""
ethernet_alert = ""
disconnect_alert = ""
param_hard_disk = 0
param_wifi = 0
param_ethernet = 0
alarmas = []


"""
Clave secreta. Esta debe ser aleatoria.
Entrarás a la CLI de Python, ahí ejecuta:
import os; print(os.urandom(16));
Eso te dará algo como:
b'\x11\xad\xec\t\x99\x8f\xfa\x86\xe8A\xd9\x1a\xf6\x12Z\xf4'
Simplemente remplaza la clave que se ve a continuación con los bytes aleatorios que generaste
"""

app.secret_key = b'\xa3w5y\x1dL|\xd3oy\x8ew\xd3D\xe9\xc8'

class InfoForm(FlaskForm):
    startdate = DateField('Fecha de inicio', format='%Y-%m-%d')
    enddate = DateField('Fecha de fin', format='%Y-%m-%d')
    submit = SubmitField('Filtrar')

@app.route('/')
def login():
    return render_template('Login.html', mensaje = "")


@app.route("/hacer_login", methods=['GET',"POST"])
def hacer_login():
    correo = request.form["correo"]
    palabra_secreta = request.form["palabra_secreta"]

    cur = conexion.connection.cursor()
    query = "SELECT PASSWORD, CHANGE_PASSWORD FROM usuarios WHERE EMAIL ='" + correo + "'"
    cur.execute(query)
    user = cur.fetchall()

    if user:
        password = user[0][0]
        change_password = user[0][1]
        if palabra_secreta == password:
            # Si coincide comprobamos que haya cambiado su contraseña si es su primer login
            #Si ya ha cambiado su contraseña
            if bool(int(change_password)):
                #iniciamos sesión y además redireccionamos
                session["usuario"] = correo
                return redirect("/home")
            #cambio de contraseña necesario
            else:
                return render_template('actualizarPassword.html', correo = correo, mensaje = "")
        else:
             # Si NO coincide, lo regresamos
            flash("Correo o contraseña incorrectos")
            return redirect("/")

    else:
        # Si NO coincide, lo regresamos
        flash("Correo o contraseña incorrectos")
        return redirect("/")

# Cerrar sesión
@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect("/")

# Un "middleware" que se ejecuta antes de responder a cualquier ruta. Aquí verificamos si el usuario ha iniciado sesión
@app.before_request
def antes_de_cada_peticion():
    ruta = request.path
    # Si no ha iniciado sesión y no quiere ir a algo relacionado al login, lo redireccionamos al login
    if not 'usuario' in session and ruta != "/actualizar_password" and ruta != "/" and ruta != "/hacer_login" and ruta != "/logout" and not ruta.startswith("/static"):
        flash("Inicia sesión para continuar")
        return redirect("/")
    # Si ya ha iniciado, no hacemos nada, es decir lo dejamos pasar

@app.route('/home')
def Home():
    if session["usuario"]:
        return render_template('home.html')
    else:
        return redirect("/")

@app.route('/empezar')
def Empezar():
    if session["usuario"]:
        return render_template('empezar.html')
    else:
        return redirect("/")

@app.route("/actualizar_password", methods=['GET',"POST"])
def actualizar_password():
    if request.method == 'POST':
        correo = request.form["correo"]
        palabra_secreta = request.form["palabra_secreta"]
        confirmar_palabra_secreta = request.form["confirmar_palabra_secreta"]

        if palabra_secreta == confirmar_palabra_secreta:
            if len(palabra_secreta) <= 10: 
                values = [palabra_secreta, 1,correo]
                conn = conexion.connection
                cur = conn.cursor()
                cur.execute("UPDATE usuarios SET PASSWORD = %s, CHANGE_PASSWORD= %s WHERE EMAIL = %s", values)
                conn.commit()
                return render_template('Login.html', mensaje = "Contraseña actualizada con éxito")
            else:
                return render_template('actualizarPassword.html', correo = correo, mensaje = "Las contraseñas debe tener max 10 caracteres.")
        else:
            return render_template('actualizarPassword.html', correo = correo, mensaje = "Las contraseñas no coinciden. Intente nuevamente.")
    else:
        return redirect("/")

@app.route('/inicio',methods = ['POST', 'GET'])
def Inicio():
    if session["usuario"]:
        if request.method == 'POST':
            form_data = request.form
            fecha_inicio = form_data.getlist('startdate')[0]
            fecha_fin = form_data.getlist('enddate')[0]
        else:
            if request.method == 'GET':
                fecha_inicio = ""
                fecha_fin = ""
        
        if request.method == 'POST' or request.method == 'GET':
            form = InfoForm()
            # Definir datos del primer grafico - Total de alarmas por tipo
            labels_g1= [
            'Desconexión',
            'Wifi',
            'Ethernet',
            'HDD',
            ]
            cur = conexion.connection.cursor()
            disconnection_count_query = "SELECT COUNT(*) AS DISCONNECTION FROM alertas WHERE TIPO_ALERTA = 'Desconexión de equipo'" + ((" AND FECHA <= '" + fecha_fin + "' AND FECHA >= '" + fecha_inicio + "'") if (fecha_inicio != "" and fecha_fin != "") else "")
            cur.execute(disconnection_count_query)
            disconnection_count=cur.fetchall()
            wifi_count_query = "SELECT COUNT(*) AS WIFI FROM alertas WHERE TIPO_ALERTA = 'Velocidad Wifi'"  + ((" AND FECHA <= '" + fecha_fin + "' AND FECHA >= '" + fecha_inicio + "'") if (fecha_inicio != "" and fecha_fin != "") else "")
            cur.execute(wifi_count_query)
            wifi_count=cur.fetchall()
            ethernet_count_query = "SELECT COUNT(*) AS ETHERNET FROM alertas WHERE TIPO_ALERTA = 'Velocidad Ethernet'"  + ((" AND FECHA <= '" + fecha_fin + "' AND FECHA >= '" + fecha_inicio + "'") if (fecha_inicio != "" and fecha_fin != "") else "")
            cur.execute(ethernet_count_query)
            ethernet_count=cur.fetchall()
            hdd_count_query = "SELECT COUNT(*) AS HDD FROM alertas WHERE TIPO_ALERTA = 'Espacio en disco HDD'"  + ((" AND FECHA <= '" + fecha_fin + "' AND FECHA >= '" + fecha_inicio + "'") if (fecha_inicio != "" and fecha_fin != "") else "")
            cur.execute(hdd_count_query)
            hdd_count=cur.fetchall()
            data_g1 = [disconnection_count[0][0], wifi_count[0][0], ethernet_count[0][0], hdd_count[0][0]]
            # Definir datos del segundo grafico - Total de alarmas por nivel
            labels_g2= [
            'Crítico',
            'Aviso',
            ]
            critico_count_query = "SELECT COUNT(*) AS CRITICO FROM alertas WHERE NIVEL = 'Crítico'"  + ((" AND FECHA <= '" + fecha_fin + "' AND FECHA >= '" + fecha_inicio + "'") if (fecha_inicio != "" and fecha_fin != "") else "")
            cur.execute(critico_count_query)
            critico_count=cur.fetchall()
            aviso_count_query = "SELECT COUNT(*) AS AVISO FROM alertas WHERE NIVEL = 'Aviso'"  + ((" AND FECHA <= '" + fecha_fin + "' AND FECHA >= '" + fecha_inicio + "'") if (fecha_inicio != "" and fecha_fin != "") else "")
            cur.execute(aviso_count_query)
            aviso_count=cur.fetchall()
            data_g2 = [critico_count[0][0], aviso_count[0][0]]

            # Definir datos del tercer grafico - Cantidad de alarmas por fecha
            critico_count_query = "SELECT FECHA, COUNT(FECHA) AS NUMERO FROM alertas "+ ((" WHERE FECHA <= '" + fecha_fin + "' AND FECHA >= '" + fecha_inicio + "'") if (fecha_inicio != "" and fecha_fin != "") else "") + " GROUP BY FECHA" 
            cur.execute(critico_count_query)

            data=cur.fetchall()
            labels_g3=[]
            data_g3=[]
            for row in data:
                labels_g3.append(str(row[0]))
                data_g3.append(row[1])
        
            return render_template('inicio.html',form = form, data_g1= data_g1,
            labels_g1=labels_g1, labels_g2=labels_g2,data_g2=data_g2,labels_g3=labels_g3,data_g3=data_g3)
    else:
        return redirect("/")


@app.route('/dispositivos')
def Dispositivos():
    if session["usuario"]:
        return render_template('dispositivos.html', mensaje = "", error= False)
    else:
        return redirect("/")

@app.route('/alarmas')
def Alarmas():
    if session["usuario"]:
        form = InfoForm()
        cur = conexion.connection.cursor()
        query = "SELECT * FROM alertas"
        cur.execute(query)
        alertas=cur.fetchall()
        alertas = alertas[::-1]
        global alarmas
        alarmas = alertas
        return render_template('alarmas.html', alarmas = alertas, form = form, selected_option = "")
    else:
        return redirect("/")

@app.route('/filtrarAlarmas',methods = ['GET','POST']) 
def FiltrarAlarmas():
    alertas = []
    ip, hostname = "",""
    if session["usuario"]:
        if request.method == 'POST':
            form = InfoForm()
            form_data = request.form
            tipo_alarma = form_data.getlist('alertTypes')[0]
            selected_option = tipo_alarma

            if tipo_alarma == "disconnection_alert":
                tipo_alarma = "Desconexión de equipo"
            if tipo_alarma == "wifi_alert":
                tipo_alarma = "Velocidad Wifi"
            if tipo_alarma == "ethernet_alert":
                tipo_alarma = "Velocidad Ethernet"
            if tipo_alarma == "hardDisk_alert":
                tipo_alarma = "Espacio en disco HDD"

            fecha_inicio = form_data.getlist('startdate')[0]
            fecha_fin = form_data.getlist('enddate')[0]

            ip = form_data.getlist('ip')[0]
            hostname = form_data.getlist('hostname')[0]

            cur = conexion.connection.cursor()
            query = "SELECT * FROM alertas"
            filters = []
            if tipo_alarma:
                filters.append(("TIPO_ALERTA = '" + tipo_alarma + "'"))
            if fecha_fin and fecha_fin:
                filters.append(("FECHA <= '" + fecha_fin + "' AND FECHA >= '" + fecha_inicio + "'"))
            if ip:
                filters.append(("IP = '" + ip + "'"))
            if hostname:
                filters.append(("NOMBRE_MAQUINA = '" + hostname + "'"))
            
            if len(filters) > 0:
                query+= " WHERE "
                for i in range(len(filters)):
                    if i == 0:
                        query+= filters[i]
                    else:
                        query+= " AND " + filters[i]
                 
            cur.execute(query)
            alertas=cur.fetchall()
            alertas = alertas[::-1]
            global alarmas
            alarmas = alertas
            return render_template('alarmas.html', alarmas = alertas, form = form, selected_option = selected_option, ip= ip, hostname= hostname)
        else:
            return redirect("/alarmas")
    else:
        return redirect("/")

@app.route('/configuracion')
def Configuracion():
    if session["usuario"]:
        cur = conexion.connection.cursor()
        query = "SELECT * FROM configuracion"
        cur.execute(query)
        configuracion=cur.fetchall()
        return render_template('configuracion.html', configuracion = configuracion[0], mensaje = "")
    else:
        return redirect("/")

@app.route('/descargarPDF') 
def DescargarPDF():
    if session["usuario"]:
        global alarmas
        values = []
        for alarma in alarmas:
            values.append(alarma[1:6] + (alarma[7],))
        pdf = create_pdf(values)
        response = make_response(pdf.output(dest='S'))
        dt = datetime.now().strftime("%Y-%m-%d")
        response.headers.set('Content-Disposition', 'attachment', filename='alerta_' + dt+ '.pdf')
        response.headers.set('Content-Type', 'application/pdf')
        return response
    else:
        return redirect("/")

@app.route('/informe/<id_dispositivo>') 
def Informes(id_dispositivo):
    if session["usuario"]:
        cur = conexion.connection.cursor()
        query = "SELECT IP FROM dispositivos WHERE ID = " + id_dispositivo 
        cur.execute(query)
        us=cur.fetchall()
        print (us)
        informe = []
        if us:
            informe = create_list(us[0][0])
        return render_template ('informe.html', us = informe)
    else:
        return redirect("/")

@app.route('/usuarios')
@app.route('/usuarios/<menuAgregarUsuario>')
@app.route('/usuarios/<usuario>/<menuAgregarUsuario>')
def VerUsuarios(usuario = None, menuAgregarUsuario = False, mensaje = "", error= False):
    if session["usuario"]:
        cur = conexion.connection.cursor()
        query = "SELECT * FROM usuarios"
        cur.execute(query)
        users=cur.fetchall()
        if usuario:
            usuario = usuario.replace(")","").replace("(","").replace("'","").split(",")
        return render_template ('usuarios.html', usuarios = users, menuAgregarUsuario = menuAgregarUsuario, usuario = usuario, mensaje = mensaje, error = error)
    else:
        return redirect("/")

@app.route('/agregarUsuario',methods = ['GET','POST']) 
def AgregarUsuario():
    if session["usuario"]:
        if request.method == 'POST':
            form_data = request.form
            correo = form_data['correo']
            password = form_data['password']
            cur = conexion.connection.cursor()
            query = "SELECT * FROM usuarios"
            cur.execute(query)
            users=cur.fetchall()
            existUser = False
            for user in users:
                if user[1] == correo:
                    existUser = True
            if not existUser:
                values = [correo, password, 1]
                conn = conexion.connection
                cur = conn.cursor()
                cur.execute("INSERT INTO usuarios (EMAIL, PASSWORD, CHANGE_PASSWORD) VALUES (%s, %s, %s)", values)
                conn.commit()
                return VerUsuarios(menuAgregarUsuario=False, mensaje = "Usuario agregado con éxito")
            else:
                return VerUsuarios(menuAgregarUsuario=False, mensaje = "El usuario ya existe", error=True)
        else:
            return VerUsuarios(menuAgregarUsuario=False, mensaje = "")

    else:
        return redirect("/")

@app.route('/editarUsuario',methods = ['GET','POST'])
def EditarUsuario():
    if session["usuario"]:
        if request.method == 'POST':
            form_data = request.form
            idUsuario = form_data['id']
            correo = form_data['correo']
            password = form_data['password']
            cur = conexion.connection.cursor()
            query = "SELECT * FROM usuarios"
            cur.execute(query)
            users=cur.fetchall()

            existUser = False
            for user in users:
                if str(user[0]) != idUsuario:
                    if user[1] == correo:
                        existUser = True

            if not existUser:
                values = [correo, password, idUsuario]
                conn = conexion.connection
                cur = conn.cursor()
                cur.execute("UPDATE usuarios SET EMAIL = %s, PASSWORD= %s WHERE ID = %s", values)
                conn.commit()
                return VerUsuarios(menuAgregarUsuario=False, mensaje = "Usuario editado con éxito")
            else:
                return VerUsuarios(menuAgregarUsuario=False, mensaje = "El usuario ya existe", error=True)
        else:
                return VerUsuarios(menuAgregarUsuario=False, mensaje = "")
    else:
        return redirect("/")

@app.route('/eliminarUsuario/<id_usuario>')
def EliminarUsuario(id_usuario):
    if session["usuario"]:
        conn = conexion.connection
        cur = conn.cursor()
        query = "DELETE FROM usuarios WHERE ID = "+id_usuario
        cur.execute(query)
        conn.commit()
        return VerUsuarios(mensaje = "Usuario eliminado con éxito")
    else:
        return redirect("/")

@app.route('/informeip/<ip_dispositivo>') 
def Informesip(ip_dispositivo):
    if session["usuario"]:
        informe = create_list(ip_dispositivo)
        return render_template ('informe.html', us = informe)
    else:
        return redirect("/")

@app.route('/livehost-result',methods = ['GET','POST'])
def livehost_result():
    if session["usuario"]:
        if request.method == 'POST':
            conn = conexion.connection
            cur = conn.cursor()
            cur.execute("TRUNCATE TABLE dispositivos")
            conn.commit()
            form_data = request.form
            usuarios=arp_scan(form_data['url'])
            if len(usuarios) > 0:
                error = False
                mensaje = "Escaneo de redes completado con éxito"
            else:
                error = True
                mensaje = "Ninguna red encontrada"

        return render_template('dispositivos.html',usuarios=usuarios, mensaje = mensaje, error= error)
    else:
        return redirect("/")

##########################BOTON CONFIGURACION DE PROGRAMA
@app.route('/update-system-configurations',methods = ['GET','POST'])
def update_system_configurations():
    mensaje = ""
    if session["usuario"]:
        if request.method == 'POST':
            global hardDisk_alert,wifi_alert, ethernet_alert, disconnect_alert, param_wifi, param_ethernet, param_hard_disk
            form_data = request.form
            hardDisk_check_box_value = request.form.getlist('hardDisk_alert')
            wifi_check_box_value = request.form.getlist('wifi_alert')
            ethernet_check_box_value = request.form.getlist('ethernet_alert')
            disconnect_check_box_values = request.form.getlist('disconnect_alert')

            if hardDisk_check_box_value:
                hardDisk_alert = "1" if hardDisk_check_box_value[0] == "on" else "0"
            else:
                hardDisk_alert = "0"

            if wifi_check_box_value:
                wifi_alert = "1" if wifi_check_box_value[0] == "on" else "0"
            else:
                wifi_alert = "0"

            if ethernet_check_box_value:
                ethernet_alert = "1" if ethernet_check_box_value[0] == "on" else "0"
            else:
                ethernet_alert = "0"

            if disconnect_check_box_values:
                disconnect_alert = "1" if disconnect_check_box_values[0] == "on" else "0"
            else:
                disconnect_alert = "0"
            
            if form_data["param_hard_disk"]:
                param_hard_disk = int(form_data["param_hard_disk"])
            if form_data["param_ethernet"]:
                param_ethernet = int(form_data["param_ethernet"])
            if form_data["param_wifi"]:
                param_wifi = int(form_data["param_wifi"])

            values = [form_data["email_receiver"],form_data["email_sender"],form_data["email_password"],form_data["seconds_interval"],hardDisk_alert,form_data["param_hard_disk"],wifi_alert,form_data["param_wifi"],ethernet_alert,form_data["param_ethernet"],disconnect_alert]
            conn = conexion.connection
            cur = conn.cursor()
            #Cuidar que en la base de datos de configuracion solo exista 1 fila con ID = 1
            cur.execute("UPDATE configuracion SET EMAIL_RECEIVER = %s, EMAIL_SENDER= %s, PASSWORD_SENDER= %s, SECONDS_INTERVAL= %s, HARDDISK_ALERT= %s, HARDDISK_PARAM=%s, WIFI_ALERT=%s , WIFI_PARAM=%s, ETHERNET_ALERT=%s, ETHERNET_PARAM=%s, DISCONNECTION_ALERT=%s WHERE ID = 1", values)
            conn.commit()
            mensaje = "Datos actualizados con éxito"
        cur = conexion.connection.cursor()
        query = "SELECT * FROM configuracion"
        cur.execute(query)
        configuracion=cur.fetchall()
        return render_template('configuracion.html', configuracion = configuracion[0], mensaje=mensaje)
    else:
        return redirect("/")

##########################CONFIGURACION DE CORREO DE ALARMAS
def scan_all_user():
    print("Activando escaneo de dispositivos".center(50, "."))
    with app.app_context():
        global hardDisk_alert,wifi_alert, ethernet_alert, disconnect_alert, param_wifi, param_ethernet, param_hard_disk
        values = [hardDisk_alert,wifi_alert,ethernet_alert,disconnect_alert,param_wifi,param_ethernet,param_hard_disk]
        hardDisk_alert = int(hardDisk_alert)
        wifi_alert = int(wifi_alert)
        ethernet_alert = int(ethernet_alert)
        disconnect_alert = int(disconnect_alert)
        cur = conexion.connection.cursor()
        cur.execute("SELECT * FROM dispositivos")
        usuarios = cur.fetchall()
        print("Usuarios activos".center(50, "-"))
    for user in usuarios:
        print(">"+str(user[1]))
        if user[1] != "192.168.0.1":
            varBinds = snmp_device_scan(comnty='public', hostip=user[1])
            #Alerta de desconexión de dispositivo
            #IP, TITULO, HORA FECHA, DESCRIPCIÓN
            #print("disconnect_alert",disconnect_alert, "on" if bool(disconnect_alert) else "off")
            if bool(disconnect_alert) and varBinds is None:
                print(">"+user[1],":Activando alerta de desconexion".center(30, "."))
                dt = datetime.now()
                date = dt.strftime("%Y-%m-%d")
                time = dt.strftime("%H:%M:%S")
                values = [date, time, user[2], "Crítico", user[1], "Desconexión de equipo", "El dispositivo ha sido desconectado de la red"]
                persist_alert(values)
                send_email(values)
            else:
                if varBinds is not None:
                    #Alerta de baja velocidad wifi
                    print(user,"SNMP con respuesta")
                    #print("wifi_alert",wifi_alert, "on" if bool(wifi_alert) else "off")
                    if bool(wifi_alert) and varBinds[14][1] < param_wifi and varBinds[14][1] > 0:
                        print(">"+user[1],":Activando alerta de velocidad Wifi".center(30, "."))
                        dt = datetime.now()
                        date = dt.strftime("%Y-%m-%d")
                        time = dt.strftime("%H:%M:%S")
                        values = [date, time, user[2], "Aviso", user[1], "Velocidad Wifi", str("La velocidad Wifi esta por debajo del rango aceptable: " + str(varBinds[14][1])+ " Mbps.")]
                        persist_alert(values)
                        send_email(values)

                    #Alerta de baja velocidad ethernet
                    #print("ethernet_alert",ethernet_alert, "on" if bool(ethernet_alert) else "off")
                    if bool(ethernet_alert) and varBinds[13][1] < param_ethernet and varBinds[13][1] > 0:
                        print(">"+user[1],":Activando alerta velocidad Ethernet".center(30, "."))
                        dt = datetime.now()
                        date = dt.strftime("%Y-%m-%d")
                        time = dt.strftime("%H:%M:%S")
                        values = [date, time, user[2], "Aviso", user[1], "Velocidad Ethernet",  str("La velocidad Ethernet esta por debajo del rango aceptable: " + str(varBinds[13][1]) + " Mbps.")]
                        persist_alert(values)
                        send_email(values)

                    #Alerta tamaño de disco optimo superado
                    #print("hardDisk_alert",hardDisk_alert, "on" if bool(hardDisk_alert) else "off")
                    if bool(hardDisk_alert) and (varBinds[9][1] / varBinds[8][1]) >= (param_hard_disk/100):
                        print(">"+user[1],":Activando alerta espacio en disco HDD".center(30, "-"))
                        dt = datetime.now()
                        date = dt.strftime("%Y-%m-%d")
                        time = dt.strftime("%H:%M:%S")
                        values = [date, time, user[2], "Aviso", user[1], "Espacio en disco HDD", "El tamaño del disco HDD ha superado el "+ str(param_hard_disk)+"%"]
                        persist_alert(values)
                        send_email(values)
    print("Escaneo finalizado".center(50, "."))

            
def persist_alert(values):
    with app.app_context():
        conn = conexion.connection
        cur = conn.cursor()
        cur.execute("INSERT INTO alertas (FECHA, HORA, NOMBRE_MAQUINA, NIVEL, IP, TIPO_ALERTA, MENSAJE) VALUES (%s, %s, %s, %s, %s, %s, %s)", values)
        conn.commit()


if __name__ == '__main__':       
    with app.app_context():
        cur = conexion.connection.cursor()
        cur.execute("SELECT SECONDS_INTERVAL, HARDDISK_ALERT, HARDDISK_PARAM, WIFI_ALERT, WIFI_PARAM, ETHERNET_ALERT, ETHERNET_PARAM, DISCONNECTION_ALERT FROM configuracion")
        data=cur.fetchall()
        hardDisk_alert = data[0][1]
        if data[0][2]:
            param_hard_disk = int(data[0][2])
        else:
            param_hard_disk = 100
        wifi_alert = data[0][3]
        if data[0][4]:
            param_wifi = int(data[0][4])
        else:
            param_hard_disk = 0
        ethernet_alert = data[0][5]
        if data[0][6]:
            param_ethernet = int(data[0][6])
        else:
            param_ethernet = 0
        disconnect_alert = data[0][7]
        

    timer = RepeatTimer(int(data[0][0]), scan_all_user)  
    timer.start() #recalling run  
    app.run('0.0.0.0', port=8080)
