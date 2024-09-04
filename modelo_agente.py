import numpy as np
from utils import puntaje_y_no_usados, separar, JUGADA_PLANTARSE, JUGADA_TIRAR, JUGADAS_STR
from collections import defaultdict
from tqdm import tqdm
from jugador import Jugador
from random import randint
import csv
from collections import Counter

# episodio = un juego entero de diezmil (con reset() se reinicia el juego)
# estado = es un turno dentro del juego
# step = una tirada de dados

class AmbienteDiezMil:
    
    def __init__(self): # por juego
        """Definir las variables de instancia de un ambiente.
        ¿Qué es propio de un ambiente de 10.000?
        """
        self.puntaje_total = 0
        self.cantidad_turnos = 0
    
    def reset(self): # por turno
        """Reinicia el ambiente para volver a realizar un episodio.
        """
        self.puntaje_total = 0
        self.cantidad_turnos = 0

class EstadoDiezMil(AmbienteDiezMil):
    def __init__(self):
        """Inicializa un estado de DiezMil, es decir, un turno."""
        super().__init__()  # Llama al constructor de la clase padre
        self.puntaje_turno = 0
        self.dados = [randint(1, 6) for _ in range(6)]  # Inicializa los dados para este turno
        self.turno_terminado = False

    def reset_turno(self):
        """Modifica el estado al terminar el turno."""
        self.puntaje_turno = 0
        self.cantidad_turnos += 1
        self.dados = [randint(1, 6) for _ in range(6)]
        self.turno_terminado = False

    def step(self, accion, dados): # por tirada
        """Dada una acción devuelve una recompensa.
        El estado es modificado acorde a la acción y su interacción con el ambiente.
        Podría ser útil devolver si terminó o no el turno.

        Args:
            accion: Acción elegida por un agente.

        Returns:
            tuple[int, bool]: Una recompensa y un flag que indica si terminó el turno. 
        """
        reward = 0 # recompensa por tirada, lo queremos usar para que el agente aprenda
        (puntaje_tirada, dados_a_tirar) = puntaje_y_no_usados(dados)
        
        #caso en el que eligio tirar y no gano nada --> RESET y penalizacion
        if puntaje_tirada == 0 and accion == JUGADA_TIRAR:
            reward = -self.puntaje_turno
            self.puntaje_turno = 0
            self.turno_terminado = True
        else:
            #caso en el que tira --> se actualiza el puntaje del turno y se tiran los dados
            if accion == JUGADA_TIRAR:
                self.puntaje_turno += puntaje_tirada
                #si sumo con todos, consiguio otra tirada y sigue
                if len(dados_a_tirar) == 0 :
                    self.dados = [randint(1, 6) for _ in range(6)] 
               #si no tiro con los que le quedan
                else: 
                    self.dados = [randint(1, 6) for _ in range(len(dados_a_tirar))] 
                self.turno_terminado = False
                reward = puntaje_tirada

            #caso en el que se planta --> se actualiza el puntaje total y se termina el turno
            elif accion == JUGADA_PLANTARSE or len(dados_a_tirar) == 0:
                self.puntaje_turno += puntaje_tirada
                self.puntaje_total += self.puntaje_turno
                self.turno_terminado = True
                reward = self.puntaje_turno

    
        return reward, dados_a_tirar
    
    def __str__(self):
        """Representación en texto de EstadoDiezMil.
        Ayuda a tener una versión legible del objeto.

        Returns:
            str: Representación en texto de EstadoDiezMil.
        """
        return f"Total: {self.puntaje_total}, Turno: {self.puntaje_turno}, Dados: {self.dados}, #Turnos: {self.cantidad_turnos}"   

