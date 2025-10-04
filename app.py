# app.py

import sys
# Importamos la función de la GUI principal
from interfaz.principal import run_gui
# Importamos la configuración de la DB (Aunque ya se llama dentro de run_gui, 
# es buena práctica tener la inicialización centralizada aquí si fuera necesario)
# from modulos.utilidades import setup_database 

def main():
    """Función principal que inicia la aplicación gráfica."""
    # La función run_gui() se encarga de:
    # 1. Llamar a setup_database()
    # 2. Inicializar QApplication
    # 3. Mostrar la MainWindow
    run_gui()

if __name__ == '__main__':
    main()