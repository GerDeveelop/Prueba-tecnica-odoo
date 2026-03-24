# 💻 Portal de Solicitudes de Activos TI para Odoo 18

![Odoo Version](https://img.shields.io/badge/Odoo-18.0-purple?style=flat-square&logo=odoo)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-LGPL--3-green?style=flat-square)

Módulo técnico diseñado para la gestión centralizada de solicitudes internas de activos tecnológicos (laptops, monitores, licencias de software, etc.). Integra un portal web público para la captura de requerimientos y un entorno backoffice administrativo robusto para su evaluación, aprobación y seguimiento.

---

## ✨ Características Principales

### 🌐 Portal Web (Frontend)
* **Acceso Público Seguro:** Rutas configuradas con `auth='public'` para permitir el registro de solicitudes externas sin consumir licencias de usuario de Odoo.
* **Interfaz Responsiva:** Formularios estilizados e intuitivos construidos con **Bootstrap 5**, nativo en el framework web de Odoo 18.
* **Creación Segura de Registros:** Implementación del método `sudo()` y protección mediante tokens CSRF para garantizar transacciones seguras desde el frontend.

### ⚙️ Gestión Backoffice (Backend)
* **Modelo de Datos Robusto (`it.asset.request`):** Arquitectura sólida con trazabilidad completa y campos calculados.
* **Flujo de Trabajo Controlado:** Transiciones de estado estrictas (Borrador ➔ Enviado ➔ Aprobado/Rechazado).
* **Vistas Optimizadas:** Interfaz UI actualizada que cumple con el esquema estricto de validación **RelaxNG** de Odoo 18 (uso de `<list>`, `<chatter/>` nativo y booleanos estrictos).
* **Lógica de Negocio Automatizada:** Asignación automática de urgencia basada en el tipo de activo (mediante `@api.onchange`) y validación de costos coherentes (mediante `@api.constrains`).
* **Secuenciación:** Generación automática de referencias únicas (ej. `REQ-0001`) para cada solicitud.

### 📄 Reportes QWeb
* **Comprobantes en PDF:** Motor QWeb integrado para la generación e impresión de comprobantes de solicitud con un solo clic, ideal para auditorías y firmas físicas.

---
### Modulo Activos IT
<img width="1309" height="386" alt="image" src="https://github.com/user-attachments/assets/57bbba07-a65a-4025-9034-ecfe0f6e6d4b" />

### 🌐 Portal Web
<img width="707" height="609" alt="image" src="https://github.com/user-attachments/assets/2c702135-74b7-4f48-88f8-3d511e6a0f36" />


### 💡 Guía de Instalación
Clonar el repositorio:
Descargar el archivo .zip o clona este repositorio y colócalo dentro del directorio de addons de tu instancia de Odoo 18.

Bash
git clone <url-del-repositorio> it_asset_request
Reiniciar el servicio de Odoo:
Para que el sistema reconozca los nuevos archivos Python, reinicia el servicio:

Bash
sudo service odoo restart 
# Alternativa si ejecutas desde el binario:
./odoo-bin -c odoo.conf -u it_asset_request

### 🐵 Activar el Modo Desarrollador:

Inicia sesión en tu base de datos de Odoo con permisos de Administrador.

Navega a Ajustes y selecciona Activar modo desarrollador (en la parte inferior de la página).

### Instalar el módulo:

Dirígete al menú principal y abre la aplicación Aplicaciones.

En el menú superior, haz clic en Actualizar lista de aplicaciones y confirma.

Elimina el filtro "Aplicaciones" en la barra de búsqueda.

Busca it_asset_request o Portal de Solicitudes de Activos TI.

Haz clic en Activar / Instalar.

### 🛠️ Casos de Uso y Pruebas
1. Registro desde el Portal Web (Empleado/Usuario)
Abre una ventana de incógnito en tu navegador y visita: http://localhost:8080/asset-request, o la red local que tengas configarada.

Completa los campos del formulario (Nombre, Tipo de Activo, Justificación, etc.).

Al enviar, el sistema te redirigirá a una pantalla de confirmación con el resumen y el estado actual de tu solicitud.

2. Gestión desde el Backoffice (Administrador TI)
Inicia sesión en Odoo y abre el módulo Activos TI.

Explora las vistas de Lista (para ver insignias de colores y estados) o Kanban/Búsqueda para filtrar las solicitudes pendientes.

Abre una solicitud, interactúa con el flujo de botones en la cabecera (Aprobar/Rechazar) y observa cómo se registra el historial en el Chatter.

Haz clic en el botón Imprimir Comprobante para descargar el reporte en formato PDF.


## 📂 Estructura del Módulo

```text
it_asset_request/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py
├── data/
│   └── sequence.xml
├── models/
│   ├── __init__.py
│   └── asset_request.py
├── report/
│   └── asset_request_report.xml
├── security/
│   └── ir.model.access.csv
├── views/
│   ├── asset_request_menus.xml
│   ├── asset_request_views.xml
│   └── website_templates.xml

