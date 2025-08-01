# 🔗 Notion Linker - Automatización de Vinculación de Bases de Datos

Este proyecto automatiza la vinculación entre dos bases de datos en Notion: **Contratos** y **Personas**. El script lee los nombres de los contratos, busca o crea las personas correspondientes, y establece las relaciones automáticamente.

## 🏛️ Arquitectura del Proyecto

```
notion_linker/
├── .env                    # Configuración y credenciales
├── .env.example           # Ejemplo de configuración
├── main.py                 # Script principal (procesamiento por lotes)
├── notion_service.py       # Servicio de Notion API (robusto)
├── analysis_service.py     # Servicio de análisis y reportes
├── test_functions.py      # Tests para funciones críticas
├── requirements.txt        # Dependencias de Python
├── notion_linker.log      # Logs de ejecución
└── README.md              # Este archivo
```

## 🚀 Instalación y Configuración

### 1. Preparar el Entorno

```bash
# Crear entorno virtual (recomendado)
python -m venv venv

# Activar el entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Credenciales

Copia el archivo de ejemplo y edítalo con tus datos reales:

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus datos reales:

```ini
# Archivo de configuración - Reemplaza con tus valores reales
NOTION_API_KEY=secret_tu_api_key_aqui
CONTRATOS_DB_ID=tu_id_base_datos_contratos
PERSONAS_DB_ID=tu_id_base_datos_personas
```

#### Cómo obtener estos valores:

1. **NOTION_API_KEY**: 
   - Ve a [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
   - Crea una nueva integración
   - Copia el "Internal Integration Token"

2. **CONTRATOS_DB_ID** y **PERSONAS_DB_ID**:
   - Abre tu base de datos en Notion
   - Copia la parte alfanumérica de la URL
   - Ejemplo: `https://www.notion.so/tuworkspace/1234567890abcdef` → `1234567890abcdef`

### 3. Configurar Permisos en Notion

1. Ve a tu base de datos de **Contratos**
2. Haz clic en "..." → "Add connections"
3. Selecciona tu integración
4. Repite el proceso para la base de datos de **Personas**

### 4. Ajustar Nombres de Propiedades

En el archivo `main.py`, verifica que estos nombres coincidan con tus columnas:

```python
CONTRATO_NOMBRE_PROP = "NOMBRE ORDENADO"  # Columna con el nombre en BD Contratos
CONTRATO_RELACION_PROP = "PERSONAS"       # Columna de relación en BD Contratos
PERSONA_NOMBRE_PROP = "NOMBRE"            # Columna principal en BD Personas
```

## 🧪 Testing

Antes de ejecutar el script principal, puedes probar las funciones críticas:

```bash
python test_functions.py
```

Este comando ejecutará tests para:
- ✅ **Limpieza de nombres**: Verifica que `clean_name()` funcione correctamente
- ✅ **Extracción de propiedades**: Valida `extract_property_value()` con diferentes tipos
- ✅ **Validación de entorno**: Confirma que `validate_environment()` detecte errores

## 🎯 Uso

```bash
python main.py
```

El script:
1. ✅ **Valida el entorno** antes de ejecutar
2. 🔍 **Verifica conexiones** a las bases de datos
3. 📋 **Valida propiedades** en ambas bases de datos
4. ⚙️ **Procesa en lotes** de forma segura
5. 🔄 **Reintenta automáticamente** en caso de errores
6. ⚡ **Maneja rate limiting** automáticamente
7. 📊 **Genera reportes** detallados y exporta a CSV
8. 🧹 **Limpia recursos** al finalizar
9. ⏱️ **Registra duración** total del proceso

## 🆕 Nuevas Funcionalidades (v4.1)

### 🧪 **Testing Automatizado**
- **Tests unitarios**: Valida funciones críticas antes de ejecutar
- **Cobertura completa**: Tests para limpieza de nombres, extracción de propiedades y validación
- **Fácil ejecución**: `python test_functions.py` para verificar todo

### 🔧 **Extracción Dinámica de Propiedades**
- **Manejo inteligente**: Detecta automáticamente el tipo de propiedad en Notion
- **Múltiples tipos**: Soporta `rich_text`, `title`, `select`, `multi_select`, `formula`, `rollup`
- **Fallback seguro**: Maneja propiedades no reconocidas de forma segura
- **Logging detallado**: Registra tipos de propiedades no manejados

