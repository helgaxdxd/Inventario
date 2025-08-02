from app import db

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
