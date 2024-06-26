# Import delle librerie necessarie
import pygame 
from path_finding import PathFinding
from ASTAR import AStar as ASTARPathFinder
import heuristics
import json
import click 
import time
import tkinter as tk


# Definizione delle costanti dei colori e delle dimensioni della finestra
WIDTH1 = 1200
WIDTH2 = 700
WIDTH = 1000
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

# Funzione per ottenere i punti intermedi tramite una finestra di dialogo
def get_punti_intermedi(punti_intermedi):
    prefixed_points = {
        "Chiave a tubo": ((16, 20)),
        "Pompa ad aria compressa": ((60, 24)),
        "Tagliatubi": ((37, 48)),
        "Idropulitrice": ((80, 20)),
        "Chiave a catena": ((35, 66)),
        "Fresa a mano": ((35,20)),
        "Torcia a gas": ((3,49)),
        "Guarnizioni assortite": ((75,3)),
        "Pinze": ((80,66)),
        "Rubinetto a sfera": ((15,3))
    }
    
    grid_maps = ["mappa_1.json", "mappa_2.json", "mappa_3.json"]
    
    root = tk.Tk()
    root.withdraw()
    
    dialog = tk.Toplevel(root)
    dialog.title("Selezione punti e mappa")
    dialog.geometry("425x400")

    checkboxes = {}  
    selected_points = []
    selected_map = None  
    
    def toggle_point(name, var):
        if var.get() == 1:
            if prefixed_points[name] not in selected_points:
                selected_points.append(prefixed_points[name])
        elif var.get() == 0:
            if prefixed_points[name] in selected_points:
                selected_points.remove(prefixed_points[name])

    def add_selected_points():
        punti_intermedi.update(selected_points)
        nonlocal selected_map  
        selected_maps = [map_name for map_name, var in checkboxes_map.items() if var.get() == 1]
        try:
            if selected_maps:
                selected_map = selected_maps[0]  
            else:
                raise ValueError("nessuna mappa selezionata")
        except ValueError as va:
            print(va)
        
        print("Nome della mappa selezionata:", selected_map)
        print("Punti intermedi aggiunti:", punti_intermedi)
        root.destroy()

    def select_all_points():
        for name in prefixed_points.keys():
            var = checkboxes[name]
            var.set(1)
            if prefixed_points[name] not in selected_points:
                selected_points.append(prefixed_points[name])

    def on_close():
        punti_intermedi.clear() 
        root.destroy()  

    dialog.protocol("WM_DELETE_WINDOW", on_close)
    
    
    main_frame = tk.Frame(dialog)
    main_frame.pack(pady=5, padx=5, fill=tk.Y, side=tk.LEFT)

    
    for i, name in enumerate(prefixed_points.keys()):
        var = tk.IntVar()
        checkbox = tk.Checkbutton(main_frame, text=name, variable=var, onvalue=1, offvalue=0,
                                   command=lambda n=name, v=var: toggle_point(n, v))
        checkbox.grid(row=i, column=0, sticky=tk.W)
        checkboxes[name] = var  
    
    select_all_button = tk.Button(main_frame, text="Seleziona Tutti", command=select_all_points)
    select_all_button.grid(row=len(prefixed_points), column=1, pady=5)

    done_button = tk.Button(main_frame, text="Aggiungi", command=add_selected_points)
    done_button.grid(row=len(prefixed_points) + 1, column=1, pady=5)

    
    map_frame = tk.Frame(dialog)
    map_frame.pack(pady=10, padx=10, fill=tk.Y, side=tk.RIGHT)

    
    checkboxes_map = {}
    for i, map_name in enumerate(grid_maps):
        var_map = tk.IntVar()
        checkbox_map = tk.Checkbutton(map_frame, text=map_name, variable=var_map, onvalue=1, offvalue=0)
        checkbox_map.grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)  
        checkboxes_map[map_name] = var_map  

    dialog.wait_window()

    return punti_intermedi, selected_map  

# Funzione per trovare il punto più vicino a partire da un punto iniziale
def trova_punto_vicino(start_point,punti_intermedi,walls):
    min_euristica = float('inf')
    prossimo_punto = None
                    
    for punto in punti_intermedi:
        euristica = heuristics.manhattan_with_barriers(start_point, punto,walls)
        if euristica < min_euristica:
            min_euristica = euristica
            prossimo_punto = punto
            
    return prossimo_punto

# Classe per rappresentare uno spot nella griglia
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

# Funzione per disegnare la griglia sulla finestra di gioco
def draw_grid(win, rows, width):
    
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, WHITE, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, WHITE, (j * gap, 0), (j * gap, width))

# Funzione per disegnare gli spot sulla finestra di gioco
def draw(win, grid):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            
            spot.draw(win)
            
    bottone_genera.show(win)
    bottone_reset.show(win)
    bottone_save.show(win)

    pygame.display.update()

