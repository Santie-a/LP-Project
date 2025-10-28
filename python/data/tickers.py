import pandas as pd
import yfinance as yf
from typing import List, Dict, Optional, Tuple

def get_ticker_types(
    n: int = 20,
    initial_tickers: Optional[List[str]] = None
) -> Dict[str, str]:
    """
    Obtiene un diccionario de tamaño n con tickers y su tipo (“Acciones”, “Bonos”, “ETF”, “Otros”),
    usando datos de yfinance. Si se proporciona initial_tickers, los incluye primero, luego completa
    hasta n con otros tickers aleatorios o seleccionados.
    
    Parámetros:
    ----------
    n : int
        Número total de entradas que debe devolver el diccionario.
    initial_tickers : Optional[List[str]]
        Lista de tickers pre-seleccionados por el usuario (opcional).
    
    Retorna:
    -------
    Dict[str, str]
        Diccionario donde cada clave es un ticker (str) y el valor es su tipo (str).
    """
    result: Dict[str, str] = {}
    
    # 1. Si hay tickers iniciales, los procesamos primero
    if initial_tickers:
        for ticker in initial_tickers:
            if len(result) >= n:
                break
            try:
                info = yf.Ticker(ticker).info
                # Identificar tipo
                sec = info.get("sector", None)
                asset_type = "Otros"
                # Simple heurística para clasificar
                if info.get("quoteType") == "ETF":
                    asset_type = "ETF"
                elif sec is not None:
                    asset_type = "Acciones"
                # Podemos añadir heurísticas para “Bonos” si info lo permite
                result[ticker] = asset_type
            except Exception:
                result[ticker] = "Desconocido"
    
    # 2. Si no alcanzamos n, añadimos tickers predeterminados o seleccionados aleatoriamente
    #    Aquí definimos una lista de tickers de ejemplo para completar (puedes ampliarla).
    fallback = [
        "SPY", "VOO", "VTI",   # ETFs
        "BND", "TLT", "IEF",   # Bonos / renta fija
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",  # Acciones
        "JNJ", "WMT", "JPM", "PG", "XOM",         # Acciones
        "GLD", "SLV", "USO",                      # Commodities / Otros
        "VNQ"                                      # REIT / Otros
    ]

    for ticker in fallback:
        if len(result) >= n:
            break
        if ticker in result:
            continue
        try:
            info = yf.Ticker(ticker).info
            sec = info.get("sector", None)
            asset_type = "Otros"
            if info.get("quoteType") == "ETF":
                asset_type = "ETF"
            elif sec is not None:
                asset_type = "Acciones"
            elif ticker in ["BND", "TLT", "IEF"]:
                asset_type = "Bonos"
            result[ticker] = asset_type
        except Exception:
            result[ticker] = "Desconocido"
        
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
        limits = [(0.05, 0.75)] * len(classes)

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
        limits = [(0.01, 0.75)] * len(assets)

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
