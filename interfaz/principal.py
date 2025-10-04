# interfaz/principal.py

import sys
# Importamos utilidades para configurar la DB
from modulos.utilidades import setup_database 
# Importamos el módulo de cámara
from modulos.camara import CameraStreamer, list_available_cameras
# Importamos la función de registro de asistencia (Prioridad 5)
from modulos.asistencia import register_attendance 
from interfaz.alumnos_widget import AlumnosWidget
from interfaz.reportes_widget import ReportesWidget # <--- IMPORTACIÓN AÑADIDA

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTabWidget, QPushButton, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QImage, QPixmap

# Conversión de imagen (Necesario para pasar de OpenCV a PyQt6)
import cv2 

# Colores y estilos (Mantenemos el mismo STYLE_SHEET)
STYLE_SHEET = """
    /* Fondo principal y barra de título */
    QMainWindow, QWidget {
        background-color: #1e1e2e; /* Dark Dracula/VSCode-like */
        color: #cdd6f4; /* Texto claro */
    }
    
    /* Pestañas (TabWidget) */
    QTabWidget::pane { 
        border: 1px solid #58586c; 
        background-color: #1e1e2e;
    }
    QTabBar::tab {
        background: #313244; /* Fondo de pestaña inactiva */
        color: #cdd6f4;
        padding: 10px;
        min-width: 100px;
    }
    QTabBar::tab:selected {
        background: #58586c; /* Fondo de pestaña activa */
        border-bottom: 2px solid #b794f9; /* Acento morado/pastel */
    }
    
    /* Botones de acción */
    QPushButton {
        background-color: #b794f9; 
        color: #1e1e2e;
        border: none;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    
    /* Labels grandes para la cámara */
    QLabel#CameraFeed {
        border: 2px dashed #b794f9; 
        background-color: #313244;
    }
"""

