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
    criticidad = db.Column(db.String(20))
    
    # Relaciones
    productos = db.relationship('ProductoCerveza', backref='maquina', lazy=True)
    predicciones = db.relationship('PrediceEstado', backref='linea', lazy=True)
    simulaciones = db.relationship('SimulacionEstado', backref='linea', lazy=True)

class ProductoCerveza(db.Model):
    __tablename__ = 'Producto_Cerveza'
    
    id_producto = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.String(100))
    tipo_cerveza = db.Column(db.String(50))
    volumen = db.Column(db.Float)
    envase = db.Column(db.String(50))
    maquina_id = db.Column(db.BigInteger, db.ForeignKey('Maquinas_Cerveceria.id'))
    
    # Relaciones
    insumos = db.relationship('InsumosCerveza', backref='producto', lazy=True)

class InsumosCerveza(db.Model):
    __tablename__ = 'Insumos_Cerveza'
    
    id_insumo = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.String(100))
    tipo = db.Column(db.String(50))
    producto_id = db.Column(db.BigInteger, db.ForeignKey('Producto_Cerveza.id_producto'))

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
    predicciones = db.relationship('PrediceEstado', backref='usuario', lazy=True)
    simulaciones = db.relationship('SimulacionEstado', backref='usuario', lazy=True)

class PrediceEstado(db.Model):
    __tablename__ = 'Predice_Estado'
    
    id_predice = db.Column(db.BigInteger, primary_key=True)
    id_usuario = db.Column(db.BigInteger, db.ForeignKey('Usuario.id_usuario'))
    id_linea = db.Column(db.BigInteger, db.ForeignKey('Maquinas_Cerveceria.id'))
    Estado_espe = db.Column(db.String(50))
    Estado_calcu = db.Column(db.String(50))
    EstadoCual = db.Column(db.Float)

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
