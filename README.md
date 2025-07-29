# 🔗 Notion Linker - Automatización de Vinculación de Bases de Datos

Este proyecto automatiza la vinculación entre dos bases de datos en Notion: **Contratos** y **Personas**. El script lee los nombres de los contratos, busca o crea las personas correspondientes, y establece las relaciones automáticamente.

## 🏛️ Arquitectura del Proyecto

```
notion_linker/
├── .env                    # Configuración y credenciales
├── main.py                 # Script principal
├── notion_service.py       # Servicio de Notion API
├── requirements.txt        # Dependencias de Python
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
PERSONA_NOMBRE_PROP = "Nombre"            # Columna principal en BD Personas
```

## 🎯 Uso

```bash
python main.py
```

El script:
1. ✅ Lee todos los contratos de tu base de datos
2. 🔍 Busca cada persona por nombre
3. ➕ Crea personas nuevas si no existen
4. 🔗 Vincula cada contrato con su persona correspondiente
5. 💾 Usa caché para evitar búsquedas repetidas

## 📊 Funcionalidades

- **Búsqueda Inteligente**: Busca personas existentes antes de crear nuevas
- **Caché Local**: Evita búsquedas repetidas para mejorar rendimiento
- **Manejo de Errores**: Continúa procesando aunque algunos elementos fallen
- **Rate Limiting**: Respeta los límites de la API de Notion
- **Logging Detallado**: Muestra el progreso en tiempo real

## ⚙️ Personalización

### Cambiar Nombres de Columnas

Si tus columnas se llaman diferente, edita estas variables en `main.py`:

```python
CONTRATO_NOMBRE_PROP = "TU_COLUMNA_NOMBRE"
CONTRATO_RELACION_PROP = "TU_COLUMNA_RELACION"
PERSONA_NOMBRE_PROP = "TU_COLUMNA_PERSONA"
```

### Agregar Propiedades Adicionales

Para incluir más datos al crear personas, edita `notion_service.py`:

```python
new_page_properties = {
    "Nombre": {
        "title": [{"text": {"content": name}}]
    },
    "Email": {
        "email": "ejemplo@email.com"
    },
    "Teléfono": {
        "phone_number": "+1234567890"
    }
}
```

## 🔧 Solución de Problemas

### Error: "Asegúrate de que las variables de entorno estén bien configuradas"
- Verifica que el archivo `.env` existe y tiene los valores correctos
- Asegúrate de que no hay espacios extra en los valores

### Error: "Error al consultar la base de datos"
- Verifica que tu API key es correcta
- Confirma que tu integración tiene permisos en ambas bases de datos

### Error: "Error buscando persona"
- Verifica que el nombre de la columna en `PERSONA_NOMBRE_PROP` es correcto
- Asegúrate de que la base de datos de Personas existe

## 📝 Notas Importantes

- El script normaliza los nombres (convierte a mayúsculas) para evitar duplicados
- Solo procesa contratos que no tienen relación ya establecida
- Incluye pausas automáticas para respetar los límites de la API
- Los errores no detienen el proceso completo

## 🤝 Contribuir

Si encuentras bugs o quieres agregar funcionalidades:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

---

¡Listo! Tu automatización de vinculación de bases de datos en Notion está completa. 🎉 