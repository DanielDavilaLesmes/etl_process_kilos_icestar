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
    # Normalizamos el contenido y eliminamos espacios
    return str(cell_value).strip().upper().replace(' ', '')

def _find_client_name(sheet, max_rows=20):
    """
    Busca el campo 'Cliente' o 'Cliente corte' en las primeras filas de la hoja
    y extrae el valor adyacente.
    """
    client_search_terms = ['CLIENTE', 'CLIENTECORTE'] 
    
    for i in range(min(max_rows, len(sheet))):
        row = sheet.iloc[i]
        
        for col_idx, cell_value in enumerate(row):
            normalized_value = _normalize_cell_content(cell_value)
            
            if normalized_value in client_search_terms:
                # El nombre del cliente debería estar en la columna adyacente
                if col_idx + 1 < len(row):
                    client_name_cell = row.iloc[col_idx + 1]
                    
                    if pd.notna(client_name_cell) and str(client_name_cell).strip():
                        # Usar el nombre completo y limpio como base para el Cliente
                        full_name = str(client_name_cell).strip()
                        return full_name
                        
    return ""


# ==============================================================================
# FUNCIONES DE EXTRACCIÓN DE SECCIONES
# ==============================================================================

def _find_header_indices(sheet, section_row_start, max_rows=10):
    """
    Busca la fila de cabeceras, identifica las columnas de Fecha, Cantidad, 
    Tarifa, Total y Observaciones, y retorna sus índices.
    """
    header_row_index = -1
    
    # 1. Buscar la fila que contiene la cabecera de fecha
    for i in range(section_row_start, section_row_start + max_rows):
        if i >= len(sheet): break
        
        row = sheet.iloc[i]
        if row.apply(lambda x: _normalize_header_name(x) == _normalize_header_name(CABECERA_FECHA)).any():
            header_row_index = i
            break
            
    if header_row_index == -1: return {}, None, section_row_start
        
    header_row = sheet.iloc[header_row_index]
    header_indices = {}
    found_quantity_header = None
    
    # 2. Buscamos el índice de la Fecha
    fecha_index = header_row[header_row.apply(lambda x: _normalize_header_name(x) == _normalize_header_name(CABECERA_FECHA))].index
    if not fecha_index.empty:
        header_indices[CABECERA_FECHA] = fecha_index[0]
        
    # 3. Buscamos Cantidad/Subtipo (el primero encontrado es el principal)
    for original_header, normalized_name in COLUMNAS_CANTIDAD_BRUTA.items():
        quantity_index = header_row[header_row.apply(lambda x: _normalize_header_name(x) == _normalize_header_name(original_header))].index
        if not quantity_index.empty:
            header_indices[normalized_name] = quantity_index[0]
            if found_quantity_header is None:
                found_quantity_header = normalized_name 
                
    # 4. Buscamos Tarifa
    for original_header, _ in COLUMNAS_TARIFA_BRUTA.items():
        tarifa_index = header_row[header_row.apply(lambda x: _normalize_header_name(x) == _normalize_header_name(original_header))].index
        if not tarifa_index.empty:
            header_indices["TARIFA"] = tarifa_index[0]
            break

    # 5. Buscamos Total
    for original_header, _ in COLUMNAS_TOTAL_BRUTA.items():
        total_index = header_row[header_row.apply(lambda x: _normalize_header_name(x) == _normalize_header_name(original_header))].index
        if not total_index.empty:
            header_indices["TOTAL"] = total_index[0]
            break
        
    # 6. Buscamos columnas de Observaciones
    observation_indices = {}
    for obs_header in COLUMNAS_OBSERVACIONES_BRUTAS:
        obs_index = header_row[header_row.apply(lambda x: _normalize_header_name(x) == _normalize_header_name(obs_header))].index
        if not obs_index.empty:
            observation_indices[obs_header] = obs_index[0]
            
    header_indices['OBSERVACIONES_MAP'] = observation_indices 
    
    return header_indices, found_quantity_header, header_row_index + 1


