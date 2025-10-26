import pandas as pd
from typing import List

# --- Crear archivo .dat para CPLEX ---
def export_to_cplex_dat(
    filename: str,
    I: List[str],
    T: List[pd.Timestamp],
    C: List[str],
    exp_returns: pd.DataFrame,
    g_matrix: pd.DataFrame
):
    """
    Genera un archivo .dat compatible con IBM CPLEX OPL
    usando los conjuntos y parámetros definidos en Python.
    """

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

    def opl_binary_matrix(name, df):
        lines = [f"{name} = ["]
        for _, row in df.iterrows():
            row_str = ", ".join(str(int(v)) for v in row)
            lines.append(f"  [{row_str}]")
        lines.append("];\n\n")
        return "\n".join(lines)

    with open(filename, "w", encoding="utf-8") as f:
        # --- Conjuntos ---
        f.write("// --- Conjuntos ---\n")
        f.write(opl_set("I", I))
        f.write(opl_set("T", [str(t.date()) for t in T]))
        f.write(opl_set("C", C))

        # --- Parámetros ---
        f.write("// --- Parámetros ---\n")
        f.write(opl_matrix("r", exp_returns))
        f.write(opl_binary_matrix("g", g_matrix))

    print(f"Archivo '{filename}' generado exitosamente.")