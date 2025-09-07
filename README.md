# 🚬 Buscador de Establecimientos España

Una aplicación web completa para buscar máquinas de tabaco y establecimientos en España. Desarrollada con FastAPI, PostgreSQL y JavaScript vanilla para un rendimiento óptimo.

## 📋 Características

- **Búsqueda rápida**: Búsqueda en tiempo real con debounce para optimizar rendimiento
- **Filtros avanzados**: Filtrado por provincia y búsqueda por nombre/dirección
- **Paginación inteligente**: Carga progresiva de resultados con botón "Cargar más"
- **Diseño responsive**: Interfaz moderna que funciona en todos los dispositivos
- **API RESTful**: Endpoints bien documentados con FastAPI
- **Base de datos optimizada**: Índices para búsquedas ultra-rápidas

## 🏗️ Arquitectura

- **Backend**: FastAPI (Python)
- **Base de Datos**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **Hosting**: Compatible con servicios gratuitos como Render

## 📋 Requisitos Previos

- Python 3.8 o superior
- PostgreSQL 12 o superior
- Node.js (opcional, para herramientas de desarrollo)

## 🚀 Instalación y Configuración Local

### 1. Clonar el repositorio

```bash
git clone <tu-repositorio>
cd buscador-establecimientos
```

### 2. Crear y activar entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos

1. Crea una base de datos PostgreSQL
2. Copia el archivo de configuración:
   ```bash
   cp .env.example .env
   ```
3. Edita el archivo `.env` y configura tu `DATABASE_URL`:
   ```
   DATABASE_URL="postgresql://usuario:contraseña@localhost:5432/nombre_base_datos"
   ```

### 5. Preparar los datos

1. Coloca tu archivo JSON con los datos de establecimientos en la raíz del proyecto como `tu_archivo_grande.json`
2. Ejecuta el script de carga de datos:
   ```bash
   python scripts/load_data.py
   ```

### 6. Iniciar el servidor backend

```bash
uvicorn main:app --reload
```

El servidor estará disponible en `http://localhost:8000`

### 7. Abrir el frontend

Abre el archivo `frontend/index.html` en tu navegador web.

## 📁 Estructura del Proyecto

```
buscador-establecimientos/
│
├── scripts/
│   └── load_data.py          # Script para cargar datos a PostgreSQL
│
├── frontend/
│   ├── index.html            # Página principal
│   ├── styles.css            # Estilos CSS
│   └── app.js               # Lógica JavaScript
│
├── .env.example             # Plantilla de configuración
├── main.py                  # API FastAPI
├── requirements.txt         # Dependencias Python
└── README.md               # Este archivo
```

## 🔧 API Endpoints

### GET `/api/establecimientos`

Busca establecimientos con filtros opcionales y paginación.

**Parámetros de consulta:**
- `search` (opcional): Texto para buscar en nombre y dirección
- `provincia` (opcional): Filtrar por provincia
- `skip` (opcional): Número de resultados a omitir (default: 0)
- `limit` (opcional): Número máximo de resultados (default: 25, max: 100)

**Ejemplo:**
```
GET /api/establecimientos?search=tabaco&provincia=Madrid&skip=0&limit=10
```

### GET `/api/provincias`

Obtiene la lista de todas las provincias disponibles.

### GET `/health`

Endpoint de salud para verificar el estado de la API.

## 🎨 Características del Frontend

- **Búsqueda en tiempo real**: Debounce de 300ms para optimizar peticiones
- **Filtros dinámicos**: Select de provincias poblado automáticamente
- **Paginación**: Carga progresiva con botón "Cargar más"
- **Estados de carga**: Indicadores visuales durante las búsquedas
- **Diseño responsive**: Adaptable a móviles y tablets
- **Animaciones suaves**: Transiciones CSS para mejor UX

## 🚀 Despliegue en Render

### 1. Preparar el proyecto

1. Asegúrate de que todos los archivos estén en el repositorio
2. Crea un archivo `render.yaml` en la raíz:

```yaml
services:
  - type: web
    name: buscador-establecimientos
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        sync: false
```

### 2. Configurar en Render

1. Conecta tu repositorio GitHub a Render
2. Selecciona el servicio web
3. Configura las variables de entorno:
   - `DATABASE_URL`: Tu URL de PostgreSQL
4. Despliega

### 3. Configurar el frontend

Para el frontend, puedes:
- Servirlo desde el mismo dominio (modificar `apiBaseUrl` en `app.js`)
- Usar un servicio de hosting estático como Netlify o Vercel
- Servirlo desde un CDN

## 🔍 Optimizaciones de Rendimiento

- **Índices de base de datos**: Índices en `provincia`, `nombre` y `direccion`
- **Índices GIN**: Para búsquedas ILIKE ultra-rápidas
- **Paginación**: Limita resultados por página
- **Debounce**: Reduce peticiones innecesarias
- **Conexiones de BD**: Pool de conexiones optimizado

## 🛠️ Desarrollo

### Estructura de la base de datos

```sql
CREATE TABLE establecimientos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    direccion VARCHAR(500),
    localidad VARCHAR(255),
    provincia VARCHAR(255)
);
```

### Índices creados automáticamente

- `idx_establecimientos_provincia`
- `idx_establecimientos_nombre`
- `idx_establecimientos_direccion`
- `idx_establecimientos_nombre_ilike` (GIN)
- `idx_establecimientos_direccion_ilike` (GIN)

## 📝 Formato de datos JSON esperado

El archivo `tu_archivo_grande.json` debe tener la siguiente estructura:

```json
[
  {
    "nombre": "Nombre del establecimiento",
    "direccion": "Dirección completa",
    "localidad": "Ciudad/Pueblo",
    "provincia": "Provincia"
  }
]
```

## 🐛 Solución de Problemas

### Error de conexión a la base de datos
- Verifica que PostgreSQL esté ejecutándose
- Confirma que la `DATABASE_URL` sea correcta
- Asegúrate de que la base de datos existe

### Error CORS en el frontend
- Verifica que el backend esté ejecutándose en el puerto correcto
- Modifica `apiBaseUrl` en `app.js` si es necesario

### Búsquedas lentas
- Ejecuta el script `load_data.py` para crear los índices
- Verifica que los índices se hayan creado correctamente

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de solución de problemas
2. Busca en los issues existentes
3. Crea un nuevo issue con detalles del problema

---

**Desarrollado con ❤️ para facilitar la búsqueda de establecimientos en España**
