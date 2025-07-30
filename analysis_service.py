import csv
import os
from datetime import datetime
from typing import List

class ProcessingAnalyzer:
    """Clase para analizar y reportar estadísticas del procesamiento."""
    
    def __init__(self):
        """Inicializa las estadísticas para la sesión."""
        self.stats = {}
        self.start_session()

    def start_session(self):
        """Inicia o resetea una nueva sesión de procesamiento para un lote."""
        self.stats = {
            'total_processed': 0, 'successful_links': 0, 'errors': 0,
            'skipped_empty_names': 0, 'new_persons_created': 0,
            'existing_persons_found': 0, 'cache_hits': 0,
            'properties_updated': 0,
            'start_time': datetime.now(), 'end_time': None,
            'error_details': [], 'new_persons_list': [],
            'properties_updated_list': [],
            'processed_contracts': []
        }
        print(f"🕐 Iniciando sesión de lote: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    def end_session(self):
        """Finaliza la sesión de procesamiento del lote."""
        self.stats['end_time'] = datetime.now()

    def record_properties_updated(self, person_id: str, person_name: str, updated_props: List[str]):
        """Registra una actualización de propiedades para una persona existente."""
        self.stats['properties_updated'] += 1
        self.stats['properties_updated_list'].append({
            'person_id': person_id,
            'person_name': person_name,
            'updated_props': ", ".join(updated_props),
            'timestamp': datetime.now()
        })
    
    def record_successful_link(self, contract_id: str, person_name: str, person_id: str):
        """Registra un enlace exitoso."""
        self.stats['successful_links'] += 1
        self.stats['processed_contracts'].append({'contract_id': contract_id, 'person_name': person_name, 'person_id': person_id, 'status': 'success', 'timestamp': datetime.now()})

    def record_error(self, contract_id: str, person_name: str, error_message: str):
        """Registra un error durante el procesamiento."""
        self.stats['errors'] += 1
        self.stats['error_details'].append({'contract_id': contract_id, 'person_name': person_name, 'error': error_message, 'timestamp': datetime.now()})

    def record_skipped_empty_name(self, contract_id: str):
        """Registra un contrato saltado por nombre vacío."""
        self.stats['skipped_empty_names'] += 1

    def record_new_person_created(self, person_name: str, person_id: str):
        """Registra una nueva persona creada."""
        self.stats['new_persons_created'] += 1
        self.stats['new_persons_list'].append({'name': person_name, 'id': person_id, 'created_at': datetime.now()})

    def record_existing_person_found(self, person_name: str, person_id: str):
        """Registra una persona existente encontrada."""
        self.stats['existing_persons_found'] += 1

    def record_cache_hit(self):
        """Registra un hit en el caché."""
        self.stats['cache_hits'] += 1
    
    def generate_console_report(self):
        """Genera un reporte completo del lote en la consola."""
        if not self.stats.get('end_time'): self.end_session()
        duration = self.stats['end_time'] - self.stats['start_time']
        
        print("\n" + "="*60)
        print("📊 REPORTE DE PROCESAMIENTO DEL LOTE")
        print("="*60)
        print(f"📈 Total procesado: {self.stats['total_processed']}")
        print(f"✅ Enlaces exitosos: {self.stats['successful_links']}")
        print(f"🔄 Propiedades actualizadas: {self.stats['properties_updated']}")
        print(f"❌ Errores: {self.stats['errors']}")
        print(f"⏱️  Duración del lote: {duration}")
        print("="*60)

    def _append_to_csv(self, filename: str, data_list: List[dict], fieldnames: List[str]):
        """Función interna para añadir datos a un CSV de forma segura."""
        if not data_list: return
        file_exists = os.path.isfile(filename)
        try:
            with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                for item in data_list:
                    row = {k: v for k, v in item.items() if k in fieldnames}
                    if 'timestamp' in row and isinstance(row['timestamp'], datetime):
                        row['timestamp'] = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                    if 'created_at' in row and isinstance(row['created_at'], datetime):
                        row['created_at'] = row['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    writer.writerow(row)
        except IOError as e:
            print(f"Error al escribir en el archivo CSV {filename}: {e}")

    def export_cumulative_reports(self):
        """Exporta los datos detallados a archivos CSV fijos, añadiendo la información."""
        print("💾 Actualizando reportes CSV acumulativos...")
        self._append_to_csv("reporte_nuevas_personas.csv", self.stats['new_persons_list'], ['name', 'id', 'created_at'])
        self._append_to_csv("reporte_errores.csv", self.stats['error_details'], ['contract_id', 'person_name', 'error', 'timestamp'])
        self._append_to_csv("reporte_propiedades_actualizadas.csv", self.stats['properties_updated_list'], ['person_id', 'person_name', 'updated_props', 'timestamp'])
        print("✅ Reportes CSV actualizados.")

    def save_session_table_report(self):
        """Guarda un reporte de la sesión actual en formato de tabla en un archivo de texto."""
        if not self.stats.get('end_time'): self.end_session()
        duration = self.stats['end_time'] - self.stats['start_time']
        timestamp = self.stats['start_time'].strftime("%Y%m%d_%H%M%S")
        filename = f"reporte_sesion_{timestamp}.txt"
        
        table = [
            "=" * 80,
            "📊 REPORTE DE SESIÓN - NOTION LINKER",
            "=" * 80,
            f"Fecha: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}",
            f"Duración: {duration}",
            "\n┌─────────────────────────────────┬─────────────┐",
            "│ Métrica                         │ Valor       │",
            "├─────────────────────────────────┼─────────────┤",
            f"│ Total Procesado                 │ {self.stats['total_processed']:>11} │",
            f"│ Enlaces Exitosos                │ {self.stats['successful_links']:>11} │",
            f"│ Propiedades Actualizadas        │ {self.stats['properties_updated']:>11} │",
            f"│ Errores                         │ {self.stats['errors']:>11} │",
            f"│ Nuevas Personas Creadas         │ {self.stats['new_persons_created']:>11} │",
            f"│ Personas Existentes Encontradas │ {self.stats['existing_persons_found']:>11} │",
            f"│ Hits en Caché                   │ {self.stats['cache_hits']:>11} │",
            "└─────────────────────────────────┴─────────────┘"
        ]
        
        if self.stats['error_details']:
            table.append("\n❌ ERRORES DETALLADOS EN ESTA SESIÓN:")
            for error in self.stats['error_details']:
                table.append(f"  • {error['person_name']}: {error['error']}")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("\n".join(table))
            print(f"📋 Reporte de sesión guardado en: {filename}")
        except IOError as e:
            print(f"Error guardando reporte de tabla: {e}")