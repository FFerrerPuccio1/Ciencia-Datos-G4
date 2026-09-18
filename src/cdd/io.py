"""Carga del mapa de rendimiento (Excel y Parquet)."""

from pathlib import Path

import pandas as pd

from cdd.paths import PROCESSED_PARQUET, RAW_XLSX, SHEET_NAME


def load_raw(path: Path | None = None, sheet_name: str = SHEET_NAME) -> pd.DataFrame:
    """Lee el Excel original. La primera vez puede tardar varios minutos."""
    source = path or RAW_XLSX
    if not source.exists():
        raise FileNotFoundError(
            f"No se encontró el Excel en {source}. "
            "Copiá el archivo a data/raw/mapa_rendimiento.xlsx"
        )
    return pd.read_excel(source, sheet_name=sheet_name, engine="openpyxl")


def to_parquet(df: pd.DataFrame, path: Path | None = None) -> Path:
    """Guarda el DataFrame en Parquet para lecturas posteriores rápidas."""
    target = path or PROCESSED_PARQUET
    target.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(target, index=False)
    return target


def load_processed(path: Path | None = None) -> pd.DataFrame:
    """Lee el Parquet procesado. Si no existe, hay que generar primero el Excel."""
    source = path or PROCESSED_PARQUET
    if not source.exists():
        raise FileNotFoundError(
            f"No hay Parquet en {source}. Ejecutá load_raw() y to_parquet() una vez."
        )
    return pd.read_parquet(source)
