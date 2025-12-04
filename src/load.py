# src/load.py

import os
from openpyxl import Workbook
from src.config import OUTPUT_FILENAME, COLUMNAS_ESTANDAR # SAC_LOG_FILENAME y timedelta no son necesarios

def create_consolidated_xlsx(data, output_dir):
    """
    Crea el archivo Excel XLSX consolidado usando openpyxl.
    """
    if not data:
        print("  -> Advertencia: No hay datos para consolidar. Se omite la creación del XLSX.")
        return None

    output_path = os.path.join(output_dir, OUTPUT_FILENAME)
    
    try:
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Movimientos VTA Consolidados"
        
        sheet.append(COLUMNAS_ESTANDAR)
        
        for row_dict in data:
            row_values = [row_dict.get(col, '') for col in COLUMNAS_ESTANDAR]
            sheet.append(row_values)
            
        workbook.save(output_path)
            
        print(f"  -> ✅ Reporte consolidado XLSX guardado exitosamente: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"  -> ❌ ERROR al escribir el XLSX consolidado: {e}")
        return None


    """
    Verifica el cumplimiento del SAC (presencia de datos del día vencido) 
    y genera un archivo de log.
    """
    if execution_date is None:
        execution_date = date.today()
        
    dia_vencido = execution_date - timedelta(days=1)
    dia_vencido_str = dia_vencido.strftime('%Y-%m-%d')
    
    compliance_met = any(row['FECHA_MOVIMIENTO'] == dia_vencido_str for row in data)
    
    if compliance_met:
        status = "CUMPLIDO"
        message = f"Se encontraron datos de Movimientos VTA para el día vencido ({dia_vencido_str})."
    else:
        status = "INCUMPLIDO"
        message = f"NO se encontraron datos de Movimientos VTA para el día vencido ({dia_vencido_str})."
        
    log_content = [
        f"====================================================",
        f"REPORTE DE CUMPLIMIENTO SAC - MOVIMIENTOS VTA",
        f"Fecha de Ejecución del ETL: {execution_date.strftime('%Y-%m-%d')}",
        f"Día Vencido Verificado: {dia_vencido_str}",
        f"ESTADO DE CUMPLIMIENTO: {status}",
        f"Mensaje: {message}",
        f"===================================================="
    ]
    
    output_path = os.path.join(output_dir, SAC_LOG_FILENAME)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as log_file:
            log_file.write('\n'.join(log_content))
            
        print(f"  -> ✅ Reporte SAC ({status}) generado en: {output_path}")
    except Exception as e:
        print(f"  -> ❌ ERROR al escribir el Log SAC: {e}")