from data.returns import expected_returns
from data.tickers import get_ticker_types, build_g_matrix
from utils.cplex_dat import export_to_cplex_dat

# Obtener un conjunto de datos inicial (Periodo de dos meses con periodos de decisión semanales)
tickers = get_ticker_types(n = 10, initial_tickers=["AAPL","MSFT","TSLA","NVDA","SPY","GOOGL","VNQ"])
exp_returns = expected_returns(list(tickers.keys()), period="2mo", price_interval="1d", freq="W")
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

# -- Pertenencia de los activos a ciertas clases (g_i,c) --
print("g_ic:")
print(g_matrix)

# Generar el archivo .dat
export_to_cplex_dat("test.dat", I, T, C, exp_returns, g_matrix)