import pygame 
from path_finding import PathFinding
from ASTAR import AStar as ASTARPathFinder
import heuristics
import json
import click 
import time
import tkinter as tk
import random
import json
#prova

WIDTH1 = 1300
WIDTH2 = 1000
WIDTH = 1000
WIN = pygame.display.set_mode((WIDTH1, WIDTH2))
pygame.display.set_caption("A* Sorbitermica")
pygame.init()

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

def get_mandatory_points(mandatory_points, select_all=False):
    prefixed_points = {
        "Chiave a tubo": ((30, 30)),
        "Pompa ad aria compressa": (random.randint(1, 99), random.randint(1, 99)),
        "Tagliatubi": (random.randint(1, 99), random.randint(1, 99)),
        "Idropulitrice": (random.randint(1, 99), random.randint(1, 99)),
        "Chiave a catena": (random.randint(1, 99), random.randint(1, 99)),
        "Fresa a mano": (random.randint(1, 99), random.randint(1, 99)),
        "Torcia a gas": (random.randint(1, 99), random.randint(1, 99)),
        "Guarnizioni assortite": (random.randint(1, 99), random.randint(1, 99)),
        "Pinze": (random.randint(1, 99), random.randint(1, 99)),
        "Rubinetto a sfera": (random.randint(1, 99), random.randint(1, 99))
    }

    root = tk.Tk()
    root.withdraw()

    dialog = tk.Toplevel(root)
    dialog.title("Seleziona i punti intermedi")
    dialog.geometry("350x450")

    selected_points = []
    checkboxes = {}  # Dizionario per memorizzare i checkbox

    def toggle_point(name, var):
        if var.get() == 1:
            selected_points.append(prefixed_points[name])
        elif var.get() == 0:
            selected_points.remove(prefixed_points[name])

    def add_selected_points():
        mandatory_points.update(selected_points)
        print("Punti intermedi aggiunti:", mandatory_points)
        dialog.destroy()

    def select_all():
        for name in prefixed_points.keys():
            var = checkboxes[name]
            var.set(1)
            if prefixed_points[name] not in selected_points:
                selected_points.append(prefixed_points[name])

    select_all_button = tk.Button(dialog, text="Seleziona Tutti", command=select_all)
    select_all_button.pack(pady=5)

    for name in prefixed_points.keys():
        var = tk.IntVar()
        checkbox = tk.Checkbutton(dialog, text=name, variable=var, onvalue=1, offvalue=0,
                                   command=lambda n=name, v=var: toggle_point(n, v))
        checkbox.pack(pady=5)
        checkboxes[name] = var  # Aggiungi il checkbox al dizionario

    done_button = tk.Button(dialog, text="Aggiungi", command=add_selected_points)
    done_button.pack(pady=5)

    dialog.wait_window()

def trova_punto_vicino(start_point,mandatory_points):
    min_euristica = float('inf')
    prossimo_punto = None
                    
    for punto in mandatory_points:
        euristica = heuristics.manhattan(start_point, punto)
        if euristica < min_euristica:
            min_euristica = euristica
            prossimo_punto = punto
            
    return prossimo_punto

class Spot:
    def __init__(self, row, col, width):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.width = width

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK
    
    def is_points(self):
        return self.color == GREEN

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_points(self):
        self.color = GREEN

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def __str__(self):
        return "({},{})".format(self.row, self.col)

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)
            

    draw_grid(win, rows, width)

    pygame.display.update()

def make_grid(rows, width, mandatory_points=None):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap)
            if mandatory_points and (i, j) in mandatory_points:
                spot.make_points()
            grid[i].append(spot)

    return grid

def make_grid_from_file(filename, width):
    f = open(filename)

    data = json.load(f)

    rows = data['rows']
    grid = []
    gap = width // rows
    
    start = (data['start'][0],data['start'][1])
    end = (data['end'][0],data['end'][1])
    
    barrier = {(ele[0],ele[1]) for ele in data['barrier']}
    
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap)
            if (i,j) in barrier:
                spot.make_barrier()
            elif (i,j) == start:
                spot.make_start()
                start = spot
            elif (i,j) == end:
                spot.make_end()
                end = spot
            grid[i].append(spot)

    return grid, start, end, rows, barrier

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col

