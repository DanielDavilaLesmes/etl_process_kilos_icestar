# src/config.py

# ==============================================================================
# 1. METADATOS Y VARIABLES GENERALES
# ==============================================================================

# Nombre del archivo consolidado de salida AHORA ES XLSX
OUTPUT_FILENAME = "Movimientos_VTA_Consolidado.xlsx" 

# Nombre del archivo de log para el reporte de cumplimiento SAC
SAC_LOG_FILENAME = "SAC_Reporte_Cumplimiento.log"

# Columna Estándar de Salida (con TIPO, SUBTIPO y CANTIDAD_MOVIMIENTO)
COLUMNAS_ESTANDAR = [
    'FECHA_MOVIMIENTO', 
    'CLIENTE', 
    'TIPO_MOVIMIENTO',       # Título completo de la sección (ej: CARGUE Y/O DESCARGUE (VTA019))
    'SUBTIPO_MOVIMIENTO',    # Cabecera específica (ej: Cargue, Descargue, Horas, Cantidad)
    'CANTIDAD_MOVIMIENTO',   # Valor numérico extraído
    'ORIGEN_SECCION',
    'ORIGEN_HOJA',        # Nombre de la cabecera bruta (ej: Cargue, Descargue)
    'FUENTE_ARCHIVO'         # Nombre del archivo fuente
]

# ⚠️ La lógica de cliente es dinámica en extract.py

# ==============================================================================
# 2. LÓGICA DE EXTRACCIÓN DINÁMICA
# ==============================================================================

# Cabeceras que contienen la cantidad/valor a extraer
COLUMNAS_CANTIDAD_BRUTA = {
    "Cargue": "Cargue",     
    "Descargue": "Descargue", 
    "Entradas": "Entrada",
    "Entrada":"Entrada",   
    "Salidas": "Salida",     
    "Cantidad": "Cantidad",   
    "Horas": "Horas",        
    "kg Cargue": "Kg_Cargue",
    "Kg Descargue": "Kg_Descargue"
}

# Cabecera que siempre contiene la fecha
CABECERA_FECHA = "Fecha"