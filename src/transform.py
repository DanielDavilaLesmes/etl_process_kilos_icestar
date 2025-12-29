# src/transform.py

from datetime import datetime
import json
import os
import re
from src.config import COLUMNAS_ESTANDAR, VTA_CLASSIFICATION_MAP, SUBTIPO_CLASSIFICATION_MAP 

# --- RUTAS DE CONFIGURACIÓN ---
PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CLIENT_MAPPING_FILE = os.path.join(PROJECT_ROOT, 'client_mapping.json') 

# Patrón regex para extraer el código VTA (VTA###)
VTA_CODE_PATTERN = re.compile(r'(VTA\d{3})', re.IGNORECASE)

# ==============================================================================
# 1. CARGA DE CONFIGURACIÓN SENSIBLE (CLIENTES/NIT)
# ==============================================================================

def _load_client_map(file_path):
    """Función para cargar el mapa de clientes desde un archivo JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            print(f"  -> Mapa de Clientes (NIT) cargado desde {os.path.basename(file_path)}.")
            return json.load(f)
    except FileNotFoundError:
        print(f"  -> ⚠️ Advertencia: Archivo de mapeo de clientes no encontrado en {file_path}. No se aplicará estandarización de clientes.")
        return {}
    except json.JSONDecodeError:
        print(f"  -> ❌ Error: El archivo de mapeo de clientes {file_path} no es un JSON válido.")
        return {}

CLIENT_MAPPING = _load_client_map(CLIENT_MAPPING_FILE)

# ==============================================================================
# 2. FUNCIONES DE LIMPIEZA BÁSICA
# ==============================================================================

def _clean_date(date_value):
    """Limpia y estandariza las fechas a formato 'YYYY-MM-DD'."""
    if isinstance(date_value, datetime):
        return date_value.strftime('%Y-%m-%d')
    elif isinstance(date_value, (int, float)):
        return None
    elif isinstance(date_value, str):
        date_value = date_value.strip()
        for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%y', '%d %b'):
            try:
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
            kilos_value = kilos_value.replace(',', '').replace('$', '').strip() 
            return round(float(kilos_value), 2)
        except ValueError:
            return 0.0
    return 0.0

# ==============================================================================
# 3. FUNCIONES DE CLASIFICACIÓN VTA (Mantenidas)
# ==============================================================================

def _clean_and_get_vta_code(tipo_movimiento_bruto):
    """Retorna solo el código VTA estandarizado (ej. 'VTA019')."""
    if not tipo_movimiento_bruto: return ""
    match = VTA_CODE_PATTERN.search(tipo_movimiento_bruto)
    return match.group(1).upper() if match else ""

def _classify_vta(vta_limpio_code):
    """Clasifica el código VTA limpio usando el mapa de config.py."""
    if not vta_limpio_code: return "OTRO"
    for category, vta_list in VTA_CLASSIFICATION_MAP.items():
        if vta_limpio_code in vta_list: return category
    return "OTRO"

# ==============================================================================
# 4. FUNCIONES DE CLASIFICACIÓN SUBTIPO (Mantenidas)
# ==============================================================================

def _clean_and_get_subtipo_code(subtipo_bruto):
    """Retorna el subtipo en mayúsculas."""
    if not subtipo_bruto: return ""
    return str(subtipo_bruto).strip().upper()

def _classify_subtipo(subtipo_limpio_code):
    """Clasifica el código de subtipo limpio usando el mapa de config.py."""
    if not subtipo_limpio_code: return "OTRO"
    for category, subtipo_list in SUBTIPO_CLASSIFICATION_MAP.items():
        if subtipo_limpio_code in subtipo_list: return category
    return "OTRO"

# ==============================================================================
# 5. FUNCIONES DE MAPEO DE CLIENTES (Mantenidas)
# ==============================================================================

def _get_standardized_client_info(client_name):
    """
    Busca el nombre del cliente extraído en el mapeo cargado (CLIENT_MAPPING) 
    y retorna el Cliente Estandarizado y el NIT.
    """
    if not client_name:
        return "SIN CLIENTE", "SIN NIT" 
        
    client_key = str(client_name).strip()
    mapping = CLIENT_MAPPING.get(client_key)
    
    if mapping:
        estandar = mapping.get('estandar', client_key.upper())
        nit = mapping.get('nit', "SIN NIT")
        return estandar, nit
    else:
        return client_key.upper(), "NO ENCONTRADO"

# ==============================================================================
# 6. FUNCIÓN PRINCIPAL DE TRANSFORMACIÓN
# ==============================================================================

def clean_and_standardize(raw_data_list):
    """
    Función principal que aplica todas las transformaciones, limpiezas, 
    clasificaciones y mapeos al conjunto de datos crudos.
    """
    transformed_data = []
    
    for row in raw_data_list:
        
        # 1. Extracción y Validación Inicial
        fecha_limpia = _clean_date(row.get('FECHA_MOVIMIENTO'))
        cantidad_limpia = _clean_kilos(row.get('CANTIDAD_MOVIMIENTO')) 
        
        # Filtrado de filas inválidas (sin fecha o cantidad cero)
        if fecha_limpia is None or cantidad_limpia == 0.0:
            continue
            
        # 2. Obtención de datos brutos
        tipo_mov_bruto = row.get('TIPO_MOVIMIENTO', '')
        subtipo_mov_bruto = row.get('SUBTIPO_MOVIMIENTO', '') 
        client_name_bruto = row.get('CLIENTE', '')

        # 3. Clasificación VTA
        vta_code_limpio = _clean_and_get_vta_code(tipo_mov_bruto)
        clasificacion_final_vta = _classify_vta(vta_code_limpio)
        
        # 4. Clasificación Subtipo
        subtipo_code_limpio = _clean_and_get_subtipo_code(subtipo_mov_bruto)
        clasificacion_final_subtipo = _classify_subtipo(subtipo_code_limpio)
        
        # 5. Mapeo de Cliente (NIT/Estandarización)
        cliente_estandar, nit = _get_standardized_client_info(client_name_bruto)

        # 6. Estandarización al formato final (Diccionario temporal)
        final_row = {
            'FECHA_MOVIMIENTO': fecha_limpia,
            'CLIENTE': client_name_bruto, 
            'CLIENTE_ESTANDAR': cliente_estandar, 
            'NIT': nit, 
            'TIPO_MOVIMIENTO': tipo_mov_bruto, 
            'TIPO_MOVIMIENTO_LIMPIO': vta_code_limpio, 
            'CLASIFICACION_VTA': clasificacion_final_vta, 
            'SUBTIPO_MOVIMIENTO': subtipo_mov_bruto, 
            'SUBTIPO_MOVIMIENTO_LIMPIO': subtipo_code_limpio, 
            'CLASIFICACION_SUBTIPO': clasificacion_final_subtipo, 
            'CANTIDAD_MOVIMIENTO': cantidad_limpia,
            
            # ✅ CORRECCIÓN CRÍTICA: Añadir las nuevas columnas de Tarifa, Total y Observaciones
            'TARIFA': row.get('TARIFA', None), 
            'TOTAL': row.get('TOTAL', None),
            'OBSERVACIONES': row.get('OBSERVACIONES', ''),

            'ORIGEN_SECCION': row.get('ORIGEN_SECCION', ''),
            'ORIGEN_HOJA': row.get('ORIGEN_HOJA', ''), 
            'FUENTE_ARCHIVO': row.get('FUENTE_ARCHIVO', '')
        }
        
        # 7. Filtrado de columnas: Aseguramos que el orden y las columnas coincidan con COLUMNAS_ESTANDAR
        transformed_row = {k: final_row.get(k, None) for k in COLUMNAS_ESTANDAR} 
        transformed_data.append(transformed_row)
        
    return transformed_data