### 🛡️ **DRY_RUN Mejorado**
- **Caché seguro**: No almacena IDs falsos en el caché durante dry-run
- **Manejo de excepciones**: Captura y registra errores durante el enlace
- **Simulación completa**: Ejecuta todo el flujo sin hacer cambios reales

### ⏱️ **Logging de Duración**
- **Tiempo total**: Registra duración completa del proceso
- **Timestamps**: Muestra hora de inicio y fin
- **Métricas**: Incluye duración en los logs finales

### ⚡ **Rate Limiting Inteligente**
- **Control automático**: Sistema de rate limiting integrado que respeta los límites de la API
- **Configuración flexible**: Ajusta `REQUESTS_PER_SECOND` según tus necesidades
- **Detección de errores**: Maneja automáticamente errores 429 (rate limit)
- **Backoff exponencial**: Espera progresivamente más tiempo en caso de errores
- **Burst protection**: Previene picos de requests que podrían causar bloqueos

### 🛡️ **Robustez y Confiabilidad**
- **Validación previa**: Verifica conexiones y propiedades antes de procesar
- **Reintentos automáticos**: Manejo robusto de errores de API con backoff exponencial
- **Validación de resultados**: Verifica que las operaciones se completaron correctamente
- **Limpieza de nombres**: Normaliza nombres para evitar duplicados
- **Logging estructurado**: Logs detallados en archivo y consola

### 🧪 **Modo Dry-Run**
- **Pruebas seguras**: Activa `DRY_RUN = True` en `main.py` para probar sin modificar Notion
- **Simulación completa**: Ejecuta todo el proceso sin hacer cambios reales
- **Validación de lógica**: Verifica que el script funciona correctamente

### 📊 **Análisis y Reportes Avanzados**
- **Reporte en consola**: Estadísticas detalladas en tiempo real
- **Exportación a CSV**: Múltiples archivos CSV con datos estructurados
- **Reporte en tabla**: Formato ASCII para fácil lectura
- **Seguimiento de errores**: Lista detallada de errores con timestamps
- **Estadísticas de rendimiento**: Tasa de éxito, duración, hits en caché

### 📦 **Procesamiento por Lotes**
- **BATCH_SIZE = 25**: Procesa solo 25 registros por ejecución
- **Ejecución múltiple**: Puedes ejecutar el script varias veces para procesar todos los registros
- **Control seguro**: Evita procesar miles de registros de una vez

### 🔍 **Consulta Optimizada**
- **Filtro directo**: Solo consulta contratos donde la columna PERSONAS esté vacía
- **Menos uso de API**: Reduce significativamente las llamadas a la API de Notion
- **Más rápido**: Evita traer todos los registros y filtrarlos localmente

### ⚙️ **Configuración Flexible**
- **Ajusta el lote**: Cambia `BATCH_SIZE` en `main.py` según tus necesidades
- **Pruebas seguras**: Comienza con 5-10 registros para probar
- **Producción**: Aumenta a 50-100 para procesar más rápido

## 📊 Funcionalidades

- **Búsqueda Inteligente**: Busca personas existentes antes de crear nuevas
- **Caché Local**: Evita búsquedas repetidas para mejorar rendimiento
- **Manejo de Errores**: Continúa procesando aunque algunos elementos fallen
- **Rate Limiting Automático**: Respeta los límites de la API de Notion
- **Logging Detallado**: Muestra el progreso en tiempo real
- **Procesamiento por Lotes**: Control seguro del número de registros procesados
- **Análisis Completo**: Estadísticas detalladas y reportes exportables
- **Validación Robusta**: Verifica conexiones y propiedades antes de procesar
- **Reintentos Automáticos**: Maneja errores temporales de la API
- **Modo Dry-Run**: Prueba sin hacer cambios reales
- **Testing Automatizado**: Valida funciones críticas antes de ejecutar
- **Extracción Dinámica**: Maneja diferentes tipos de propiedades de Notion

## 📈 Reportes Generados

