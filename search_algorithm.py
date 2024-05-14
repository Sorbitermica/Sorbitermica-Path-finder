class Node:
    def __init__(self, state, parent=None, action=None, g=0, h=0):
        """
        Inizializza un nuovo nodo.

        Args:
            state: Lo stato rappresentato dal nodo.
            parent: Il nodo genitore del nodo corrente (default: None).
            action: L'azione che ha portato a questo nodo (default: None).
            g: Il costo effettivo dal nodo di partenza al nodo corrente (default: 0).
            h: L'euristica dal nodo corrente al nodo di destinazione (default: 0).
        """
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g
        self.h = h
        
    def __lt__(self, other):
        """
        Confronta due nodi in base alla loro somma di g e h.

        Args:
            other: Altro nodo con cui confrontare.

        Returns:
            True se il nodo corrente ha una somma di g e h minore rispetto all'altro nodo, altrimenti False.
        """
        return (self.g + self.h) < (other.g + other.h)

class SearchAlgorithm:
    def __init__(self, view=False):
        """
        Inizializza un nuovo algoritmo di ricerca.

        Args:
            view: Indica se visualizzare i nodi espansi durante la ricerca (default: False).
        """
        self.expanded = 0
        self.expanded_states = set()
        self.view = view
    
    def update_expanded(self, state):
        """
        Aggiorna il conteggio dei nodi espansi.

        Args:
            state: Lo stato del nodo espanso.
        """
        if self.view:
            self.expanded_states.add(state)
        self.expanded += 1
    
    def reset_expanded(self):
        """Resetta il conteggio dei nodi espansi."""
        if self.view:
            self.expanded_states = set()
        self.expanded = 0
    
    def extract_solution(self, node) -> list:
        """
        Estrae la soluzione dal nodo finale risalendo ai nodi genitori.

        Args:
            node: Il nodo finale della soluzione.

        Returns:
            Una lista di azioni che rappresentano la soluzione.
        """
        sol = []
        while node.parent is not None:
            sol.insert(0, node.action)
            node = node.parent
        return sol
