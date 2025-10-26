from pandas.tseries.offsets import DateOffset
import pandas as pd
import yfinance as yf
from typing import List

def download_close(tickers: List[str], period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Descarga los precios de cierre ('Close') de los tickers indicados usando yfinance.
    
    Parámetros:
    ----------
    - tickers: List[str] ->
        lista de símbolos de los activos.
    - period: str ->
        rango de tiempo a descargar (por ejemplo, '1y' = 1 año).
    - interval: str ->
        frecuencia de los precios ('1d', '1wk', '1mo', etc.).
    
    Retorna:
    ----------
    pd.DataFrame:
        DataFrame con índice = fechas, columnas = tickers y valores = precios de cierre.
    """
    df = yf.download(tickers, period=period, interval=interval, progress=False, threads=True)['Close']
    
    # Si solo hay un ticker, convertir Series a DataFrame
    if isinstance(df, pd.Series):
        df = df.to_frame()
    return df


def expected_returns(
    tickers: List[str],
    period: str = "1y",
    price_interval: str = "1d",
    freq: str = "M",
    lambda_: float = 0.94
) -> pd.DataFrame:
    """
    Calcula los retornos esperados usando EWMA para una lista de tickers.
    
    Parámetros:
    ----------
    - tickers: List[str] ->
        lista de símbolos de activos.
    - period: str ->
        rango de tiempo histórico para la descarga de precios.
    - price_interval: str ->
        frecuencia de los precios históricos ('1d', '1w', '1mo').
    - freq: str ->
        frecuencia de agregación para los retornos esperados ('M' mensual, 'W' semanal, etc.).
    - lambda_: float ->
        factor de decaimiento de EWMA (0 < lambda_ < 1).
    
    Retorna:
    ----------
    pd.DataFrame:
        DataFrame con índice = períodos de decisión (final de mes, semana, etc.)
        y columnas = tickers. Cada valor es el retorno esperado EWMA para ese período.
    """
    # 1. Descargar precios de cierre
    prices_df = download_close(tickers, period=period, interval=price_interval)

    # 2. Calcular retornos simples diarios
    returns = prices_df.pct_change().dropna()

    # 3. Reagrupar por frecuencia deseada
    resampled_returns = (1 + returns).resample(freq).prod() - 1

    # 4. Calcular EWMA
    ewma_returns = resampled_returns.ewm(alpha=1 - lambda_, adjust=False).mean()

    # 5. Ajustar fechas para que el primer período sea el día actual
    n_periods = len(ewma_returns)
    new_dates = pd.date_range(start=pd.Timestamp.today().normalize(), periods=n_periods, freq=freq)
    ewma_returns = ewma_returns.copy()
    ewma_returns.index = new_dates

    # 6. Retornar transpuesta (tickers como filas)
    return ewma_returns.T