### 1. Reporte en Consola
```
📊 REPORTE DE PROCESAMIENTO
============================================================
📈 Total procesado: 25
✅ Enlaces exitosos: 23
❌ Errores: 2
⏱️  Duración: 0:00:45.123456

👥 PERSONAS:
   ➕ Nuevas creadas: 5
   🔍 Existentes encontradas: 18
   💾 Hits en caché: 3

⏭️  Saltados (nombres vacíos): 0
📊 Tasa de éxito: 92.0%
```

### 2. Archivos CSV Exportados
- **`reporte_procesamiento_YYYYMMDD_HHMMSS_resumen.csv`**: Estadísticas generales
- **`reporte_procesamiento_YYYYMMDD_HHMMSS_contratos.csv`**: Detalle de cada contrato procesado
- **`reporte_procesamiento_YYYYMMDD_HHMMSS_nuevas_personas.csv`**: Lista de nuevas personas creadas
- **`reporte_procesamiento_YYYYMMDD_HHMMSS_errores.csv`**: Detalle de errores encontrados

### 3. Reporte en Tabla
```
┌─────────────────────────────────┬─────────────┐
│ Métrica                        │ Valor       │
├─────────────────────────────────┼─────────────┤
│ Total Procesado                │          25 │
│ Enlaces Exitosos               │          23 │
│ Errores                        │           2 │
│ Nuevas Personas Creadas        │           5 │
│ Personas Existentes Encontradas│          18 │
│ Hits en Caché                  │           3 │
│ Saltados (Nombres Vacíos)      │           0 │
│ Tasa de Éxito (%)              │        92.0 │
└─────────────────────────────────┴─────────────┘
```

### 4. Logs Detallados
- **`notion_linker.log`**: Logs del script principal
- **`notion_service.log`**: Logs específicos del servicio de Notion

## ⚙️ Personalización

### Configurar Rate Limiting

Para ajustar el comportamiento de rate limiting, edita en `main.py`:

```python
REQUESTS_PER_SECOND = 2.0  # Más conservador: 2 requests/segundo
REQUESTS_PER_SECOND = 3.0  # Más agresivo: 3 requests/segundo (límite máximo)
```

### Modo Dry-Run (Pruebas)

Para probar sin hacer cambios reales, edita en `main.py`:

```python
DRY_RUN = True  # Cambia a True para probar sin modificar Notion
```

### Cambiar Tamaño del Lote

Para procesar más o menos registros por ejecución, edita en `main.py`:

```python
BATCH_SIZE = 10  # Para procesar solo 10 registros
BATCH_SIZE = 50  # Para procesar 50 registros
```

### Cambiar Nombres de Columnas

Si tus columnas se llaman diferente, edita estas variables en `main.py`:

```python
CONTRATO_NOMBRE_PROP = "TU_COLUMNA_NOMBRE"
CONTRATO_RELACION_PROP = "TU_COLUMNA_RELACION"
PERSONA_NOMBRE_PROP = "TU_COLUMNA_PERSONA"
```

### Configurar Reintentos

Para ajustar el comportamiento de reintentos, edita en `notion_service.py`:

```python
notion = NotionService(
    contract_relation_prop=CONTRATO_RELACION_PROP,
    max_retries=5,      # Número de reintentos
    retry_delay=3,      # Segundos entre reintentos
    requests_per_second=2.5  # Rate limiting
)
```

## 🔧 Solución de Problemas

### Error: "Variables de entorno faltantes"
- Verifica que el archivo `.env` existe y tiene los valores correctos
- Usa `.env.example` como plantilla
- Asegúrate de que no hay espacios extra en los valores

### Error: "No se puede conectar a la base de datos"
- Verifica que tu API key es correcta
- Confirma que tu integración tiene permisos en ambas bases de datos
- Revisa los logs en `notion_service.log` para más detalles

### Error: "Propiedad no encontrada en BD"
- Verifica que los nombres de las propiedades en `main.py` coinciden exactamente
- Revisa los logs para ver las propiedades disponibles
- Confirma que las propiedades existen en las bases de datos

### El script no encuentra contratos para procesar
- Verifica que hay contratos sin enlazar en tu base de datos
- Confirma que la columna `CONTRATO_RELACION_PROP` está configurada correctamente
- Usa el modo dry-run para verificar la lógica

### Errores de API frecuentes
- El script incluye reintentos automáticos
- Revisa los logs para ver si hay problemas de conectividad
- Considera aumentar `retry_delay` si hay muchos errores

