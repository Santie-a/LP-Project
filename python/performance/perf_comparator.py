import pandas as pd
import matplotlib.pyplot as plt

def simulate_real_vs_plan(
    x_df: pd.DataFrame,
    w_series: pd.Series,
    returns: pd.DataFrame,
    W0: float,
    plot: bool = True
):
    # cálculo del capital simulado real
    real = W0 + x_df.mul(returns, fill_value=0).sum(axis=1).cumsum()
    
    # DataFrame combinado
    comparison = pd.DataFrame({
        "planned": w_series,
        "real": real
    })

    # Métricas del reporte
    final_diff = comparison["real"].iloc[-1] - comparison["planned"].iloc[-1]
    mean_abs_diff = (comparison["real"] - comparison["planned"]).abs().mean()
    pct_error = ((comparison["real"] - comparison["planned"]) / comparison["planned"]).mean() * 100

    # Impresión del reporte
    print("=== Reporte de Comparación ===")
    print(f"Capital final planificado: {comparison['planned'].iloc[-1]:.2f}")
    print(f"Capital final real:        {comparison['real'].iloc[-1]:.2f}")
    print(f"Diferencia final:          {final_diff:.2f}")
    print(f"Diferencia promedio:       {mean_abs_diff:.2f}")
    print(f"Error promedio (%):        {pct_error:.2f}%")
    print("==============================")

    if plot:
        plt.figure(figsize=(10,6))
        plt.plot(comparison.index, comparison["planned"], label="Planned")
        plt.plot(comparison.index, comparison["real"], label="Real", linestyle="--")
        plt.xlabel("Date")
        plt.ylabel("Capital")
        plt.title("Planned vs Real Capital")
        plt.legend()
        plt.grid(True)
        plt.show()
    
    return comparison
