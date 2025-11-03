import pandas as pd

from data.returns import expected_returns
from data.tickers import get_ticker_types, build_g_matrix, asset_limits, class_limits, generate_transaction_costs
from utils.cplex_dat import export_to_cplex_dat

# Fechas para rangos en predicción de precios (opcional)
today = pd.Timestamp.today().normalize()
start_date = today - pd.DateOffset(months=25)
end_date = today - pd.DateOffset(months=13)

# Obtener un conjunto de datos inicial (Periodo de dos meses con periodos de decisión semanales)
tickers = get_ticker_types(n = 10, initial_tickers=["AAPL", "SPY", "EURUSD=X", "BTC-USD", "ES=F", "NVDA", "MSFT"])
exp_returns = expected_returns(list(tickers.keys()), period="1mo", price_interval="1d", freq="W", date_range=(start_date, end_date))
g_matrix = build_g_matrix(tickers)

# --- Conjuntos ---
print("Conjuntos", "\n")

# -- Activos financieros (I) --
print("Activos financieros (I)")
I = list(sorted(tickers.keys()))
print(I, '\n')

# -- Periodos de decisión (T) --
T = list(exp_returns.columns)
print("Periodos de decisión (T)")
print(T, '\n')

# -- Clases de activo (C) --
C = sorted(set(tickers.values()))
print("Clases de activo (C)")
print(C, '\n')

# --- Parámetros ---

# -- Retornos esperados (r_i,j) --
print("r_ij:")
print(exp_returns, "\n")

# -- Costos proporcionales
c_buy, c_sell = generate_transaction_costs(tickers)
print("c_buy_i")
print(c_buy, "\n")

print("c_sell_i")
print(c_sell, "\n")

# -- Pertenencia de los activos a ciertas clases (g_i,c) --
print("g_ic:")
print(g_matrix, "\n")

# -- Capital inicial W0 --
W0 = 100
print("W0: ", W0, "\n")

# -- Límites L_c, U_c --
L_c, U_c = class_limits(C)
print(L_c, U_c)

# -- Límites x_min_i, U_c --
x_min, x_max = asset_limits(I)
print(x_min, x_max)

# Generar el archivo .dat
export_to_cplex_dat("portfolio.dat", I, T, C, W0, exp_returns, c_buy, c_sell, g_matrix, L_c, U_c, x_min, x_max)