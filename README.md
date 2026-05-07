# MacroQuant Lab

MacroQuant Lab es un proyecto de aprendizaje aplicado para estudiar activos financieros, riesgo, rentabilidad y variables macroeconomicas con Python.

La idea central es construir, paso a paso, una herramienta que permita responder preguntas como:

- Que activos han tenido mejor rentabilidad ajustada por riesgo?
- Como cambian volatilidad y drawdowns entre renta variable, bonos, oro, dolar y Bitcoin?
- Que ocurre con distintos activos cuando cambian los tipos, la inflacion o el ciclo economico?
- Que cartera simple se comporta mejor frente a un benchmark?

## Fase Actual

La Fase 1 ya esta funcional: analisis exploratorio de activos.

Incluye:

1. Descargar precios de activos financieros.
2. Calcular retornos diarios y mensuales.
3. Medir rentabilidad anualizada, volatilidad, Sharpe y drawdown maximo.
4. Visualizar rentabilidad acumulada, drawdowns y correlaciones.
5. Dejar el codigo preparado para dashboard.

Estamos entrando en la Fase 2: analisis macro y regimenes economicos.

Incluye:

1. Descargar variables macroeconomicas desde FRED.
2. Transformar datos macro en indicadores interpretables.
3. Clasificar meses en regimenes simples de inflacion, tipos, crecimiento y curva.
4. Estudiar que activos se comportan mejor en cada regimen.

## Activos Iniciales

El proyecto empieza con activos liquidos y faciles de consultar desde Yahoo Finance:

| Nombre | Ticker | Idea que representa |
| --- | --- | --- |
| S&P 500 | SPY | Bolsa estadounidense amplia |
| Nasdaq 100 | QQQ | Crecimiento y tecnologia |
| Oro | GLD | Activo refugio |
| Bonos USA largo plazo | TLT | Duracion y sensibilidad a tipos |
| Bitcoin | BTC-USD | Criptoactivo |
| Petroleo | USO | Energia y materias primas |
| Dolar USA | UUP | Fortaleza del dolar |
| Apple | AAPL | Empresa tecnologica |
| Microsoft | MSFT | Empresa tecnologica |
| Nvidia | NVDA | Semiconductores e IA |
| Santander | SAN.MC | Banco europeo |
| Inditex | ITX.MC | Consumo europeo |

## Variables Macro Iniciales

| Variable | Fuente FRED | Uso |
| --- | --- | --- |
| CPI | CPIAUCSL | Inflacion interanual |
| Fed Funds Rate | FEDFUNDS | Tipos de interes oficiales |
| Desempleo | UNRATE | Mercado laboral |
| PIB real | GDPC1 | Crecimiento economico |
| Treasury 10Y | DGS10 | Tipo largo |
| Treasury 2Y | DGS2 | Tipo corto |
| Treasury 10Y real | DFII10 | Tipo real |
| M2 | M2SL | Masa monetaria |
| VIX | VIXCLS | Volatilidad esperada del S&P 500 |

## Estructura

```text
macroquant-lab/
|-- app/
|   `-- streamlit_app.py
|-- data/
|   |-- raw/
|   `-- processed/
|-- notebooks/
|   |-- 01_asset_exploration.ipynb
|   `-- 02_macro_regimes.ipynb
|-- reports/
|-- scripts/
|   |-- run_asset_snapshot.py
|   `-- run_macro_snapshot.py
|-- src/
|   `-- macroquant_lab/
|       |-- config.py
|       |-- data_loader.py
|       |-- macro.py
|       |-- metrics.py
|       `-- visualization.py
|-- tests/
|-- README.md
|-- pyproject.toml
`-- requirements.txt
```

## Instalacion

Desde la carpeta del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## Analisis

Ejecuta el snapshot de activos:

```powershell
python scripts/run_asset_snapshot.py
```

Ejecuta el snapshot macro:

```powershell
python scripts/run_macro_snapshot.py
```

Abre los notebooks:

```text
notebooks/01_asset_exploration.ipynb
notebooks/02_macro_regimes.ipynb
```

El primer notebook estudia:

- `price`: precio ajustado del activo.
- `return`: variacion porcentual entre dos fechas.
- `volatility`: dispersion de los retornos.
- `Sharpe ratio`: rentabilidad por unidad de riesgo.
- `drawdown`: caida desde un maximo previo.
- `correlation`: relacion lineal entre activos.

El segundo notebook estudia:

- inflacion interanual.
- tipos oficiales.
- curva 10Y-2Y.
- crecimiento del PIB.
- rentabilidad de activos por regimen macro.

## Dashboard

Cuando quieras probar la app:

```powershell
streamlit run app/streamlit_app.py
```

El dashboard incluye:

- precios.
- rentabilidad acumulada.
- drawdowns.
- correlaciones.
- indicadores macro.
- retornos por regimen macro.
- tabla de metricas.

## Ruta De Aprendizaje

1. Medir activos: retornos, volatilidad, Sharpe, drawdown y correlaciones.
2. Introducir macro: inflacion, tipos, desempleo, PIB, VIX y curva 10Y-2Y.
3. Definir regimenes macroeconomicos.
4. Construir estrategias simples: momentum, medias moviles y risk parity.
5. Comparar carteras contra benchmark.
6. Convertir el trabajo en dashboard, informe y demo presentable.

## Nota

Este repositorio es educativo. No contiene recomendaciones de inversion ni pretende predecir precios.
