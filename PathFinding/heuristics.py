import math

def manhattan(start, goal) -> int:
    # Calcola la distanza di Manhattan tra il punto di partenza e il punto di arrivo, includendo i punti obbligati
    return int(math.fabs(goal[0] - start[0]) + math.fabs(goal[1] - start[1]))



def blind(start, goal,mandatory_points) -> int:
    return len(mandatory_points)

