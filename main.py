import os
import time
import logging
import datetime
from dotenv import load_dotenv
from notion_service import NotionService
from analysis_service import ProcessingAnalyzer

# --- CONFIGURACIÓN ---
load_dotenv()

# ¡AJUSTA ESTOS VALORES SI TUS COLUMNAS SE LLAMAN DIFERENTE!
CONTRATO_NOMBRE_PROP = "NOMBRE ORDENADO"
CONTRATO_RELACION_PROP = "PERSONAS"
PERSONA_NOMBRE_PROP = "NOMBRE" # La columna principal (título) en tu BD de Personas

# ¡NUEVO! Define cuántos registros procesar en cada ejecución para probar de forma segura.
BATCH_SIZE = 25

# ¡NUEVO! Modo de prueba sin realizar cambios reales
DRY_RUN = True  # Cambia a True para probar sin modificar Notion

# ¡NUEVO! Configuración de rate limiting
REQUESTS_PER_SECOND = 2.5  # Límite seguro: 2.5 requests/segundo (por debajo del límite de 3)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('notion_linker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def validate_environment():
    """Valida que todas las variables de entorno estén configuradas."""
    required_vars = ["NOTION_API_KEY", "CONTRATOS_DB_ID", "PERSONAS_DB_ID"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Variables de entorno faltantes: {missing_vars}")
        return False
    
    logger.info("✅ Variables de entorno configuradas correctamente")
    return True

def validate_notion_connection(notion_service, contratos_db_id, personas_db_id):
    """Valida la conexión y propiedades de las bases de datos."""
    logger.info("🔍 Validando conexión a Notion...")
    
    # Validar conexión a BD de Contratos
    if not notion_service.validate_database_connection(contratos_db_id):
        logger.error("❌ No se puede conectar a la base de datos de Contratos")
        return False
    
    # Validar conexión a BD de Personas
    if not notion_service.validate_database_connection(personas_db_id):
        logger.error("❌ No se puede conectar a la base de datos de Personas")
        return False
    
    # Validar propiedades en BD de Contratos
    if not notion_service.validate_property_exists(contratos_db_id, CONTRATO_NOMBRE_PROP):
        logger.error(f"❌ Propiedad '{CONTRATO_NOMBRE_PROP}' no encontrada en BD de Contratos")
        return False
    
    if not notion_service.validate_property_exists(contratos_db_id, CONTRATO_RELACION_PROP):
        logger.error(f"❌ Propiedad '{CONTRATO_RELACION_PROP}' no encontrada en BD de Contratos")
        return False
    
    # Validar propiedades en BD de Personas
    if not notion_service.validate_property_exists(personas_db_id, PERSONA_NOMBRE_PROP):
        logger.error(f"❌ Propiedad '{PERSONA_NOMBRE_PROP}' no encontrada en BD de Personas")
        return False
    
    logger.info("✅ Todas las validaciones de conexión exitosas")
    return True

def clean_name(name):
    """Limpia y normaliza un nombre para evitar duplicados."""
    if not name:
        return ""
    
    # Limpiar espacios extra y normalizar
    cleaned = name.strip().upper()
    
    # Remover caracteres problemáticos comunes
    replacements = {
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ü': 'U', 'Ñ': 'N',
        'À': 'A', 'È': 'E', 'Ì': 'I', 'Ò': 'O', 'Ù': 'U',
        'Â': 'A', 'Ê': 'E', 'Î': 'I', 'Ô': 'O', 'Û': 'U'
    }
    
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    
    return cleaned

def extract_property_value(properties, property_name):
    """
    Extrae el valor de una propiedad de Notion de forma dinámica.
    Maneja diferentes tipos de propiedades (rich_text, title, etc.)
    """
    if not properties or property_name not in properties:
        return ""
    
    prop = properties[property_name]
    prop_type = prop.get("type", "")
    
    if prop_type == "rich_text":
        rich_text_list = prop.get("rich_text", [])
        if rich_text_list:
            return rich_text_list[0].get("plain_text", "")
    elif prop_type == "title":
        title_list = prop.get("title", [])
        if title_list:
            return title_list[0].get("plain_text", "")
    elif prop_type == "select":
        select_obj = prop.get("select", {})
        return select_obj.get("name", "")
    elif prop_type == "multi_select":
        multi_select_list = prop.get("multi_select", [])
        if multi_select_list:
            return multi_select_list[0].get("name", "")
    elif prop_type == "formula":
        formula_obj = prop.get("formula", {})
        return formula_obj.get("string", "") or str(formula_obj.get("number", ""))
    elif prop_type == "rollup":
        rollup_obj = prop.get("rollup", {})
        if rollup_obj.get("type") == "array":
            array_list = rollup_obj.get("array", [])
            if array_list:
                return str(array_list[0])
    
    # Fallback: intentar extraer como string genérico
    logger.warning(f"⚠️ Tipo de propiedad '{property_name}' no manejado: {prop_type}")
    return str(prop.get("string", "") or prop.get("number", "") or "")

# --- LÓGICA PRINCIPAL ---
def main():
    """Orquesta el proceso de sincronización por lotes con validaciones robustas."""
    
    # Registrar tiempo de inicio
    start_time = datetime.datetime.now()
    logger.info(f"🚀 Iniciando proceso de vinculación: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Validar entorno
    if not validate_environment():
        return
    
    contratos_db_id = os.getenv("CONTRATOS_DB_ID")
    personas_db_id = os.getenv("PERSONAS_DB_ID")
    
    # 2. Inicializar servicios con rate limiting configurado
    notion = NotionService(
        contract_relation_prop=CONTRATO_RELACION_PROP,
        requests_per_second=REQUESTS_PER_SECOND
    )
    analyzer = ProcessingAnalyzer()
    analyzer.start_session()
    
    # 3. Validar conexión y propiedades
    if not validate_notion_connection(notion, contratos_db_id, personas_db_id):
        analyzer.end_session()
        return
    
    # 4. Mostrar modo de ejecución y configuración de rate limiting
    if DRY_RUN:
        logger.warning("🧪 MODO DRY-RUN ACTIVADO - No se realizarán cambios en Notion")
    else:
        logger.info("🚀 MODO PRODUCCIÓN - Se realizarán cambios en Notion")
    
    logger.info(f"⚡ Rate limiting configurado: {REQUESTS_PER_SECOND} requests/segundo")
    logger.info(f"📦 Tamaño de lote: {BATCH_SIZE} registros")
    
    person_cache = {} # Caché para optimizar { "nombre": "page_id" }

    logger.info(f"🚀 Iniciando la sincronización. Se procesarán hasta {BATCH_SIZE} contratos sin enlace por ejecución.")
    
    # 5. Obtener un lote de contratos que NO tengan la relación de persona
    contracts_to_process = notion.get_unlinked_contracts(contratos_db_id, BATCH_SIZE)
    
    if not contracts_to_process:
        logger.info("🎉 ¡Excelente! No se encontraron contratos pendientes de enlazar.")
        analyzer.end_session()
        analyzer.generate_console_report()
        return
        
    total_contracts = len(contracts_to_process)
    analyzer.stats['total_processed'] = total_contracts
    logger.info(f"🔍 Se encontraron {total_contracts} contratos para procesar en este lote.")

    # 6. Iterar sobre cada contrato del lote
    for idx, contract in enumerate(contracts_to_process):
        contract_id = contract["id"]
        properties = contract["properties"]

        # Extraer y limpiar nombre del contrato usando función dinámica
        person_name_raw = extract_property_value(properties, CONTRATO_NOMBRE_PROP)
        if not person_name_raw:
            logger.warning(f"⚠️  ({idx+1}/{total_contracts}) Saltando contrato {contract_id}: sin nombre.")
            analyzer.record_skipped_empty_name(contract_id)
            continue
        
        person_name = clean_name(person_name_raw)

        if not person_name:
            logger.warning(f"⚠️  ({idx+1}/{total_contracts}) Saltando contrato {contract_id}: el nombre está vacío después de limpiar.")
            analyzer.record_skipped_empty_name(contract_id)
            continue
        
        logger.info(f"⚙️  ({idx+1}/{total_contracts}) Procesando: {person_name}")
        person_page_id = None

        # 7. Buscar o crear la persona (con caché)
        if person_name in person_cache:
            person_page_id = person_cache[person_name]
            logger.info(f"   -> Encontrado en caché.")
            analyzer.record_cache_hit()
        else:
            person_page = notion.find_person_by_name(personas_db_id, PERSONA_NOMBRE_PROP, person_name)
            if person_page:
                person_page_id = person_page.get("id")
                if person_page_id:
                    logger.info(f"   -> Encontrado en Notion.")
                    analyzer.record_existing_person_found(person_name, person_page_id)
                else:
                    logger.error(f"   -> Error: Persona encontrada pero sin ID válido")
                    analyzer.record_error(contract_id, person_name, "Persona sin ID válido")
                    continue
            else:
                if not DRY_RUN:
                    logger.info(f"   -> No encontrado. Creando persona...")
                    new_person_page = notion.create_person(personas_db_id, PERSONA_NOMBRE_PROP, person_name)
                    if new_person_page:
                        person_page_id = new_person_page.get("id")
                        if person_page_id:
                            analyzer.record_new_person_created(person_name, person_page_id)
                        else:
                            logger.error(f"   -> Error: Persona creada pero sin ID válido")
                            analyzer.record_error(contract_id, person_name, "Persona creada sin ID válido")
                            continue
                    else:
                        logger.error(f"   -> Error al crear persona")
                        analyzer.record_error(contract_id, person_name, "Error al crear persona")
                        continue
                else:
                    logger.info(f"   -> [DRY-RUN] Simulando creación de persona: {person_name}")
                    analyzer.record_new_person_created(person_name, "DRY_RUN_ID")
                    person_page_id = "DRY_RUN_ID"
            
            # ¡MEJORA! Solo almacenar en caché si NO estamos en DRY_RUN
            if not DRY_RUN and person_page_id:
                person_cache[person_name] = person_page_id

        # 8. Enlazar la persona al contrato
        if person_page_id:
            if not DRY_RUN:
                try:
                    success = notion.link_person_to_contract(contract_id, person_page_id)
                    if success:
                        logger.info(f"   -> Enlace completado.")
                        analyzer.record_successful_link(contract_id, person_name, person_page_id)
                    else:
                        error_msg = "Error al enlazar - validación falló"
                        logger.error(f"   -> 🛑 {error_msg}")
                        analyzer.record_error(contract_id, person_name, error_msg)
                except Exception as e:
                    error_msg = f"Excepción al enlazar: {str(e)}"
                    logger.error(f"   -> 🛑 {error_msg}")
                    analyzer.record_error(contract_id, person_name, error_msg)
            else:
                logger.info(f"   -> [DRY-RUN] Simulando enlace: {person_name}")
                analyzer.record_successful_link(contract_id, person_name, person_page_id)
        else:
            error_msg = "No se pudo obtener el ID de la persona"
            logger.error(f"   -> 🛑 {error_msg}")
            analyzer.record_error(contract_id, person_name, error_msg)

        # 9. Rate limiting automático (ya manejado por NotionService)
        # No necesitamos time.sleep() aquí porque el rate limiting se maneja automáticamente

    # 10. Limpiar caché
    person_cache.clear()
    logger.info("🧹 Caché de personas limpiado")

    # 11. Mostrar estadísticas de rate limiting
    rate_stats = notion.get_rate_limit_stats()
    logger.info(f"📊 Estadísticas de rate limiting: {rate_stats['current_request_count']} requests procesados")

    # 12. Finalizar análisis y generar reportes
    analyzer.end_session()
    
    # Generar reporte en consola
    analyzer.generate_console_report()
    
    # Exportar a CSV
    csv_prefix = analyzer.export_to_csv()
    
    # Generar y guardar reporte en tabla
    analyzer.save_table_report()
    
    # 13. Registrar duración total del proceso
    end_time = datetime.datetime.now()
    duration = end_time - start_time
    logger.info(f"⏱️ Duración total del proceso: {duration}")
    logger.info(f"🎉 Lote de {total_contracts} registros procesado. Vuelve a ejecutar el script para procesar el siguiente lote.")
    logger.info(f"📊 Reportes generados con prefijo: {csv_prefix}")

if __name__ == "__main__":
    main() 