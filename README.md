<div id="top"></div>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python" alt="Python 3.x">
  <img src="https://img.shields.io/badge/Framework-PyQt6-green?logo=qt" alt="PyQt6">
  <img src="https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite" alt="SQLite">
  <img src="https://img.shields.io/badge/Computer_Vision-OpenCV-8A2BE2?logo=opencv" alt="OpenCV">
</p>

<h1 align="center">PROYECTIS - Sistema de Asistencia QR</h1>
<p align="center">Documentación Completa del Sistema de Asistencia en Entornos Educativos</p>

---

<h2>I. Resumen y Objetivo del Proyecto 🚀</h2>

<p><strong>PROYECTIS</strong> es una aplicación de escritorio desarrollada en <strong>Python</strong> con el framework <strong>PyQt6</strong>, diseñada para automatizar y gestionar la toma de asistencia. Utiliza la <strong>webcam (OpenCV)</strong> para escanear códigos QR que identifican a cada alumno, registrando la hora de entrada de manera eficiente y segura en una base de datos local <strong>SQLite</strong>.</p>

<h3>Objetivos Funcionales Clave:</h3>
<ul>
    <li>Registro de Alumnos (CRUD Básico).</li>
    <li>Generación de Códigos QR personalizados (por alumno).</li>
    <li>Lectura de QR en tiempo real desde la webcam.</li>
    <li>Registro de Asistencia con prevención de duplicados (cooldown).</li>
    <li>Generación de Reportes históricos en formato CSV.</li>
</ul>

<h3>Stack Tecnológico Principal:</h3>
<table>
  <thead>
    <tr>
      <th>Componente</th>
      <th>Tecnología</th>
      <th>Propósito</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Interfaz Gráfica</td>
      <td><strong>PyQt6</strong></td>
      <td>Aplicación de escritorio</td>
    </tr>
    <tr>
      <td>Base de Datos</td>
      <td><strong>SQLite + SQLAlchemy</strong></td>
      <td>Persistencia de datos y ORM</td>
    </tr>
    <tr>
      <td>Visión/Cámara</td>
      <td><strong>OpenCV (cv2)</strong></td>
      <td>Captura y procesamiento de video</td>
    </tr>
    <tr>
      <td>Lectura/Generación QR</td>
      <td><strong>pyzbar, qrcode</strong></td>
      <td>Manejo de códigos QR</td>
    </tr>
    <tr>
      <td>Reportes</td>
      <td><strong>pandas</strong></td>
      <td>Exportación a CSV</td>
    </tr>
  </tbody>
</table>

---

<h2>II. Configuración e Instalación (Linux) 🛠️</h2>

<p>Sigue estos pasos en tu sistema Linux para configurar el entorno de desarrollo y ejecutar la aplicación.</p>

<h3>1. Requisitos Previos</h3>
<ul>
    <li><strong>Python 3.x</strong> instalado.</li>
    <li>Acceso a la terminal (se recomienda <strong>VSCodium</strong>).</li>
</ul>

<h3>2. Crear y Activar el Entorno Virtual (venv)</h3>
<pre><code># Crear el entorno (si no existe)
python3 -m venv .venv

# Activar el entorno
source .venv/bin/activate
</code></pre>

<h3>3. Instalar Dependencias</h3>
<p>El proyecto requiere las siguientes librerías:</p>
<pre>PyQt6 SQLAlchemy opencv-python pyzbar qrcode Pillow pandas</pre>
<p>Instala todas con:</p>
<pre><code>(.venv) ulises@ulises-smartr8ce:~$ pip install PyQt6 SQLAlchemy opencv-python pyzbar qrcode Pillow pandas
</code></pre>

<h3>4. Ejecutar la Aplicación</h3>
<pre><code>(.venv) ulises@ulises-smartr8ce:~$ python app.py
</code></pre>

<blockquote>
    <strong>Nota:</strong> Al iniciar por primera vez, se creará automáticamente la base de datos <code>datos/asistencia.db</code> y las carpetas necesarias (<code>datos QR/</code>) en el Escritorio del usuario.
</blockquote>

---

<h2>III. Estructura de Archivos y Módulos 📂</h2>

<pre><code>Proyecto_Asistencia_QR/
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
</code></pre>

---

<h2>IV. Documentación Detallada de Módulos 🧠</h2>

<h3>1. <code>modulos/utilidades.py</code> (Modelos de DB y Configuración)</h3>
<p>Define la conexión con SQLite usando SQLAlchemy y los modelos de las dos tablas principales: <code>Student</code> y <code>Attendance</code>.</p>
<table>
  <thead>
    <tr>
      <th>Modelo</th>
      <th>Descripción</th>
      <th>Campos Clave</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Student</strong></td>
      <td>Alumnos registrados en el sistema.</td>
      <td><code>matricula</code> (UNIQUE, Indexado), <code>qr_color_hex</code></td>
    </tr>
    <tr>
      <td><strong>Attendance</strong></td>
      <td>Registro de cada pase de lista.</td>
      <td><code>matricula</code> (Indexado), <code>time_stamp</code></td>
    </tr>
  </tbody>
