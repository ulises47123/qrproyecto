# modulos/reportes.py

import sys
import os
import pandas as pd
from datetime import datetime

# Ajuste de PATH para importar módulos del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

from modulos.utilidades import Session, Student, Attendance, MAIN_EXPORT_FOLDER

# Asegúrate de que pandas esté instalado: pip install pandas

def get_attendance_data() -> pd.DataFrame:
    """
    Obtiene todos los registros de asistencia y los combina con los datos del alumno.
    
    Returns:
        pd.DataFrame: DataFrame con la asistencia y detalles del alumno.
    """
    session = Session()
    try:
        # Consulta para obtener todos los registros de asistencia
        attendance_records = session.query(Attendance).all()
        
        # Convertir los resultados en una lista de diccionarios
        data = []
        for record in attendance_records:
            # Obtener el alumno usando el matricula del registro (eficiente)
            student = session.query(Student).filter(Student.matricula == record.matricula).one_or_none()
            
            if student:
                data.append({
                    'ID_Asistencia': record.id,
                    'Matrícula': record.matricula,
                    'Nombre': student.first_name,
                    'Apellido': student.last_name,
                    'Curso': student.course,
                    'Fecha': record.time_stamp.strftime('%Y-%m-%d'),
                    'Hora': record.time_stamp.strftime('%H:%M:%S')
                })
        
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error al obtener datos de asistencia: {e}")
        return pd.DataFrame()
    finally:
        session.close()

def export_attendance_to_csv(df: pd.DataFrame, filename_suffix: str = "reporte") -> str:
    """
    Exporta un DataFrame de asistencia a un archivo CSV en la carpeta de exportación.
    
    Args:
        df (pd.DataFrame): DataFrame a exportar.
        filename_suffix (str): Sufijo para el nombre del archivo.
        
    Returns:
        str: Ruta completa donde se guardó el archivo o mensaje de error.
    """
    if df.empty:
        return "Error: DataFrame vacío. No hay datos para exportar."

    # 1. Crear la carpeta con la fecha de hoy dentro de 'datos QR'
    today_folder = MAIN_EXPORT_FOLDER / datetime.now().strftime('%Y-%m-%d')
    today_folder.mkdir(parents=True, exist_ok=True)
    
    # 2. Generar nombre de archivo único
    timestamp = datetime.now().strftime('%H%M%S')
    filename = f"{filename_suffix}_{timestamp}.csv"
    file_path = today_folder / filename

    try:
        # 3. Guardar el archivo CSV
        df.to_csv(file_path, index=False, encoding='utf-8')
        return str(file_path)
    except Exception as e:
        return f"Error al exportar CSV: {e}"

# --- PRUEBA DE FUNCIONALIDAD ---
if __name__ == '__main__':
    print("--- Prueba de Reportes ---")
    
    # 1. Obtener los datos
    df_reporte = get_attendance_data()
    print(f"Registros de asistencia encontrados: {len(df_reporte)}")
    
    if not df_reporte.empty:
        # 2. Exportar
        export_result = export_attendance_to_csv(df_reporte, "asistencia_general")
        print(f"Resultado de la exportación: {export_result}")
    else:
        print("No hay registros de asistencia en la base de datos para exportar.")