import pandas as pd
from typing import List

# --- Crear archivo .dat para CPLEX ---
def export_to_cplex_dat(
    filename: str,
    I: List[str],
    T: List[pd.Timestamp],
    C: List[str],
    W0: int,
    exp_returns: pd.DataFrame,
    g_matrix: pd.DataFrame,
    L_c: pd.DataFrame,
    U_c: pd.DataFrame,
    x_min: pd.DataFrame,
    x_max: pd.DataFrame
):
    """
    Genera un archivo .dat compatible con IBM CPLEX OPL
    usando los conjuntos y parámetros definidos en Python.
    """

    def opl_value(name, value):
        return f"{name} = {value};\n\n"

    def opl_set(name, values):
        formatted = ", ".join(f'"{v}"' for v in values)
        return f"{name} = {{ {formatted} }};\n\n"

    def opl_matrix(name, df):
        lines = [f"{name} = ["]
        for _, row in df.iterrows():
            row_str = ", ".join(f"{v:.6f}" for v in row)
            lines.append(f"  [{row_str}]")
        lines.append("];\n\n")
        return "\n".join(lines)
    
    def opl_list(name, df):
        if df.shape[1] != 1:
            raise ValueError("El DataFrame debe tener exactamente una columna.")
        
        values = df.iloc[:, 0].tolist()
        formatted_values = ", ".join(f"{v:.6f}" for v in values)
        return f"{name} = [{formatted_values}];\n\n"

    def opl_binary_matrix(name, df):
        lines = [f"{name} = ["]
        for _, row in df.iterrows():
            row_str = ", ".join(str(int(v)) for v in row)
            lines.append(f"  [{row_str}]")
        lines.append("];\n\n")
        return "\n".join(lines)

    dates_list = [str(t.date()) for t in T]

    with open(filename, "w", encoding="utf-8") as f:
        # --- Conjuntos ---
        f.write("// --- Conjuntos ---\n")
        f.write(opl_set("I", I))
        f.write(opl_value("H", len(dates_list)))
        f.write(opl_set("D", dates_list))
        f.write(opl_set("C", C))

        # --- Parámetros ---
        f.write("// --- Parámetros ---\n")
        f.write(opl_matrix("r", exp_returns))
        f.write(opl_binary_matrix("g", g_matrix))
        f.write(opl_value("W0", W0))
        f.write(opl_list("L", L_c))
        f.write(opl_list("U", U_c))
        f.write(opl_list("X_min", x_min))
        f.write(opl_list("X_max", x_max))

    print(f"Archivo '{filename}' generado exitosamente.")