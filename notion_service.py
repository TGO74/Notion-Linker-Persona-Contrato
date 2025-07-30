import os
import time
import logging
from notion_client import Client, APIResponseError

class RateLimiter:
    """Clase para manejar el rate limiting de la API de Notion."""
    def __init__(self, requests_per_second=2.5):
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0
    
    def wait_if_needed(self):
        """Espera si es necesario para respetar el rate limit."""
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_interval:
            time.sleep(self.min_interval - time_since_last)
        self.last_request_time = time.time()

class NotionService:
    """Servicio para interactuar con la API de Notion con manejo robusto de errores."""
    
    def __init__(self, contract_relation_prop, max_retries=3, retry_delay=2, requests_per_second=2.5):
        self.client = Client(auth=os.getenv("NOTION_API_KEY"))
        self.contract_relation_prop = contract_relation_prop
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limiter = RateLimiter(requests_per_second)
        self.logger = logging.getLogger(__name__)

    def _retry_api_call(self, api_call, *args, **kwargs):
        """Ejecuta una llamada a la API con reintentos automáticos y rate limiting."""
        for attempt in range(self.max_retries):
            try:
                self.rate_limiter.wait_if_needed()
                return api_call(*args, **kwargs)
            except APIResponseError as e:
                self.logger.warning(f"Intento {attempt + 1}/{self.max_retries} falló: {e}")
                if "rate limit" in str(e).lower() or "429" in str(e):
                    wait_time = self.retry_delay * (2 ** attempt)
                    self.logger.warning(f"Rate limit detectado, esperando {wait_time} segundos...")
                    time.sleep(wait_time)
                elif attempt >= self.max_retries - 1:
                    self.logger.error("Todos los reintentos fallaron para la operación.")
                    raise
            except Exception as e:
                self.logger.error(f"Error inesperado en la API: {e}"); raise
    
    def get_unlinked_contracts(self, db_id: str, batch_size: int):
        """Obtiene un lote de contratos donde la relación está vacía."""
        self.logger.info(f"Consultando lote de {batch_size} contratos sin enlace...")
        try:
            response = self._retry_api_call(
                self.client.databases.query,
                database_id=db_id,
                filter={"property": self.contract_relation_prop, "relation": {"is_empty": True}},
                page_size=batch_size
            )
            return response.get("results", [])
        except Exception as e:
            self.logger.error(f"Fallo crítico al consultar contratos: {e}"); return []

    def find_person_by_name(self, db_id: str, name_prop: str, name: str):
        """Busca una persona por nombre y devuelve el objeto completo de la página."""
        self.logger.debug(f"Buscando persona: {name}")
        try:
            response = self._retry_api_call(
                self.client.databases.query,
                database_id=db_id,
                filter={"property": name_prop, "title": {"equals": name}}
            )
            return response.get("results")[0] if response.get("results") else None
        except Exception as e:
            self.logger.error(f"Fallo crítico buscando a '{name}': {e}"); return None

    def create_person(self, db_id: str, name_prop: str, name: str, correo: str = None, sexo: str = None):
        """Crea una nueva persona, incluyendo correo y sexo si se proveen."""
        properties = {name_prop: {"title": [{"text": {"content": name}}]}}
        if correo:
            properties["CORREO"] = {"email": correo}
        if sexo:
            properties["SEXO"] = {"select": {"name": sexo}}
        
        self.logger.info(f"Creando nueva persona: {name} con propiedades {list(properties.keys())}")
        try:
            new_person = self._retry_api_call(
                self.client.pages.create,
                parent={"database_id": db_id},
                properties=properties
            )
            self.logger.info(f"✅ Persona creada exitosamente: {name}")
            return new_person
        except Exception as e:
            self.logger.error(f"❌ Fallo crítico al crear persona '{name}': {e}"); return None

    def update_person_properties(self, page_id: str, properties_to_update: dict):
        """Actualiza propiedades específicas de una página de persona."""
        if not properties_to_update:
            self.logger.debug(f"No hay propiedades para actualizar en la página {page_id[:8]}...")
            return True
        
        self.logger.info(f"Actualizando propiedades {list(properties_to_update.keys())} para la página {page_id[:8]}...")
        try:
            self._retry_api_call(
                self.client.pages.update,
                page_id=page_id,
                properties=properties_to_update
            )
            self.logger.info(f"✅ Propiedades actualizadas para {page_id[:8]}...")
            return True
        except Exception as e:
            self.logger.error(f"❌ Fallo crítico al actualizar propiedades para {page_id}: {e}")
            return False

    def link_person_to_contract(self, contract_page_id: str, person_page_id: str):
        """Enlaza una persona a un contrato."""
        self.logger.debug(f"Enlazando contrato {contract_page_id[:8]}... con persona {person_page_id[:8]}...")
        try:
            self._retry_api_call(
                self.client.pages.update,
                page_id=contract_page_id,
                properties={self.contract_relation_prop: {"relation": [{"id": person_page_id}]}}
            )
            self.logger.info(f"✅ Enlace exitoso: {contract_page_id[:8]}... -> {person_page_id[:8]}...")
            return True
        except Exception as e:
            self.logger.error(f"❌ Fallo crítico al enlazar contrato '{contract_page_id}': {e}"); return False

    # --- Métodos de validación y estadísticas ---
    def validate_database_connection(self, db_id: str):
        self.logger.info(f"Validando conexión a BD: {db_id[:8]}...")
        try:
            self._retry_api_call(self.client.databases.retrieve, database_id=db_id)
            return True
        except Exception: return False
    
    def validate_property_exists(self, db_id: str, property_name: str):
        self.logger.debug(f"Validando propiedad '{property_name}' en BD {db_id[:8]}...")
        try:
            db = self._retry_api_call(self.client.databases.retrieve, database_id=db_id)
            return property_name in db["properties"]
        except Exception: return False
        
    def get_rate_limit_stats(self):
        return {'requests_per_second': self.rate_limiter.requests_per_second}