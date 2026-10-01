# Guion de presentación — EDA mapa de rendimiento

Presentación **solo con la notebook** [`01_eda_mapa_rendimiento.ipynb`](01_eda_mapa_rendimiento.ipynb). No uses PowerPoint: abrí el `.ipynb` en Jupyter o Colab y recorré las celdas. Este archivo es el texto oral.

**Orden en vivo:** carga → nulos y rangos → `clean_yield_map` → boxplots → histogramas → mapa → pasadas → correlación → notas.

La celda de boxplots usa `clean` **antes** de definirlo. Corré primero la sección 3 (`clean = clean_yield_map(df)`) y recién después los boxplots.

Saltá las celdas de setup de Colab salvo que pregunten por reproducibilidad.

**Antes vs después (honesto):** el filtro no sacó filas. El “antes” es esquema + nulos + rangos sobre `df`. El “después” es el mismo recuento (103.439) con tipos y `Time` tipificados. No hay un mapa o histograma crudo distinto del limpio: **eso es el hallazgo**.

---

## Apertura (celda 0)

Este trabajo es un EDA de un **mapa de rendimiento de maíz** del lote **Oviedo - Lote1**. Cada fila es un punto georreferenciado del monitor de cosecha: rendimiento, humedad, velocidad, elevación y coordenadas. El Excel es pesado, unas 103 mil filas; lo convertimos a Parquet para no releerlo cada vez.

El notebook termina en **calidad de dato**. No prometas interpolación, kriging ni modelos.

---

## 1. Carga (Excel → Parquet)

Mostrá `df.shape` y `df.head()`.

Quedaron **103.439 filas y 21 columnas**. Un lote, muchas pasadas (`Dataset`, por ejemplo `TLG00067`). La variable de interés espacial es **`Yld_Mass_D`** (masa seca), no la húmeda, porque ya descuenta humedad del grano.

---

## 2. Limpieza y transformación (lo de más impacto)

Acá va nulos, faltantes, extremos y selección de columnas.

### Nulos y faltantes

Mostrá la tabla de nulos: **todo 0**.

No hubo imputación porque **no hay nulos**. Tampoco hay columnas vacías. El problema de calidad no es “faltantes en Excel”, sino **valores operativos raros** típicos de monitor (cabeceras, velocidad, GPS). El código está preparado para cortarlos aunque **en este lote el filtro no disparó**.

### Transformaciones que sí importan

La limpieza está en `clean_yield_map`:

1. **Tipos numéricos** (`pd.to_numeric`): evita que un número venga como texto y rompa gráficos o correlación.
2. **`Time`**: serial de Excel → datetime (origen 1899-12-30). En el `describe`, las fechas caen en **2007-01-01**. Si preguntan: es un serial mal anclado o sin zona horaria; no lo uses como calendario agrícola real sin cruzar otra fuente.
3. **Filtros físicos** (impacto en *este* dataset = **0 filas**):
   - `lat` / `lon` no nulos
   - velocidad **0.1–20 km/h**
   - rendimiento húmedo y seco **≥ 0**
   - humedad **0–40 %**

Mostrá: **filas crudas 103.439 / limpias 103.439 / descartadas 0**.

El impacto no fue “borramos basura”: fue **validar que el crudo ya estaba dentro de rangos físicos**. Velocidad 1.28–14.2 km/h, humedad 14.0–16.5 %, rendimiento seco 3.43–11.51, GPS completo. El código queda como red de seguridad para el próximo lote.

### Extremos (no nulos)

Aunque no se filtraron, **sí hay colas**. Eso se ve en el boxplot y en el `describe`.

| Variable | min | mediana | max | Qué decir |
| --- | --- | --- | --- | --- |
| `Yld_Mass_D` | 3.43 | 7.52 | 11.51 | Colas: cabeceras o zonas reales. No se recortó por IQR a propósito (limpieza *mínima*). |
| `Moisture__` | 14.04 | 15.31 | 16.55 | Muy concentrada (~15 %). Pocos extremos. |
| `Speed_km_h` | 1.28 | 6.01 | 14.22 | Caja ~5.5–6.5. Máximos: posible traslado o cambio de pasada. |
| `Elevation_` | 539.8 | 555.5 | 565.8 | Relieve suave (~26 m). |

**Criterio de extremos:** umbrales **físicos** (velocidad, humedad, rendimiento negativo, GPS), no percentiles. Justificación: no queremos borrar variación espacial real del lote.

### Selección de columnas

No se dropearon columnas del archivo: siguen **21**. Para el análisis se eligió un subconjunto.

**Se usan en gráficos:** `Yld_Mass_D`, `Moisture__`, `Speed_km_h`, `Elevation_`, `Dataset`, `lat`, `lon`, `Time`.

