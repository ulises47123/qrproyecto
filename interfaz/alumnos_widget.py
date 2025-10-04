# interfaz/alumnos_widget.py

import sys
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QColorDialog, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

# Añade la raíz del proyecto al PATH para las importaciones (necesario si se ejecuta solo)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

from modulos.alumnos import create_student
# Importamos también el modelo Attendance para eliminar registros relacionados
from modulos.utilidades import Session, Student, MAIN_EXPORT_FOLDER, Attendance 

class AlumnosWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_color = QColor(128, 0, 128) # Morado por defecto (HEX: 800080)
        
        self.main_layout = QHBoxLayout(self)
        
        self.setup_creation_form()
        self.setup_student_list()
        
        # Cargar los datos iniciales al arrancar
        self.load_students()

    # -----------------------------------------------------------------
    # PARTE IZQUIERDA: FORMULARIO DE CREACIÓN
    # -----------------------------------------------------------------

    def setup_creation_form(self):
        form_widget = QWidget()
        form_widget.setFixedWidth(350)
        
        form_layout = QVBoxLayout(form_widget)
        
        # Título
        form_layout.addWidget(QLabel("<h2>Registrar Nuevo Alumno</h2>"))

        # Campos de entrada
        self.field_matricula = QLineEdit()
        self.field_nombre = QLineEdit()
        self.field_apellido = QLineEdit()
        self.field_curso = QLineEdit()
        
        # Botón para seleccionar color
        self.btn_color = QPushButton("Color QR (Morado)")
        self.btn_color.clicked.connect(self.select_qr_color)
        
        # Botón principal
        self.btn_register = QPushButton("Registrar Alumno y Generar QR")
        self.btn_register.setStyleSheet("background-color: #6a0dad;") # Morado más fuerte
        self.btn_register.clicked.connect(self.register_new_student)

        # Organización de campos en un QFormLayout
        layout = QFormLayout()
        layout.addRow("Matrícula:", self.field_matricula)
        layout.addRow("Nombre:", self.field_nombre)
        layout.addRow("Apellido:", self.field_apellido)
        layout.addRow("Curso:", self.field_curso)
        layout.addRow("Color QR:", self.btn_color)
        
        form_layout.addLayout(layout)
        form_layout.addWidget(self.btn_register)
        form_layout.addStretch(1) # Rellena el espacio
        
        self.main_layout.addWidget(form_widget)

    def select_qr_color(self):
        # Abre el diálogo de selección de color
        color = QColorDialog.getColor(self.selected_color, self, "Seleccionar Color del QR")
        if color.isValid():
            self.selected_color = color
            # Actualizar el texto del botón con el nuevo color HEX
            hex_color = self.selected_color.name()[1:].upper()
            self.btn_color.setText(f"Color QR ({hex_color})")
            # Aplicar color al botón (para visualización)
            self.btn_color.setStyleSheet(f"background-color: #{hex_color}; color: #1e1e2e;")

    def register_new_student(self):
        # 1. Obtener datos y validar
        matricula = self.field_matricula.text().strip()
        nombre = self.field_nombre.text().strip()
        apellido = self.field_apellido.text().strip()
        curso = self.field_curso.text().strip()
        color_hex = self.selected_color.name()[1:]

        if not matricula or not nombre or not apellido:
            QMessageBox.warning(self, "Error de Datos", "Los campos Matrícula, Nombre y Apellido no pueden estar vacíos.")
            return

        # 2. Llamar a la lógica de creación (módulo alumnos.py)
        new_student = create_student(nombre, apellido, matricula, curso, color_hex)

        if new_student:
            QMessageBox.information(self, "Registro Exitoso", 
                                    f"Alumno {nombre} {apellido} registrado. QR guardado en la carpeta 'datos QR'.")
            self.clear_fields()
            self.load_students() # Recargar la tabla
        else:
            # El error ya fue impreso en consola por create_student (ej: matrícula duplicada)
            QMessageBox.critical(self, "Error de Registro", 
                                 "No se pudo registrar al alumno. Verifique que la matrícula no esté duplicada.")

    def clear_fields(self):
        self.field_matricula.clear()
        self.field_nombre.clear()
        self.field_apellido.clear()
        self.field_curso.clear()
        self.selected_color = QColor(128, 0, 128)
        self.btn_color.setText("Color QR (Morado)")
        self.btn_color.setStyleSheet("background-color: #6a0dad;")


    # -----------------------------------------------------------------
    # PARTE DERECHA: TABLA Y GESTIÓN DE ALUMNOS (Leer y Eliminar)
    # -----------------------------------------------------------------

    def setup_student_list(self):
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        
        list_layout.addWidget(QLabel("<h2>Alumnos Registrados</h2>"))
        
        # Tabla
        self.student_table = QTableWidget()
        self.student_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # <--- DESHABILITA LA EDICIÓN
        self.student_table.setColumnCount(4)
        self.student_table.setHorizontalHeaderLabels(["Matrícula", "Nombre", "Curso", "Registrado"])
        self.student_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        list_layout.addWidget(self.student_table)
        
        # Controles de la lista (refrescar/exportar/eliminar)
        control_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Refrescar Lista")
        self.btn_refresh.clicked.connect(self.load_students)
        
        self.btn_export_qr = QPushButton("Descargar QR Seleccionado")
        self.btn_export_qr.setEnabled(False) # Se activa al seleccionar fila
        
        # Botón de Eliminar
        self.btn_delete = QPushButton("Eliminar Alumno")
        self.btn_delete.setStyleSheet("background-color: #f38ba8;") # Color de eliminación
        self.btn_delete.setEnabled(False) 

        # Conectar señales para habilitar/deshabilitar botones al seleccionar fila
        def enable_row_buttons():
            is_row_selected = len(self.student_table.selectedItems()) > 0
            self.btn_export_qr.setEnabled(is_row_selected)
            self.btn_delete.setEnabled(is_row_selected)

        self.student_table.itemSelectionChanged.connect(enable_row_buttons)
        self.btn_delete.clicked.connect(self.delete_selected_student) # Conexión a la nueva función
        
        control_layout.addWidget(self.btn_refresh)
        control_layout.addWidget(self.btn_export_qr)
        control_layout.addWidget(self.btn_delete)
        
        list_layout.addLayout(control_layout)
        
        self.main_layout.addWidget(list_widget, 1) # Toma el resto del espacio

    def load_students(self):
        """Carga todos los alumnos de la base de datos en la tabla."""
        session = Session()
        students = session.query(Student).all()
        session.close()

        self.student_table.setRowCount(len(students))
        
        for row, student in enumerate(students):
            # Matrícula
            self.student_table.setItem(row, 0, QTableWidgetItem(student.matricula))
            # Nombre completo
            self.student_table.setItem(row, 1, QTableWidgetItem(f"{student.first_name} {student.last_name}"))
            # Curso
            self.student_table.setItem(row, 2, QTableWidgetItem(student.course or "N/A"))
            # Fecha de Registro
            self.student_table.setItem(row, 3, QTableWidgetItem(student.registered_on.strftime("%Y-%m-%d")))

    def delete_selected_student(self):
        """Elimina al alumno seleccionado y sus registros de asistencia."""
        selected_rows = self.student_table.selectedIndexes()
        
        if not selected_rows:
            QMessageBox.warning(self, "Selección", "Debe seleccionar un alumno para eliminar.")
            return

        # Obtenemos la matrícula de la fila seleccionada (columna 0)
        row_index = selected_rows[0].row()
        matricula = self.student_table.item(row_index, 0).text()
        nombre = self.student_table.item(row_index, 1).text()

        # Preguntar confirmación
        reply = QMessageBox.question(self, 'Confirmar Eliminación',
            f"¿Está seguro de que desea eliminar al alumno:\n{nombre} ({matricula})?\n\nEsta acción eliminará también sus registros de asistencia y es irreversible.", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            session = Session()
            try:
                # 1. Eliminar asistencias relacionadas primero
                session.query(Attendance).filter(Attendance.matricula == matricula).delete(synchronize_session=False) 
                
                # 2. Eliminar al alumno
                student = session.query(Student).filter(Student.matricula == matricula).one()
                session.delete(student)
                
                session.commit()
                QMessageBox.information(self, "Eliminación Exitosa", f"Alumno {nombre} eliminado correctamente.")
                self.load_students() # Recargar la tabla
                
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Error de DB", f"No se pudo eliminar al alumno. Error: {e}")
            finally:
                session.close()

# --- Prueba del Módulo (Opcional, pero no necesario si se integra directamente) ---
if __name__ == '__main__':
    print("Este módulo debe ser integrado en interfaz/principal.py")