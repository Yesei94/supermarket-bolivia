# SuperMarket Plataforma Profesional Integrada

Plataforma web para administrar un supermercado con arquitectura de microservicios. Incluye autenticacion JWT, gestion de empresas y sucursales, catalogo de productos, inventario con kardex, clientes con puntos, ventas con factura, notificaciones simuladas, reportes y exportaciones a Excel.

## Resumen del proyecto

El sistema esta compuesto por **7 microservicios FastAPI** y una **interfaz web integrada** servida con Nginx. Cada servicio tiene su propia responsabilidad, su propia base SQLite, documentacion Swagger y validacion de token JWT.

La interfaz permite ejecutar el flujo completo de operacion:

- Crear supermercado y sucursales.
- Registrar productos manualmente o por archivo Excel.
- Registrar clientes.
- Ingresar inventario por sucursal.
- Transferir stock entre sucursales.
- Vender productos con descuento automatico de inventario.
- Generar factura de venta.
- Asignar puntos al cliente.
- Registrar notificaciones de venta y stock bajo.
- Consultar dashboard, kardex, eventos y reportes.
- Exportar inventario y ventas en Excel.

## Arquitectura

| Servicio | Puerto | Base de datos | Responsabilidad |
|---|---:|---|---|
| Auth Service | 8000 | Memoria | Login, roles y emision de JWT |
| Company Service | 8001 | `company.db` | Supermercados y sucursales |
| Product Service | 8002 | `product.db` | Productos, categorias, marcas, precios y carga Excel |
| Inventory Service | 8003 | `inventory.db` | Stock, ingresos, salidas, transferencias, kardex, alertas y exportacion Excel |
| Customer Service | 8004 | `customer.db` | Clientes, documentos, historial basico y puntos |
| Notification Service | 8005 | `notification.db` | Notificaciones simuladas |
| Sales Service | 8006 | `sales.db` | Ventas, facturas, descuento de stock, ganancias, puntos y exportacion Excel |
| Frontend | 8080 | - | Interfaz profesional integrada |

## Tecnologias usadas

- Python 3.
- FastAPI.
- Uvicorn.
- SQLAlchemy.
- SQLite.
- Pydantic.
- python-jose para JWT.
- HTTPX para comunicacion entre microservicios.
- OpenPyXL para importacion y exportacion Excel.
- Docker y Docker Compose.
- Nginx para servir el frontend.
- HTML, CSS y JavaScript puro.
- Canvas API para graficos del dashboard.

## Como ejecutar

Desde la carpeta raiz del proyecto:

```powershell
docker compose up --build
```

Luego abre la interfaz:

```text
http://localhost:8080
```

## Credenciales

Usuarios disponibles en el servicio de autenticacion:

| Usuario | Contrasena | Rol |
|---|---|---|
| `admin` | `admin123` | `ADMIN` |
| `cajero` | `cajero123` | `CAJERO` |
| `supervisor` | `supervisor123` | `SUPERVISOR` |

En la interfaz existe un boton **Login admin** que inicia sesion rapidamente con el usuario administrador.

## Documentacion Swagger

Cada microservicio expone su documentacion interactiva:

```text
http://localhost:8000/docs
http://localhost:8001/docs
http://localhost:8002/docs
http://localhost:8003/docs
http://localhost:8004/docs
http://localhost:8005/docs
http://localhost:8006/docs
```

Tambien se puede validar el estado de cada servicio con:

```text
GET /health
```

## Funcionalidades implementadas

### Autenticacion

- Login con usuario y contrasena.
- Generacion de token JWT con expiracion de 8 horas.
- Roles incluidos en el token.
- Validacion de `Authorization: Bearer <token>` en los microservicios protegidos.
- CORS habilitado para integracion con el frontend.

### Empresas y sucursales

- Crear supermercado o empresa.
- Listar empresas.
- Consultar empresa por ID.
- Crear sucursales asociadas a una empresa.
- Listar sucursales.
- Consultar sucursal por ID.
- La sucursal conserva el nombre de la empresa para facilitar reportes y seleccion en pantalla.

### Productos

- Crear productos con codigo, nombre, categoria, marca, codigo de barras, precio base y estado.
- Listar productos.
- Consultar producto por ID.
- Actualizar producto.
- Eliminar producto.
- Listar categorias predefinidas:
  - Lacteos.
  - Abarrotes.
  - Bebidas.
  - Limpieza.
  - Carnes.
  - Panaderia.
- Cargar productos desde Excel mediante `POST /products/loadExcel`.
- La carga Excel crea productos nuevos o actualiza productos existentes segun el codigo.
- Manejo de errores por fila al importar Excel.

### Inventario

