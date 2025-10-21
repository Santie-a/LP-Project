import pandas as pd
import yfinance as yf
from typing import List

def download_close(tickers: List[str], period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Descarga los precios de cierre ('Close') de los tickers indicados usando yfinance.
    
    Parámetros:
    - tickers: lista de símbolos de los activos.
    - period: rango de tiempo a descargar (por ejemplo, '1y' = 1 año).
    - interval: frecuencia de los precios ('1d', '1wk', '1mo', etc.).
    
    Retorna:
    - DataFrame con índice = fechas, columnas = tickers y valores = precios de cierre.
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
    - tickers: lista de símbolos de activos.
    - period: rango de tiempo histórico para la descarga de precios.
    - price_interval: frecuencia de los precios históricos ('1d', '1wk', '1mo').
    - freq: frecuencia de agregación para los retornos esperados ('M' mensual, 'W' semanal, etc.).
    - lambda_: factor de decaimiento de EWMA (0 < lambda_ < 1).
    
    Retorna:
    - DataFrame con índice = períodos de decisión (final de mes, semana, etc.)
      y columnas = tickers. Cada valor es el retorno esperado EWMA para ese período.
    """
    # 1. Descargar precios de cierre
    prices_df = download_close(tickers, period=period, interval=price_interval)
    
    # 2. Calcular retornos simples diarios (o del intervalo elegido)
    returns = prices_df.pct_change().dropna()
    
    # 3. Reagrupar a la frecuencia deseada (mensual, semanal, etc.)
    #    Fórmula de acumulación: (1 + r1)*(1 + r2)*...*(1 + rn) - 1
    resampled_returns = (1 + returns).resample(freq).prod() - 1
    
    # 4. Calcular EWMA para suavizar los retornos y ponderar más los recientes
    ewma_returns = resampled_returns.ewm(alpha=1-lambda_, adjust=False).mean()
    
    return ewma_returns
