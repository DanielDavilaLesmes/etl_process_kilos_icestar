# src/extract.py

import pandas as pd
import numpy as np
import re
import os 
from src.config import (
    COLUMNAS_CANTIDAD_BRUTA, CABECERA_FECHA, 
    COLUMNAS_TARIFA_BRUTA, COLUMNAS_TOTAL_BRUTA, 
    COLUMNAS_OBSERVACIONES_BRUTAS
)

# ==============================================================================
# FUNCIONES AUXILIARES DE BÚSQUEDA Y NORMALIZACIÓN
# ==============================================================================

def _normalize_header_name(header):
    """Limpia y normaliza el nombre de una cabecera para búsqueda."""
    if pd.isna(header):
        return ""
    s = str(header).strip().upper()
    s = re.sub(r'[^\w\s]', '', s) 
    return s.replace(' ', '')

def _normalize_cell_content(cell_value):
    """Limpia y normaliza el contenido de una celda para buscar 'Cliente'."""
    if pd.isna(cell_value):
        return ""
    return str(cell_value).strip().upper().replace(' ', '')

def _find_client_name(sheet, max_rows=20):
    """Busca el campo 'Cliente' o 'Cliente corte' en las primeras filas."""
    client_search_terms = ['CLIENTE', 'CLIENTECORTE'] 
    
    for i in range(min(max_rows, len(sheet))):
        row = sheet.iloc[i]
        for col_idx, cell_value in enumerate(row):
            normalized_value = _normalize_cell_content(cell_value)
            if normalized_value in client_search_terms:
                if col_idx + 1 < len(row):
                    client_name_cell = row.iloc[col_idx + 1]
                    if pd.notna(client_name_cell) and str(client_name_cell).strip():
                        return str(client_name_cell).strip()
    return ""

# ==============================================================================
# FUNCIONES DE EXTRACCIÓN DE SECCIONES
# ==============================================================================

def _find_header_indices(sheet, section_row_start, max_rows=10):
    """Identifica las columnas de Fecha, Cantidad, Tarifa, Total y Observaciones."""
    header_row_index = -1
    for i in range(section_row_start, section_row_start + max_rows):
        if i >= len(sheet): break
        row = sheet.iloc[i]
        if row.apply(lambda x: _normalize_header_name(x) == _normalize_header_name(CABECERA_FECHA)).any():
            header_row_index = i
            break
            
    if header_row_index == -1: return {}, None, section_row_start
        
    header_row = sheet.iloc[header_row_index]
    header_indices = {}
    
    # 1. Índice de Fecha
    fecha_index = header_row[header_row.apply(lambda x: _normalize_header_name(x) == _normalize_header_name(CABECERA_FECHA))].index
    if not fecha_index.empty:
        header_indices[CABECERA_FECHA] = fecha_index[0]
        
    # 2. Índices de Cantidades (Múltiples posibles)
    quantity_indices = {}
    for original_header, normalized_name in COLUMNAS_CANTIDAD_BRUTA.items():
        q_idx = header_row[header_row.apply(lambda x: _normalize_header_name(x) == _normalize_header_name(original_header))].index
        if not q_idx.empty:
            quantity_indices[normalized_name] = q_idx[0]
    header_indices['QUANTITIES'] = quantity_indices

    # 3. Tarifa y Total
    for h_map, brutos in [( "TARIFA", COLUMNAS_TARIFA_BRUTA), ("TOTAL", COLUMNAS_TOTAL_BRUTA)]:
        for original_header in brutos:
            idx = header_row[header_row.apply(lambda x: _normalize_header_name(x) == _normalize_header_name(original_header))].index
            if not idx.empty:
                header_indices[h_map] = idx[0]
                break
        
    # 4. Observaciones
    obs_map = {}
    for obs_header in COLUMNAS_OBSERVACIONES_BRUTAS:
        idx = header_row[header_row.apply(lambda x: _normalize_header_name(x) == _normalize_header_name(obs_header))].index
        if not idx.empty:
            obs_map[obs_header] = idx[0]
    header_indices['OBSERVACIONES_MAP'] = obs_map 
    
    return header_indices, header_row_index + 1