class AgenteQLearning:
    def __init__(self, ambiente: AmbienteDiezMil, *args, **kwargs):
        """Inicializa un agente de Q-learning."""
        self.ambiente = ambiente
        self.estado = EstadoDiezMil()
        self.alpha = 0.6 
        self.gamma = 0.9 #tiene muy en cuenta el rweard de haber hecho dicha accion
        self.epsilon = 0.55 #10% veces va a hacer random
        self.epsilon_decay = 0.995
        self.q_table = defaultdict(lambda: [0.0, 1.0]) 
           
    def elegir_accion(self, dados,puntaje_actual):
        """Selecciona una acción de acuerdo a una política ε-greedy."""
        if np.random.rand() < self.epsilon:
            self.epsilon *= self.epsilon_decay
            accion = np.random.choice([JUGADA_PLANTARSE, JUGADA_TIRAR]) # random entre JUGADA_PLANTARSE o JUGADA_TIRAR
            return [JUGADA_PLANTARSE, JUGADA_TIRAR].index(accion) #devuelve la poscion donde esta accion
        else:
            estado = (len(dados), puntaje_actual)
            return np.argmax(self.q_table[estado])
         # accede a los valores de Q almacenados para dados y devuelve el reward maximo entre las dos acciones
                                                         # si los dos valores son iguales, devuelve 0 (plantarse)
                                                         
    def entrenar(self, episodios: int, verbose: bool = False) -> None:
        """Dada una cantidad de episodios (cantidad de juegos diezmil),
           se repite el ciclo del algoritmo de Q-learning."""
        for episodio in tqdm(range(episodios), desc="Entrenando al Agente Q-Learning"):
            self.estado.reset()
            while self.estado.puntaje_total <= 10000:
                tirada = 0
                while not self.estado.turno_terminado: # mientras no haya terminado el turno (turno_terinado = False)
                    tirada += 1
                    # me guardo el estado actual (podriamos hacer que get estado sea esto)
                    dados_actual = self.estado.dados
                    (puntaje_tirada, _) = puntaje_y_no_usados(dados_actual)
                    puntos_actual = self.estado.puntaje_turno + puntaje_tirada
                    cant_dados_actual = len(dados_actual)
                    estado_actual = (cant_dados_actual, puntos_actual)

                    #eligo accion con estado actual
                    accion = self.elegir_accion(dados_actual,puntos_actual)
                    
                    #realizamos la accion y obtenemos la recompensa (se actualizan los puntos turno y puntos totales)
                    reward, dados_a_tirar = self.estado.step(accion, dados_actual) 

                    #me guardo el estado futuro segun la accion
                    (puntaje_tirada_futura, _) = puntaje_y_no_usados(self.estado.dados) #aca algo me hace ruido (si se planta el estado futuro usa los mimos dados. Esta guardadno un puntaje futuro que no es (6,0))
                    if accion == JUGADA_TIRAR:
                        estado_futuro  = (len(self.estado.dados),self.estado.puntaje_turno+puntaje_tirada_futura)
                    else:
                        # estado_futuro  = (len(dados_a_tirar),self.estado.puntaje_turno)
                        estado_futuro  = (6,0)
                    
                    #actualizar tabla
                    max_q = float(np.max(self.q_table[estado_futuro])) 
                    self.q_table[estado_actual][accion] += self.alpha * (reward + self.gamma * max_q - self.q_table[estado_actual][accion])
                    
                    # print para seguir el turno 
                    print(f'tirada {tirada} estado_actual: {estado_actual}, accion: {JUGADAS_STR[accion]}, reward: {reward}, estado_futuro: {estado_futuro}, max_q: {max_q}, q_table: {self.q_table[estado_actual]}')

                #puntos turno = 0, 6 nuevos dados random y turno terminado = False
                self.estado.reset_turno()
                


    def guardar_politica(self, filename: str):
        """Almacena la política del agente en un archivo CSV."""
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Estado Dados', 'Q(Plantarse)', 'Q(Tirar)'])
            
            for tuple, valores_q in self.q_table.items():
                writer.writerow([tuple, valores_q[0], valores_q[1]])

        print(f"Política guardada en {filename}")

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
        accion_idx = self.politica.get(f'({len(dados)}, {puntaje_turno+puntaje})', 1)
        
        if accion_idx == 0:
            accion = JUGADA_PLANTARSE
        else:
            accion = JUGADA_TIRAR

        return accion, dados_a_tirar
    




"""
[111622] = 1000 _>tirar
544 = 1050 -> plantarse
6,0 
"""



    