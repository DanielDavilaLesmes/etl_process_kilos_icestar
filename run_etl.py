# run_etl.py

import os
import shutil
from datetime import datetime, date # ✅ CORRECCIÓN: Importación de datetime/date al inicio
from src import extract, transform, load
from src.config import OUTPUT_FILENAME

# ==============================================================================
# 1. CONFIGURACIÓN DE RUTAS
# ==============================================================================

# Directorios a crear o usar
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_DIR = os.path.join(BASE_DIR, "Work")
OUTPUT_DIR = os.path.join(BASE_DIR, "Export", "Reportes")

# Carpeta fuente de los archivos (¡AJUSTAR ESTA RUTA!)
SOURCE_DIR = "C:\\Users\\sopex\\Cold Chile S.A\\Excelencia Operacional - Excelencia Operacional\\Daniel\\Desarrollos\\etl_process_kilos_icestar\\Import\\Kilos_Fuente" 


# ==============================================================================
# 2. FUNCIONES DE SETUP Y LIMPIEZA
# ==============================================================================

def setup_environment(source_dir, work_dir):
    """Crea directorios y copia archivos XLSX/XLSM de la fuente a la carpeta de trabajo."""
    print(f"-> Buscando archivos en fuente original: {source_dir}")
    
    if not os.path.exists(source_dir):
        print(f"❌ ERROR: Directorio fuente no encontrado: {source_dir}")
        return False
        
    # Limpiar y crear Work/Output
    shutil.rmtree(work_dir, ignore_errors=True)
    os.makedirs(work_dir, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    copied_files = []
    
    # Lista de extensiones a copiar
    valid_extensions = ('.xlsx', '.xlsm')
    
    for filename in os.listdir(source_dir):
        if filename.lower().endswith(valid_extensions):
            source_path = os.path.join(source_dir, filename)
            dest_path = os.path.join(work_dir, filename)
            try:
                shutil.copy2(source_path, dest_path)
                copied_files.append(dest_path)
            except Exception as e:
                print(f"❌ Error al copiar {filename}: {e}")
                
    if not copied_files:
        print("⚠️ Advertencia: No se encontraron archivos XLSX/XLSM para procesar.")
        return False
        
    print(f"  -> ✅ {len(copied_files)} archivos copiados a {work_dir}")
    return copied_files


# ==============================================================================
# 3. PROCESO PRINCIPAL (ETL)
# ==============================================================================

def main():
    start_time = datetime.now()
    today_date = date.today()
    
    print("=" * 50)
    print(f"      🚀 INICIO DE PROCESO ETL - MOVIMIENTOS VTA 🚀      ")
    print(f"      Fecha de Ejecución: {today_date.strftime('%Y-%m-%d')}")
    print("=" * 50)

    consolidated_data = []

    try:
        # 1. SETUP Y COPIADO
        print("\n-> Paso 1: Copiado de Archivos a Carpeta de Trabajo...")
        files_to_process = setup_environment(SOURCE_DIR, WORK_DIR)
        
        if not files_to_process:
            print("Proceso detenido.")
            return

        # 2. EXTRACCIÓN Y TRANSFORMACIÓN (E&T)
        print("\n-> Paso 2: Extracción y Transformación de Archivos...")
        
        for file_path in files_to_process:
            file_name = os.path.basename(file_path)
            # Ya no se imprime aquí, se imprime dentro de extract.extract_data_from_excel
            
            raw_data = extract.extract_data_from_excel(file_path)
            transformed_chunk = transform.clean_and_standardize(raw_data)
            
            if transformed_chunk:
                print(f"    -> ✅ {len(transformed_chunk)} filas listas para consolidación.")
                consolidated_data.extend(transformed_chunk)
            else:
                print(f"    -> ⚠️ Archivo {file_name} procesado, pero sin datos útiles para consolidación.")

        # 3. CARGA (Consolidación)
        if consolidated_data:
            print(f"\n-> Paso 3: Carga (Consolidación) | Total: {len(consolidated_data)} filas...")
            load.create_consolidated_xlsx(consolidated_data, OUTPUT_DIR) 
        else:
            print("\n-> Proceso ETL finalizado sin datos para consolidar.")

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO EN EL PROCESO PRINCIPAL: {e}")
        
    finally:
        end_time = datetime.now()
        duration = end_time - start_time
        print(f"Tiempo total de ejecución: {duration.total_seconds():.2f} segundos.")
        print("=" * 50)


if __name__ == "__main__":
    # La importación aquí ya no es necesaria, pero no afecta si se deja
    main()