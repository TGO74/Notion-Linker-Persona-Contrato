import os
import logging
import datetime
from dotenv import load_dotenv
from notion_service import NotionService
from analysis_service import ProcessingAnalyzer

# --- CONFIGURACIÓN ---
load_dotenv()
# Nombres de propiedades en Notion (ajusta si es necesario)
CONTRATO_NOMBRE_PROP = "NOMBRE ORDENADO"
CONTRATO_CORREO_PROP = "CORREO"
CONTRATO_SEXO_PROP = "SEXO"
CONTRATO_RELACION_PROP = "PERSONAS"
PERSONA_NOMBRE_PROP = "NOMBRE"
# Configuraciones de ejecución
BATCH_SIZE = 10
DRY_RUN = False  # Poner en True para simular sin hacer cambios reales
REQUESTS_PER_SECOND = 2.5

# --- Configuración de Logging ---
logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler('notion_linker.log', 'a', 'utf-8')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)

# --- Funciones Auxiliares ---
def clean_name(name: str) -> str:
    """Limpia y normaliza un nombre para consistencia."""
    if not name: return ""
    cleaned = name.strip().upper()
    replacements = {'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ñ': 'N'}
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    return cleaned

def extract_property_value(properties: dict, prop_name: str) -> str:
    """Extrae el valor de texto de varios tipos de propiedades de Notion."""
    prop = properties.get(prop_name)
    if not prop: return ""
    
    prop_type = prop.get("type", "")
    if prop_type in ["title", "rich_text"]:
        key = "title" if prop_type == "title" else "rich_text"
        if prop.get(key): return prop[key][0].get("plain_text", "")
    elif prop_type == "email":
        return prop.get("email", "")
    elif prop_type == "select" and prop.get("select"):
        return prop["select"].get("name", "")
    return ""

# --- Lógica Principal ---
def main():
    """Orquesta el proceso completo de sincronización y enriquecimiento de datos."""
    start_time = datetime.datetime.now()
    logger.info(f"🚀 Iniciando proceso: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if DRY_RUN:
        logger.warning("🧪 MODO DRY-RUN ACTIVADO - No se realizarán cambios en Notion.")

    contratos_db_id = os.getenv("CONTRATOS_DB_ID")
    personas_db_id = os.getenv("PERSONAS_DB_ID")
    
    notion = NotionService(
        contract_relation_prop=CONTRATO_RELACION_PROP,
        requests_per_second=REQUESTS_PER_SECOND
    )
    analyzer = ProcessingAnalyzer()
    
    logger.info(f"Iniciando la sincronización. Se procesarán hasta {BATCH_SIZE} contratos sin enlace.")
    
    # 1. Obtener un lote de contratos que NO tengan la relación de persona
    contracts_to_process = notion.get_unlinked_contracts(contratos_db_id, BATCH_SIZE)
    
    if not contracts_to_process:
        logger.info("🎉 ¡Excelente! No se encontraron contratos pendientes de enlazar.")
        return
        
    total_in_batch = len(contracts_to_process)
    analyzer.start_session()
    analyzer.stats['total_processed'] = total_in_batch

    person_cache = {}

    # 2. Iterar sobre cada contrato del lote
    for idx, contract in enumerate(contracts_to_process):
        contract_id = contract["id"]
        properties = contract["properties"]
        
        person_name = clean_name(extract_property_value(properties, CONTRATO_NOMBRE_PROP))
        
        if not person_name:
            analyzer.record_skipped_empty_name(contract_id)
            continue
            
        correo = extract_property_value(properties, CONTRATO_CORREO_PROP).strip()
        sexo = extract_property_value(properties, CONTRATO_SEXO_PROP)
        
        logger.info(f"⚙️ ({idx+1}/{total_in_batch}) Procesando: {person_name}")
        person_page_id = None
        
        # 3. Buscar o crear la persona (con caché para eficiencia)
        if person_name in person_cache:
            person_page_id = person_cache[person_name]
            logger.info("   -> Encontrado en caché.")
            analyzer.record_cache_hit()
        else:
            person_page = notion.find_person_by_name(personas_db_id, PERSONA_NOMBRE_PROP, person_name)
            
            if person_page:  # La persona ya existe
                person_page_id = person_page["id"]
                analyzer.record_existing_person_found(person_name, person_page_id)
                
                # 4. Lógica de enriquecimiento: Actualizar si las propiedades están vacías
                props_to_update = {}
                person_props = person_page.get("properties", {})
                
                if correo and not extract_property_value(person_props, "CORREO"):
                    props_to_update["CORREO"] = {"email": correo}
                if sexo and not extract_property_value(person_props, "SEXO"):
                    props_to_update["SEXO"] = {"select": {"name": sexo}}
                
                if props_to_update:
                    logger.info(f"   -> Actualizando propiedades existentes: {list(props_to_update.keys())}")
                    if not DRY_RUN:
                        notion.update_person_properties(person_page_id, props_to_update)
                    analyzer.record_properties_updated(person_page_id, person_name, list(props_to_update.keys()))
            
            else:  # La persona no existe, se debe crear
                logger.info(f"   -> No encontrado. Creando persona con datos: Correo='{correo}', Sexo='{sexo}'")
                if not DRY_RUN:
                    new_person_page = notion.create_person(personas_db_id, PERSONA_NOMBRE_PROP, person_name, correo, sexo)
                    if new_person_page: person_page_id = new_person_page.get("id")
                else:
                    person_page_id = "DRY_RUN_ID"
                
                if person_page_id: analyzer.record_new_person_created(person_name, person_page_id)
            
            if person_page_id and person_page_id != "DRY_RUN_ID":
                person_cache[person_name] = person_page_id

        # 5. Enlazar el contrato con la persona
        if person_page_id:
            if not DRY_RUN:
                notion.link_person_to_contract(contract_id, person_page_id)
            analyzer.record_successful_link(contract_id, person_name, person_page_id)
        else:
            analyzer.record_error(contract_id, person_name, "No se pudo encontrar o crear la persona.")

    # 6. Finalizar y generar reportes
    analyzer.end_session()
    analyzer.generate_console_report()
    analyzer.export_cumulative_reports()
    analyzer.save_session_table_report()
    
    logger.info("✅ Proceso de lote finalizado.")

if __name__ == "__main__":
    main()