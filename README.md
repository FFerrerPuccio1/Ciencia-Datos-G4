# CDD — Mapa de rendimiento

Proyecto de ciencia de datos en Python para analizar un mapa de rendimiento de maíz (monitor de cosecha) del lote **Oviedo - Lote1**.

Cada fila es un **punto georreferenciado** registrado por el monitor: rendimiento, humedad, velocidad y coordenadas.

## Requisitos

- Python 3.11 o superior (probado con 3.13)
- El Excel original, copiado como `data/raw/mapa_rendimiento.xlsx`

## Setup

En la raíz del proyecto:

```bash
python -m venv .venv
```

Windows (Git Bash / bash):

```bash
source .venv/Scripts/activate
pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Para importar el paquete `cdd` desde notebooks o scripts:

```bash
export PYTHONPATH=src
```

En PowerShell: `$env:PYTHONPATH = "src"`

## Cómo correr el EDA

```bash
export PYTHONPATH=src
jupyter notebook notebooks/01_eda_mapa_rendimiento.ipynb
```

O con Jupyter Lab:

```bash
jupyter lab notebooks/01_eda_mapa_rendimiento.ipynb
```

**La primera lectura del Excel puede tardar varios minutos** (~103 mil filas, XML interno ~80 MB). El notebook guarda un Parquet en `data/processed/mapa_rendimiento.parquet`. Las corridas siguientes deben usar ese archivo.

## Dataset

| Ítem | Valor |
| --- | --- |
| Archivo crudo | `data/raw/mapa_rendimiento.xlsx` (copia de `mapa rendimient.xlsx`) |
| Hoja | `julio_oviedo_lote_120__maiz_202` |
| Filas | ~103.440 |
| Columnas | 21 |
| Cultivo / lote | Maíz, Oviedo - Lote1 |
| Coordenadas | `lat` ≈ -32.66, `lon` ≈ -64.27 |

### Columnas

**Identificación**

| Columna | Descripción |
| --- | --- |
| `fid` | Identificador de fila |
| `Field` | Nombre del lote (`Oviedo - Lote1`) |
| `Dataset` | Identificador de pasada (`TLG00067`, …) |
| `Pass_Num` | Número de pasada |
| `Obj__Id` | ID de objeto del monitor |

**Rendimiento**

| Columna | Descripción |
| --- | --- |
| `Yld_Mass_W` | Masa de rendimiento húmedo |
| `Yld_Mass_D` | Masa de rendimiento seco |
| `Moisture__` | Humedad (%) |
| `Crop_Flw_M` | Flujo de cultivo (masa) |
| `Crop_Flw_V` | Flujo de cultivo (volumen) |
| `Prod_ha_h_` | Productividad (ha/h) |

**Operación**

| Columna | Descripción |
| --- | --- |
| `Swth_Wdth_` | Ancho de labor |
| `Speed_km_h` | Velocidad (km/h) |
| `Distance_m` | Distancia del intervalo (m) |
| `Duration_s` | Duración del intervalo (s) |
| `Track_deg_` | Rumbo (grados) |
| `Area_Count` | Estado de conteo de área (`On` / otros) |

**Espacio-tiempo**

| Columna | Descripción |
| --- | --- |
| `Elevation_` | Elevación |
| `Time` | En el Excel es serial de fecha; pandas suele convertirlo al leer. Si queda numérico, `clean_yield_map` lo pasa a datetime |
| `lat` | Latitud |
| `lon` | Longitud |

## Estructura

```
CDD/
├── data/
│   ├── raw/mapa_rendimiento.xlsx
│   └── processed/          # Parquet generado (gitignored)
├── notebooks/
│   └── 01_eda_mapa_rendimiento.ipynb
├── src/cdd/
│   ├── io.py               # load_raw, to_parquet, load_processed
│   ├── cleaning.py         # tipos, fecha, filtros mínimos
│   └── paths.py
├── requirements.txt
└── README.md
```

Flujo:

1. `load_raw()` lee el Excel.
2. `to_parquet()` guarda una copia rápida.
3. `clean_yield_map()` tipifica columnas, convierte `Time` y filtra coordenadas nulas y valores no físicos (velocidad, rendimiento negativo, humedad fuera de 0–40 %).

## Reproducir el EDA

Con el venv activo y `PYTHONPATH=src`:

```python
from cdd.io import load_processed, load_raw, to_parquet
from cdd.cleaning import clean_yield_map
from cdd.paths import PROCESSED_PARQUET

if PROCESSED_PARQUET.exists():
    df = load_processed()
else:
    df = load_raw()
    to_parquet(df)

clean = clean_yield_map(df)
print(clean.shape)
```

El notebook `01_eda_mapa_rendimiento.ipynb` cubre esquema, nulos, distribuciones, mapa de puntos por `Yld_Mass_D` y comparación por pasada (`Dataset`).

## Siguientes pasos (fuera de esta base)

- Interpolación espacial (p. ej. kriging) e interpolación a grilla
- Filtrado avanzado de bordes de lote y arranques de pasada
- Modelos predictivos o zonificación
- Informe de hallazgos
