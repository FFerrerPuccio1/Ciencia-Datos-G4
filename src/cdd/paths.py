"""Rutas del proyecto."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
RAW_XLSX = DATA_RAW / "mapa_rendimiento.xlsx"
PROCESSED_PARQUET = DATA_PROCESSED / "mapa_rendimiento.parquet"
SHEET_NAME = "julio_oviedo_lote_120__maiz_202"
