from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class MaquinasCerveceria(db.Model):
    __tablename__ = 'Maquinas_Cerveceria'
    
    id = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    tipo_maquina = db.Column(db.String(50))
    frec_manteni = db.Column(db.String(50))
    temp_mini = db.Column(db.Float)
    temp_maxi = db.Column(db.Float)
    uso_operativo = db.Column(db.Float)
    presion_max = db.Column(db.Float)
    criticidad = db.Column(db.String(50))
    
    # Relaciones
    ejercicios = db.relationship('Ejercicio', backref='maquina', lazy=True)
    simulaciones = db.relationship('SimulacionEstado', backref='linea', lazy=True)

class Usuario(db.Model):
    __tablename__ = 'Usuario'
    
    id_usuario = db.Column(db.BigInteger, primary_key=True)
    Nombre = db.Column(db.String(100))
    ApelP_pater = db.Column(db.String(100))
    ApelP_mater = db.Column(db.String(100))
    Rol = db.Column(db.String(50))
    Usuario = db.Column(db.String(50))
    Password = db.Column(db.String(100))
    
    # Relaciones
    ejercicios = db.relationship('Ejercicio', backref='usuario', lazy=True)
    simulaciones = db.relationship('SimulacionEstado', backref='usuario', lazy=True)

class Ejercicio(db.Model):
    __tablename__ = 'Ejercicio'
    
    id = db.Column(db.BigInteger, primary_key=True)
    id_usuario = db.Column(db.BigInteger, db.ForeignKey('Usuario.id_usuario'))
    id_maquina = db.Column(db.BigInteger, db.ForeignKey('Maquinas_Cerveceria.id'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    matriz_estados = db.Column(db.Text)  # Almacenado como JSON o serializado
    vector_inicial = db.Column(db.Text)  # Almacenado como JSON o serializado

class SimulacionEstado(db.Model):
    __tablename__ = 'Simulacion_estado'
    
    id_simulacion = db.Column(db.BigInteger, primary_key=True)
    linea_id = db.Column(db.BigInteger, db.ForeignKey('Maquinas_Cerveceria.id'))
    usuario_id = db.Column(db.BigInteger, db.ForeignKey('Usuario.id_usuario'))
    Fecha = db.Column(db.DateTime, default=datetime.utcnow)
    Acc_IA = db.Column(db.String(100))
    Acc_humana = db.Column(db.String(100))
    Acc_final = db.Column(db.String(100))
    Intervenido = db.Column(db.Boolean)
    Temperatura = db.Column(db.Float)
    Presion = db.Column(db.Float)
    Uso = db.Column(db.Float)
    Recompensa = db.Column(db.Float)
    Comentario = db.Column(db.Text)
    vibracion = db.Column(db.Float)
