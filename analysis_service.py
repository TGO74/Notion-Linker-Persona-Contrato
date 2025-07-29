import csv
import json
from datetime import datetime
from typing import Dict, List, Any

class ProcessingAnalyzer:
    """Clase para analizar y reportar estadísticas del procesamiento."""
    
    def __init__(self):
        self.stats = {
            'total_processed': 0,
            'successful_links': 0,
            'errors': 0,
            'skipped_empty_names': 0,
            'new_persons_created': 0,
            'existing_persons_found': 0,
            'cache_hits': 0,
            'start_time': None,
            'end_time': None,
            'error_details': [],
            'new_persons_list': [],
            'processed_contracts': []
        }
    
    def start_session(self):
        """Inicia una nueva sesión de procesamiento."""
        self.stats['start_time'] = datetime.now()
        print(f"🕐 Iniciando sesión: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    def end_session(self):
        """Finaliza la sesión de procesamiento."""
        self.stats['end_time'] = datetime.now()
        duration = self.stats['end_time'] - self.stats['start_time']
        print(f"🕐 Sesión finalizada: {self.stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Duración total: {duration}")
    
    def record_successful_link(self, contract_id: str, person_name: str, person_id: str):
        """Registra un enlace exitoso."""
        self.stats['successful_links'] += 1
        self.stats['processed_contracts'].append({
            'contract_id': contract_id,
            'person_name': person_name,
            'person_id': person_id,
            'status': 'success',
            'timestamp': datetime.now()
        })
    
    def record_error(self, contract_id: str, person_name: str, error_message: str):
        """Registra un error durante el procesamiento."""
        self.stats['errors'] += 1
        self.stats['error_details'].append({
            'contract_id': contract_id,
            'person_name': person_name,
            'error': error_message,
            'timestamp': datetime.now()
        })
        self.stats['processed_contracts'].append({
            'contract_id': contract_id,
            'person_name': person_name,
            'status': 'error',
            'error': error_message,
            'timestamp': datetime.now()
        })
    
    def record_skipped_empty_name(self, contract_id: str):
        """Registra un contrato saltado por nombre vacío."""
        self.stats['skipped_empty_names'] += 1
        self.stats['processed_contracts'].append({
            'contract_id': contract_id,
            'status': 'skipped',
            'reason': 'nombre_vacio',
            'timestamp': datetime.now()
        })
    
    def record_new_person_created(self, person_name: str, person_id: str):
        """Registra una nueva persona creada."""
        self.stats['new_persons_created'] += 1
        self.stats['new_persons_list'].append({
            'name': person_name,
            'id': person_id,
            'created_at': datetime.now()
        })
    
    def record_existing_person_found(self, person_name: str, person_id: str):
        """Registra una persona existente encontrada."""
        self.stats['existing_persons_found'] += 1
    
    def record_cache_hit(self):
        """Registra un hit en el caché."""
        self.stats['cache_hits'] += 1
    
    def generate_console_report(self):
        """Genera un reporte completo en consola."""
        if not self.stats['start_time']:
            return
        
        duration = self.stats['end_time'] - self.stats['start_time'] if self.stats['end_time'] else datetime.now() - self.stats['start_time']
        
        print("\n" + "="*60)
        print("📊 REPORTE DE PROCESAMIENTO")
        print("="*60)
        
        # Estadísticas generales
        print(f"📈 Total procesado: {self.stats['total_processed']}")
        print(f"✅ Enlaces exitosos: {self.stats['successful_links']}")
        print(f"❌ Errores: {self.stats['errors']}")
        print(f"⏱️  Duración: {duration}")
        
        # Estadísticas de personas
        print(f"\n👥 PERSONAS:")
        print(f"   ➕ Nuevas creadas: {self.stats['new_persons_created']}")
        print(f"   🔍 Existentes encontradas: {self.stats['existing_persons_found']}")
        print(f"   💾 Hits en caché: {self.stats['cache_hits']}")
        
        # Otros
        print(f"⏭️  Saltados (nombres vacíos): {self.stats['skipped_empty_names']}")
        
        # Tasa de éxito
        if self.stats['total_processed'] > 0:
            success_rate = (self.stats['successful_links'] / self.stats['total_processed']) * 100
            print(f"📊 Tasa de éxito: {success_rate:.1f}%")
        
        # Lista de nuevas personas
        if self.stats['new_persons_list']:
            print(f"\n🆕 NUEVAS PERSONAS CREADAS ({len(self.stats['new_persons_list'])}):")
            for person in self.stats['new_persons_list']:
                print(f"   • {person['name']} (ID: {person['id'][:8]}...)")
        
        # Errores detallados
        if self.stats['error_details']:
            print(f"\n❌ ERRORES DETALLADOS ({len(self.stats['error_details'])}):")
            for error in self.stats['error_details']:
                print(f"   • {error['person_name']}: {error['error']}")
        
        print("="*60)
    
    def export_to_csv(self, filename: str = None) -> str:
        """Exporta todos los datos a archivos CSV."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reporte_procesamiento_{timestamp}"
        
        # 1. Exportar resumen general
        self._export_summary_csv(f"{filename}_resumen.csv")
        
        # 2. Exportar contratos procesados
        self._export_contracts_csv(f"{filename}_contratos.csv")
        
        # 3. Exportar nuevas personas
        self._export_new_persons_csv(f"{filename}_nuevas_personas.csv")
        
        # 4. Exportar errores
        self._export_errors_csv(f"{filename}_errores.csv")
        
        print(f"💾 Archivos CSV exportados con prefijo: {filename}")
        return filename
    
    def _export_summary_csv(self, filename: str):
        """Exporta el resumen general a CSV."""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Métrica', 'Valor'])
            writer.writerow(['Total Procesado', self.stats['total_processed']])
            writer.writerow(['Enlaces Exitosos', self.stats['successful_links']])
            writer.writerow(['Errores', self.stats['errors']])
            writer.writerow(['Nuevas Personas Creadas', self.stats['new_persons_created']])
            writer.writerow(['Personas Existentes Encontradas', self.stats['existing_persons_found']])
            writer.writerow(['Hits en Caché', self.stats['cache_hits']])
            writer.writerow(['Saltados (Nombres Vacíos)', self.stats['skipped_empty_names']])
            
            if self.stats['total_processed'] > 0:
                success_rate = (self.stats['successful_links'] / self.stats['total_processed']) * 100
                writer.writerow(['Tasa de Éxito (%)', f"{success_rate:.1f}"])
            
            if self.stats['start_time'] and self.stats['end_time']:
                duration = self.stats['end_time'] - self.stats['start_time']
                writer.writerow(['Duración Total', str(duration)])
    
    def _export_contracts_csv(self, filename: str):
        """Exporta los contratos procesados a CSV."""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['contract_id', 'person_name', 'person_id', 'status', 'error', 'timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for contract in self.stats['processed_contracts']:
                row = {
                    'contract_id': contract.get('contract_id', ''),
                    'person_name': contract.get('person_name', ''),
                    'person_id': contract.get('person_id', ''),
                    'status': contract.get('status', ''),
                    'error': contract.get('error', ''),
                    'timestamp': contract.get('timestamp', '').strftime('%Y-%m-%d %H:%M:%S') if contract.get('timestamp') else ''
                }
                writer.writerow(row)
    
    def _export_new_persons_csv(self, filename: str):
        """Exporta las nuevas personas creadas a CSV."""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'id', 'created_at']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for person in self.stats['new_persons_list']:
                row = {
                    'name': person['name'],
                    'id': person['id'],
                    'created_at': person['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                }
                writer.writerow(row)
    
    def _export_errors_csv(self, filename: str):
        """Exporta los errores detallados a CSV."""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['contract_id', 'person_name', 'error', 'timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for error in self.stats['error_details']:
                row = {
                    'contract_id': error['contract_id'],
                    'person_name': error['person_name'],
                    'error': error['error'],
                    'timestamp': error['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                }
                writer.writerow(row)
    
    def generate_table_report(self) -> str:
        """Genera un reporte en formato de tabla ASCII."""
        if not self.stats['start_time']:
            return "No hay datos para generar reporte."
        
        duration = self.stats['end_time'] - self.stats['start_time'] if self.stats['end_time'] else datetime.now() - self.stats['start_time']
        
        table = []
        table.append("=" * 80)
        table.append("📊 REPORTE DE PROCESAMIENTO - NOTION LINKER")
        table.append("=" * 80)
        table.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        table.append(f"Duración: {duration}")
        table.append("")
        
        # Tabla de estadísticas
        table.append("┌─────────────────────────────────┬─────────────┐")
        table.append("│ Métrica                        │ Valor       │")
        table.append("├─────────────────────────────────┼─────────────┤")
        table.append(f"│ Total Procesado                │ {self.stats['total_processed']:>11} │")
        table.append(f"│ Enlaces Exitosos               │ {self.stats['successful_links']:>11} │")
        table.append(f"│ Errores                        │ {self.stats['errors']:>11} │")
        table.append(f"│ Nuevas Personas Creadas        │ {self.stats['new_persons_created']:>11} │")
        table.append(f"│ Personas Existentes Encontradas│ {self.stats['existing_persons_found']:>11} │")
        table.append(f"│ Hits en Caché                  │ {self.stats['cache_hits']:>11} │")
        table.append(f"│ Saltados (Nombres Vacíos)      │ {self.stats['skipped_empty_names']:>11} │")
        
        if self.stats['total_processed'] > 0:
            success_rate = (self.stats['successful_links'] / self.stats['total_processed']) * 100
            table.append(f"│ Tasa de Éxito (%)              │ {success_rate:>10.1f} │")
        
        table.append("└─────────────────────────────────┴─────────────┘")
        
        # Lista de nuevas personas
        if self.stats['new_persons_list']:
            table.append("")
            table.append("🆕 NUEVAS PERSONAS CREADAS:")
            table.append("┌─────────────────────────────────┬─────────────────────────────────┐")
            table.append("│ Nombre                         │ ID                              │")
            table.append("├─────────────────────────────────┼─────────────────────────────────┤")
            for person in self.stats['new_persons_list']:
                name = person['name'][:30] + "..." if len(person['name']) > 30 else person['name']
                person_id = person['id'][:30] + "..." if len(person['id']) > 30 else person['id']
                table.append(f"│ {name:<31} │ {person_id:<31} │")
            table.append("└─────────────────────────────────┴─────────────────────────────────┘")
        
        # Lista de errores
        if self.stats['error_details']:
            table.append("")
            table.append("❌ ERRORES DETALLADOS:")
            table.append("┌─────────────────────────────────┬─────────────────────────────────┐")
            table.append("│ Persona                        │ Error                           │")
            table.append("├─────────────────────────────────┼─────────────────────────────────┤")
            for error in self.stats['error_details']:
                name = error['person_name'][:30] + "..." if len(error['person_name']) > 30 else error['person_name']
                error_msg = error['error'][:30] + "..." if len(error['error']) > 30 else error['error']
                table.append(f"│ {name:<31} │ {error_msg:<31} │")
            table.append("└─────────────────────────────────┴─────────────────────────────────┘")
        
        table.append("")
        table.append("=" * 80)
        
        return "\n".join(table)
    
    def save_table_report(self, filename: str = None) -> str:
        """Guarda el reporte en formato tabla en un archivo de texto."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reporte_tabla_{timestamp}.txt"
        
        table_content = self.generate_table_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(table_content)
        
        print(f"📋 Reporte en tabla guardado en: {filename}")
        return filename 