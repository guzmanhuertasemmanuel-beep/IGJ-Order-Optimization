# IGJ Order Optimization

## 1. Descripción del proyecto

**IGJ Order Optimization** es un ecosistema de software desacoplado y de alta disponibilidad diseñado específicamente para automatizar y optimizar de extremo a extremo la gestión de pedidos en la cafetería del **Instituto Gauss Jordan**.

El sistema reemplaza por completo el modelo de gestión manual analógico (notas de papel) con una infraestructura robusta cliente-servidor distribuida. Su propósito fundamental es mitigar cuellos de botella en horas pico, erradicar fallas en la cadena de preparación, proporcionar control estricto e histórico sobre el inventario y centralizar la información financiera para la toma de decisiones estratégicas de la administración.

---

## 2. Tecnologías utilizadas

La arquitectura actual del proyecto está distribuida bajo un stack tecnológico moderno, escalable y multiplataforma:

* **Backend (API Server):** Python 3 con el micro-framework **Flask**, organizado de forma modular mediante **Flask Blueprints** para aislar las capas operativas.
* **Base de Datos:** **PostgreSQL 18** (migrado desde SQLite), garantizando alta disponibilidad, concurrencia masiva y estricta conformidad **ACID**. Se utiliza la librería `psycopg2` para la gestión avanzada de conexiones y manejo estricto de transacciones (*rollbacks* automatizados ante fallas).
* **Cliente de Escritorio Nativo:** Desarrollado en **Java** utilizando el framework de interfaz gráfica **JavaFX** y gestionado mediante **Maven**, eliminando las limitaciones del entorno puramente web en estaciones de trabajo clave.
* **Cliente Web (SPA):** HTML5, CSS3 y **JavaScript (AJAX/Fetch API)** para módulos de cara al usuario basados en interfaces reactivas de una sola página.
* **Infraestructura:** Scripts automatizados en Python/Bash para el mantenimiento del sistema y limpieza de datos en caliente.

---

## 3. Características principales

* **Arquitectura Híbrida Multiplataforma:** Interoperabilidad transparente entre las interfaces web reactivas y la aplicación nativa de escritorio JavaFX.
* **Control de Saturación Optimizado:** Lógica de negocio restringida que limita estrictamente a un máximo de **5 pedidos simultáneos activos** (estados "Pendiente" o "En Preparación") en cocina, evitando sobrecargar al personal y asegurando la calidad del servicio.
* **Garantía Transaccional Completa:** Mecanismos de validación de stock concurrentes que aplican reversiones (*rollbacks*) automáticas si un producto se agota en el milisegundo exacto de la ordenación.
* **Business Intelligence & Dashboard Financiero:** Módulo administrativo avanzado para auditorías monetarias, permitiendo el desglose analítico de ventas en tiempo real y la diferenciación automática de ingresos (efectivo vs. tarjeta).
* **Mantenimiento Automatizado de Infraestructura:** Tareas programadas en el servidor que monitorizan el estado de las órdenes, forzando la transición a "Entregado" en pedidos estancados (por ejemplo, listos por más de 5 minutos) para liberar memoria operativa.

---

## 4. Instrucciones de instalación

### Requisitos previos

* Python 3.10 o superior
* Java JDK 17 o superior y Apache Maven
* Instancia activa de PostgreSQL 18

### Paso 1: Configurar el Servidor Backend (Flask)

1. Clonar el repositorio localmente:
```bash
git clone https://github.com/guzmanhuertasemmanuel-beep/IGJ-Order-Optimization.git
cd IGJ-Order-Optimization

```


2. Instalar y activar un entorno virtual de Python:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

```


3. Instalar las dependencias de la API:
```bash
pip install flask psycopg2-binary

```


4. Configurar las credenciales de acceso a tu instancia de PostgreSQL 18 en el archivo de entorno o gestor de base de datos (`db_manager.py`).

### Paso 2: Configurar el Cliente de Escritorio (JavaFX)

1. Dirigirse al directorio del módulo Java del proyecto.
2. Descargar las dependencias y compilar el proyecto utilizando Maven:
```bash
mvn clean install

```



---

## 5. Cómo usar el proyecto

1. **Iniciar la API y el Servidor de Base de Datos:**
Ejecuta el servidor Flask para abrir los endpoints REST:
```bash
python app.py

```


El backend comenzará a escuchar solicitudes en `http://127.0.0.1:5000`.
2. **Lanzar la Aplicación de Escritorio JavaFX:**
En una terminal independiente dentro del módulo de Java, ejecuta:
```bash
mvn javafx:run

```


3. **Acceso a los Módulos Operativos:**
* **Clientes (Alumnos):** Interactúan mediante la interfaz web reactiva (SPA) expuesta en la raíz del servidor para enviar órdenes.
* **Cocina y Despacho:** Visualización en tiempo real desde el cliente dedicado.
* **Administración:** Acceso protegido bajo credenciales seguras para la visualización del Dashboard Financiero y alteración de existencias en el menú.



---

## 6. Estructura del proyecto

El código fuente está estructurado de manera desacoplada para separar la lógica del servidor de los clientes:

* `app.py`: Inicializador del servidor Flask y orquestador central de los Blueprints de la API.
* `db_manager.py`: Controlador de conexiones a PostgreSQL 18, encargado del ciclo de vida de las transacciones y rollbacks ACID.
* `rutas/` / `blueprints/`: Lógica interna dividida por contextos de negocio (`cliente.py`, `cocina.py`, `admin.py`).
* `desktop-javafx/` *(o directorio homólogo de Java)*: Proyecto estructurado con Maven (`pom.xml` y código fuente en `src/main/java`) que gestiona el cliente de escritorio.
* `templates/` y `static/`: Contenedores de la interfaz web SPA (HTML estático, CSS modular y scripts AJAX/Fetch).
* `scripts/`: Automatizaciones del sistema para tareas de mantenimiento en caliente.

---

## 7. Contribuciones

Este proyecto se desarrolla bajo fines académicos y de optimización técnica por estudiantes del **Instituto Gauss Jordan**, Grupo **BI-1601**. Si deseas contribuir al ecosistema (por ejemplo, migrar la capa de comunicación síncrona/polling a WebSockets reactivos), sigue estos pasos:

1. Realiza un *Fork* del repositorio.
2. Crea una rama con una característica descriptiva (`git checkout -b feature/NuevaMejora`).
3. Sube tus cambios (*Commit*) con mensajes técnicos claros.
4. Envía un *Pull Request* hacia la rama principal para su correspondiente revisión por el equipo técnico.

---

## 8. Licencia

Este software fue construido dentro del marco académico institucional del "Proyecto Aula". Su distribución, código fuente y uso asociado son de carácter educativo y de propiedad intelectual compartida con el Instituto Gauss Jordan.

---

## 9. Información de contacto

Para aclaraciones sobre la arquitectura del sistema, reportes de fallos en el manejo de transacciones con PostgreSQL o dudas técnicas del cliente JavaFX, puedes ponerte en contacto con el equipo de desarrollo a través de:

* **Correo electrónico principal:** guzmanhuertaserik@gmail.com
* **Equipo de Desarrollo (Grupo BI-1601):**
* Erik Emmanuel Guzmán Huertas
* Santiago Leon Badillo Cuevas
* Raúl Isaac Delgadillo Gonzalez
* Cesar Emilio Prieto Flores
