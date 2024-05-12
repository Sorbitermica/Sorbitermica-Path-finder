import tkinter as tk
from tkinter import ttk
import pygame
import sys

# Definizione dei colori
BIANCO = (255, 255, 255)
NERO = (0, 0, 0)
ROSSO = (255, 0, 0)

# Funzione per disegnare la griglia
def disegna_griglia(finestra):
    for riga in range(0, larghezza, 20):
        pygame.draw.line(finestra, NERO, (riga, 0), (riga, altezza))
    for colonna in range(0, altezza, 20):
        pygame.draw.line(finestra, NERO, (0, colonna), (larghezza, colonna))

# Funzione per disegnare i punti selezionati
def disegna_punti_selezionati(finestra, punti_selezionati):
    for punto in punti_selezionati:
        pygame.draw.rect(finestra, ROSSO, (punto[0], punto[1], 20, 20))

# Funzione principale
def main(punti_selezionati):
    # Inizializzazione di Pygame
    pygame.init()

    # Creazione della finestra di gioco
    finestra = pygame.display.set_mode((larghezza, altezza))
    pygame.display.set_caption("Seleziona Punti")

    clock = pygame.time.Clock()

    while True:
        finestra.fill(BIANCO)
        disegna_griglia(finestra)
        disegna_punti_selezionati(finestra, punti_selezionati)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()
        clock.tick(60)

def seleziona_tutti(punti_selezionati, lista_punti):
    punti_selezionati.clear()
    for punto in lista_punti:
        if punto not in punti_selezionati:
            punti_selezionati.append(punto)

# Funzione per avviare Pygame
def avvia_pygame(punti_selezionati):
    main(punti_selezionati)

# Dimensioni della finestra di gioco
larghezza = 600
altezza = 400

# Creazione dell'interfaccia di Tkinter
root = tk.Tk()
root.title("Seleziona Punti")

frame = ttk.Frame(root, padding="20")
frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

lista_punti_prefissati = [(20, 20), (100, 200), (300, 100), (500, 300)]  # Esempio di punti prefissati

punti_selezionati = []

for punto in lista_punti_prefissati:
    ttk.Checkbutton(frame, text=f"({punto[0]}, {punto[1]})", command=lambda p=punto: aggiungi_punto(punti_selezionati, p)).grid(sticky=tk.W)

bottone_seleziona_tutti = ttk.Button(root, text="Seleziona tutti", command=lambda: seleziona_tutti(punti_selezionati, lista_punti_prefissati))
bottone_seleziona_tutti.grid(column=0, row=1, pady=10)

bottone_avvia_pygame = ttk.Button(root, text="Avvia Pygame", command=lambda: avvia_pygame(punti_selezionati))
bottone_avvia_pygame.grid(column=0, row=2, pady=10)

root.mainloop()