def _extract_data_from_section(sheet, section_title, section_range, sheet_name, file_name, client_name):
    """
    Extrae los datos de una sección VTA dada, asegurando la validación 
    de Fecha y Cantidad/Kg.
    """
    start_row, end_row = section_range
    extracted_data = []

    # 1. Encontrar índices de cabecera y fila de datos
    header_info, found_quantity_name, data_row_start = _find_header_indices(sheet, start_row, end_row - start_row)
    
    if CABECERA_FECHA not in header_info or not found_quantity_name:
        return []
        
    fecha_col_index = header_info[CABECERA_FECHA]
    quantity_col_indices = {k: v for k, v in header_info.items() if k in COLUMNAS_CANTIDAD_BRUTA.values()}
    
    tarifa_col_index = header_info.get("TARIFA") 
    total_col_index = header_info.get("TOTAL")   
    observation_map = header_info.get('OBSERVACIONES_MAP', {})
    
    # 2. Iterar sobre las filas de datos
    for i in range(data_row_start, end_row):
        row = sheet.iloc[i] 
        
        # Uso de .iloc[] para acceso robusto a la celda por posición
        fecha_val = row.iloc[fecha_col_index] if fecha_col_index < len(row) else np.nan 
        
        has_quantity = False
        cantidad_valores = {} 
        
        for name, index in quantity_col_indices.items():
            val = row.iloc[index] if index < len(row) else np.nan
            
            if pd.notna(val) and isinstance(val, (int, float, str)):
                try:
                    # Limpieza preliminar para validación numérica (soportando formatos de miles)
                    val_str = str(val).replace('$', '').replace('.', '').replace(',', '').strip()
                    num_val = float(val_str)
                    if num_val != 0:
                        has_quantity = True
                        cantidad_valores[name] = val
                except ValueError:
                    pass

        # 🛑 REGLA CLAVE: Ignorar fila si no hay FECHA O no hay CANTIDAD válida
        if pd.isna(fecha_val) or not has_quantity:
            continue
            
        # 3. Construir la fila de datos
        row_data = {
            'FECHA_MOVIMIENTO': fecha_val,
            'CLIENTE': client_name, # Nombre del cliente capturado
            'TIPO_MOVIMIENTO': section_title,
            'ORIGEN_SECCION': section_title,
            'ORIGEN_HOJA': sheet_name,
            'FUENTE_ARCHIVO': file_name,
            'CANTIDAD_MOVIMIENTO': None,
            'SUBTIPO_MOVIMIENTO': None, 
            
            # Captura de TARIFA, TOTAL y OBSERVACIONES
            'TARIFA': row.iloc[tarifa_col_index] if tarifa_col_index is not None and tarifa_col_index < len(row) else None,    
            'TOTAL': row.iloc[total_col_index] if total_col_index is not None and total_col_index < len(row) else None,     
            'OBSERVACIONES': "" 
        }
        
        # 4. Asignar CANTIDAD y SUBTIPO (usando el primer subtipo encontrado)
        if found_quantity_name and found_quantity_name in cantidad_valores:
            row_data['SUBTIPO_MOVIMIENTO'] = found_quantity_name
            row_data['CANTIDAD_MOVIMIENTO'] = cantidad_valores[found_quantity_name]
        
        # 5. Consolidar OBSERVACIONES
        observations = []
        for obs_name, obs_index in observation_map.items():
            obs_val = row.iloc[obs_index] if obs_index < len(row) else None
            if pd.notna(obs_val):
                observations.append(f"{obs_name}: {obs_val}")
                
        row_data['OBSERVACIONES'] = ' | '.join(observations)

        extracted_data.append(row_data)

    return extracted_data


# ==============================================================================
# FUNCIÓN PRINCIPAL
# ==============================================================================

def extract_data_from_excel(file_path):
    """
    Procesa un archivo Excel, extrayendo datos de todas las secciones VTA.
    """
    try:
        xls = pd.ExcelFile(file_path, engine='openpyxl')
        all_data = []
        file_name = os.path.basename(file_path)
        
        print(f"  -> Procesando {file_name}...")
        
        client_name = ""
        
        # 1. Buscar el nombre del cliente en la primera hoja
        if xls.sheet_names:
            # Solo analizamos la primera hoja para el nombre del cliente
            first_sheet = xls.parse(xls.sheet_names[0], header=None)
            client_name = _find_client_name(first_sheet) 

        # 2. Fallback: Si no se encuentra en la hoja, usar el nombre del archivo
        if not client_name:
            client_name = file_name.split(' ')[0].split('-')[0].split('_')[0]
            
        print(f"    -> Cliente identificado: {client_name}")
        
        # 3. Iterar sobre todas las hojas para la extracción VTA
        for sheet_name in xls.sheet_names:
            # Omitir hojas de resumen o de metadatos
            if sheet_name.lower() in ['resumen', 'general', 'datos', 'cierre', 'factura']:
                continue
                
            sheet = xls.parse(sheet_name, header=None)
            
            # Identificar secciones VTA
            vta_sections = []
            current_section_title = None
            current_section_start = -1
            
            vta_pattern = re.compile(r'\(VTA\d{3}\)', re.IGNORECASE)
            
            for row_idx in range(len(sheet)):
                row = sheet.iloc[row_idx]
                
                # Busca el patrón en toda la fila y retorna el objeto Match si lo encuentra
                title_match = row.apply(lambda x: vta_pattern.search(str(x).upper())).dropna()
                
                if not title_match.empty:
                    # Capturamos el valor de la celda que contiene el patrón
                    cell_index_with_vta = title_match.index[0]
                    new_title = str(row.loc[cell_index_with_vta]) 
                    
                    if current_section_title is not None:
                        vta_sections.append({
                            'title': current_section_title,
                            'range': (current_section_start, row_idx)
                        })
                    
                    current_section_title = new_title
                    current_section_start = row_idx
                
            # Cerrar la última sección encontrada
            if current_section_title is not None:
                vta_sections.append({
                    'title': current_section_title,
                    'range': (current_section_start, len(sheet))
                })

            # Extraer datos de cada sección VTA
            for section in vta_sections:
                data = _extract_data_from_section(
                    sheet, 
                    section['title'], 
                    section['range'], 
                    sheet_name, 
                    file_name,
                    client_name
                )
                all_data.extend(data)
                
        return all_data

    except Exception as e:
        print(f"  -> ❌ Error al procesar el archivo {os.path.basename(file_path)}: {e}")
        return []