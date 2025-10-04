# interfaz/reportes_widget.py

import sys
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QFileDialog
from PyQt6.QtCore import Qt

# Ajuste de PATH para importar módulos del proyecto (necesario si se ejecuta solo)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

from modulos.reportes import get_attendance_data, export_attendance_to_csv

class ReportesWidget(QWidget):
    """Widget para la generación y exportación de reportes de asistencia."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(QLabel("<h2>Generación de Reportes</h2>"))
        main_layout.addWidget(QLabel("Haz clic para generar un archivo CSV con el registro histórico de todas las asistencias."))
        
        self.btn_generate = QPushButton("Generar Reporte General de Asistencia")
        # Estilo para destacar el botón de exportación
        self.btn_generate.setStyleSheet("background-color: #8be9fd; color: #1e1e2e; font-size: 14pt; padding: 15px; font-weight: bold;") 
        self.btn_generate.clicked.connect(self.generate_report)
        
        main_layout.addWidget(self.btn_generate)
        main_layout.addStretch(1)

    def generate_report(self):
        # 1. Obtener datos
        df = get_attendance_data()
        
        if df.empty:
            QMessageBox.warning(self, "Sin Datos", "No hay registros de asistencia en la base de datos para generar el reporte.")
            return

        # 2. Exportar a CSV
        export_result_path = export_attendance_to_csv(df, "asistencia_historico")
        
        if export_result_path.startswith("Error"):
            QMessageBox.critical(self, "Error de Exportación", f"Ocurrió un error al guardar el archivo:\n{export_result_path}")
        else:
            # Mostrar mensaje de éxito y ofrecer abrir la carpeta
            reply = QMessageBox.information(
                self, 
                "Reporte Generado", 
                f"✅ Reporte guardado con éxito.\n\nRuta: {export_result_path}",
                QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Ok
            )
            
            if reply == QMessageBox.StandardButton.Open:
                # Intento de abrir la carpeta contenedora (solo el directorio con la fecha)
                import os
                try:
                    report_dir = os.path.dirname(export_result_path)
                    # En sistemas Linux, usamos la llamada al comando "xdg-open" para abrir archivos/carpetas
                    os.system(f'xdg-open "{report_dir}"')
                except Exception:
                    # Fallback si el comando falla
                    QMessageBox.warning(self, "Abrir Carpeta", 
                                        "No se pudo abrir automáticamente la carpeta. La ruta es:\n" + os.path.dirname(export_result_path))