def _extract_data_from_section(sheet, section_title, section_range, sheet_name, file_name, client_name):
    """Extrae datos permitiendo múltiples métricas por fila (ej. Cargue y Descargue)."""
    start_row, end_row = section_range
    extracted_data = []

    header_info, data_row_start = _find_header_indices(sheet, start_row, end_row - start_row)
    
    if CABECERA_FECHA not in header_info or not header_info.get('QUANTITIES'):
        return []
        
    fecha_idx = header_info[CABECERA_FECHA]
    quant_map = header_info['QUANTITIES']
    tarifa_idx = header_info.get("TARIFA") 
    total_idx = header_info.get("TOTAL")   
    obs_map = header_info.get('OBSERVACIONES_MAP', {})
    
    for i in range(data_row_start, end_row):
        row = sheet.iloc[i] 
        fecha_val = row.iloc[fecha_idx] if fecha_idx < len(row) else np.nan 

        if pd.isna(fecha_val):
            continue

        # Procesar cada columna de cantidad detectada de forma independiente
        for q_name, q_idx in quant_map.items():
            val = row.iloc[q_idx] if q_idx < len(row) else np.nan
            
            try:
                # Limpieza y validación numérica
                num_val = float(str(val).replace('$', '').replace('.', '').replace(',', '').strip()) if pd.notna(val) else 0
                
                if num_val != 0:
                    # Construir observaciones
                    observations = []
                    for name, idx in obs_map.items():
                        obs_val = row.iloc[idx] if idx < len(row) else None
                        if pd.notna(obs_val): observations.append(f"{name}: {obs_val}")

                    row_data = {
                        'FECHA_MOVIMIENTO': fecha_val,
                        'CLIENTE': client_name,
                        'TIPO_MOVIMIENTO': section_title,
                        'ORIGEN_SECCION': section_title,
                        'ORIGEN_HOJA': sheet_name,
                        'FUENTE_ARCHIVO': file_name,
                        'SUBTIPO_MOVIMIENTO': q_name,
                        'CANTIDAD_MOVIMIENTO': val, # Se mantiene el original para transform.py
                        'TARIFA': row.iloc[tarifa_idx] if tarifa_idx is not None else None,    
                        'TOTAL': row.iloc[total_idx] if total_idx is not None else None,     
                        'OBSERVACIONES': ' | '.join(observations)
                    }
                    extracted_data.append(row_data)
            except (ValueError, TypeError):
                continue

    return extracted_data

# ==============================================================================
# FUNCIÓN PRINCIPAL
# ==============================================================================

def extract_data_from_excel(file_path):
    """Procesa un archivo Excel extrayendo todas las secciones VTA."""
    try:
        xls = pd.ExcelFile(file_path, engine='openpyxl')
        all_data = []
        file_name = os.path.basename(file_path)
        print(f"  -> Procesando {file_name}...")
        
        client_name = ""
        if xls.sheet_names:
            first_sheet = xls.parse(xls.sheet_names[0], header=None)
            client_name = _find_client_name(first_sheet) 

        if not client_name:
            client_name = file_name.split(' ')[0].split('-')[0].split('_')[0]
            
        print(f"     -> Cliente identificado: {client_name}")
        
        vta_pattern = re.compile(r'\(VTA\d{3}\)', re.IGNORECASE)

        for sheet_name in xls.sheet_names:
            if sheet_name.lower() in ['resumen', 'general', 'datos', 'cierre', 'factura']:
                continue
                
            sheet = xls.parse(sheet_name, header=None)
            vta_sections = []
            current_title, current_start = None, -1
            
            for row_idx in range(len(sheet)):
                row = sheet.iloc[row_idx]
                match = row.apply(lambda x: vta_pattern.search(str(x).upper())).dropna()
                
                if not match.empty:
                    if current_title is not None:
                        vta_sections.append({'title': current_title, 'range': (current_start, row_idx)})
                    current_title = str(row.loc[match.index[0]])
                    current_start = row_idx
                
            if current_title is not None:
                vta_sections.append({'title': current_title, 'range': (current_start, len(sheet))})

            for section in vta_sections:
                data = _extract_data_from_section(sheet, section['title'], section['range'], sheet_name, file_name, client_name)
                all_data.extend(data)
                
        return all_data

    except Exception as e:
        print(f"  -> ❌ Error en {os.path.basename(file_path)}: {e}")
        return []