- Registrar ingreso de mercaderia por producto y sucursal.
- Guardar costo, precio de venta y stock minimo.
- Consultar inventario por producto.
- Consultar balance consolidado de inventario.
- Registrar salidas de inventario.
- Descontar stock automaticamente cuando se registra una venta.
- Transferir stock entre sucursales.
- Crear inventario destino automaticamente si se transfiere a una sucursal sin stock previo.
- Validar stock insuficiente.
- Registrar eventos internos de inventario.
- Registrar movimientos en kardex:
  - `ENTRADA`.
  - `SALIDA`.
  - `TRANSFERENCIA_SALIDA`.
  - `TRANSFERENCIA_ENTRADA`.
  - `EXCEL`.
- Detectar stock bajo.
- Registrar evento `StockLow`.
- Enviar notificacion simulada cuando el stock queda por debajo o igual al minimo.
- Importar inventario desde Excel mediante `POST /inventory/loadExcel`.
- Exportar reporte profesional de inventario en Excel mediante `GET /reports/inventory.xlsx`.

### Clientes

- Crear clientes con nombre y documento.
- Listar clientes.
- Consultar cliente por ID.
- Asignar puntos acumulables.
- Consultar historial basico del cliente.
- Los puntos se asignan automaticamente desde ventas: 1 punto por cada 10 Bs vendidos.

### Ventas y facturacion

- Registrar venta por cliente, producto, sucursal, cantidad y forma de pago.
- Consultar producto desde Product Service.
- Consultar cliente desde Customer Service.
- Consultar stock desde Inventory Service.
- Validar existencia de stock en la sucursal.
- Validar stock suficiente.
- Calcular precio unitario, costo unitario, total y ganancia.
- Generar numero de factura con formato `FAC-YYYYMMDD-timestamp`.
- Descontar inventario automaticamente.
- Asignar puntos al cliente.
- Registrar notificacion simulada de venta completada.
- Listar ventas.
- Consultar ventas del dia.
- Agrupar ventas del dia por forma de pago.
- Consultar utilidad contable en `/accounting/profit`.
- Exportar reporte profesional de ventas en Excel mediante `GET /reports/sales.xlsx`.

### Notificaciones

- Crear notificaciones simuladas.
- Listar notificaciones.
- Registrar notificaciones de venta.
- Registrar alertas de stock bajo desde inventario.
- La interfaz clasifica visualmente las notificaciones por prioridad:
  - Alta para stock bajo.
  - Media para ventas.
  - Baja para transferencias.
  - Normal para otros eventos.

### Frontend

- Interfaz unica para consumir todos los microservicios.
- Menu lateral con modulos:
  - Dashboard.
  - Empresa / Sucursales.
  - Productos.
  - Clientes.
  - Inventario.
  - Ventas / Factura.
  - Reportes.
  - Notificaciones.
- Login integrado.
- Validaciones en formularios.
- Selectores dinamicos cargados desde APIs.
- Autocompletado de datos comerciales al seleccionar producto, cliente o sucursal.
- Factura visible despues de registrar una venta.
- Tablas de empresas, sucursales, productos, clientes, inventario, ventas, reportes, notificaciones y eventos.
- Dashboard con metricas:
  - Stock total.
  - Ingresos del dia.
  - Ganancia.
  - Cantidad de ventas.
- Grafico de barras para stock por producto.
- Grafico tipo dona para ventas por forma de pago.
- Panel de alertas de stock bajo.
- Carga de productos por Excel desde la pantalla de productos.
- Descarga de reportes Excel desde la pantalla de reportes.

## Endpoints principales

### Auth Service

| Metodo | Endpoint | Descripcion |
|---|---|---|
| `GET` | `/health` | Estado del servicio |
| `POST` | `/auth/login` | Login y generacion de JWT |

### Company Service

| Metodo | Endpoint | Descripcion |
|---|---|---|
| `GET` | `/health` | Estado del servicio |
| `POST` | `/companies` | Crear empresa |
| `GET` | `/companies` | Listar empresas |
| `GET` | `/companies/{company_id}` | Consultar empresa |
| `POST` | `/branches` | Crear sucursal |
| `GET` | `/branches` | Listar sucursales |
| `GET` | `/branches/{branch_id}` | Consultar sucursal |

### Product Service

| Metodo | Endpoint | Descripcion |
|---|---|---|
| `GET` | `/health` | Estado del servicio |
| `POST` | `/products` | Crear producto |
| `POST` | `/products/loadExcel` | Cargar productos desde Excel |
| `GET` | `/products` | Listar productos |
| `GET` | `/products/{product_id}` | Consultar producto |
| `PUT` | `/products/{product_id}` | Actualizar producto |
| `DELETE` | `/products/{product_id}` | Eliminar producto |
| `GET` | `/categories` | Listar categorias |

### Inventory Service

