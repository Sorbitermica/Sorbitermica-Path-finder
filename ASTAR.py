from search_algorithm import SearchAlgorithm
from queue import PriorityQueue
from search_algorithm import Node

class AstarNode(Node):
    def __init__(self, state, parent=None, action=None, g=0, h=0):
        """
        Inizializza un nuovo nodo per l'algoritmo A*.

        Args:
            state: Lo stato rappresentato dal nodo.
            parent: Il nodo genitore del nodo corrente (default: None).
            action: L'azione che ha portato a questo nodo (default: None).
            g: Il costo effettivo dal nodo di partenza al nodo corrente (default: 0).
            h: L'euristica dal nodo corrente al nodo di destinazione (default: 0).
        """
        self.h = h
        super().__init__(state, parent, action, g)
        
    def __lt__(self, other):
        """
        Confronta due nodi A* in base alla loro somma di g e h.

        Args:
            other: Altro nodo con cui confrontare.

        Returns:
            True se il nodo corrente ha una somma di g e h minore rispetto all'altro nodo, altrimenti False.
        """
        return (self.g + self.h) < (other.g + other.h)

class AStar(SearchAlgorithm):
    def __init__(self, heuristic=lambda: 0, view=True, w=1):
        """
        Inizializza un nuovo algoritmo di ricerca A*.

        Args:
            heuristic: La funzione euristica da utilizzare (default: funzione costante 0).
            view: Indica se visualizzare i nodi espansi durante la ricerca (default: True).
            w: Fattore di pesatura per l'euristica (default: 1).
        """
        self.heuristic = heuristic
        self.w = w
        super().__init__(view)

    def solve(self, problem) -> list:
        """
        Risolve il problema utilizzando l'algoritmo A*.

        Args:
            problem: Il problema di ricerca.

        Returns:
            Una lista di azioni che rappresentano la soluzione.
        """
        reached = set()
        frontier = PriorityQueue()
        
        reached.add(problem.init)
        h = self.heuristic(problem.init, problem.goal, problem.barrier)
        frontier.put((h, AstarNode(problem.init, None, None, 0, h)))
        
        while not frontier.empty():
            _, node = frontier.get()
            if problem.isGoal(node.state):
                return self.extract_solution(node)
            
            for action, state in problem.getSuccessors(node.state):
                if state not in reached:
                    self.update_expanded(state)
                    reached.add(state)
                    g = node.g + 1
                    h = self.heuristic(state, problem.goal, problem.barrier)
                    f = g + h * self.w  
                    frontier.put((f, AstarNode(state, node, action, g, h)))
        
        return None