**Se dejan fuera del relato** (constantes o IDs):

- `Field`: un solo valor (`Oviedo - Lote1`); no discrimina.
- `Area_Count`: siempre `On`; no discrimina.
- `Swth_Wdth_`: siempre **6.825**; no hay variación. El notebook avisa que el solape real no está en esa columna.
- `fid`, `Obj__Id`, `Pass_Num`: identificadores. `Pass_Num` se sustituye por `Dataset` (9 pasadas) en el boxplot.
- `Yld_Mass_W`, flujos, `Prod_ha_h_`, `Distance_m`, `Duration_s`, `Track_deg_`: no entran a histogramas, mapa ni correlación. Criterio: **evitar colinealidad y ruido operativo**. El target es masa seca más contexto (humedad, marcha, relieve, espacio).

Si preguntan `Yld_Mass_W` vs `Yld_Mass_D`: se prioriza **seca** porque la húmeda mezcla agua del grano con productividad.

Si preguntan por las unidades de los ejes: el notebook dice kg/ha; las magnitudes ~7.5 son las típicas de **t/ha** en maíz. No inventes: “así está rotulado en el EDA”.

---

## 3. Gráficos

### Boxplots — auditoría de outliers (“antes” conceptual)

Cuatro cajas: rendimiento seco, humedad, velocidad, elevación (`showfliers=True`).

Sirve para **ver colas**, no para zonificar. Humedad casi sin outliers. Velocidad tiene puntos altos (14 km/h) lejos de la operación típica (~6 km/h). Rendimiento tiene bigotes anchos: heterogeneidad intra-lote. Elevación simétrica y acotada.

**Después del filtro:** las cajas serían iguales (0 filas menos). El proceso **no recortó outliers estadísticos**.

### Histogramas + KDE — forma de la distribución (“después”)

Mismos cuatro ejes.

- **Rendimiento seco:** aproximadamente unimodal, media ≈ mediana (7.56 vs 7.52), desvío 1.31. No hay bimodalidad fuerte: un lote, no dos cultivos.
- **Humedad:** muy picuda (std 0.44). El grano salió parejo; no explica gran parte del mapa de rinde.
- **Velocidad:** centrada en ~6 km/h, cola a la derecha. Relacionable con calidad de medición (flujo/velocidad).
- **Elevación:** dos hombros posibles; relieve del lote, no error.

Estas formas **coinciden con el crudo** porque no filtramos puntos.

### Mapa de puntos por `Yld_Mass_D`

Scatter `lon` / `lat` coloreado por rendimiento seco (muestra de hasta 40.000 puntos, paleta rojo → verde).

Es el producto del EDA: **variación espacial intra-lote**. Zonas verdes = más rinde seco; rojas = menos. El muestreo es para dibujar; el análisis usa las 103 mil filas. Limitación: pueden quedar **bordes y cabeceras**; el ancho fijo no corrige solapes. **No es un mapa interpolado.**

### Boxplot por pasada (`Dataset`)

`showfliers=False`, 9 datasets. La más grande es `TLG00081` (~29.774 puntos).

Compara **sesgo entre archivos/pasadas**, no puntos sueltos. Si una pasada está corrida hacia abajo, puede ser cabecera, horario o un sector del lote. Es control de calidad y primer indicio de zonificación. No afirmes causa (suelo vs operación) solo con este gráfico.

### Heatmap de correlación

Matriz 4×4: rinde, humedad, velocidad, elevación. Pearson lineal.

Esperable: humedad poco ligada al rinde si casi no varía; elevación y velocidad pueden correlacionar débilmente. **No implica causalidad.** Leé los números en el gráfico en vivo; no los memorices. Las variables de flujo no se metieron para no inflar la matriz con colineales del mismo sensor.

---

## Cierre (notas de calidad)

- Cabeceras: velocidad baja o flujo inestable.
- Solapes: `Swth_Wdth_` constante.
- Picos de masa en frenadas o cambio de rumbo.
- `Time` convertido; zona horaria dudosa.
- GPS: no había nulos; los bordes pueden quedar.

**Frase final:**  
En este lote la limpieza mínima **no redujo el n**. El impacto fue **diagnóstico**: dato completo, rangos físicos OK, y la señal está en el **espacio y en las pasadas**, no en imputar nulos. Siguiente paso (fuera de esta notebook): filtrar bordes y, recién ahí, interpolar.

---

## Qué no decir

- Que “limpiamos miles de outliers” (falso: 0 descartadas).
- Que el boxplot de la sección 2 es el crudo si el código usa `clean`.
- Modelos, kriging o recomendaciones agronómicas que el notebook no calcula.
