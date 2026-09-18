"""Limpieza mínima del mapa de rendimiento."""

import pandas as pd

NUMERIC_COLUMNS = [
    "fid",
    "Pass_Num",
    "Obj__Id",
    "Swth_Wdth_",
    "Yld_Mass_W",
    "Yld_Mass_D",
    "Moisture__",
    "Crop_Flw_M",
    "Crop_Flw_V",
    "Speed_km_h",
    "Distance_m",
    "Duration_s",
    "Track_deg_",
    "Elevation_",
    "Prod_ha_h_",
    "lat",
    "lon",
]


def excel_serial_to_datetime(series: pd.Series) -> pd.Series:
    """Convierte serial de Excel a datetime (origen 1899-12-30)."""
    return pd.to_datetime(series, unit="D", origin="1899-12-30")


def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in NUMERIC_COLUMNS:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    if "Time" in out.columns and not pd.api.types.is_datetime64_any_dtype(out["Time"]):
        out["Time"] = excel_serial_to_datetime(pd.to_numeric(out["Time"], errors="coerce"))
    for col in ("Field", "Dataset", "Area_Count"):
        if col in out.columns:
            out[col] = out[col].astype("string")
    return out


def filter_physical(df: pd.DataFrame) -> pd.DataFrame:
    """Descarta coordenadas nulas y valores operativos claramente no físicos."""
    out = df.copy()
    mask = out["lat"].notna() & out["lon"].notna()
    if "Speed_km_h" in out.columns:
        mask &= out["Speed_km_h"].between(0.1, 20)
    if "Yld_Mass_D" in out.columns:
        mask &= out["Yld_Mass_D"] >= 0
    if "Yld_Mass_W" in out.columns:
        mask &= out["Yld_Mass_W"] >= 0
    if "Moisture__" in out.columns:
        mask &= out["Moisture__"].between(0, 40)
    return out.loc[mask].reset_index(drop=True)


def clean_yield_map(df: pd.DataFrame) -> pd.DataFrame:
    """Tipos, fecha y filtros mínimos de calidad."""
    return filter_physical(coerce_types(df))
