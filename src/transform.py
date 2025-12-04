# src/transform.py

from datetime import datetime
from src.config import COLUMNAS_ESTANDAR


def _clean_date(date_value):
    """Limpia y estandariza las fechas a formato 'YYYY-MM-DD'."""
    if isinstance(date_value, datetime):
        return date_value.strftime('%Y-%m-%d')
    elif isinstance(date_value, (int, float)):
        # Si es un número, podría ser un serial de Excel, lo ignoramos por seguridad
        return None
    elif isinstance(date_value, str):
        date_value = date_value.strip()
        # Intentar parsear el mes abreviado o formatos comunes (ej: 01 dic)
        for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%y', '%d %b'):
            try:
                # Esto manejaría '01 dic' si se usa un locale adecuado, 
                # pero para evitar dependencias, nos enfocamos en formatos estándar
                return datetime.strptime(date_value, fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
    return None

def _clean_kilos(kilos_value):
    """Limpia valores numéricos de cantidad."""
    if isinstance(kilos_value, (int, float)):
        return round(float(kilos_value), 2)
    elif isinstance(kilos_value, str):
        try:
            # Intentar limpiar comas y puntos como separadores de miles
            kilos_value = kilos_value.replace(',', '').replace('.', '') 
            return round(float(kilos_value), 2)
        except ValueError:
            return 0.0
    return 0.0

def clean_and_standardize(raw_data_list):
    """
    Aplica limpieza y mapeo de columnas a una lista de diccionarios de datos brutos.
    """
    transformed_data = []
    
    for row in raw_data_list:
        
        # 1. Limpieza de Fecha y Cantidad
        fecha_limpia = _clean_date(row.get('FECHA_MOVIMIENTO'))
        cantidad_limpia = _clean_kilos(row.get('CANTIDAD_MOVIMIENTO')) 
        
        # 2. Validación y Filtrado
        if fecha_limpia is None or cantidad_limpia == 0.0:
            continue
            
        # 3. Estandarización al formato final
        final_row = {
            'FECHA_MOVIMIENTO': fecha_limpia,
            'CLIENTE': row.get('CLIENTE', ''), 
            'TIPO_MOVIMIENTO': row.get('TIPO_MOVIMIENTO', ''), 
            'SUBTIPO_MOVIMIENTO': row.get('SUBTIPO_MOVIMIENTO', ''),
            'CANTIDAD_MOVIMIENTO': cantidad_limpia, 
            'ORIGEN_SECCION': row.get('ORIGEN_SECCION', ''),
            'ORIGEN_HOJA': row.get('ORIGEN_HOJA', ''),         # ⬅️ ¡AÑADIDO! Aseguramos que la columna sea incluida aquí
            'FUENTE_ARCHIVO': row.get('FUENTE_ARCHIVO', '')
        }
        
        # 4. Aseguramos que solo las columnas estándar pasen
        transformed_row = {k: final_row[k] for k in COLUMNAS_ESTANDAR if k in final_row}
        transformed_data.append(transformed_row)
        
    return transformed_data