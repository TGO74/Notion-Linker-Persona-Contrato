import os
from notion_client import Client, APIResponseError

class NotionService:
    """
    Clase que encapsula las interacciones con la API de Notion.
    """
    def __init__(self):
        # Inicializa el cliente usando la API Key del archivo .env
        self.client = Client(auth=os.getenv("NOTION_API_KEY"))

    def get_all_database_pages(self, db_id: str):
        """
        Obtiene todas las páginas de una base de datos, manejando la paginación.
        """
        pages = []
        has_more = True
        next_cursor = None
        while has_more:
            try:
                response = self.client.databases.query(
                    database_id=db_id,
                    start_cursor=next_cursor
                )
                pages.extend(response.get("results"))
                has_more = response.get("has_more")
                next_cursor = response.get("next_cursor")
            except APIResponseError as e:
                print(f"Error al consultar la base de datos: {e}")
                return []
        return pages

    def find_person_by_name(self, db_id: str, name: str):
        """
        Busca una persona por su nombre exacto en la base de datos de Personas.
        Asume que la propiedad 'title' de la BD Personas se llama 'Nombre'.
        """
        try:
            response = self.client.databases.query(
                database_id=db_id,
                filter={
                    "property": "Nombre", # IMPORTANTE: Reemplaza "Nombre" si tu columna de título se llama diferente
                    "title": {
                        "equals": name
                    }
                }
            )
            results = response.get("results")
            if results:
                return results[0] # Devuelve el primer resultado encontrado
            return None
        except APIResponseError as e:
            print(f"Error buscando persona '{name}': {e}")
            return None

    def create_person(self, db_id: str, name: str):
        """
        Crea una nueva persona en la base de datos de Personas.
        Asume que la propiedad 'title' de la BD Personas se llama 'Nombre'.
        """
        new_page_properties = {
            "Nombre": { # IMPORTANTE: Reemplaza "Nombre" si tu columna de título se llama diferente
                "title": [
                    {
                        "text": {
                            "content": name
                        }
                    }
                ]
            }
            # Puedes añadir aquí otras propiedades si quieres (ej. Sexo)
        }
        try:
            new_person = self.client.pages.create(
                parent={"database_id": db_id},
                properties=new_page_properties
            )
            print(f"✅ Persona creada: {name}")
            return new_person
        except APIResponseError as e:
            print(f"Error al crear persona '{name}': {e}")
            return None

    def link_person_to_contract(self, contract_page_id: str, person_page_id: str):
        """
        Actualiza un contrato para enlazarlo con una persona.
        Asume que la propiedad de relación en la BD Contratos se llama 'PERSONAS'.
        """
        properties_to_update = {
            "PERSONAS": { # IMPORTANTE: Reemplaza "PERSONAS" si tu columna de relación se llama diferente
                "relation": [
                    {
                        "id": person_page_id
                    }
                ]
            }
        }
        try:
            self.client.pages.update(
                page_id=contract_page_id,
                properties=properties_to_update
            )
        except APIResponseError as e:
            print(f"Error al enlazar contrato '{contract_page_id}' con persona '{person_page_id}': {e}") 