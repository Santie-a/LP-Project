from pandas.tseries.offsets import DateOffset
import pandas as pd
import yfinance as yf
from typing import List

from typing import List, Optional, Tuple
import pandas as pd
import yfinance as yf

def download_close(
    tickers: List[str],
    period: str = "1y",
    interval: str = "1d",
    date_range: Optional[Tuple[pd.Timestamp, Optional[pd.Timestamp]]] = None
) -> pd.DataFrame:
    """
    Descarga los precios de cierre ('Close') de los tickers indicados usando yfinance.
    
    Parámetros:
    ----------
    - tickers: List[str] ->
        lista de símbolos de los activos.
    - period: str ->
        rango de tiempo a descargar (por ejemplo, '1y' = 1 año). Usado si no se especifica date_range.
    - interval: str ->
        frecuencia de los precios ('1d', '1wk', '1mo', etc.).
    - date_range: Optional[Tuple[pd.Timestamp, Optional[pd.Timestamp]]] ->
        tupla (start_date, end_date). Si se especifica, ignora 'period'.
        Si end_date es None, se usa la fecha actual.
    
    Retorna:
    ----------
    pd.DataFrame:
        DataFrame con índice = fechas, columnas = tickers y valores = precios de cierre.
    """
    # Determine how to fetch data
    if date_range is not None:
        start_date, end_date = date_range
        if end_date is None:
            end_date = pd.Timestamp.today()
        df = yf.download(
            tickers=tickers,
            start=start_date,
            end=end_date,
            interval=interval,
            progress=False,
            threads=True
        )['Close']
    else:
        df = yf.download(
            tickers=tickers,
            period=period,
            interval=interval,
            progress=False,
            threads=True
        )['Close']

    # Convert Series to DataFrame if only one ticker
    if isinstance(df, pd.Series):
        df = df.to_frame()
    
    return df


from typing import List, Optional, Tuple
import pandas as pd

def expected_returns(
    tickers: List[str],
    period: str = "1y",
    price_interval: str = "1d",
    freq: str = "M",
    lambda_: float = 0.94,
    date_range: Optional[Tuple[pd.Timestamp, Optional[pd.Timestamp]]] = None
) -> pd.DataFrame:
    """
    Calcula los retornos esperados usando EWMA para una lista de tickers.
    
    Parámetros:
    ----------
    - tickers: List[str] ->
        lista de símbolos de activos.
    - period: str ->
        rango de tiempo histórico para la descarga de precios (usado si no se especifica date_range).
    - price_interval: str ->
        frecuencia de los precios históricos ('1d', '1w', '1mo').
    - freq: str ->
        frecuencia de agregación para los retornos esperados ('M' mensual, 'W' semanal, 'D' diario, etc.).
    - lambda_: float ->
        factor de decaimiento de EWMA (0 < lambda_ < 1).
    - date_range: Optional[Tuple[pd.Timestamp, Optional[pd.Timestamp]]] ->
        tupla (start_date, end_date). Si se especifica, ignora 'period'.
        Si end_date es None, se usa la fecha actual como límite superior.
    
    Retorna:
    ----------
    pd.DataFrame:
        DataFrame con índice = períodos de decisión (final de mes, semana, etc.)
        y columnas = tickers. Cada valor es el retorno esperado EWMA para ese período.
    """
    # 1. Descargar precios de cierre
    if date_range is not None:
        start_date, end_date = date_range
        if end_date is None:
            end_date = pd.Timestamp.today()
        prices_df = download_close(tickers, date_range=date_range, interval=price_interval)
    else:
        prices_df = download_close(tickers, period=period, interval=price_interval)

    # 2. Calcular retornos simples diarios
    returns = prices_df.pct_change().dropna()

    # 3. Reagrupar por frecuencia deseada
    resampled_returns = (1 + returns).resample(freq).prod() - 1

    # 4. Calcular EWMA
    ewma_returns = resampled_returns.ewm(alpha=1 - lambda_, adjust=False).mean()

        # 5. Ajustar fechas del índice según el rango temporal
    n_periods = len(ewma_returns)
    
    if date_range is not None:
        start_date, end_date = date_range
        # Si end_date no se pasa, usar hoy
        if end_date is None:
            end_date = pd.Timestamp.today().normalize()
        # El índice terminará en end_date y tendrá n_periods
        new_dates = pd.date_range(start=end_date, periods=n_periods, freq=freq)
    else:
        # Mantener el comportamiento original
        new_dates = pd.date_range(start=pd.Timestamp.today().normalize(), periods=n_periods, freq=freq)

    ewma_returns = ewma_returns.copy()
    ewma_returns.index = new_dates


    # 6. Retornar transpuesta (tickers como filas)
    return ewma_returns.T

