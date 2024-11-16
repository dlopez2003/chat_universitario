from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import re  # Para la validación de correos electrónicos

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta'  # Cambia esto por una clave secreta más segura

# Conexión a la base de datos
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # Cambia si tu base de datos no está en localhost
        user="root",       # Cambia con tu usuario de base de datos
        password="",       # Cambia con tu contraseña de base de datos
        database="login_chat"
    )

# Ruta para la página de inicio (index)
@app.route('/')
def index():
    if 'usuario' in session:
        return redirect(url_for('bienvenido'))
    return render_template('index.html')

# Ruta para la página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        
        # Verifica las credenciales en la base de datos
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if user and check_password_hash(user[2], contrasena):  # Compara la contraseña encriptada
            session['usuario'] = user[1]  # Guarda el correo del usuario en la sesión
            return redirect(url_for('bienvenido'))  # Redirige a la página de bienvenida
        else:
            return "Credenciales incorrectas", 401  # Si las credenciales son incorrectas
    
    return render_template('login.html')

# Ruta para la página de bienvenida
@app.route('/bienvenido')
def bienvenido():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('bienvenido.html')

# Ruta para registrar nuevos usuarios
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        
        # Validación del correo institucional
        if not re.match(r"[a-zA-Z0-9._%+-]+@uab\.edu\.bo$", correo):
            return "El correo debe ser institucional de la Universidad Adventista de Bolivia (ejemplo: usuario@uab.edu.bo)", 400
        
        # Encripta la contraseña
        contrasena_encriptada = generate_password_hash(contrasena)

        # Inserta un nuevo usuario en la base de datos
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO usuarios (correo, contrasena) VALUES (%s, %s)", (correo, contrasena_encriptada))
        connection.commit()
        cursor.close()
        connection.close()
        
        return redirect(url_for('login'))  # Redirige al login tras el registro
    
    return render_template('registro.html')

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('usuario', None)  # Elimina el usuario de la sesión
    return redirect(url_for('index'))  # Redirige a la página de inicio

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Escucha en 0.0.0.0 para ser accesible desde otros dispositivos en la misma red
    