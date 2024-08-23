from random import randint
from abc import ABC, abstractmethod
from utils import puntaje_y_no_usados, JUGADA_PLANTARSE, JUGADA_TIRAR

class Jugador(ABC):
    @abstractmethod
    def jugar(self, puntaje_total:int, puntaje_turno:int, dados:list[int],
              verbose:bool=False) -> tuple[int,list[int]]:
        pass

class JugadorAleatorio(Jugador):
    def __init__(self, nombre:str):
        self.nombre = nombre
        
    def jugar(self, puntaje_total:int, puntaje_turno:int, dados:list[int],
              verbose:bool=False) -> tuple[int,list[int]]:
        (puntaje, no_usados) = puntaje_y_no_usados(dados)
        if randint(0, 1)==0:
            return (JUGADA_PLANTARSE, [])
        else:
            return (JUGADA_TIRAR, no_usados)

class JugadorSiempreSePlanta(Jugador):
    def __init__(self, nombre:str):
        self.nombre = nombre
        
    def jugar(self, puntaje_total:int, puntaje_turno:int, dados:list[int], 
              verbose:bool=False) -> tuple[int,list[int]]:
        return (JUGADA_PLANTARSE, [])
