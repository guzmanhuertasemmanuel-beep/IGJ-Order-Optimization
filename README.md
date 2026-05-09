# IGJ Order Optimization

## 1. Descripción del proyecto

**IGJ Order Optimization** es un sistema integral de información diseñado para transformar la gestión de pedidos de la cafetería del **Instituto Gauss Jordan**. El propósito principal es migrar de un modelo de gestión manual (basado en notas de papel) a un proceso totalmente automatizado y digitalizado mediante una arquitectura cliente-servidor.

El sistema resuelve problemáticas críticas como:

* 
**Ineficiencia operativa:** Errores en la toma de órdenes y tiempos de espera prolongados.


* 
**Falta de control:** Ausencia de un registro histórico de ventas y de un control de inventario en tiempo real.


* 
**Saturación del servicio:** Colapso del flujo de trabajo durante horas pico por exceso de pedidos simultáneos.




## 2. Tecnologías utilizadas

El proyecto se fundamenta en un stack tecnológico moderno de código abierto:

* 
**Backend:** Python 3 con el micro-framework **Flask** para la lógica de negocio y gestión de rutas.


* 
**Base de Datos:** **SQLite**, un sistema de gestión relacional ligero y de arquitectura *serverless*.


* 
**Frontend:** HTML5 para la estructura, CSS3 para el diseño responsivo y **JavaScript (AJAX/Fetch)** para actualizaciones en tiempo real sin recargar la página.


* **Arquitectura:** Modularizada mediante **Flask Blueprints** para separar las responsabilidades de cliente, cocina y administración.


## 3. Características principales

* 
**Registro Automatizado:** Interfaz intuitiva para que los estudiantes realicen sus pedidos desde dispositivos tipo tableta.


* 
**Dashboard de Cocina:** Visualización dinámica y en tiempo real de pedidos pendientes para el personal operativo.


* 
**Control de Saturación:** Límite estricto de **10 pedidos simultáneos** activos (estado "Pendiente" o "En Preparación") para evitar el colapso del personal.


* 
**Gestión de Inventario:** Validación automática de la disponibilidad de productos antes de confirmar la orden.


* **Módulo Administrativo:** Panel seguro para agregar/eliminar productos, cambiar disponibilidad y visualizar reportes de ventas (efectivo vs. tarjeta).
* **Auto-limpieza de Pedidos:** Sistema que marca automáticamente como "Entregado" aquellos pedidos que llevan más de 5 minutos en estado "Listo".


## 4. Instrucciones de instalación

Para ejecutar este proyecto localmente, sigue estos pasos:

1. **Clonar el repositorio:**
```bash
git clone https://github.com/tu-usuario/igj-order-optimization.git
cd igj-order-optimization

```


2. **Crear un entorno virtual (recomendado):**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

```


3. **Instalar dependencias:**
Este proyecto requiere Flask.
```bash
pip install flask

```


4. **Inicializar la base de datos:**
El sistema está configurado para crear las tablas automáticamente al iniciar la aplicación por primera vez mediante la función `crear_tablas()` en `app.py`.

---

## 5. Cómo usar el proyecto

1. **Iniciar el servidor:**
```bash
python app.py

```


La aplicación se ejecutará en modo *debug* en `http://127.0.0.1:5000`.
2. **Acceso por Roles:**
* **Clientes (Estudiantes):** Acceder a la raíz `/` para ver el menú y ordenar.
* **Personal de Cocina:** Acceder a `/cocina` o `/pedidos` para gestionar las órdenes entrantes.
* **Administrador:** * Ir a `/login`.
* Contraseña predeterminada: `admin123`.
* Desde aquí se gestionan productos y se consultan las ventas del día en `/ventas`.





## 6. Estructura del proyecto

La organización de los archivos sigue un patrón modular:

* `app.py`: Punto de entrada principal y registro de Blueprints.
* `db_manager.py`: Configuración de la conexión a SQLite y creación de esquemas.
* `rutas/`: Directorio que contiene la lógica de cada módulo:
* `cliente.py`: Gestión del menú y toma de pedidos.
* `cocina.py`: Dashboard operativo y actualización de estados.
* `admin.py`: Control de inventario, seguridad y reportes financieros.


* `database.db`: Archivo de base de datos SQLite.
* `templates/`: (Inferido) Archivos HTML para las interfaces de usuario.
* `static/`: (Inferido) Archivos CSS y JavaScript.


## 7. Contribuciones

Este es un proyecto académico desarrollado por alumnos del **Instituto Especializado en Computación y Administración (I.E.C.A) Gauss Jordan**, Grupo **BI-1601**. Las contribuciones para mejorar la eficiencia del sistema, proponer migraciones a bases de datos como PostgreSQL o implementar WebSockets son bienvenidas mediante *Pull Requests*.


## 8. Licencia

Este proyecto fue desarrollado bajo el marco del "Proyecto Aula" de la materia **Sistemas de Información**. Su uso es principalmente educativo y académico para el Instituto Gauss Jordan.

* ## 9. Información de contacto
Para dudas técnicas, sugerencias sobre la implementación, revisión de la arquitectura del sistema o propuestas de mejora continua, puedes contactar al equipo desarrollador a través de:

* **Correo electrónico:** guzmanhuertaserik@gmail.com
* **Equipo de Desarrollo (Grupo BI-1601):** 
  * Erik Emmanuel Guzmán Huertas
  
