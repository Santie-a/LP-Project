import pandas as pd
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt
import pandas as pd

def simulate_real_vs_plan(
    x_df: pd.DataFrame,
    w_series: pd.Series,
    returns: pd.DataFrame,
    W0: float,
    plot: bool = True
):
    # cálculo del capital simulado real
    real = W0 + x_df.mul(returns, fill_value=0).sum(axis=1).cumsum()
    
    # DataFrame combinado para comparación
    comparison = pd.DataFrame({
        "planned": w_series,
        "real": real
    })

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

