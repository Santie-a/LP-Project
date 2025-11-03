import pandas as pd
import yfinance as yf
from typing import List, Dict, Optional, Tuple

from pprint import pprint

import yfinance as yf
from typing import Dict, List, Optional

def get_ticker_types(
    n: int = 20,
    initial_tickers: Optional[List[str]] = None
) -> Dict[str, str]:
    """
    Obtiene un diccionario de tamaño n con tickers y su tipo (“Acciones”, “Bonos”, “ETF”, “Índice”, “Cripto”, “Otros”),
    usando datos de yfinance y un fallback preclasificado.
    
    Si se proporciona initial_tickers, se incluyen primero; el resto se completa con el fallback.
    """

    result: Dict[str, str] = {}

    # --- Fallback preclasificado (más robusto y diverso) ---
    fallback = {
        # Acciones
        "AAPL": "Acciones", "MSFT": "Acciones", "GOOGL": "Acciones", "AMZN": "Acciones",
        "TSLA": "Acciones", "JPM": "Acciones", "JNJ": "Acciones", "XOM": "Acciones",
        "PG": "Acciones", "WMT": "Acciones",

        # ETFs
        "SPY": "ETF", "VOO": "ETF", "VTI": "ETF", "QQQ": "ETF", "GLD": "ETF",
        "SLV": "ETF", "VNQ": "ETF", "XLK": "ETF", "XLF": "ETF", "XLE": "ETF",

        # Bonos / renta fija
        "BND": "Bonos", "TLT": "Bonos", "IEF": "Bonos", "SHY": "Bonos", "LQD": "Bonos",

        # Criptomonedas
        "BTC-USD": "Cripto", "ETH-USD": "Cripto",

        # Commodities
        "USO": "Commodities", "UNG": "Commodities"
    }

    # --- Función auxiliar para inferir tipo desde info de yfinance ---
    def infer_type(info, fallback_type="Otros"):
        qtype = (info.get("quoteType") or "").upper()
        name = ((info.get("shortName") or info.get("longName") or "")).upper()

        if "ETF" in name or qtype == "ETF":
            return "ETF"
        elif qtype == "MUTUALFUND":
            return "Fondo"
        elif qtype == "INDEX":
            return "Índice"
        elif qtype == "BOND":
            return "Bonos"
        elif qtype == "CURRENCY":
            return "Divisa"
        elif qtype == "CRYPTOCURRENCY":
            return "Cripto"
        elif "BOND" in name or "TREASURY" in name:
            return "Bonos"
        elif "FUND" in name:
            return "ETF"
        elif qtype == "EQUITY":
            return "Acciones"
        else:
            return fallback_type

    # --- Procesar tickers iniciales (si existen) ---
    if initial_tickers:
        for ticker in initial_tickers:
            if len(result) >= n:
                break
            try:
                info = yf.Ticker(ticker).info
                fallback_type = fallback.get(ticker, "Otros")
                asset_type = infer_type(info, fallback_type)
                result[ticker] = asset_type
            except Exception:
                result[ticker] = fallback.get(ticker, "Desconocido")

    # --- Completar con fallback preclasificado ---
    for ticker, pre_type in fallback.items():
        if len(result) >= n:
            break
        if ticker in result:
            continue
        try:
            info = yf.Ticker(ticker).info
            asset_type = infer_type(info, pre_type)
            result[ticker] = asset_type
        except Exception:
            result[ticker] = pre_type  # Usa el tipo del fallback como respaldo

    return result


def build_g_matrix(tickers_classes: Dict[str, str]) -> pd.DataFrame:
    """
    Construye la matriz binaria g_{i,c} que indica la pertenencia
    de cada activo i a una clase de activo c.

    Parámetros:
    ----------
    - tickers : list[str] -> 
        Lista de símbolos de los activos (por ejemplo, ['AAPL', 'GOOG', 'TSLA', 'BND']).
    - class_map : dict[str, str] ->
        Diccionario que asocia cada ticker con su clase (por ejemplo, {'AAPL': 'Acciones', 'BND': 'Bonos'}).

    Retorna:
    -------
    pd.DataFrame:
        DataFrame binario con índice = tickers, columnas = clases de activos,
        y valores g_{i,c} ∈ {0,1}.
    """
    tickers = sorted(tickers_classes.keys())

    # 1. Obtener las clases únicas
    classes = sorted(set(tickers_classes.values()))

    # 2. Inicializar la matriz binaria con ceros
    g = pd.DataFrame(0, index=tickers, columns=classes, dtype=int)

    # 3. Asignar 1 donde corresponda según el mapeo
    for ticker in tickers:
        cls = tickers_classes.get(ticker)
        if cls in g.columns:
            g.loc[ticker, cls] = 1

    return g