| Metodo | Endpoint | Descripcion |
|---|---|---|
| `GET` | `/health` | Estado del servicio |
| `POST` | `/inventory/input` | Ingreso de mercaderia |
| `POST` | `/inventory/output` | Salida de mercaderia |
| `POST` | `/inventory/transfer` | Transferencia entre sucursales |
| `POST` | `/inventory/loadExcel` | Cargar inventario desde Excel |
| `GET` | `/inventory/product/{product_id}` | Inventario por producto |
| `GET` | `/inventory/balance` | Balance consolidado |
| `GET` | `/inventory/kardex/{product_id}` | Kardex por producto |
| `GET` | `/inventory/events` | Eventos de inventario |
| `GET` | `/reports/inventory.xlsx` | Exportar inventario Excel |

### Customer Service

| Metodo | Endpoint | Descripcion |
|---|---|---|
| `GET` | `/health` | Estado del servicio |
| `POST` | `/customers` | Crear cliente |
| `GET` | `/customers` | Listar clientes |
| `GET` | `/customers/{customer_id}` | Consultar cliente |
| `POST` | `/customers/{customer_id}/points` | Asignar puntos |
| `GET` | `/customers/{customer_id}/history` | Historial basico |

### Notification Service

| Metodo | Endpoint | Descripcion |
|---|---|---|
| `GET` | `/health` | Estado del servicio |
| `POST` | `/notifications` | Crear notificacion simulada |
| `GET` | `/notifications` | Listar notificaciones |

### Sales Service

| Metodo | Endpoint | Descripcion |
|---|---|---|
| `GET` | `/health` | Estado del servicio |
| `POST` | `/sales` | Registrar venta |
| `GET` | `/sales` | Listar ventas |
| `GET` | `/reports/sales/today` | Ventas del dia |
| `GET` | `/accounting/profit` | Ingresos, costos y ganancia |
| `GET` | `/reports/sales.xlsx` | Exportar ventas Excel |

## Flujo recomendado de prueba

1. Abrir `http://localhost:8080`.
2. Presionar **Login admin**.
3. Ir a **Empresa / Sucursales** y crear una empresa, por ejemplo `OXXO Bolivia`.
4. Crear dos sucursales, por ejemplo `Sucursal Prado` y `Sucursal El Alto`.
5. Ir a **Productos** y crear un producto manualmente, por ejemplo `LECHE980`.
6. Opcionalmente cargar productos desde Excel con el archivo `productos_10.xlsx`.
7. Ir a **Clientes** y registrar un cliente.
8. Ir a **Inventario** y registrar ingreso de mercaderia en una sucursal.
9. Revisar el kardex del producto.
10. Ir a **Ventas / Factura** y registrar una venta.
11. Verificar que se genere la factura.
12. Confirmar que el stock haya bajado automaticamente.
13. Confirmar que el cliente haya recibido puntos.
14. Transferir stock entre sucursales desde **Inventario**.
15. Revisar **Reportes** para ver inventario consolidado, ventas del dia, ingresos y ganancia.
16. Descargar los reportes Excel.
17. Revisar **Notificaciones** para ver ventas, alertas y eventos.

## Formato para carga Excel de productos

La importacion de productos espera un archivo Excel con encabezados en la primera fila y datos desde la segunda fila:

| Columna | Campo |
|---|---|
| A | Codigo |
| B | Nombre |
| C | Categoria |
| D | Marca |
| E | Codigo de barras |
| F | Precio base |
| G | Estado |

El sistema crea productos nuevos o actualiza los existentes usando el codigo como identificador.

## Formato para carga Excel de inventario

La importacion de inventario espera las siguientes columnas:

| Columna | Campo |
|---|---|
| A | Product ID |
| B | Codigo de producto |
| C | Nombre de producto |
| D | Empresa |
| E | Branch ID |
| F | Nombre de sucursal |
| G | Cantidad |
| H | Costo |
| I | Precio |
| J | Stock minimo |

## Comunicacion entre servicios

El `docker-compose.yml` conecta los servicios usando nombres internos de Docker:

- Sales Service consulta Product Service para obtener el precio del producto.
- Sales Service consulta Customer Service para validar cliente y asignar puntos.
- Sales Service consulta Inventory Service para validar y descontar stock.
- Sales Service envia una notificacion de venta a Notification Service.
- Inventory Service envia alertas de stock bajo a Notification Service.

## Bases de datos

Cada microservicio administra su propia base SQLite:

```text
company.db
product.db
inventory.db
customer.db
notification.db
sales.db
```

Estas bases se crean automaticamente al iniciar los servicios.

## Reportes implementados

- Reporte consolidado de inventario en pantalla.
- Reporte de ventas del dia en pantalla.
- Total de stock general.
- Total de ingresos del dia.
- Ganancia del dia.
- Ventas por forma de pago.
- Alertas de stock bajo.
- Eventos de inventario.
- Kardex por producto.
- Exportacion Excel de inventario con formato profesional.
- Exportacion Excel de ventas con hoja de resumen y hoja de detalle.