class CameraWidget(QWidget):
    """Widget que contiene la vista de la cámara y los controles."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.camera_streamer = None
        self.current_camera_id = -1
        
        self.setup_ui()
        self.setup_camera()

    def setup_ui(self):
        # Layout principal de la pestaña de asistencia
        main_layout = QHBoxLayout(self)
        
        # Panel Izquierdo: Visualización de la Cámara (70% del ancho)
        self.camera_feed = QLabel("Iniciando Cámara...")
        self.camera_feed.setObjectName("CameraFeed")
        self.camera_feed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_feed.setFixedSize(640, 480) # Tamaño estándar para la vista de la cámara
        main_layout.addWidget(self.camera_feed, 70) # 70% de espacio
        
        # Panel Derecho: Controles y Registro (30% del ancho)
        control_panel = QVBoxLayout()
        
        # Selección de Cámara
        control_panel.addWidget(QLabel("Seleccionar Cámara:"))
        self.camera_selector = QComboBox()
        control_panel.addWidget(self.camera_selector)
        
        # Botones
        self.btn_start = QPushButton("Iniciar Asistencia")
        self.btn_stop = QPushButton("Detener Asistencia")
        self.btn_stop.setEnabled(False) # Deshabilitado al inicio
        
        control_panel.addWidget(self.btn_start)
        control_panel.addWidget(self.btn_stop)
        
        # Área de Información / Registro
        control_panel.addStretch(1) # Espacio flexible
        control_panel.addWidget(QLabel("Último Registro:"))
        self.last_registration_label = QLabel("Esperando escaneo...")
        control_panel.addWidget(self.last_registration_label)
        control_panel.addStretch(2)
        
        main_layout.addLayout(control_panel, 30) # 30% de espacio

    def setup_camera(self):
        # 1. Listar cámaras disponibles
        cameras = list_available_cameras()
        if not cameras:
            self.camera_feed.setText("❌ No se detectaron cámaras.")
            self.btn_start.setEnabled(False)
            return

        # 2. Llenar el ComboBox
        for cam_id in cameras:
            self.camera_selector.addItem(f"Cámara ID {cam_id}", cam_id)
        
        # 3. Conexión de señales
        self.btn_start.clicked.connect(self.start_camera)
        self.btn_stop.clicked.connect(self.stop_camera)

    def start_camera(self):
        if self.camera_streamer and self.camera_streamer.running:
            return

        # Obtener el ID seleccionado
        self.current_camera_id = self.camera_selector.currentData()
        
        # Inicializar el streamer
        self.camera_streamer = CameraStreamer(camera_id=self.current_camera_id)
        
        # Conectar las señales del hilo a los slots de la GUI
        self.camera_streamer.frame_ready.connect(self.update_frame)
        self.camera_streamer.qr_detected.connect(self.handle_qr_scan)
        
        self.camera_streamer.start()
        
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.camera_feed.setText("Cámara activa...")

    def stop_camera(self):
        if self.camera_streamer:
            self.camera_streamer.stop()
            self.camera_streamer = None
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.camera_feed.setText("Cámara detenida.")
            self.camera_feed.clear() # Limpiar el feed
            
    def update_frame(self, frame):
        """Convierte el frame de OpenCV a QPixmap para mostrar en el QLabel."""
        try:
            # OpenCV usa BGR; debemos convertirlo a RGB para QImage
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            
            # Crear QImage
            convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            # Escalar y mostrar
            p = QPixmap.fromImage(convert_to_Qt_format)
            self.camera_feed.setPixmap(p.scaled(self.camera_feed.size(), 
                                               Qt.AspectRatioMode.KeepAspectRatio, 
                                               Qt.TransformationMode.SmoothTransformation))
        except Exception as e:
            print(f"Error al actualizar frame: {e}")

    def handle_qr_scan(self, qr_data):
        """Maneja el dato del QR escaneado (matrícula) y registra la asistencia."""
        # 1. Pausamos el stream para evitar re-scaneo inmediato
        if self.camera_streamer:
            self.camera_streamer.pause()
        
        # 2. Llamar a la lógica de asistencia (Prioridad 5)
        result = register_attendance(qr_data)
        
        # 3. Actualizar la etiqueta y el feedback al usuario
        self.last_registration_label.setText(f"{result['message']}")
        
        # 4. Establecer el color del mensaje según el estado
        color_map = {
            "success": "lime",   # Verde
            "warning": "yellow", # Amarillo
            "error": "red"       # Rojo
        }
        status_color = color_map.get(result['status'], "white")
        self.last_registration_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")

        # 5. Reanudar el stream después de 3 segundos
        QTimer.singleShot(3000, self.resume_camera_after_scan)


    def resume_camera_after_scan(self):
        if self.camera_streamer:
            self.camera_streamer.resume()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PROYECTIS - Asistencia Docente QR")
        self.setMinimumSize(QSize(900, 600))
        self.setStyleSheet(STYLE_SHEET)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Configuración de DB al inicio de la aplicación
        setup_database()

        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Arial", 10))
        
        # 1. Dashboard (PUNTO B APLICADO)
        self.tab_dashboard = ReportesWidget() # <-- WIDGET DE REPORTES INTEGRADO
        
        # 2. Gestión de Alumnos 
        self.tab_alumnos = AlumnosWidget() # <-- WIDGET DE ALUMNOS INTEGRADO
        
        # 3. Pestaña de Asistencia
        self.tab_asistencia = CameraWidget() 
        
        self.tabs.addTab(self.tab_dashboard, "Inicio / Dashboard")
        self.tabs.addTab(self.tab_alumnos, "Gestión de Alumnos")
        self.tabs.addTab(self.tab_asistencia, "Registro de Asistencia") 
        
        self.main_layout.addWidget(self.tabs)
        
        # Aseguramos que la cámara se detenga al cerrar la aplicación
        QApplication.instance().aboutToQuit.connect(self.cleanup_camera)

    def cleanup_camera(self):
        """Detiene la cámara al cerrar la ventana."""
        self.tab_asistencia.stop_camera()


def run_gui():
    """Inicializa la aplicación y la ventana principal."""
    app = QApplication(sys.argv)
    app.setPalette(app.style().standardPalette()) 
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    run_gui()