</table>
<p>La función <code>setup_database()</code> crea el archivo <code>asistencia.db</code> y todas las tablas al inicio.</p>

<h3>2. <code>modulos/alumnos.py</code> (Gestión de Alumnos y QR)</h3>
<p>Contiene la lógica para el registro (Create) de alumnos y la generación de sus códigos QR.</p>
<table>
  <thead>
    <tr>
      <th>Función</th>
      <th>Descripción</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>generate_qr_code(data, filename, color_hex)</code></td>
      <td>Crea un archivo PNG del QR usando la matrícula. Se guarda en <code>datos QR/</code>.</td>
    </tr>
    <tr>
      <td><code>create_student(...)</code></td>
      <td>Registra al nuevo alumno, verifica unicidad de matrícula y llama a <code>generate_qr_code</code>. Maneja el error <code>IntegrityError</code>.</td>
    </tr>
  </tbody>
</table>

<h3>3. <code>modulos/asistencia.py</code> (Lógica de Registro)</h3>
<p>Controla el proceso de marcar la asistencia, aplicando validaciones cruciales.</p>
<ul>
    <li><strong><code>COOLDOWN_SECONDS = 10</code></strong>: Límite de tiempo (en segundos) para evitar registros duplicados.</li>
    <li><strong><code>register_attendance(matricula)</code></strong>:
        <ol>
            <li>Verifica si la matrícula existe.</li>
            <li><strong>Verifica el Cooldown</strong>: Si el último registro fue hace menos de 10 segundos, retorna ⚠️ **ALERTA**.</li>
            <li>Si pasa, guarda un nuevo registro en la tabla <code>Attendance</code>.</li>
        </ol>
    </li>
</ul>
<p><strong>Salida de <code>register_attendance</code> (Formato <code>dict</code>):</strong></p>
<pre><code>{"status": "success", "message": "..."}
{"status": "warning", "message": "..."} (Cooldown)
{"status": "error", "message": "..."} (Matrícula no existe o error fatal)
</code></pre>

<h3>4. <code>modulos/reportes.py</code> (Lógica de Exportación)</h3>
<p>Encargado de la exportación de datos históricos a archivos CSV.</p>
<table>
  <thead>
    <tr>
      <th>Función</th>
      <th>Descripción</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>get_attendance_data()</code></td>
      <td>Consulta la DB para obtener TODOS los registros de asistencia y los combina con los datos de los alumnos. Retorna un <strong>DataFrame de pandas</strong>.</td>
    </tr>
    <tr>
      <td><code>export_attendance_to_csv(df, filename_suffix)</code></td>
      <td>Toma el DataFrame, crea una subcarpeta con la fecha actual (<code>datos QR/YYYY-MM-DD/</code>) y guarda el contenido en un archivo CSV. Usa <strong><code>;</code> como separador</strong>.</td>
    </tr>
  </tbody>
</table>

---

<h2>V. Funcionalidad de Interfaz (PyQt6) 🖥️</h2>

<h3><code>interfaz/principal.py</code></h3>
<p>Configura el tema oscuro y organiza la aplicación en tres pestañas principales:</p>
<ul>
    <li><strong>Inicio / Dashboard</strong>: Contiene el <code>ReportesWidget</code>.</li>
    <li><strong>Gestión de Alumnos</strong>: Contiene el <code>AlumnosWidget</code> (CRUD y tabla).</li>
    <li><strong>Registro de Asistencia</strong>: Contiene el <code>CameraWidget</code> (Webcam y escaneo).</li>
</ul>

<h3><code>interfaz/alumnos_widget.py</code></h3>
<ul>
    <li>Muestra la lista de alumnos en una tabla no editable.</li>
    <li>Permite el registro de nuevos alumnos y la selección de color del QR.</li>
    <li>Incluye la función de **Eliminación (Delete)**, que borra al alumno y **todos sus registros asociados** en <code>Attendance</code> para mantener la integridad.</li>
</ul>

<h3><code>interfaz/reportes_widget.py</code></h3>
<ul>
    <li>Contiene el botón de **"Generar Reporte General de Asistencia"**.</li>
    <li>Al hacer clic, llama a la lógica de <code>modulos/reportes.py</code> y muestra la ruta de guardado, ofreciendo abrir la carpeta contenedora en Linux (<code>xdg-open</code>).</li>
</ul>

<p align="right"><a href="#top">🔼 Volver arriba</a></p>