def class_limits(
    classes: List[str],
    limits: Optional[List[Tuple[float, float]]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Genera dos DataFrames con los límites mínimos y máximos de inversión por clase.

    Parámetros:
    ----
    - classes: lista de nombres o identificadores de clases de activos.
    - limits: lista opcional de tuplas (L_c, U_c) para cada clase.
              Si no se especifica, se usa el valor por defecto (0.05, 0.90) para todas.

    Retorna:
    ----
    - DataFrames con índice = nombre de la clase y columna ['L_c'] y ['U_c'].
    """
    if limits is None:
        limits = [(0.1, 0.75)] * len(classes)

    if len(limits) != len(classes):
        raise ValueError("La longitud de 'limits' debe coincidir con la longitud de 'classes'.")

    df_L = pd.DataFrame({
        'L_c': [L for L, _ in limits]
    }, index=classes)

    df_U = pd.DataFrame({
        'U_c': [U for _, U in limits]
    }, index=classes)

    df_L.index.name = 'Clase'
    df_U.index.name = 'Clase'
    return df_L, df_U


def asset_limits(
    assets: List[str],
    limits: Optional[List[Tuple[float, float]]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Genera dos DataFrames con los límites mínimos y máximos de inversión por activo.

    Parámetros:
    ----
    - assets: lista de tickers o identificadores de activos.
    - limits: lista opcional de tuplas (x_i^{min}, x_i^{max}) para cada activo.
              Si no se especifica, se usa el valor por defecto (0.00, 1.00) para todas.

    Retorna:
    ----
    - DataFrames con índice = ticker y columna ['x_i_min'] y ['x_i_max'].
    """
    if limits is None:
        limits = [(0, 0.75)] * len(assets)

    if len(limits) != len(assets):
        raise ValueError("La longitud de 'limits' debe coincidir con la longitud de 'assets'.")

    df_xmin = pd.DataFrame({
        'x_i_min': [xmin for xmin, _ in limits]
    }, index=assets)

    df_xmax = pd.DataFrame({
        'x_i_max': [xmax for _, xmax in limits]
    }, index=assets)

    df_xmin.index.name = 'Activo'
    df_xmax.index.name = 'Activo'

    return df_xmin, df_xmax


def generate_transaction_costs(tickers_dict):
    """
    Genera costos proporcionales de compra y venta para cada activo.
    
    Parámetros:
    ----
    - tickers_dict: dict {ticker: tipo} donde tipo ∈ {"Acciones", "Bonos", "ETF"}.
    
    Retorna:
    ----
    - (c_buy_df, c_sell_df): dos DataFrames con los costos proporcionales por activo.
    """
    # Definir valores base por clase de activo (en proporciones)
    base_costs = {
        "Acciones": {"buy": 0.0010, "sell": 0.0015},   # 0.10% compra / 0.15% venta
        "ETF": {"buy": 0.0005, "sell": 0.0010},        # 0.05% / 0.10% (alta liquidez)
        "Fondo": {"buy": 0.0015, "sell": 0.0020},      # 0.15% / 0.20% (menor liquidez intradía)
        "Bonos": {"buy": 0.0020, "sell": 0.0025},      # 0.20% / 0.25% (spreads mayores)
        "Cripto": {"buy": 0.0025, "sell": 0.0030},     # 0.25% / 0.30% (costos de exchange)
        "Divisa": {"buy": 0.0002, "sell": 0.0003},     # 0.02% / 0.03% (spreads mínimos)
        "Otros": {"buy": 0.0015, "sell": 0.0020}       # genérico (commodities, REITs, etc.)
    }


    # Construir listas de resultados
    data_buy, data_sell = {}, {}

    for ticker, tipo in tickers_dict.items():
        tipo = tipo if tipo in base_costs else "Otros"
        data_buy[ticker] = base_costs[tipo]["buy"]
        data_sell[ticker] = base_costs[tipo]["sell"]

    # Convertir a DataFrame (una sola columna)
    c_buy_df = pd.DataFrame.from_dict(data_buy, orient="index", columns=["c_buy"])
    c_sell_df = pd.DataFrame.from_dict(data_sell, orient="index", columns=["c_sell"])

    return c_buy_df, c_sell_df