# Funzione per creare la griglia di spot
def make_grid(rows, width, punti_intermedi):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap)
            if punti_intermedi and (i, j) in punti_intermedi:
                spot.make_points()
            grid[i].append(spot)

    return grid

# Funzione per ottenere la posizione cliccata dall'utente nella finestra di gioco
def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col

# Funzione per creare la griglia da un file JSON
def make_grid_from_file(filename, width, punti_intermedi):

    if filename is None:
        raise ValueError("Il nome del file non può essere None")

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
            elif punti_intermedi and (i, j) in punti_intermedi:
                spot.make_points()
            grid[i].append(spot)

    return grid, start, end, rows, barrier, punti_intermedi

# Funzione per contrassegnare gli spot lungo il percorso calcolato
def mark_spots(start, end, grid, plan,win):
    
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
            start = current_spot
            # Aggiorna la visualizzazione della finestra
            draw(win, grid)
            pygame.display.update()
            pygame.time.wait(5)  # Attendi per un breve periodo
            
    # Ensure end spot remains marked as end
    
    end.make_end()      

# Funzione per contrassegnare gli spot espansi durante la ricerca
def mark_expanded(exp, grid):
    for e in exp:
        current_spot = grid[e[0]][e[1]]
        if current_spot.is_points() or current_spot.is_end():
               continue
        current_spot.make_closed()

# Funzione per contrassegnare i punti intermedi sulla griglia
def mark_points(point, grid):
    for e in point:
        grid[e[0]][e[1]].make_points()

# Funzione per trovare il percorso tramite l'algoritmo di ricerca selezionato
def trova_percorso(rows,wall,start,end,punti_intermedi,search_algorithm):

    world = PathFinding.World(rows-1,rows-1,wall)
    percorso = []
    # Inizializzazione del punto corrente come punto di partenza
    initial_point = (start.row, start.col)
    final_point = (end.row,end.col)

    if punti_intermedi.__len__() != 0:
        # Calcolo dell'euristica tra il punto di partenza e il primo punto intermedio
        prossimo_punto = trova_punto_vicino(initial_point,punti_intermedi,wall)
        p = PathFinding(world,(initial_point),(prossimo_punto),wall)
        current_point= prossimo_punto  
        plan = search_algorithm.solve(p)

        if plan:
            percorso.extend(plan)
            punti_intermedi.remove(prossimo_punto) 
        # Calcolo dell'euristica tra il punto più vicino lo start e un punto intermedio

            while punti_intermedi:
                # Trova il punto intermedio più vicino al punto corrente
                prossimo_punto = trova_punto_vicino(current_point, punti_intermedi,wall)
                # Calcola il percorso tra il punto corrente e il punto intermedio
                p = PathFinding(world, current_point, prossimo_punto,wall)
                plan = search_algorithm.solve(p)

                if plan:
                    percorso.extend(plan)
                    # Aggiorna il punto corrente al punto appena trovato
                    current_point = prossimo_punto
                    # Rimuovi il punto intermedio appena trovato dalla lista dei punti intermedi
                    punti_intermedi.remove(prossimo_punto)
        #Calcolo dell'euristica tra l'ultimo punto e il punto finale
        int_p = PathFinding(world,(current_point),(final_point),wall)
        int_plan = (search_algorithm.solve(int_p))

        if int_plan:
            percorso.extend(int_plan)

    else : 
        final_p = PathFinding(world,(initial_point),(final_point),wall)
        final_plan = (search_algorithm.solve(final_p))

        if final_plan:
    
            percorso.extend(final_plan)
            
    return percorso

# Funzione per salvare la griglia in un file JSON
def save_to_file(grid, start, end,map_name):
    barrier = list()
    for x in grid:
        for spot in x:
            if spot.is_barrier():
                barrier.append((spot.row,spot.col))
    res = {"rows":len(grid), "start": (start.row,start.col), "end": (end.row,end.col), "barrier":barrier}
    data = json.dumps(res,indent=4)
    with open(map_name, "w") as data_file:
        data_file.write(data)

# Classe per rappresentare un bottone sulla finestra di gioco
class Button:
    """Create a button, then blit the surface in the while loop"""
 
    def __init__(self, text, pos, width, height, font_size=18, bg="navy", fg="white", border_color="black", border_width=2, feedback=""):
        self.x, self.y = pos
        self.width = width
        self.height = height
        self.font_size = font_size
        self.bg = bg
        self.fg = fg
        self.border_color = border_color
        self.border_width = border_width
        
        if feedback == "":
            self.feedback = text
        else:
            self.feedback = feedback
        
        self.change_text(text)

    def change_text(self, text):
        self.font = pygame.font.SysFont("Arial", self.font_size)
        self.text = self.font.render(text, True, pygame.Color(self.fg))
        text_width, text_height = self.text.get_size()
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill(pygame.Color(self.border_color))
        self.surface.fill(pygame.Color(self.bg), pygame.Rect(self.border_width, self.border_width, self.width - self.border_width * 2, self.height - self.border_width * 2))
        text_x = (self.width - text_width) // 2
        text_y = (self.height - text_height) // 2
        self.surface.blit(self.text, (text_x, text_y))
        self.rect = self.surface.get_rect(topleft=(self.x, self.y))
 
    def show(self,WIN):
        WIN.blit(self.surface, (self.x, self.y))
 
    def click(self, event, grid, start, end):
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(x, y):
                    if grid is not None and start is not None and end is not None:
                        return True
        return False
    
    def click_save(self, event, grid, start, end,filename):
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(x, y):
                    if grid is not None and start is not None and end is not None:
                        save_to_file(grid, start, end, filename)
                        print("mappa salvata")
                        
    
