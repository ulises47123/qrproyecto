# modulos/asistencia.py

import sys
import os
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound

from sqlalchemy import Text 
# --- SOLUCIÓN TEMPORAL PARA PRUEBAS ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 
# ---------------------------------------

from modulos.utilidades import Session, Student, Attendance

def register_attendance(matricula: str) -> dict:
    """
    Busca al alumno por matrícula y registra su asistencia si existe.
    """
    session = Session()
    try:
        # 1. Buscar al alumno por matrícula
        student = session.query(Student).filter(Student.matricula == matricula).one_or_none()

        if student is None:
            return {
                "status": "error",
                "message": f"❌ Matrícula no registrada: {matricula}",
                "data": None
            }
        
        # 2. Verificar si ya registró asistencia hoy (Prevención de Duplicados)
        today = datetime.now().date()
        
        # Filtra asistencias del alumno para el día de hoy
        recent_attendance = (
            session.query(Attendance)
            .filter(Attendance.matricula == matricula)
            # SQLAlchemy: Compara la parte de la fecha del time_stamp con la fecha de hoy
            .filter(Attendance.time_stamp.cast(Text).like(f"{today.isoformat()}%")) 
            .one_or_none()
        )

        if recent_attendance:
            return {
                "status": "warning",
                "message": f"⚠️ {student.first_name} {student.last_name} ya registró su asistencia hoy a las {recent_attendance.time_stamp.strftime('%H:%M:%S')}.",
                "data": student
            }

        # 3. Registrar la asistencia
        new_attendance = Attendance(
            student_id=student.id,
            matricula=matricula,
            time_stamp=datetime.now()
        )
        
        session.add(new_attendance)
        session.commit()

        return {
            "status": "success",
            "message": f"✅ Asistencia registrada para {student.first_name} {student.last_name} ({matricula}).",
            "data": student
        }

    except NoResultFound:
        return {
            "status": "error",
            "message": f"❌ Error de búsqueda en DB (NoResultFound)",
            "data": None
        }
    except Exception as e:
        session.rollback()
        return {
            "status": "error",
            "message": f"❌ Error de DB desconocido: {e}",
            "data": None
        }
    finally:
        session.close()


if __name__ == '__main__':
    print("--- Prueba de Registro de Asistencia (Matrícula Válida) ---")
    
    # Intento 1: Primera asistencia del día (Debe ser SUCCESS)
    result_valid = register_attendance("2025001")
    print(result_valid["message"])
    
    # Intento 2: Segunda asistencia del día (Debe ser WARNING)
    print("\n--- Prueba de Detección de Duplicados (Mismo día) ---")
    result_duplicate = register_attendance("2025001")
    print(result_duplicate["message"])

    # Intento 3: Matrícula Inválida (Debe ser ERROR)
    print("\n--- Prueba de Matrícula No Registrada ---")
    result_invalid = register_attendance("9999999")
    print(result_invalid["message"])