# modulos/alumnos.py

import sys
import os
# Añade el directorio padre (Proyecto_Asistencia_QR) al PATH para las importaciones
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

from modulos.utilidades import Session, Student, MAIN_EXPORT_FOLDER
# ... el resto del código ...

# modulos/alumnos.py

from modulos.utilidades import Session, Student, MAIN_EXPORT_FOLDER
from datetime import datetime
import qrcode
from PIL import Image
from pathlib import Path

# --- Configuración de Carpetas de QR ---
QR_FOLDER = MAIN_EXPORT_FOLDER / 'QR'
QR_FOLDER.mkdir(parents=True, exist_ok=True) # Asegura que la subcarpeta QR exista

def generate_qr_code(qr_data: str, matricula: str, qr_color: str = '000000') -> str:
    """
    Genera un QR, lo guarda como PNG y devuelve la ruta del archivo.
    
    Args:
        qr_data (str): El string único a codificar (generalmente la matrícula).
        matricula (str): La matrícula para nombrar el archivo.
        qr_color (str): Color HEX del QR (por defecto negro).
        
    Returns:
        str: La ruta completa donde se guardó el archivo PNG.
    """
    try:
        # Convertir color HEX a tupla RGB si es necesario (para Pillow)
        fill_color = tuple(int(qr_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Crear el objeto QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # Crear imagen con color opcional [cite: 15]
        img = qr.make_image(fill_color=fill_color, back_color="white").convert('RGB')
        
        # Nombre del archivo: student_<matricula>.png [cite: 71, 130]
        file_name = f"student_{matricula}.png"
        save_path = QR_FOLDER / file_name
        
        img.save(save_path)
        return str(save_path)
        
    except Exception as e:
        print(f"Error al generar QR para {matricula}: {e}")
        return ""


def create_student(first_name: str, last_name: str, matricula: str, course: str, qr_color: str = '000000') -> Student or None:
    """
    Crea un nuevo alumno, genera su QR y lo registra en la base de datos.
    
    Args:
        first_name (str), last_name (str), matricula (str), course (str), qr_color (str)
        
    Returns:
        Student: El objeto Student si fue creado exitosamente, None en caso contrario.
    """
    session = Session()
    try:
        # 1. Usar la matrícula como el dato QR único [cite: 94]
        qr_data = matricula
        
        # 2. Generar y guardar el archivo QR
        qr_path = generate_qr_code(qr_data, matricula, qr_color)
        
        if not qr_path:
             # Si falla la generación del QR, cancelamos
            return None

        # 3. Crear el nuevo objeto Student
        new_student = Student(
            first_name=first_name,
            last_name=last_name,
            matricula=matricula,
            course=course,
            qr_data=qr_data,
            qr_color=qr_color,
            photo_path="", # Opcional, por ahora vacío
            active=True,
            registered_on=datetime.now()
        )
        
        # 4. Agregar a la sesión y hacer commit (guardar) [cite: 101]
        session.add(new_student)
        session.commit()
        
        return new_student
        
    except Exception as e:
        session.rollback()
        # Verificar si el error es por matrícula duplicada (UNIQUE constraint)
        if "UNIQUE constraint failed" in str(e):
            print(f"Error: La matrícula {matricula} ya está registrada.")
        else:
            print(f"Error desconocido al crear alumno: {e}")
        return None
        
    finally:
        session.close()

# --- Función de prueba (Simulación del flujo 1) ---
if __name__ == '__main__':
    print("--- Prueba de Creación de Alumno y QR (Flujo 1) ---")
    
    # Datos de prueba
    nombre = "Juan"
    apellido = "Pérez"
    mat = "2025001"
    curso = "Matemáticas I"
    color = "800080" # Morado (ajustando al tema preferido) [cite: 2]
    
    alumno_creado = create_student(nombre, apellido, mat, curso, color)
    
    if alumno_creado:
        print(f"\n✅ Alumno creado exitosamente:")
        print(f"   Nombre: {alumno_creado.first_name} {alumno_creado.last_name}")
        print(f"   Matrícula: {alumno_creado.matricula}")
        print(f"   QR guardado en: {QR_FOLDER}/student_{mat}.png")
        
        # Intentar crear el mismo alumno (debe fallar)
        print("\n--- Intento de duplicado ---")
        duplicado = create_student(nombre, apellido, mat, curso, color)
        if duplicado is None:
            print("❌ Prueba de duplicado exitosa: No se permitió registrar la misma matrícula.")
    else:
        print("\n❌ Error al crear alumno de prueba.")