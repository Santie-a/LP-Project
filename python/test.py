from data.returns import expected_returns
from data.tickers import get_ticker_types, build_g_matrix, asset_limits, class_limits
from utils.cplex_dat import export_to_cplex_dat

# Obtener un conjunto de datos inicial (Periodo de dos meses con periodos de decisión semanales)
tickers = get_ticker_types(n = 10, initial_tickers=["AAPL","MSFT","NVDA","SPY","GOOGL"])
exp_returns = expected_returns(list(tickers.keys()), period="1y", price_interval="1d", freq="W")
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
print(g_matrix, "\n")

# -- Capital inicial W0 --
W0 = 15000
print("W0: ", W0, "\n")

# -- Límites L_c, U_c --
L_c, U_c = class_limits(C)
print(L_c, U_c)

# -- Límites x_min_i, U_c --
x_min, x_max = asset_limits(I)
print(x_min, x_max)

# Generar el archivo .dat
export_to_cplex_dat("test.dat", I, T, C, W0, exp_returns, g_matrix, L_c, U_c, x_min, x_max)