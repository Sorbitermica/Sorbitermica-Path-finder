import math

def manhattan_with_barriers(punto1, punto2, barriere) -> int:
    """
    Calcola la distanza di Manhattan tra due punti con l'aggiunta del costo delle barriere lungo il percorso.

    Args:
        punto1: Le coordinate del primo punto (x, y).
        punto2: Le coordinate del secondo punto (x, y).
        barriere: Lista di coordinate delle barriere nel formato [(x1, y1), (x2, y2), ...].

    Returns:
        La distanza di Manhattan tra i due punti con il costo delle barriere lungo il percorso.
    """
    x1, y1 = punto1
    x2, y2 = punto2
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    # Calcolo del costo delle barriere lungo il percorso
    barrier_cost = sum(0.1 for barriera in barriere if (barriera[0] > min(x1, x2) and barriera[0] < max(x1, x2) and
                                                         barriera[1] > min(y1, y2) and barriera[1] < max(y1, y2)))
    return dx + dy + barrier_cost
