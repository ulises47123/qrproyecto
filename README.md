################################################################################

PROYECTIS - DOCUMENTACIÓN COMPLETA DEL SISTEMA DE ASISTENCIA QR
################################################################################

I. RESUMEN Y OBJETIVO DEL PROYECTO
PROYECTIS es una aplicación de escritorio desarrollada en Python con el framework PyQt6, diseñada para automatizar y gestionar la toma de asistencia en entornos educativos. Utiliza la webcam para escanear códigos QR que identifican a cada alumno, registrando la hora de entrada de manera eficiente y segura en una base de datos local SQLite.

Objetivos Funcionales:

Registro de Alumnos (CRUD Básico).

Generación de Códigos QR personalizados (por alumno).

Lectura de QR en tiempo real desde la webcam.

Registro de Asistencia con prevención de duplicados (cooldown).

Generación de Reportes históricos en formato CSV.

Stack Tecnológico Principal:

Interfaz Gráfica: PyQt6

Base de Datos: SQLite + SQLAlchemy

Visión/Cámara: OpenCV (cv2)

Lectura/Generación QR: pyzbar, qrcode

Reportes: pandas

II. CONFIGURACIÓN E INSTALACIÓN (README)
Sigue estos pasos en tu sistema Linux para configurar el entorno de desarrollo y ejecutar la aplicación.

1. Requisitos Previos
Python 3.x instalado.

Acceso a la terminal (se recomienda VSCodium).

2. Crear y Activar el Entorno Virtual (venv)
# Crear el entorno (si no existe)
python3 -m venv .venv

# Activar el entorno
source .venv/bin/activate

3. Instalar Dependencias (requirements.txt)
El proyecto requiere las siguientes librerías:

PyQt6
SQLAlchemy
opencv-python
pyzbar
qrcode
Pillow 
pandas

Instala todas las dependencias con el siguiente comando:

(.venv) ulises@ulises-smartr8ce:~$ pip install PyQt6 SQLAlchemy opencv-python pyzbar qrcode Pillow pandas

4. Ejecutar la Aplicación
(.venv) ulises@ulises-smartr8ce:~$ python app.py

Nota: Al iniciar por primera vez, se creará automáticamente la base de datos datos/asistencia.db y las carpetas necesarias (datos QR/) en el Escritorio del usuario.

III. ESTRUCTURA DE ARCHIVOS Y MÓDULOS
Proyecto_Asistencia_QR/
├── datos/
│   └── asistencia.db           # Base de datos SQLite
├── datos QR/
│   ├── [Matrícula].png         # Códigos QR generados
│   └── YYYY-MM-DD/             # Subcarpetas para reportes (Ej: 2025-10-04)
├── modulos/
│   ├── alumnos.py              # Lógica de gestión de alumnos y QR
│   ├── asistencia.py           # Lógica de registro de asistencia (Cooldown)
│   ├── camara.py               # Hilo y lógica de captura de video/QR
│   ├── reportes.py             # Lógica para exportar a CSV (pandas)
│   └── utilidades.py           # Configuración de DB, modelos (ORM), rutas
├── interfaz/
│   ├── principal.py            # Ventana principal (QMainWindow y pestañas)
│   ├── alumnos_widget.py       # Pestaña para CRUD y tabla de alumnos
│   ├── reportes_widget.py      # Pestaña para generar reportes
│   └── ...
└── app.py                      # Punto de inicio del programa

IV. DOCUMENTACIÓN DETALLADA DE MÓDULOS
1. modulos/utilidades.py (Modelos de DB y Configuración)
Define la conexión con SQLite usando SQLAlchemy y los modelos de las dos tablas principales: Student y Attendance.

Modelo

Descripción

Campos Clave

Student

Alumnos registrados en el sistema.

matricula (UNIQUE, Indexado), qr_color_hex

Attendance

Registro de cada pase de lista.

matricula (Indexado), time_stamp

La función setup_database() se encarga de crear el archivo asistencia.db y todas las tablas al inicio.

2. modulos/alumnos.py (Gestión de Alumnos y QR)
Contiene la lógica para el registro (Create) de alumnos y la generación de sus códigos QR.

Función

Descripción

generate_qr_code(data, filename, color_hex)

Crea un archivo PNG del QR usando la matrícula (data) como contenido. El archivo se guarda en la carpeta datos QR/.

create_student(...)

Registra al nuevo alumno en la tabla Student. Verifica la unicidad de la matrícula y, si es exitoso, llama a generate_qr_code. Maneja el error IntegrityError (matrícula duplicada).

3. modulos/asistencia.py (Lógica de Registro)
Controla el proceso de marcar la asistencia, aplicando validaciones cruciales.

Constante/Función

Descripción

COOLDOWN_SECONDS = 10

Límite de tiempo (en segundos) para evitar registros duplicados.

register_attendance(matricula)

Función central. 1. Busca si la matrícula existe en Student. 2. Verifica el Cooldown: Si el último registro del alumno fue hace menos de 10 segundos, retorna una ⚠️ ALERTA. 3. Si pasa la validación, crea y guarda un nuevo registro en la tabla Attendance.

Salida de register_attendance (Formato dict):

{"status": "success", "message": "..."}

{"status": "warning", "message": "..."} (Cooldown)

{"status": "error", "message": "..."} (Matrícula no existe o error fatal)

4. modulos/reportes.py (Lógica de Exportación)
Encargado de la exportación de datos históricos a archivos CSV.

Función

Descripción

get_attendance_data()

Consulta la DB para obtener TODOS los registros de asistencia (Attendance) y los combina con los datos completos de los alumnos (Student). Retorna un DataFrame de pandas.

export_attendance_to_csv(df, filename_suffix)

Toma el DataFrame, crea una subcarpeta con la fecha actual (datos QR/YYYY-MM-DD/) y guarda el contenido en un archivo CSV. Usa ; como separador para mejor compatibilidad con Excel.

V. FUNCIONALIDAD DE INTERFAZ (PyQt6)
interfaz/principal.py: Configura el tema oscuro y organiza la aplicación en tres pestañas principales:

Inicio / Dashboard: Contiene el ReportesWidget.

Gestión de Alumnos: Contiene el AlumnosWidget (CRUD y tabla).

Registro de Asistencia: Contiene el CameraWidget (Webcam y escaneo).

interfaz/alumnos_widget.py:

Muestra la lista de alumnos en una tabla no editable.

Permite el registro de nuevos alumnos y la selección de color del QR.

Incluye la función de Eliminación (Delete), que borra al alumno y todos sus registros asociados en la tabla Attendance para mantener la integridad.

interfaz/reportes_widget.py:

Contiene el botón de "Generar Reporte General de Asistencia".

Al hacer clic, llama a la lógica de modulos/reportes.py y muestra la ruta de guardado, ofreciendo abrir la carpeta contenedora en Linux (xdg-open).
