import math

def manhattan(start, goal) -> int:
    # Calcola la distanza di Manhattan tra il punto di partenza e il punto di arrivo, includendo i punti obbligati
    return int(math.fabs(goal[0] - start[0]) + math.fabs(goal[1] - start[1]))

def blind(start, goal,mandatory_points) -> int:
    return len(mandatory_points)

def manhattan_with_barriers(start, goal, barriers) -> int:
    # Calcola la distanza di Manhattan tra il punto di partenza e il punto di arrivo,
    # tenendo conto delle barriere
    x1, y1 = start
    x2, y2 = goal
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    # Calcola il costo aggiuntivo per ogni barriera tra start e goal
    barrier_cost = sum(100 for barrier in barriers if (barrier[0] > min(x1, x2) and barrier[0] < max(x1, x2) and
                                                      barrier[1] > min(y1, y2) and barrier[1] < max(y1, y2)))
    return dx + dy + barrier_cost