### Errores de Rate Limiting
- El sistema de rate limiting es automático
- Si ves errores 429, el script esperará automáticamente
- Considera reducir `REQUESTS_PER_SECOND` si hay muchos errores de rate limiting

### Los archivos CSV no se generan
- Verifica que tienes permisos de escritura en la carpeta del proyecto
- Asegúrate de que no hay otros procesos usando los archivos
- Revisa los logs para errores de escritura

### Tests fallan
- Ejecuta `python test_functions.py` para identificar problemas
- Verifica que todas las dependencias están instaladas
- Revisa que el archivo `main.py` está en el mismo directorio

## 📝 Notas Importantes

- **Rate limiting automático**: El script maneja automáticamente los límites de la API
- **Validación previa**: El script valida todo antes de procesar
- **Reintentos automáticos**: Maneja errores temporales de la API
- **Limpieza de nombres**: Normaliza nombres para evitar duplicados
- **Modo dry-run**: Prueba sin hacer cambios reales
- **Logging completo**: Todos los eventos se registran en archivos
- **Limpieza de recursos**: El caché se limpia automáticamente
- **Validación de resultados**: Verifica que las operaciones fueron exitosas
- **Testing automatizado**: Valida funciones críticas antes de ejecutar
- **Extracción dinámica**: Maneja diferentes tipos de propiedades de Notion

## 🚀 Flujo de Trabajo Recomendado

1. **Configura las credenciales** usando `.env.example`
2. **Ejecuta los tests**: `python test_functions.py`
3. **Prueba con dry-run**: `DRY_RUN = True`
4. **Ejecuta el script**: `python main.py`
5. **Revisa los logs**: `notion_linker.log` y `notion_service.log`
6. **Verifica los reportes** generados (consola, CSV, tabla)
7. **Desactiva dry-run**: `DRY_RUN = False`
8. **Prueba con un lote pequeño**: `BATCH_SIZE = 5`
9. **Ejecuta en producción**: `BATCH_SIZE = 25`
10. **Ejecuta repetidamente** hasta procesar todos los registros
11. **Analiza los reportes CSV** para identificar patrones o problemas

## 📊 Análisis de Datos

Los archivos CSV generados te permiten:

- **Analizar patrones de errores** para mejorar el proceso
- **Identificar nombres problemáticos** que necesitan atención manual
- **Seguir el progreso** a lo largo de múltiples ejecuciones
- **Generar estadísticas** para reportes de gestión
- **Auditar las nuevas personas** creadas automáticamente
- **Monitorear rendimiento** de la API de Notion

## 🛡️ Características de Seguridad

- **Rate limiting inteligente**: Respeta automáticamente los límites de la API
- **Validación completa**: Verifica todo antes de procesar
- **Reintentos inteligentes**: Maneja errores temporales
- **Modo dry-run**: Prueba sin riesgo
- **Logging detallado**: Auditoría completa de operaciones
- **Limpieza de datos**: Normaliza nombres para evitar duplicados
- **Validación de resultados**: Confirma que las operaciones fueron exitosas
- **Testing automatizado**: Valida funciones críticas antes de ejecutar

## ⚡ Rate Limiting Detallado

### ¿Por qué es importante?
Notion permite un promedio de **3 solicitudes por segundo**. Si superas este límite, la API te devolverá un error 429 y podrías ser bloqueado temporalmente.

### ¿Cómo funciona nuestro sistema?
1. **Control automático**: Cada llamada a la API espera automáticamente si es necesario
2. **Configuración segura**: Por defecto usa 2.5 requests/segundo (por debajo del límite)
3. **Detección de errores**: Si recibe un error 429, espera progresivamente más tiempo
4. **Burst protection**: Previene picos de requests que podrían causar bloqueos

### Configuración recomendada:
- **Desarrollo/Pruebas**: `REQUESTS_PER_SECOND = 1.5` (muy conservador)
- **Producción**: `REQUESTS_PER_SECOND = 2.5` (seguro)
- **Alto rendimiento**: `REQUESTS_PER_SECOND = 3.0` (límite máximo)

## 🤝 Contribuir

Si encuentras bugs o quieres agregar funcionalidades:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

---

¡Listo! Tu automatización de vinculación de bases de datos en Notion está completa, robusta y lista para producción. 🎉