def make_grid_from_file(filename, width, mandatory_points=None):
    f = open(filename)
    data = json.load(f)

    rows = data['rows']
    grid = []
    gap = width // rows
    
    start = (data['start'][0], data['start'][1])
    end = (data['end'][0], data['end'][1])
    barrier = {(ele[0], ele[1]) for ele in data['barrier']}
    
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap)
            if (i, j) in barrier:
                spot.make_barrier()
            elif (i, j) == start:
                spot.make_start()
                start = spot
            elif (i, j) == end:
                spot.make_end()
                end = spot
            elif mandatory_points and (i, j) in mandatory_points:
                spot.make_points()
            grid[i].append(spot)

    return grid, start, end, rows, barrier, mandatory_points

def mark_spots(start, end, grid, plan):
    x = start.row
    y = start.col
    for a in plan:
        if a == 'N':
            y += 1
        elif a == 'S':
            y -= 1
        elif a == 'E':
            x += 1
        elif a == 'W':
            x -= 1
        if 0 <= x < len(grid) and 0 <= y < len(grid[0]):
            current_spot = grid[x][y]
            # Ignore marking over grey spots and the end spot
            if current_spot.is_points() or current_spot.is_end():
               continue
            current_spot.make_path()
            
    # Ensure end spot remains marked as end
    
    end.make_end()      
    start.make_start()  

def mark_expanded(exp, grid):
    for e in exp:
        grid[e[0]][e[1]].make_closed()


def save_to_file(grid, start, end, filename="temp.json"):
    barrier = list()
    for x in grid:
        for spot in x:
            if spot.is_barrier():
                barrier.append((spot.row,spot.col))
    res = {"rows":len(grid), "start": (start.row,start.col), "end": (end.row,end.col), "barrier":barrier}
    data = json.dumps(res,indent=4)
    with open(filename,"w") as data_file:
        data_file.write(data)
    
def mark_points(point, grid):
    for e in point:
        grid[e[0]][e[1]].make_points()

def save_to_file(grid, start, end, filename="temp.json"):
    barrier = list()
    for x in grid:
        for spot in x:
            if spot.is_barrier():
                barrier.append((spot.row,spot.col))
    res = {"rows":len(grid), "start": (start.row,start.col), "end": (end.row,end.col), "barrier":barrier}
    data = json.dumps(res,indent=4)
    with open(filename,"w") as data_file:
        data_file.write(data)

class Button:
    """Create a button, then blit the surface in the while loop"""
 
    def __init__(self, text,  pos, font, bg="black", feedback=""):
        self.x, self.y = pos
        self.font = pygame.font.SysFont("Arial", font)
        if feedback == "":
            self.feedback = "text"
        else:
            self.feedback = feedback
        self.change_text(text, bg)
 
    def change_text(self, text, bg="black"):
        self.text = self.font.render(text, 1, pygame.Color("White"))
        self.size = self.text.get_size()
        self.surface = pygame.Surface(self.size)
        self.surface.fill(bg)
        self.surface.blit(self.text, (0, 0))
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])
 
    def show(self):
        WIN.blit(self.surface, (self.x, self.y))
 
    def click(self, event, grid, start, end):
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(x, y):
                    if grid is not None and start is not None and end is not None:
                        save_to_file(grid, start, end, "tempmap.json")
                        self.change_text(self.feedback, bg="red")  

save_map_button = Button(
    "Save Map",
    (WIDTH+100, 100),
    font=20,
    bg="navy",
    feedback="Saved")

load_map_button = Button(
    "Load Map",
    (WIDTH+100, 200),
    font=20,
    bg="navy",
    feedback="Loaded")

clock = pygame.time.Clock()

@click.command()
@click.option('-w', '--width', default = WIDTH, help = "Width of the Windows")
@click.option('-r', '--rows', default = 100, help = "Number of rows/columns in the map")
@click.option('-s', '--search_algorithm', default = "ASTAR", help = "Search algorithm to be used")
@click.option('-f', '--filename', default = 'tempmap.json', help = "Initialize map with data from file")