bottone_genera = Button(
    "Genera percorso",
    (WIDTH+25, 50),
    width=150,
    height=30,
    font_size=20,
    bg=(0, 100, 0),
    fg="white",
    border_color="black",
    border_width=3,
    feedback="Generato"
)

bottone_reset = Button(
    "Reset",
    (WIDTH + 25, 120),
    width=150,
    height=30,
    font_size=18,
    bg="red",
    fg="white",
    border_color="black",
    border_width=3,
    feedback="Reset"
)

bottone_save = Button(
    "Save",
    (WIDTH + 25, 190),
    width=150,
    height=30,
    font_size=18,
    bg="blue",
    fg="white",
    border_color="black",
    border_width=3,
    feedback="Reset" 
)


clock = pygame.time.Clock()

# Funzione principale del programma
@click.command()
@click.option('-w', '--width', default = WIDTH, help = "Width of the Windows")
@click.option('-r', '--rows', default = 100, help = "Number of rows/columns in the map")
@click.option('-s', '--search_algorithm', default = "ASTAR", help = "Search algorithm to be used")
@click.option('-f', '--filename', default = None, help = "Initialize map with data from file")

def main(width, rows, search_algorithm, filename):
    
    start = None
    end = None
    ROWS = rows
    punti_intermedi = set()

    search_algorithm == 'ASTAR'
    search_algorithm = ASTARPathFinder(heuristics.manhattan_with_barriers,True)

    punti_intermedi,filename = get_punti_intermedi(punti_intermedi)

    grid, start, end, rows, wall,punti_intermedi = make_grid_from_file(filename, width, punti_intermedi)

    WIN = pygame.display.set_mode((WIDTH1, WIDTH2))
    pygame.display.set_caption("A* Sorbitermica")
        
    run = True

    while run:
        
        draw(WIN, grid)

        pygame.display.update()
        
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                run = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:

                if pygame.mouse.get_pressed()[0]:  
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

            elif pygame.mouse.get_pressed()[2]: 
                pos = pygame.mouse.get_pos()
                if pos[0] < width and pos[1] < width:
                    row, col = get_clicked_pos(pos, rows, width)
                    spot = grid[row][col]
                    spot.reset()
                    try:
                        wall.remove((row,col))
                    except KeyError:
                        print("La posizione ({},{}) non esiste in wall.".format(row, col))
                    if spot == start:
                        start = None
                    elif spot == end:
                        end = None

            elif pygame.mouse.get_pressed()[1]:
                pos = pygame.mouse.get_pos()
                if pos[0] < width and pos[1] < width:
                    row,col = get_clicked_pos(pos, rows, width)
                    spot=grid[row][col]
                    if pos in punti_intermedi:
                        punti_intermedi.remove((row,col))
                    else: 
                        spot.make_points()
                        punti_intermedi.add((row,col))

            bottone_save.click_save(event,grid,start,end,filename)

            clicked_reset = bottone_reset.click(event, grid, start, end)
            if clicked_reset:
                pygame.display.quit()
                filename = None
                punti_intermedi = set()
                punti_intermedi,filename =get_punti_intermedi(punti_intermedi)

                WIN = pygame.display.set_mode((WIDTH1, WIDTH2))
                pygame.display.set_caption("A* Sorbitermica")
                
                pygame.display.update()
                
                grid, start, end, rows, wall,punti_intermedi = make_grid_from_file(filename, width, punti_intermedi)

            clicked_genera = bottone_genera.click(event, grid, start, end)
            if clicked_genera:
                now1 = time.time()   
                
                percorso = trova_percorso(rows, wall, start, end, punti_intermedi, search_algorithm)

                now2 = time.time()
                
                now = (now2 - now1)

                print("Number of Expansion: {} in {} seconds".format(search_algorithm.expanded, now))

                if percorso is not None:
                    print(percorso)
                    print("Cost of the plan is: {}".format(len(percorso)))
                    mark_spots(start, end, grid, percorso, WIN)
                    draw(WIN, grid)
                    pygame.display.update()  
                
    pygame.quit()

if __name__ == '__main__':
    main()