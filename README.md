# Ferias Locales de Arica

Aplicación web en Django (patrón MVT, ORM, vistas basadas en funciones) para gestionar ferias locales: puestos, vendedores, productos, ubicaciones y eventos, con carrito de compras y pago con Webpay Plus (ambiente de integración).

## Aplicaciones

| App | Responsabilidad |
|---|---|
| `feria` | Ubicación, Vendedor, Puesto y Producto, con su CRUD |
| `usuarios` | Registro, inicio de sesión, Perfil con rol y decoradores de acceso |
| `carrito` | Carrito, órdenes y pago con Webpay |
| `eventos` | Eventos y asistencia de los usuarios |

## Roles

| Rol | Puede |
|---|---|
| Administrador | CRUD de todos los modelos y ver todas las órdenes |
| Vendedor | Gestionar solo sus puestos y productos; comprar como usuario |
| Usuario General | Ver información, comprar, ver solo sus órdenes y asistir a eventos |

Las restricciones se aplican en el servidor: un usuario sin el rol recibe 403 o 404 aunque escriba la URL directa.

## Instalación

```bash
git clone https://github.com/Lucax4d/Ferias.git
cd Ferias
python -m venv venv
source venv/Scripts/activate      # PowerShell: venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env        # completa SECRET_KEY y las credenciales de Webpay
python manage.py migrate
python manage.py cargar_datos
python manage.py runserver
```

Abre `http://127.0.0.1:8000/`.

## Usuarios de ejemplo (solo para pruebas locales)

Se crean con `python manage.py cargar_datos`. Contraseña de todos: `clave12345`.

| Usuario | Rol |
|---|---|
| `admin` | Administrador |
| `vendedor1`, `vendedor2` | Vendedor |
| `cliente1` | Usuario General |

## Pruebas

```bash
python manage.py test
```

Incluyen permisos por rol, una matriz de URLs por tipo de usuario, el carrito, el pago con Webpay simulado y la asistencia a eventos.

## Pago con Webpay (ambiente de pruebas)

Tarjeta de prueba Visa `4051 8856 0044 6623`, CVV `123`, vencimiento futuro. En la autenticación, RUT `11.111.111-1` y clave `123`. Los datos vigentes están en developers.transbank.cl.

## Variables de entorno

La configuración sensible vive en un archivo `.env` que **no se sube a GitHub**. La plantilla es `.env.example`:

| Variable | Para qué sirve |
|---|---|
| `SECRET_KEY` | Clave con la que Django firma sesiones y cookies |
| `DEBUG` | `True` en desarrollo; en producción debe ser `False` |
| `ALLOWED_HOSTS` | Direcciones desde las que se puede acceder, separadas por coma |
| `WEBPAY_COMMERCE_CODE`, `WEBPAY_API_KEY` | Credenciales de prueba (sandbox) de Transbank |
| `WEBPAY_ENV` | `TEST` usa el sandbox; `LIVE` usa la integración real |

Para generar una clave nueva:

```bash
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

## Ramas y versiones

Flujo: `feature/*` hacia `develop` y entregas estables en `main`.

| Versión | Contenido |
|---|---|
| v0.1.0 | Estructura del proyecto y modelos |
| v0.2.0 | Roles |
| v0.3.0 | Login y CRUD de puestos y productos |
| v0.4.0 | Carrito y órdenes |
| v0.5.0 | Pago con Webpay |
| v0.6.0 | Ubicaciones y eventos |
| v0.7.0 | Datos de ejemplo y validación por rol |
| v1.0.0 | Entrega |