def main(width, rows, search_algorithm, filename):
    win = WIN
    start = None
    end = None
    ROWS = rows
    mandatory_points = set()
    points= set()
    points.update(mandatory_points)
    
    get_mandatory_points(mandatory_points)
    
    search_algorithm == 'ASTAR'
    search_algorithm = ASTARPathFinder(heuristics.manhattan,True)

    if filename == 'tempmap.json':
        grid, start, end, rows, wall,mandatory_points = make_grid_from_file(filename, width, mandatory_points)
    else:
        grid = make_grid(rows, width,mandatory_points)
        wall = set()
    run = True
    
    while run:
        
        draw(win, grid, rows, width)

        save_map_button.show()
        load_map_button.show()
        pygame.display.update()
        

        for event in pygame.event.get():
            pygame.display.update()
            if event.type == pygame.QUIT:
                run = False
            save_map_button.click(event, grid, start, end)

            if pygame.mouse.get_pressed()[0]:  # LEFT
                pos = pygame.mouse.get_pos()
                if pos[0] < width and pos[1] < width:
                    row, col = get_clicked_pos(pos, rows, width)
                    spot = grid[row][col]
                    if not start and spot != end:
                        start = spot
                        start.make_start()
                        
                    elif not end and spot != start:
                        end = spot
                        end.make_end()

                    elif spot != end and spot != start:
                        spot.make_barrier()
                        wall.add((row,col))

            if pygame.mouse.get_pressed()[2]: # RIGHT
                pos = pygame.mouse.get_pos()
                if pos[0] < width and pos[1] < width:
                    row, col = get_clicked_pos(pos, rows, width)
                    spot = grid[row][col]
                    spot.reset()
                    wall.remove((row,col))
                    if spot == start:
                        start = None
                    elif spot == end:
                        end = None

            if pygame.mouse.get_pressed()[1]:
                pos = pygame.mouse.get_pos()
                if pos[0] < width and pos[1] < width:
                    row,col = get_clicked_pos(pos, rows, width)
                    spot=grid[row][col]
                    
                    if pos in mandatory_points:
                        mandatory_points.remove((row,col))
                    else: 
                        spot.make_points()
                        mandatory_points.add((row,col))
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end and not event.key == pygame.K_c:
                    
                    now1 = time.time()   
                    world = PathFinding.World(rows-1,rows-1,wall)
                    all_plan = []
                    # Inizializzazione del punto corrente come punto di partenza
                    initial_point = (start.row, start.col)
                    final_point = (end.row,end.col)
                if mandatory_points.__len__() != 0:
                    # Calcolo dell'euristica tra il punto di partenza e il primo punto intermedio
                    prossimo_punto = trova_punto_vicino(initial_point,mandatory_points)
                    p = PathFinding(world,(initial_point),(prossimo_punto))
                    current_point= prossimo_punto  
                    plan = search_algorithm.solve(p)
                    if plan:
                        all_plan.extend(plan)
                        mandatory_points.remove(prossimo_punto) 
                    # Calcolo dell'euristica tra il punto più vicino lo start e un punto intermedio
                        while mandatory_points:
                            # Trova il punto intermedio più vicino al punto corrente
                            prossimo_punto = trova_punto_vicino(current_point, mandatory_points)
                            # Calcola il percorso tra il punto corrente e il punto intermedio
                            p = PathFinding(world, current_point, prossimo_punto)
                            plan = search_algorithm.solve(p)
                            if plan:
                                all_plan.extend(plan)
                                # Aggiorna il punto corrente al punto appena trovato
                                current_point = prossimo_punto
                                # Rimuovi il punto intermedio appena trovato dalla lista dei punti intermedi
                                mandatory_points.remove(prossimo_punto)
                    #Calcolo dell'euristica tra l'ultimo punto e il punto finale
                    int_p = PathFinding(world,(current_point),(final_point))
                    int_plan = (search_algorithm.solve(int_p))
                    if int_plan:
                        all_plan.extend(int_plan)
                else : 
                    final_p = PathFinding(world,(initial_point),(final_point))
                    final_plan = (search_algorithm.solve(final_p))
                    if final_plan:
                        all_plan.extend(final_plan)

                now2 = time.time()
                now= (now2 - now1)

                print("Number of Expansion: {} in {} seconds".format(search_algorithm.expanded,now))

                #mark_expanded(search_algorithm.expanded_states, grid)
                
                if all_plan is not None:
                    print(all_plan)
                    print("Cost of the plan is: {}".format(len(all_plan)))
                    mark_spots(start,end,grid,all_plan)
                    
                    draw(win, grid, rows, width)
                    
                if event.key == pygame.K_c:
                    
                    start = None
                    end = None
                    mandatory_points = set()  # reimposta la lista dei punti obbligati a vuota
                    points=set()
                    all_plan = None
                    grid = make_grid(rows, width)
                    wall = set()
                    pygame.display.update()
                    
                    
    pygame.quit()

if __name__ == '__main__':
    main()
