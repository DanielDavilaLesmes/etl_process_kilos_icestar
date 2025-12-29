# src/config.py
# Módulo de configuración global del ETL.

# ==============================================================================
# 1. METADATOS Y VARIABLES GENERALES
# ==============================================================================

OUTPUT_FILENAME = "Movimientos_VTA_Consolidado.xlsx" 
SAC_LOG_FILENAME = "SAC_Reporte_Cumplimiento.log"

# Columna Estándar de Salida (Estructura final con 17 columnas)
COLUMNAS_ESTANDAR = [
    'FECHA_MOVIMIENTO', 
    'CLIENTE',                   
    'CLIENTE_ESTANDAR',          
    'NIT',                       
    'TIPO_MOVIMIENTO',           
    'TIPO_MOVIMIENTO_LIMPIO',    
    'CLASIFICACION_VTA',         
    'SUBTIPO_MOVIMIENTO',        
    'SUBTIPO_MOVIMIENTO_LIMPIO', 
    'CLASIFICACION_SUBTIPO',     
    'CANTIDAD_MOVIMIENTO',
    'TARIFA',                   # Nueva columna
    'TOTAL',                    # Nueva columna
    'OBSERVACIONES',            # Nueva columna
    'ORIGEN_SECCION',        
    'ORIGEN_HOJA',           
    'FUENTE_ARCHIVO'         
]

# ==============================================================================
# 2. LÓGICA DE EXTRACCIÓN DINÁMICA
# ==============================================================================

CABECERA_FECHA = "Fecha"

# Mapeo de Cabeceras de Cantidad/Valor (Bruto -> Estándar)
COLUMNAS_CANTIDAD_BRUTA = {
    "Cargue": "CARGUE",     
    "Descargue": "DESCARGUE", 
    "Entradas": "ENTRADA",   
    "Salidas": "SALIDA",     
    "Cantidad": "CANTIDAD",   
    "Horas": "HORAS",        
    "Kg Cargue": "KG_CARGUE_VTA43", 
    "Kg Descargue": "KG_DESCARGUE",
    "Cargue cx": "CARGUE_CX",
    "Descargue cx": "DESCARGUE_CX",
    "Posiciones Contratadas": "POSICIONES_CONTRATADAS",
    "Posiciones Ocupadas": "POSICIONES_OCUPADAS"
}

# Mapeo de Cabeceras de Tarifa (Bruto -> Estándar)
COLUMNAS_TARIFA_BRUTA = {
    "Tarifa": "TARIFA",
    "Tarifas": "TARIFA",
    "Tarifa c/u": "TARIFA",
    "Tarifa unitaria": "TARIFA"
}

# Mapeo de Cabeceras de Total (Bruto -> Estándar)
COLUMNAS_TOTAL_BRUTA = {
    "Total": "TOTAL",
    "Subtotal": "TOTAL",
    "Total General": "TOTAL"
}

# Cabeceras que contienen información de observaciones o texto descriptivo
COLUMNAS_OBSERVACIONES_BRUTAS = [
    "Nota",                       
    "Facturas correspondientes",  
    "Proveedor",
    "Remision"                     # Remisión se incluye para contexto
]

# ==============================================================================
# 3. CLASIFICACIÓN DE MOVIMIENTOS Y CLIENTES
# ==============================================================================

# Clasificación de VTA (Usando TIPO_MOVIMIENTO_LIMPIO = VTA###)
VTA_CLASSIFICATION_MAP = {
    "INGRESO": ["VTA010", "VTA037"], 
    "SALIDA": ["VTA012", "VTA014"],
    "INTERNO": ["VTA017", "VTA029"],
    "SERVICIO_OPERACIONAL": ["VTA019", "VTA036", "VTA011", "VTA021"],
    "SERVICIO_AUXILIAR": ["VTA025"],
    "ALMACENAMIENTO": ["VTA008"]
}

# Clasificación de Subtipos (Usando SUBTIPO_MOVIMIENTO_LIMPIO)
SUBTIPO_CLASSIFICATION_MAP = {
    "KILOS_O_PESO": ["KG_CARGUE_VTA43", "KG_DESCARGUE"],
    "UNIDADES_Y_OTROS": ["CARGUE", "DESCARGUE", "CARGUE_CX", "DESCARGUE_CX", "CANTIDAD", "POSICIONES_CONTRATADAS", "POSICIONES_OCUPADAS"],
    "TIEMPO_O_COSTO": ["HORAS"]
}

# Nota: CLIENT_MAPPING se carga desde 'client_mapping.json' en transform.py