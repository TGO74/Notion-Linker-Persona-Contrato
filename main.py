import os
import time
from dotenv import load_dotenv
from notion_service import NotionService

# --- CONFIGURACIÓN ---
# Carga las variables del archivo .env
load_dotenv()

# Nombres de las propiedades en tus bases de datos de Notion.
# ¡AJUSTA ESTOS VALORES SI TUS COLUMNAS SE LLAMAN DIFERENTE!
CONTRATO_NOMBRE_PROP = "NOMBRE ORDENADO"
CONTRATO_RELACION_PROP = "PERSONAS"
PERSONA_NOMBRE_PROP = "Nombre" # La columna principal (título) en tu BD de Personas

# --- LÓGICA PRINCIPAL ---
def main():
    """
    Orquesta el proceso de sincronización.
    """
    contratos_db_id = os.getenv("CONTRATOS_DB_ID")
    personas_db_id = os.getenv("PERSONAS_DB_ID")
    
    if not all([contratos_db_id, personas_db_id, os.getenv("NOTION_API_KEY")]):
        print("🛑 Error: Asegúrate de que las variables de entorno estén bien configuradas en el archivo .env")
        return

    notion = NotionService()
    person_cache = {} # Caché para evitar buscar la misma persona múltiples veces { "nombre": "page_id" }

    print("🚀 Iniciando la sincronización de contratos y personas...")
    
    # 1. Obtener todos los contratos
    contracts = notion.get_all_database_pages(contratos_db_id)
    total_contracts = len(contracts)
    print(f"🔍 Se encontraron {total_contracts} contratos para procesar.")

    # 2. Iterar sobre cada contrato
    for idx, contract in enumerate(contracts):
        contract_id = contract["id"]
        properties = contract["properties"]

        # Extraer nombre del contrato
        # El formato es una lista, tomamos el primer elemento si existe
        nombre_ordenado_list = properties.get(CONTRATO_NOMBRE_PROP, {}).get("rich_text", [])
        if not nombre_ordenado_list:
            print(f"⚠️  ({idx+1}/{total_contracts}) Saltando contrato {contract_id}: sin nombre.")
            continue
        
        person_name_raw = nombre_ordenado_list[0].get("plain_text", "")
        person_name = person_name_raw.strip().upper() # Normalizar nombre

        if not person_name:
            print(f"⚠️  ({idx+1}/{total_contracts}) Saltando contrato {contract_id}: el nombre está vacío.")
            continue
        
        # Revisar si la relación ya existe para no reprocesar
        if properties.get(CONTRATO_RELACION_PROP, {}).get("relation"):
            print(f"✅ ({idx+1}/{total_contracts}) Contrato ya enlazado para: {person_name}")
            continue

        print(f"⚙️  ({idx+1}/{total_contracts}) Procesando: {person_name}")
        person_page_id = None

        # 3. Buscar o crear la persona
        if person_name in person_cache:
            person_page_id = person_cache[person_name]
            print(f"   -> Encontrado en caché.")
        else:
            # Buscar en Notion
            person_page = notion.find_person_by_name(personas_db_id, person_name)
            if person_page:
                person_page_id = person_page["id"]
                print(f"   -> Encontrado en Notion.")
            else:
                # Si no existe, crear
                print(f"   -> No encontrado. Creando persona...")
                new_person_page = notion.create_person(personas_db_id, person_name)
                if new_person_page:
                    person_page_id = new_person_page["id"]
            
            # Guardar en caché para futuras referencias
            if person_page_id:
                person_cache[person_name] = person_page_id

        # 4. Enlazar la persona al contrato
        if person_page_id:
            notion.link_person_to_contract(contract_id, person_page_id)
            print(f"   -> Enlace completado.")
        else:
            print(f"   -> 🛑 Error: No se pudo obtener el ID para '{person_name}'. No se pudo enlazar.")

        # 5. Pausa para respetar el límite de la API de Notion
        time.sleep(0.4) # ~2.5 peticiones por segundo

    print("\n🎉 ¡Proceso finalizado!")


if __name__ == "__main__":
    main() 