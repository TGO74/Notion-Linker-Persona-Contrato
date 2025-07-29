import os
import time
import logging
from notion_client import Client, APIResponseError

class RateLimiter:
    """Clase para manejar el rate limiting de la API de Notion."""
    
    def __init__(self, requests_per_second=2.5, burst_limit=10):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.burst_limit = burst_limit
        self.last_request_time = 0
        self.request_count = 0
        self.burst_start_time = time.time()
    
    def wait_if_needed(self):
        """Espera si es necesario para respetar el rate limit."""
        current_time = time.time()
        
        # Reiniciar contador de burst si han pasado más de 1 segundo
        if current_time - self.burst_start_time > 1.0:
            self.request_count = 0
            self.burst_start_time = current_time
        
        # Verificar límite de burst
        if self.request_count >= self.burst_limit:
            sleep_time = 1.0 - (current_time - self.burst_start_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
                self.request_count = 0
                self.burst_start_time = time.time()
        
        # Verificar intervalo mínimo entre requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1

class NotionService:
    """Servicio para interactuar con la API de Notion con manejo robusto de errores."""
    
    def __init__(self, contract_relation_prop, max_retries=3, retry_delay=2, requests_per_second=2.5):
        self.client = Client(auth=os.getenv("NOTION_API_KEY"))
        self.contract_relation_prop = contract_relation_prop
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limiter = RateLimiter(requests_per_second=requests_per_second)
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('notion_service.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _retry_api_call(self, api_call, *args, **kwargs):
        """Ejecuta una llamada a la API con reintentos automáticos y rate limiting."""
        for attempt in range(self.max_retries):
            try:
                # Esperar si es necesario para respetar el rate limit
                self.rate_limiter.wait_if_needed()
                
                # Ejecutar la llamada a la API
                result = api_call(*args, **kwargs)
                
                # Log exitoso
                self.logger.debug(f"API call exitoso (intento {attempt + 1})")
                return result
                
            except APIResponseError as e:
                self.logger.warning(f"Intento {attempt + 1}/{self.max_retries} falló: {e}")
                
                # Si es un error de rate limiting, esperar más tiempo
                if "rate limit" in str(e).lower() or "429" in str(e):
                    wait_time = self.retry_delay * (2 ** attempt)  # Backoff exponencial
                    self.logger.warning(f"Rate limit detectado, esperando {wait_time} segundos...")
                    time.sleep(wait_time)
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # Backoff exponencial
                else:
                    self.logger.error(f"Todos los reintentos fallaron para la operación")
                    raise
            except Exception as e:
                self.logger.error(f"Error inesperado en la API: {e}")
                raise
    
    def get_unlinked_contracts(self, db_id: str, batch_size: int):
        """Obtiene contratos sin enlazar con reintentos automáticos y rate limiting."""
        try:
            self.logger.info(f"Consultando contratos sin enlazar (lote de {batch_size})")
            response = self._retry_api_call(
                self.client.databases.query,
                database_id=db_id,
                filter={
                    "property": self.contract_relation_prop,
                    "relation": {
                        "is_empty": True
                    }
                },
                page_size=batch_size
            )
            contracts = response.get("results", [])
            self.logger.info(f"Encontrados {len(contracts)} contratos sin enlazar")
            return contracts
        except Exception as e:
            self.logger.error(f"Error al consultar contratos no enlazados: {e}")
            return []

    def find_person_by_name(self, db_id: str, name_prop: str, name: str):
        """Busca una persona por nombre con validación, reintentos y rate limiting."""
        try:
            self.logger.debug(f"Buscando persona: {name}")
            response = self._retry_api_call(
                self.client.databases.query,
                database_id=db_id,
                filter={
                    "property": name_prop,
                    "title": {
                        "equals": name
                    }
                }
            )
            results = response.get("results", [])
            
            if results:
                person = results[0]
                person_id = person.get("id")
                if person_id:
                    self.logger.info(f"Persona encontrada: {name} (ID: {person_id[:8]}...)")
                    return person
                else:
                    self.logger.warning(f"Persona encontrada pero sin ID válido: {name}")
                    return None
            else:
                self.logger.info(f"Persona no encontrada: {name}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error buscando persona '{name}': {e}")
            return None

    def create_person(self, db_id: str, name_prop: str, name: str):
        """Crea una nueva persona con validación completa del resultado y rate limiting."""
        new_page_properties = {
            name_prop: {
                "title": [{"text": {"content": name}}]
            }
        }
        
        try:
            self.logger.info(f"Creando nueva persona: {name}")
            new_person = self._retry_api_call(
                self.client.pages.create,
                parent={"database_id": db_id},
                properties=new_page_properties
            )
            
            # Validar que la creación fue exitosa
            person_id = new_person.get("id")
            if person_id:
                self.logger.info(f"✅ Persona creada exitosamente: {name} (ID: {person_id[:8]}...)")
                return new_person
            else:
                self.logger.error(f"❌ Error: Persona creada pero sin ID válido: {name}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error al crear persona '{name}': {e}")
            return None

    def link_person_to_contract(self, contract_page_id: str, person_page_id: str):
        """Enlaza una persona a un contrato con validación y rate limiting."""
        properties_to_update = {
            self.contract_relation_prop: {
                "relation": [{"id": person_page_id}]
            }
        }
        
        try:
            self.logger.debug(f"Enlazando contrato {contract_page_id[:8]}... con persona {person_page_id[:8]}...")
            updated_page = self._retry_api_call(
                self.client.pages.update,
                page_id=contract_page_id,
                properties=properties_to_update
            )
            
            # Validar que la actualización fue exitosa
            updated_relation = updated_page.get("properties", {}).get(self.contract_relation_prop, {})
            if updated_relation.get("relation"):
                self.logger.info(f"✅ Enlace exitoso: contrato {contract_page_id[:8]}... -> persona {person_page_id[:8]}...")
                return True
            else:
                self.logger.error(f"❌ Error: Enlace falló - relación no actualizada")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error al enlazar contrato '{contract_page_id}' con persona '{person_page_id}': {e}")
            return False
    
    def validate_database_connection(self, db_id: str):
        """Valida que se puede conectar a la base de datos con rate limiting."""
        try:
            self.logger.info(f"Validando conexión a BD: {db_id[:8]}...")
            response = self._retry_api_call(
                self.client.databases.retrieve,
                database_id=db_id
            )
            db_name = response.get("title", [{}])[0].get("plain_text", "Sin nombre")
            self.logger.info(f"✅ Conexión exitosa a BD: {db_name}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error conectando a BD {db_id}: {e}")
            return False
    
    def validate_property_exists(self, db_id: str, property_name: str):
        """Valida que una propiedad existe en la base de datos con rate limiting."""
        try:
            self.logger.debug(f"Validando propiedad '{property_name}' en BD {db_id[:8]}...")
            response = self._retry_api_call(
                self.client.databases.retrieve,
                database_id=db_id
            )
            properties = response.get("properties", {})
            
            if property_name in properties:
                self.logger.info(f"✅ Propiedad '{property_name}' encontrada en BD")
                return True
            else:
                self.logger.error(f"❌ Propiedad '{property_name}' NO encontrada en BD")
                available_props = list(properties.keys())
                self.logger.info(f"Propiedades disponibles: {available_props}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error validando propiedad '{property_name}': {e}")
            return False
    
    def get_rate_limit_stats(self):
        """Obtiene estadísticas del rate limiter para debugging."""
        return {
            'requests_per_second': self.rate_limiter.requests_per_second,
            'min_interval': self.rate_limiter.min_interval,
            'burst_limit': self.rate_limiter.burst_limit,
            'current_request_count': self.rate_limiter.request_count
        } 