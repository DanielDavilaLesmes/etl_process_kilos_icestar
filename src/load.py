# src/load.py

import os
from openpyxl import Workbook
from src.config import OUTPUT_FILENAME, COLUMNAS_ESTANDAR 

def create_consolidated_xlsx(data, output_dir):
    """
    Crea el archivo Excel XLSX consolidado usando openpyxl.
    """
    if not data:
        print("  -> Advertencia: No hay datos para consolidar. Se omite la creación del XLSX.")
        return None

    output_path = os.path.join(output_dir, OUTPUT_FILENAME)
    
    try:
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Movimientos VTA Consolidados"
        
        # 1. Escribir las cabeceras
        sheet.append(COLUMNAS_ESTANDAR)
        
        # 2. Escribir los datos
        for row_dict in data:
            # Aseguramos que los datos se lean en el orden correcto
            row_values = [row_dict.get(col, '') for col in COLUMNAS_ESTANDAR] 
            sheet.append(row_values)
            
        workbook.save(output_path)
            
        print(f"  -> ✅ Reporte consolidado XLSX guardado exitosamente: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"  -> ❌ ERROR al escribir el XLSX consolidado: {e}")
        return None