
class SearchProblem(object):
    def __init__(self, init, goal, actions :set, world, cost :dict,barrier):
        """
        Inizializza un nuovo problema di ricerca.

        Args:
            init: Lo stato iniziale del problema.
            goal: Lo stato obiettivo del problema.
            actions: Insieme di azioni disponibili.
            world: Oggetto che rappresenta il mondo in cui avviene la ricerca.
            cost: Dizionario che assegna un costo a ciascuna azione.
            barrier: Barriera rappresentativa del mondo.
        """
        self.init = init
        self.goal = goal
        self.actions = actions
        self.world = world
        self.cost = cost
        self.barrier = barrier

class PathFinding(SearchProblem):
    def __init__(self, world, init, goal,barrier): 
        actions = ['N','S','W','E']
        cost = [(a,1) for a in actions]
        super().__init__(init, goal, actions, world, cost,barrier)
        

    def getSuccessors(self, state): 
        """
        Ottiene gli stati successori dello stato attuale in base alle azioni disponibili.

        Args:
            state: Lo stato corrente.

        Returns:
            Un insieme di coppie (azione, stato_successivo) rappresentanti gli stati successori validi.
        """
        successors = set()
        for a in self.actions:
            if a == 'N':
                next_state = (state[0], state[1]+1)
            elif a == 'S':
                 next_state = (state[0], state[1]-1)
            elif a == 'W':
                next_state = (state[0]-1, state[1])
            elif a == 'E':
                next_state = (state[0]+1, state[1])
            if next_state not in self.world.walls and self.isInTheLimits(next_state):
                
                successors.add((a, next_state))
        return successors
            
    def isInTheLimits(self, state :tuple): 
        """
        Verifica se lo stato si trova nei limiti del mondo.

        Args:
            state: Lo stato da verificare.

        Returns:
            True se lo stato è all'interno dei limiti del mondo, altrimenti False.
        """
        return state[0] >=0 and state[0] <= self.world.x_limit and state[1] >= 0 and state[1] <= self.world.y_limit


    def isGoal(self,state):
        """
        Verifica se lo stato corrente è lo stato obiettivo.

        Args:
            state: Lo stato corrente.

        Returns:
            True se lo stato corrente coincide con lo stato obiettivo, altrimenti False.
        """
        return state[0] == self.goal[0] and state[1] == self.goal[1]
    
    class World:

        def __init__(self, x_limit, y_limit, walls):
            """
        Inizializza un nuovo mondo.

        Args:
            x_limit: Limite dell'asse x.
            y_limit: Limite dell'asse y.
            walls: Lista di muri nel mondo.
        """
            self.x_limit = x_limit
            self.y_limit = y_limit
            self.walls = walls


