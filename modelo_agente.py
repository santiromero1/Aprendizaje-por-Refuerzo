import numpy as np
from utils import puntaje_y_no_usados, separar, JUGADA_PLANTARSE, JUGADA_TIRAR, JUGADAS_STR
from collections import defaultdict
from tqdm import tqdm
from jugador import Jugador
from random import randint
import csv
from collections import Counter

# episodio = un ambiente = un juego entero de diezmil (con reset() se reinicia el juego)
# estado = es un turno dentro del juego
# step = una tirada de dados


class DiezMil():
    def __init__(self):
        """Inicializa un estado de DiezMil, es decir, un turno."""
        self.puntaje_total = 0 # cantidad de turnos en el entrenar()
        self.puntaje_turno = 0
        self.dados = [randint(1, 6) for _ in range(6)]  # Inicializa los dados para este turno
        self.turno_terminado = False

    def reset_juego(self):
        self.puntaje_total = 0 

    def reset_turno(self):
        """Modifica el estado al terminar el turno."""
        self.puntaje_turno = 0
        self.dados = [randint(1, 6) for _ in range(6)]
        self.turno_terminado = False

    def step(self, accion, dados): # por tirada
        """Dada una acción devuelve una recompensa.
        El estado es modificado acorde a la acción y su interacción con el ambiente.
        Podría ser útil devolver si terminó o no el turno.

        Args:
            accion: Acción elegida por un agente.

        Returns:
            recompensa, dados a tirar. 
        """
        reward = 0 # recompensa por tirada, lo queremos usar para que el agente aprenda
        (puntaje_tirada, dados_a_tirar) = puntaje_y_no_usados(dados)
        
        #caso en el que eligio tirar y no gano nada --> RESET y penalizacion --> reward es una penalizacion (a mayor puntaje, mayor es la penalizacion)
        if puntaje_tirada == 0 and accion == JUGADA_TIRAR:
            reward = -self.puntaje_turno
            self.puntaje_turno = 0
            self.turno_terminado = True
        else:
            #caso en el que tira --> se actualiza el puntaje del turno y se tiran los dados --> reward es la tirada
            if accion == JUGADA_TIRAR:
                self.puntaje_turno += puntaje_tirada
                #si sumo con todos, consiguio otra tirada y sigue
                if len(dados_a_tirar) == 0 :
                    self.dados = [randint(1, 6) for _ in range(6)] 
               #si no, tiro con los que le quedan
                else: 
                    self.dados = [randint(1, 6) for _ in range(len(dados_a_tirar))] 
                self.turno_terminado = False
                reward = puntaje_tirada

            #caso en el que se planta --> se actualiza el puntaje total y se termina el turno --> reward es el puntaje de turno (lo premio si se planta con muchos)
            elif accion == JUGADA_PLANTARSE:
                self.puntaje_turno += puntaje_tirada
                self.puntaje_total += self.puntaje_turno
                self.turno_terminado = True
                reward = self.puntaje_turno

    
        return reward
    
    def __str__(self):
        return f"Total: {self.puntaje_total}, Turno: {self.puntaje_turno}, Dados: {self.dados}"   

