# modulos/camara.py

import cv2
from pyzbar.pyzbar import decode
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
import numpy as np

# Constantes
CAMERA_ID_DEFAULT = 0  # Cámara predeterminada

class CameraStreamer(QThread):
    """
    Clase que maneja el stream de la cámara en un hilo separado y emite 
    las imágenes de frame y los datos del QR detectado.
    """
    # Señales para comunicar con la GUI
    frame_ready = pyqtSignal(np.ndarray) # Envía el frame de video (imagen)
    qr_detected = pyqtSignal(str)       # Envía el contenido del QR detectado

    def __init__(self, camera_id=CAMERA_ID_DEFAULT, parent=None):
        super().__init__(parent)
        self.camera_id = camera_id
        self.running = False
        self.capture = None
        self.is_paused = False
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        
    def run(self):
        """Método que se ejecuta cuando se inicia el hilo."""
        self.running = True
        self.capture = cv2.VideoCapture(self.camera_id)

        if not self.capture.isOpened():
            print(f"Error: No se pudo abrir la cámara {self.camera_id}.")
            self.running = False
            return

        while self.running:
            # Lógica de pausa
            self.mutex.lock()
            if self.is_paused:
                self.condition.wait(self.mutex)
            self.mutex.unlock()
            
            # 1. Leer Frame
            ret, frame = self.capture.read()
            if not ret:
                print("Error: No se pudo leer el frame.")
                break
            
            # 2. Detección de QR
            decoded_objects = decode(frame)
            if decoded_objects:
                for obj in decoded_objects:
                    qr_data = obj.data.decode('utf-8')
                    # Emitir la señal de QR detectado
                    self.qr_detected.emit(qr_data)
                    
                    # Dibujar un recuadro verde alrededor del QR detectado
                    points = obj.polygon
                    if len(points) == 4:
                        pts = np.array(points, np.int32)
                        pts = pts.reshape((-1, 1, 2))
                        cv2.polylines(frame, [pts], True, (0, 255, 0), 3) # BGR: Verde
                        
            # 3. Emitir Frame para mostrar en la GUI
            self.frame_ready.emit(frame)

        # Liberar recursos al terminar
        if self.capture:
            self.capture.release()
        print(f"Stream de cámara {self.camera_id} detenido.")

    def stop(self):
        """Detiene el hilo del stream."""
        self.running = False
        self.condition.wakeAll() # Despierta el hilo si está en pausa
        self.wait() # Espera a que el hilo termine
        
    def pause(self):
        """Pausa el procesamiento de frames."""
        self.is_paused = True
        
    def resume(self):
        """Reanuda el procesamiento de frames."""
        self.is_paused = False
        self.condition.wakeAll()

# ----------------------------------------------------
# Función de Utilidad: Listar Cámaras
# ----------------------------------------------------
def list_available_cameras():
    """
    Intenta abrir varias cámaras para detectar cuáles están disponibles.
    
    Returns:
        list: Lista de IDs de cámaras disponibles (ej: [0, 1]).
    """
    available_cams = []
    # Generalmente se prueba hasta el ID 5, ya que pocas máquinas tienen más
    for i in range(5): 
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cams.append(i)
            cap.release()
            # print(f"Cámara detectada en ID: {i}") # Para debug
        
    return available_cams

# --- Prueba del módulo (solo para validar OpenCV y PyZBar) ---
if __name__ == '__main__':
    # Esta prueba es difícil de hacer sin una GUI, pero verificamos la lista.
    print("--- Prueba de Detección de Cámaras ---")
    cams = list_available_cameras()
    if cams:
        print(f"✅ Cámaras disponibles detectadas: {cams}")
        print("La clase CameraStreamer está lista para ser integrada en la GUI.")
        # Nota: La visualización del frame requiere PyQt6
    else:
        print("❌ Advertencia: No se detectaron cámaras disponibles (OpenCV).")
        print("Verifique que la webcam esté conectada y que OpenCV tenga los permisos.")