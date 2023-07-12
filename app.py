#!/usr/bin/python3

###########
# IMPORTS #
###########
from flask import Flask,render_template,request,redirect,url_for,session,flash
from flask_mysqldb import MySQL
import re
import random
import string
import pdfkit
from flask import make_response


# TODO: This is for security
"""
this function will sanitize
for Server Side Template Injection Vulnerabilities(SSTI)
"""
def sanitize_ssti(form):
    return re.sub("^[A-Za-z0-9]","",form)

# all password character's
# this is for generate key
characters = string.digits + string.ascii_letters + string.punctuation
length = 32

# start app
app = Flask(__name__)

# anti csrf
app.secret_key = "".join(random.sample(characters,length))

# config to connect to MYSQL DB
app.config['MYSQ_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'm3y'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'school'

mysql = MySQL(app)

# home route
# like: http://site.com
@app.route("/")
def home():
    return render_template("home.html")

# Some Errors handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

# this is for students data
@app.route("/estudiantes")
def students():
    return render_template("students.html")

# Gallery 
@app.route("/galeria")
def gallery():
    return render_template("gallery.html")

# History
@app.route("/historia")
def history():
    return render_template("history.html")

# some videos :)
@app.route("/videos")
def videos():
    return render_template("videos.html")

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/login",methods=["GET","POST"])
def login():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM useradmin WHERE usuario = % s AND password = % s',(username,password,))
        account = cursor.fetchone()
        
        
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            return render_template('index.html',message='Logeado/a Exitosamente')
        
        elif not username and not password:
            return render_template('login.html',message='Por favor rellene los campos!')

        else:
            message = 'Usuario/Contraseña Incorrecta'
    
    return render_template('login.html',message=message)

# Dashboard
@app.route("/index")
def index():
    if 'loggedin' in session:
        return render_template("index.html")

    return redirect(url_for('login'))


@app.route("/display",methods=['GET','POST'])
def display():
    if 'loggedin' in session:
        if request.method == 'POST':
            codigo = request.form['codigo']
            cur = mysql.connection.cursor()
            data=cur.execute("SELECT * FROM alumno WHERE codigo=%s",(codigo,))
            user=cur.fetchall()

            if user:
                return render_template('display.html',users=user)


        return render_template('display.html')

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
	session.pop('loggedin',None)
	session.pop('id',None)
	session.pop('username',None)
	return redirect(url_for('login'))

# Insert new alumno to db
@app.route('/new-alumno', methods=['POST'])
def NewAlumno():
    if request.method == 'POST':
        codigo = request.form['codigo']
        firstname = request.form['firstname']
        firstsurname = request.form['firstsurname']
        cedula = request.form['cedula']
        secondname = request.form['secondname']
        secondsurname = request.form['secondsurname']
        edad = request.form['edad']
        sexo = request.form['sexo']
        hb = request.form['hb']
        discapacidad = request.form['discapacidad']
        deportefav = request.form['deportefav']

        cur = mysql.connection.cursor()
        
        cur.execute('SELECT * FROM alumno WHERE codigo = %s',(codigo,))
        account = cur.fetchone()
        
        if account:
            flash('Lo sentimos la cuenta ya existe!')
        else:
            
            sql = "INSERT INTO alumno (codigo,primernombre,primerapellido,cedula,segundonombre,segundoapellido,edad,sexo,hd,discapacidad,deportefav) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            data = (codigo,firstname,secondname,cedula,secondname,secondsurname,edad,sexo,hb,discapacidad,deportefav)
            
            cur.execute(sql,data)
            mysql.connection.commit()
    
    return redirect(url_for('register'))
    

# Insert new parent to db
@app.route('/new-representante', methods=['GET', 'POST'])
def newRepresentante():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cedula = request.form['cedula']
        edad = request.form['edad']
        ocupacion = request.form['ocupacion']
        sexo = request.form['sexo']

        # connection
        cur = mysql.connection.cursor()

        cur.execute('SELECT * FROM representante WHERE cedula = %s',(cedula,))
        account = cur.fetchone()

        if account:
            flash('Lo sentimos la cuenta ya existe!')
        else:
            sql = "INSERT INTO representante (nombre,cedula,edad,ocupacion,sexo) VALUES (%s,%s,%s,%s,%s)"
            
            data = (nombre,cedula,edad,ocupacion,sexo)
            cur.execute(sql,data)
            mysql.connection.commit()

    return redirect(url_for('register'))

# Inscripcion Page
@app.route('/register', methods =['GET'])
def register():
    return render_template('register.html')

# Update Page
@app.route('/indexupdate',methods=['GET','POST'])
def indexupdate():
    if 'loggedin' in session:
        if request.method == 'POST':
            codigo = request.form.get('codigo',False)
            cedula = request.form.get('cedula',False)
            
            connection1=mysql.connection
            cur1 = connection1.cursor()
            cur1.execute("SELECT * FROM alumno WHERE codigo=%s",(codigo,))
            user=cur1.fetchall()

            if user:
                return render_template('updateindex.html',users=user)
            
            try:
                conn = mysql.connection.cursor()
                conn.execute('SELECT * FROM representante WHERE cedula=%s',(cedula,))
                repuser=conn.fetchall()
                
                if repuser:
                    return render_template('updateindex.html',representanes=repuser)
            except Exception as e:
                print(e)

        return render_template('updateindex.html')


# Modify Alumno route
@app.route('/modify-alumno/<int:codigo>')
def ModifyAlumno(codigo):
    conn = mysql.connection.cursor()

    conn.execute('SELECT * FROM alumno WHERE codigo=%s',(codigo,))
    alm = conn.fetchall()
    mysql.connection.commit()

    return render_template('edit.html',alm=alm)


# Update
@app.route("/updateAlumno",methods=['GET','POST'])
def updateAlumno():
    codigo = request.values.get('codigo')
    _primernombre = request.form['firstname']
    _primerApellido = request.form['firstsurname']
    _cedula = request.form['cedula']
    _secondName = request.form['secondname']
    _secondSurname = request.form['secondsurname']
    _edad = request.form['edad']
    _sexo = request.form['sexo']
    _hd = request.form['hd']
    _discapacidad = request.form['discapacidad']
    _deporteFav = request.form['deportefav']

    sql = "UPDATE alumno SET primernombre=%s,primerapellido=%s,cedula=%s,segundonombre=%s,segundoapellido=%s,edad=%s,sexo=%s,hd=%s,discapacidad=%s,deportefav=%s WHERE codigo=%s"
    data=(_primernombre,_primerApellido,_cedula,_secondName,_secondSurname,_edad,_sexo,_hd,_discapacidad,_deporteFav,codigo)

    cur = mysql.connection.cursor()
    cur.execute(sql,data)
    mysql.connection.commit()

    return redirect('/indexupdate')

@app.route('/updateRepresentante',methods=['GET','POST'])
def updateRepresentante():
    cedula = request.values.get('cedula')
    nombre = request.form['nombre']
    edad = request.form['edad']
    ocupacion = request.form['ocupacion']
    sexo = request.form['sexo']

    sql = "UPDATE representante SET nombre=%s,edad=%s,ocupacion=%s,sexo=%s WHERE cedula=%s"
    data=(nombre,edad,ocupacion,sexo,cedula)

    cursor = mysql.connection.cursor()
    cursor.execute(sql,data)
    mysql.connection.commit()

    return redirect('/indexupdate')


# Parent Modification
@app.route('/modify-representante/<int:cedula>')
def modifyRepresentante(cedula):
    conn = mysql.connection.cursor()

    conn.execute('SELECT * FROM representante WHERE cedula=%s',(cedula,))
    rep = conn.fetchall()
    mysql.connection.commit()

    return render_template('edit-parent.html',rep=rep)


# Search alumno by codigo
@app.route("/buscar",methods=['GET','POST'])
def buscar():
    msg=''
    if 'loggedin' in session:
        if request.method == 'POST':
            userdetails = request.form
            codigo = userdetails['codigo']

            cur = mysql.connection.cursor()
            data = cur.execute("SELECT codigo FROM alumno where codigo = %s",(codigo,))

            if data > 0 :
                msg='Alumno Registrado!'
            else:
                msg='Alumno No Registrado!'

        return render_template("buscar.html",msg=msg)
    return render_template("login.html")

# Periodo Academico Template
@app.route('/perido_acamedico', methods=['GET', 'POST'])
def periodoAcademico():
    if 'loggedin' in session:
        if request.method == 'POST':
            year = request.form['year']

            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM periodo_academico_%s;' % (year))
            estudents = cur.fetchall()

            if estudents:
                return render_template('periodoacademico.html',estudents=estudents)
                
        return render_template('periodoacademico.html')

# Constancia Estudio route
@app.route('/constancia')
def constancia():
    if 'loggedin' in session:
        name = "Constancia Del Estudiante"
        html = render_template(
            "constancia.html",
            name=name)
        pdf = pdfkit.from_string(html, False)
        response = make_response(pdf)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = "inline; filename=output.pdf"
        return response


# reporte routes
@app.route('/reporte')
def reporte():
    return render_template('reporte.html')

# too many routes for 'reporte' route
# show students each one
# this go from 1 to 6
@app.route('/estudianteinicial')
def estudianteinicial():
    return render_template('estudianteinicial.html')

@app.route('/estudiantes1')
def estudiantes1():
    return render_template('estudiantes1.html')

@app.route('/estudiantes2')
def estudiantes2():
    return render_template('estudiantes2.html')

@app.route('/estudiantes3')
def estudiantes3():
    return render_template('estudiantes3.html')

@app.route('/estudiantes4')
def estudiantes4():
    return render_template('estudiantes4.html')


@app.route('/estudiantes5')
def estudiantes5():
    return render_template('estudiantes5.html')

@app.route('/estudiantes6')
def estudiantes6():
    return render_template('estudiantes6.html')

# TODO CHANGE THIS FUNC TO DELETE USER FROM PAGE BUT NOT FROM DB 
# Delete an user from DB 
@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        codigo = request.form['codigo']

        # connect 
        cursor = mysql.connection.cursor()

        # get user if 'exists'
        # True / False
        cursor.execute('SELECT * FROM alumno WHERE codigo = %s',(codigo,)) 
        code = cursor.fetchone()

        if code:
            # delete sql sentence
            cursor.execute('DELETE FROM alumno WHERE codigo = %s',(codigo,))
            mysql.connection.commit()
            return render_template('delete.html',message='Desincorporado del sistema exitosamente!')

        # the alumno doesn't exists
        else:
            return render_template('delete.html',message='El alumno no esta inscrito')
    
    return render_template('delete.html')

if __name__ == "__main__":
    # start server 
    app.run(host='192.168.250.20')