class AgenteQLearning:
    def __init__(self, *args, **kwargs):
        """Inicializa un agente de Q-learning."""
        self.estado = DiezMil()
        self.alpha = 0.6 #lr alto para que converga mas rapido
        self.gamma = 0.9 #tiene muy en cuenta el max_q del estado futuro
        self.epsilon = 0.8 #80% veces va a hacer random al principio, disminuye en un 0.995 por cada vez que el random es usado
        self.epsilon_decay = 0.995
        self.q_table = defaultdict(lambda: [0.0, 1.0]) 
           
    def elegir_accion(self, estado_actual):
        """Selecciona una acción de acuerdo a una política ε-greedy."""
        if np.random.rand() < self.epsilon:
            self.epsilon *= self.epsilon_decay
            accion = np.random.choice([JUGADA_PLANTARSE, JUGADA_TIRAR]) # random entre JUGADA_PLANTARSE o JUGADA_TIRAR
            return [JUGADA_PLANTARSE, JUGADA_TIRAR].index(accion) #devuelve la poscion donde esta accion
        else:
            return np.argmax(self.q_table[estado_actual])
         # accede a los valores de Q almacenados para dados y devuelve el reward maximo entre las dos acciones
                                                         # si los dos valores son iguales, devuelve 0 (plantarse)
                                                         
    def entrenar(self, episodios: int, verbose: bool = False) -> None:
        """Dada una cantidad de episodios (cantidad de juegos diezmil),
           se repite el ciclo del algoritmo de Q-learning."""
        for episodio in tqdm(range(episodios), desc="Entrenando al Agente Q-Learning"):
            self.estado.reset_juego()
            while self.estado.puntaje_total <= 10000:
                tirada = 0
                while not self.estado.turno_terminado: # mientras no haya terminado el turno (turno_terinado = False)
                    tirada += 1

                    # me guardo el estado actual (cantidad de dados y puntaje turno+tirada)
                    dados_actual = self.estado.dados
                    (puntaje_tirada, dados_a_tirar_actual) = puntaje_y_no_usados(dados_actual)
                    puntos_actual = self.estado.puntaje_turno + puntaje_tirada
                    estado_actual = (len(dados_a_tirar_actual), puntos_actual) # nos importa la cantidad de dados a tirar, no sus valores.

                    #elijo la accion segun el estado actual
                    accion = self.elegir_accion(estado_actual)
                    
                    #realizamos la accion y obtenemos la recompensa (se actualizan los dados, los puntos turno y puntos totales)
                    reward = self.estado.step(accion, dados_actual) 

                    #me guardo el estado futuro segun la accion tomada.
                    (puntaje_tirada_futura, dados_a_tirar_futuro) = puntaje_y_no_usados(self.estado.dados) #no use dados_a_tirar_actual porque no estan randomizados, los agarro desde self.estado.dados para que sean nuevos (son del mismo len igual)
                    if accion == JUGADA_TIRAR:
                        estado_futuro  = (len(dados_a_tirar_futuro),self.estado.puntaje_turno+puntaje_tirada_futura)
                    else:
                        # estado_futuro  = (len(dados_a_tirar),self.estado.puntaje_turno)
                        estado_futuro  = (6,0)
                    
                    #actualizar tabla
                    max_q = float(np.max(self.q_table[estado_futuro])) 
                    self.q_table[estado_actual][accion] += self.alpha * (reward + self.gamma * max_q - self.q_table[estado_actual][accion])
                    
                    # print para seguir el turno 
                    # print(f'tirada {tirada} estado_actual: {estado_actual}, accion: {JUGADAS_STR[accion]}, reward: {reward}, estado_futuro: {estado_futuro}, max_q: {max_q}, q_table: {self.q_table[estado_actual]}')

                #puntos turno = 0, 6 nuevos dados random y turno terminado = False
                self.estado.reset_turno()
                
    def guardar_politica(self, filename: str):
        """Almacena la política del agente en un archivo CSV."""
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Estado Dados', 'Q(Plantarse)', 'Q(Tirar)'])
            
            for tuple, valores_q in self.q_table.items():
                writer.writerow([tuple, valores_q[0], valores_q[1]])

        print(f"Politica guardada en {filename}")

class JugadorEntrenado(Jugador):
    def __init__(self, nombre: str, filename_politica: str):
        self.nombre = nombre
        self.politica = self._leer_politica(filename_politica)
        # print(self.politica)
        
    def _leer_politica(self, filename: str, SEP: str = ','):
        """Carga una política entrenada con un agente de RL, que está guardada
        en el archivo filename en un formato conveniente.

        Args:
            filename (str): Nombre/Path del archivo que contiene a una política almacenada. 
            SEP (str): Separador de columnas en el archivo.
        
        Returns:
            dict: Un diccionario que mapea estados del juego a acciones.
        """
        politica = {}
        with open(filename, 'r') as file:
            reader = csv.reader(file, delimiter=SEP)
            next(reader)  # Omitir el encabezado
            for row in reader:
                estado_tuple, q_plantarse, q_tirar = row
                q_tirar = float(q_tirar)
                q_plantarse = float(q_plantarse)
                
                # Determinar la mejor acción: 0 para plantars, 1 para etirar
                mejor_accion = 0 if q_tirar <= q_plantarse else 1
                
                # Guardar en el diccionario de política
                politica[estado_tuple] = mejor_accion
        
        return politica
    

    def jugar(self, puntaje_total:int, puntaje_turno:int, dados:list[int],
              verbose:bool=False) -> tuple[int,list[int]]:
        (puntaje, dados_a_tirar) = puntaje_y_no_usados(dados)
        accion_idx = self.politica.get(f'({len(dados_a_tirar)}, {puntaje_turno+puntaje})', 1)
        
        if accion_idx == 0:
            accion = JUGADA_PLANTARSE
        else:
            accion = JUGADA_TIRAR

        return accion, dados_a_tirar
    

    