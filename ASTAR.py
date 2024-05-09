from search_algorithm import SearchAlgorithm
from queue import PriorityQueue
from search_algorithm import Node

class AstarNode(Node):
    def __init__(self, state, parent=None, action=None, g=0, h=0):
        self.h = h
        super().__init__(state, parent, action, g)
        
    def __lt__(self, other):
        return (self.g + self.h) < (other.g + other.h)

class AStar(SearchAlgorithm):
    def __init__(self, heuristic=lambda x, y: 0, view=True, w=1):
        self.heuristic = heuristic
        self.w = w
        super().__init__(view)

    def solve(self, problem) -> list:
        reached = set()
        frontier = PriorityQueue()
        
        reached.add(problem.init)
        h = self.heuristic(problem.init, problem.goal,problem.barrier)
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
                    h = self.heuristic(state, problem.goal,problem.barrier)
                    f = g + h * self.w  # Calcolo della priorità f = g + h*w
                    frontier.put((f, AstarNode(state, node, action, g, h)))
        
        return None
        


        