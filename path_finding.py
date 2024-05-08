
class SearchProblem(object):
    """
    This is a base Search Problem. Implement this to get your specific implementation depending on your domain
    """
    def __init__(self, init, goal, actions :set, world, cost :dict):
        self.init = init
        self.goal = goal
        self.actions = actions
        self.world = world
        self.cost = cost

class PathFinding(SearchProblem):
    def __init__(self, world, init, goal): 
        actions = ['N','S','W','E']
        cost = [(a,1) for a in actions]
        super().__init__(init, goal, actions, world, cost)
        

    def getSuccessors(self, state): 
        # Genera i successori dello stato corrente
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
            
    def isInTheLimits(self, state :tuple): # Controlla che lo stato non ecceda i bordi del mondo 
        return state[0] >=0 and state[0] <= self.world.x_limit and state[1] >= 0 and state[1] <= self.world.y_limit


    def isGoal(self,state): # state è un array di due elementi che rappresentano (x,y)
        return state[0] == self.goal[0] and state[1] == self.goal[1]
    
    class World:
        def __init__(self, x_limit, y_limit, walls):
            self.x_limit = x_limit
            self.y_limit = y_limit
            self.walls = walls


