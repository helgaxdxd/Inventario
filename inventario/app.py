from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import event
from sqlalchemy.engine import Engine
from docxtpl import DocxTemplate
from datetime import datetime
from docx2pdf import convert
import io, os, tempfile

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # cámbiala

# ======== CONFIGURACIÓN SQLCIPHER =========
db_path = os.path.join(os.path.dirname(__file__), 'inventario.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

DB_PASSWORD = "MiClaveSegura123"  # cámbiala

@event.listens_for(Engine, "connect")
def set_sqlcipher_key(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute(f"PRAGMA key='{DB_PASSWORD}';")
    cursor.close()

# ========= MODELOS =========
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Equipo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_equipo = db.Column(db.String(100), nullable=False)
    responsable = db.Column(db.String(100))
    sistema_operativo = db.Column(db.String(100))
    office = db.Column(db.String(100))
    area_asignada = db.Column(db.String(100))
    tipo = db.Column(db.String(50))
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    numero_serie = db.Column(db.String(100), unique=True)
    disco_duro = db.Column(db.String(100))
    mac_address = db.Column(db.String(50))
    ip_address = db.Column(db.String(50))
    comentarios = db.Column(db.Text)
    estado = db.Column(db.String(50), default='uso')

# ========= RUTAS PRINCIPALES =========
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    equipos = Equipo.query.all()
    return render_template('index.html', equipos=equipos)

# --------- CREAR ----------
@app.route('/crear', methods=['GET', 'POST'])
def crear():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        nuevo = Equipo(
            nombre_equipo=request.form['nombre_equipo'],
            responsable=request.form['responsable'],
            sistema_operativo=request.form['sistema_operativo'],
            office=request.form['office'],
            area_asignada=request.form['area_asignada'],
            tipo=request.form['tipo'],
            marca=request.form['marca'],
            modelo=request.form['modelo'],
            numero_serie=request.form['numero_serie'],
            disco_duro=request.form['disco_duro'],
            mac_address=request.form['mac_address'],
            ip_address=request.form['ip_address'],
            comentarios=request.form['comentarios'],
            estado=request.form['estado']
        )
        db.session.add(nuevo)
        db.session.commit()
        flash('Equipo agregado correctamente', 'success')
        return redirect(url_for('index'))
    return render_template('crear.html')

# --------- EDITAR ----------
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    equipo = Equipo.query.get_or_404(id)
    if request.method == 'POST':
        equipo.nombre_equipo = request.form['nombre_equipo']
        equipo.responsable = request.form['responsable']
        equipo.sistema_operativo = request.form['sistema_operativo']
        equipo.office = request.form['office']
        equipo.area_asignada = request.form['area_asignada']
        equipo.tipo = request.form['tipo']
        equipo.marca = request.form['marca']
        equipo.modelo = request.form['modelo']
        equipo.numero_serie = request.form['numero_serie']
        equipo.disco_duro = request.form['disco_duro']
        equipo.mac_address = request.form['mac_address']
        equipo.ip_address = request.form['ip_address']
        equipo.comentarios = request.form['comentarios']
        equipo.estado = request.form['estado']
        db.session.commit()
        flash('Equipo actualizado correctamente', 'success')
        return redirect(url_for('index'))
    return render_template('editar.html', equipo=equipo)

# --------- ELIMINAR ----------
@app.route('/eliminar/<int:id>')
def eliminar(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    equipo = Equipo.query.get_or_404(id)
    db.session.delete(equipo)
    db.session.commit()
    flash('Equipo eliminado', 'info')
    return redirect(url_for('index'))

# --------- GENERAR RESPONSIVA PDF ----------
@app.route('/responsiva/<int:id>')
def responsiva(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    equipo = Equipo.query.get_or_404(id)
    doc = DocxTemplate("CARTAS_RESGUARDO_PLANTILLA.docx")
    context = {
        "fecha": datetime.now().strftime("%A, %d de %B de %Y"),
        "marca": equipo.marca,
        "modelo": equipo.modelo,
        "numero_serie": equipo.numero_serie,
        "sistema_operativo": equipo.sistema_operativo,
        "office": equipo.office,
        "responsable": equipo.responsable.upper() if equipo.responsable else "SIN ASIGNAR"
    }
    doc.render(context)
    temp_docx = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(temp_docx.name)

    # Convertir a PDF con Word/Pages
    pdf_path = temp_docx.name.replace(".docx", ".pdf")
    convert(temp_docx.name, pdf_path)
    return send_file(pdf_path, as_attachment=True, download_name=f"Responsiva_{equipo.nombre_equipo}.pdf")

# --------- LOGIN / REGISTRO ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        nuevo = Usuario(nombre=nombre, correo=correo, password=password)
        db.session.add(nuevo)
        db.session.commit()
        flash('Cuenta creada, inicia sesión', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']
        user = Usuario.query.filter_by(correo=correo).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Bienvenido', 'success')
            return redirect(url_for('index'))
        flash('Credenciales inválidas', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))

# ========= INICIO =========
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
