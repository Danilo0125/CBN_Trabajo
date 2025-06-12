from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class MaquinasCerveceria(db.Model):
    __tablename__ = 'Maquinas_Cerveceria'
    
    id = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    tipo_maquina = db.Column(db.String(50))
    frec_manteni = db.Column(db.String(50))
    
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
    matriz_estados = db.Column(db.Text)  # Almacenado como JSON
    vector_inicial = db.Column(db.Text)  # Almacenado como JSON
    num_pasos = db.Column(db.Integer, default=5)
    resultado = db.Column(db.Text)  # Almacenado como JSON
    nombres_estados = db.Column(db.Text)  # Almacenado como JSON - nombres de los 4 estados
    descripcion = db.Column(db.Text)
    
    def set_matriz_estados(self, matriz):
        """Convierte la matriz a formato JSON para almacenamiento"""
        self.matriz_estados = json.dumps(matriz)
    
    def get_matriz_estados(self):
        """Convierte el JSON almacenado a matriz"""
        return json.loads(self.matriz_estados) if self.matriz_estados else None
    
    def set_vector_inicial(self, vector):
        """Convierte el vector a formato JSON para almacenamiento"""
        self.vector_inicial = json.dumps(vector)
    
    def get_vector_inicial(self):
        """Convierte el JSON almacenado a vector"""
        return json.loads(self.vector_inicial) if self.vector_inicial else None
    
    def set_resultado(self, resultado):
        """Convierte el resultado a formato JSON para almacenamiento"""
        self.resultado = json.dumps(resultado)
    
    def get_resultado(self):
        """Convierte el JSON almacenado a resultado"""
        return json.loads(self.resultado) if self.resultado else None
    
    def set_nombres_estados(self, nombres):
        """Convierte los nombres de estados a formato JSON para almacenamiento"""
        self.nombres_estados = json.dumps(nombres)
    
    def get_nombres_estados(self):
        """Convierte el JSON almacenado a nombres de estados"""
        return json.loads(self.nombres_estados) if self.nombres_estados else None

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
