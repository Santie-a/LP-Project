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
