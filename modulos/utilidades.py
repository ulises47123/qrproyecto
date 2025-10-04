# modulos/utilidades.py

import os
# Eliminamos import sqlite3, ya que SQLAlchemy lo maneja internamente
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, Text, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# --- Configuración de Rutas ---

# Carpeta principal del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
# Ruta a la DB: 'base_datos/asistencia.db'
DB_PATH = PROJECT_ROOT / "base_datos" / "asistencia.db"

def get_desktop_folder():
    """Busca y devuelve la ruta al Escritorio en sistemas Linux/Windows."""
    # En Linux, suele ser ~/Escritorio
    desktop = Path.home() / 'Escritorio' 
    # Si no existe, usa el HOME del usuario
    if not desktop.is_dir():
        desktop = Path.home()
    
    return desktop

# Carpeta de guardado obligatorio en el Escritorio: 'datos QR'
MAIN_EXPORT_FOLDER = get_desktop_folder() / 'datos QR'

# --- Configuración de Base de Datos (SQLAlchemy) ---

# Crea el directorio si no existe (importante antes de conectar)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Define el motor de la base de datos
engine = create_engine(f"sqlite:///{DB_PATH}")
# Clase base para la definición de tablas (ORM)
Base = declarative_base()
# Generador de sesiones (para interactuar con la DB)
Session = sessionmaker(bind=engine)

# --- Definición de Modelos (students y asistencias) ---

class Student(Base):
    """Modelo ORM para la tabla students"""
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    matricula = Column(Text, unique=True, nullable=False)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    course = Column(Text)
    photo_path = Column(Text)
    qr_data = Column(Text, nullable=False)
    qr_color = Column(Text)
    registered_on = Column(DateTime, default=datetime.now)
    active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Student(matricula='{self.matricula}', name='{self.first_name} {self.last_name}')>"

class Attendance(Base):
    """Modelo ORM para la tabla asistencias"""
    __tablename__ = 'asistencias'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, nullable=False) # ID del alumno (Clave foránea virtual)
    matricula = Column(Text, nullable=False) # Copia de la matrícula (para búsquedas rápidas)
    time_stamp = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Attendance(matricula='{self.matricula}', time='{self.time_stamp}')>"


def setup_database():
    """Crea todas las tablas definidas si no existen en la DB."""
    # Base.metadata.create_all(engine) crea *todas* las clases derivadas de Base (Student y Attendance).
    Base.metadata.create_all(engine)
    # Crea la carpeta principal de guardado si no existe en el Escritorio
    MAIN_EXPORT_FOLDER.mkdir(parents=True, exist_ok=True)
    print(f"Base de datos y carpetas de exportación configuradas.")
    print(f"DB creada en: {DB_PATH}")
    print(f"Carpeta 'datos QR' en: {MAIN_EXPORT_FOLDER}")


# Ejecutar la configuración al iniciar el módulo
if __name__ == '__main__':
    setup_database()