import pandas as pd
from perf_comparator import simulate_real_vs_plan
import yfinance as yf

def read_W0_from_params(file_path: str = "params.txt") -> float:
    """
    Extrae el valor de W0 desde un archivo de parámetros de texto.

    Parámetros
    ----------
    file_path : str
        Ruta al archivo params.txt exportado por OPL.

    Retorna
    -------
    float
        Valor numérico del capital inicial W0.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            # Eliminar espacios y saltos de línea
            line = line.strip()
            if line.startswith("Capital inicial (W0)"):
                # Separar por '=' y limpiar
                parts = line.replace(" ", "").split(":")
                if len(parts) > 1:
                    try:
                        return float(parts[1])
                    except ValueError:
                        raise ValueError(f"Valor inválido para W0 en {file_path}: {parts[1]}")
    raise ValueError("No se encontró el parámetro W0 en el archivo.")


# --- Lectura del archivo de resultados ---
eval_n = 4
base_path = f"./model/evaluation/eval{eval_n}"

df = pd.read_csv(f"{base_path}/results.csv")

# --- Separar las variables ---
variables = ["x", "y", "z", "W"]
dfs = {}

for var in variables:
    df_var = df[df["Variable"] == var].copy()
    if var == "W":
        dfs[var] = df_var.drop(columns=["Activo", "Variable"]).reset_index(drop=True)
    else:
        dfs[var] = df_var.drop(columns=["Variable"]).reset_index(drop=True)

W0 = read_W0_from_params(f"{base_path}/params.txt")

# Cambiar el formato de dfs["x"]
x_df: pd.DataFrame = dfs["x"].T

# Guardar la fila "Activo" como nombres de columna
column_names = x_df.loc["Activo"]

# Eliminar la fila "Activo"
x_df = x_df.drop("Activo")

# Convertir índice a datetime
x_df.index = pd.to_datetime(x_df.index)

# Asignar los nombres de columna correctos
x_df.columns = column_names

x_df.columns.name = "Ticker"
x_df.index.name = "Date"

# Cambiar el formato de dfs["W"]
w_df: pd.DataFrame = dfs["W"].T

w_df.index = pd.to_datetime(w_df.index)
w_df.index.name = "Date"
w_series = w_df.iloc[:, 0]
print(w_series)


tickers = x_df.columns.to_list()
dates = x_df.index.to_list()
start_date, end_date = dates[0], dates[-1]
difference: pd.Timedelta = (dates[1] - dates[0]).days

if difference <= 1:
    frequency = "D"
elif difference <= 7:
    frequency = "W"
elif difference <= 31:
    frequency = "M"
else:
    frequency = "Y"

prices_df = yf.download(
    tickers=tickers,
    start=start_date,
    end=end_date,
    interval="1d",
    progress=False,
    threads=True
)['Close']

returns = prices_df.dropna().pct_change()
returns = (1 + returns).resample(frequency).prod() - 1

print(simulate_real_vs_plan(x_df, w_series, returns, W0, plot=True))