

# 📄 README: ETL - CONSOLIDADOR DE MOVIMIENTOS VTA ICESTAR

**Autor:** Daniel Davila Lesmes
**Empresa:** IceStar Latam - Medellín
**Contacto:** daniel.davila@icestarlatam.com

**Copyright © 2025 IceStar Latam. Todos los derechos reservados.**
**Versión:** 01
**Fecha:** 2025-12-03

---

## 🚀 Descripción del Proyecto

Este proyecto implementa un proceso ETL (Extracción, Transformación y Carga) en Python diseñado para consolidar datos de múltiples reportes de facturación de servicios (Excel/XLSM) generados por el sistema de IceStar, identificados mediante códigos **VTA###**.

El script maneja la variabilidad en la estructura de los archivos fuente (columnas de datos, posición del cliente y secciones de servicio VTA) mediante lógica de detección dinámica y regularización.

### Características Clave

* **Detección Dinámica de Clientes:** Identifica el nombre del cliente buscando la etiqueta "Cliente" en las primeras filas, sin depender de una celda fija.
* **Detección Universal de Servicios (VTA###):** Utiliza expresiones regulares para encontrar y extraer datos de **cualquier sección** cuyo título contenga el patrón `VTA` seguido de tres dígitos (ej., VTA019, VTA010, VTA025).
* **Extracción de Columnas Variables:** Mapea cabeceras comunes de cantidad (`Cargue`, `Descargue`, `Entradas`, `Salidas`, `Cantidad`, `Horas`, etc.) a una única columna consolidada (`CANTIDAD_MOVIMIENTO`).
* **Salida Estandarizada:** Genera un único archivo **`.xlsx`** consolidado con una estructura limpia y fácil de analizar, incluyendo el nombre del archivo y la hoja de origen (`ORIGEN_HOJA`).

---

## ⚙️ Prerrequisitos

Para ejecutar el proyecto, necesitarás tener instalado Python y las siguientes librerías:

1.  **Python 3.8+**
2.  **Librerías Python:** `openpyxl` y `datetime` (incluida en Python estándar).

Puedes instalar las dependencias usando `pip`:

```bash
pip install openpyxl
````

-----

## 📁 Estructura del Proyecto

La estructura del proyecto es modular y sigue el patrón ETL:

````
/etl_process_movimientos_vta
├── src/                      # Módulos del proceso ETL
│   ├── __init__.py           # Inicialización del paquete
│   ├── config.py             # Constantes y configuración global
│   ├── extract.py            # Lógica de extracción y detección dinámica
│   ├── transform.py          # Lógica de limpieza y estandarización de datos
│   └── load.py               # Lógica de carga (generación del archivo XLSX)
├── Export/                   # Directorio de salida (generado por el script)
│   └── Reportes/             # Contiene el archivo consolidado final
│       └── Movimientos_VTA_Consolidado.xlsx
├── Work/                     # Directorio de trabajo (temporal, generado por el script)
└── run_etl.py                # Script principal de ejecución

````

-----

## 📝 Instrucciones de Uso

Sigue estos pasos para replicar y ejecutar el proceso ETL:

### 1\. Preparación del Entorno

1.  Clona o descarga el proyecto en tu máquina local.
2.  Crea una carpeta que contenga los archivos fuente de Excel/XLSM que deseas procesar.
      * *Ejemplo de ruta de la carpeta fuente:* `C:\MisDocumentos\Facturacion_IceStar`

### 2\. Configuración de Rutas

Abre el archivo principal **`run_etl.py`** y localiza la sección `1. CONFIGURACIÓN DE RUTAS`.

Modifica la variable `SOURCE_DIR` para que apunte a la ruta de la carpeta donde se encuentran tus archivos Excel:

```python
# run_etl.py (Fragmento)

# Carpeta fuente de los archivos (¡AJUSTAR ESTA RUTA!)
SOURCE_DIR = r"C:\MisDocumentos\Facturacion_IceStar" 
```

### 3\. Ejecución del ETL

Ejecuta el script principal desde la línea de comandos (asegúrate de estar en el directorio raíz del proyecto):

```bash
python run_etl.py
```

### 4\. Resultados

Al finalizar la ejecución:

  * El sistema copiará todos los archivos `.xlsx` y `.xlsm` a la carpeta temporal **`./Work`**.
  * El archivo de salida consolidado se generará en **`./Export/Reportes/Movimientos_VTA_Consolidado.xlsx`**.

-----

## 📊 Estructura del Archivo de Salida

El archivo `Movimientos_VTA_Consolidado.xlsx` tendrá las siguientes columnas:

| Columna | Descripción | Ejemplo de Valor |
| :--- | :--- | :--- |
| **FECHA\_MOVIMIENTO** | Fecha de la operación (formato YYYY-MM-DD). | 2025-12-03 |
| **CLIENTE** | Nombre del cliente extraído dinámicamente. | ATLANTIC |
| **TIPO\_MOVIMIENTO** | Título completo de la sección VTA. | CARGUE Y/O DESCARGUE (VTA019) |
| **SUBTIPO\_MOVIMIENTO** | Tipo de movimiento específico extraído. | Cargue, Entrada, Horas, Cantidad |
| **CANTIDAD\_MOVIMIENTO** | Valor numérico de la cantidad (Kilos, Horas, Unidades). | 6335.00 |
| **ORIGEN\_SECCION** | Nombre de la cabecera original del valor. | Cargue, Cantidad |
| **ORIGEN\_HOJA** | **Nombre de la hoja** donde se extrajo el dato. | Hoja1, Enero 2025 |
| **FUENTE\_ARCHIVO** | Nombre del archivo Excel original. | Amazonas 2025.xlsm |

-----

## 🔑 Archivos de Configuración Importantes

| Archivo | Variables Clave | Propósito |
| :--- | :--- | :--- |
| **`src/config.py`** | `COLUMNAS_ESTANDAR` | Define el orden y el nombre de las 8 columnas de salida. |
| | `COLUMNAS_CANTIDAD_BRUTA` | Diccionario de mapeo de cabeceras brutas (`Cargue`, `Cantidad`, etc.) a subtipos. |
| **`src/extract.py`** | `VTA_PATTERN` | Expresión regular que define la búsqueda de `(VTA\d{3})`. |
| | `get_client_name()` | Función que implementa la detección dinámica del cliente. |

```