import numpy as np
from utils import puntaje_y_no_usados, separar, JUGADA_PLANTARSE, JUGADA_TIRAR, JUGADAS_STR
from collections import defaultdict
from tqdm import tqdm
from jugador import Jugador
from random import randint
import csv

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

    def step(self, dados, accion): # por tirada
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
        print(dados)
        print(dados_a_tirar)
        if puntaje_tirada == 0:
            reward = -1
            self.reset_turno()
            self.turno_terminado = True
        
        elif accion == JUGADA_TIRAR:
            self.puntaje_turno += puntaje_tirada
            dados = [randint(1, 6) for _ in range(len(dados_a_tirar))] 
            self.turno_terminado = False
            reward = 1
            if len(dados_a_tirar) <= 2: # Penalización si sigue tirando con pocos dados (ej. <= 2 dados)
                reward = -0.5

        elif accion == JUGADA_PLANTARSE or len(dados_a_tirar) == 0:
            self.puntaje_turno += puntaje_tirada
            self.puntaje_total += self.puntaje_turno
            if len(dados_a_tirar) >= 3: # Penalización si sigue tirando con pocos dados (ej. <= 2 dados)
                reward = -0.5

            if self.puntaje_turno >= 300:
                reward = 1  # Recompensa positiva por tomar una decisión segura
            self.turno_terminado = True
        print(puntaje_tirada, self.puntaje_turno)
        return reward, dados
    
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
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.1
        self.q_table = defaultdict(lambda: [0.0, 0.0])
        self.log_file = 'acciones_qlearning.csv'
    
    def elegir_accion(self, dados):
        """Selecciona una acción de acuerdo a una política ε-greedy."""
        if np.random.rand() < self.epsilon:
            accion = np.random.choice([JUGADA_PLANTARSE, JUGADA_TIRAR]) # random entre 0 o 1
            return [JUGADA_PLANTARSE, JUGADA_TIRAR].index(accion)
        else:
            return np.argmax(self.q_table[tuple(dados)]) # accede a los valores de Q almacenados para dados y devuelve el reward maximo entre las dos acciones
                                                         # si los dos valores son iguales, devuelve 0 (plantarse)
                                                         
    def entrenar(self, episodios: int, verbose: bool = False) -> None:
        """Dada una cantidad de episodios (cantidad de juegos diezmil),
           se repite el ciclo del algoritmo de Q-learning."""
        episodio = 0
        for episodio in tqdm(range(episodios), desc="Entrenando al Agente Q-Learning"):
            self.ambiente.reset()
            episodio += 1
            while self.ambiente.puntaje_total <= 10000:
                tirada = 0
                while not self.estado.turno_terminado: # mientras no haya terminado el turno (turno_terinado = False)
                    tirada += 1
                    accion = self.elegir_accion(self.estado.dados) # 1(TIRAR) o 0(PLANTARSE)
                    dados = self.estado.dados # Guardar los dados 
                    print(type(dados))
                    reward, dados_nuevos = self.estado.step(accion, dados) # Realizar la acción y obtener la recompensa

                    print(f"Episodio: {episodio}")
                    # print(f"q_table_vieja: {self.q_table[tuple(dados)]}")

                    max_q = float(np.max(self.q_table[tuple(dados_nuevos)])) # guarda la maxima recompensa entre las acciones (tirar, plantarse)
                    self.q_table[tuple(dados)][accion] += self.alpha * (reward + self.gamma * max_q - self.q_table[tuple(dados)][accion])
                    
                    print(f"Turnos: {self.estado.cantidad_turnos}")
                    print(f"Tirada: {tirada}")
                    print(f"Dados: {dados}")
                    print(f"Accion: {JUGADAS_STR[accion]}")
                    print(f"reward: {reward}")
                    # print(f"q_table: {self.q_table[tuple(dados)]}")
                    print(f"Puntaje de Turno: {self.estado.puntaje_turno}")
                    # print(f"Puntaje Total: {self.ambiente.puntaje_total}")

                self.estado.reset_turno()

                
                
                
            if verbose and (episodio + 1) % 100 == 0:
                print(f"Episodio {episodio + 1}/{episodios} completado. Puntaje Total: {self.ambiente.puntaje_total}")

            # Guardar la información en un archivo CSV
            self.log_accion(episodio + 1, self.ambiente.cantidad_turnos, dados, self.estado.puntaje_turno, self.ambiente.puntaje_total, accion)
                
    def log_accion(self, episodio, turno, dados, puntaje_tirada, puntaje_total, accion):
        """Guarda la acción realizada en un archivo CSV."""
        with open(self.log_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([episodio, turno, dados, puntaje_tirada, puntaje_total, JUGADAS_STR[accion]])

    def guardar_politica(self, filename: str):
        """Almacena la política del agente en un archivo CSV."""
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Estado Dados', 'Q(Tirar)', 'Q(Plantarse)'])
            
            for dados, valores_q in self.q_table.items():
                writer.writerow([dados, valores_q[0], valores_q[1]])

        print(f"Política guardada en {filename}")

class JugadorEntrenado(Jugador):
    def __init__(self, nombre: str, filename_politica: str):
        self.nombre = nombre
        self.politica = self._leer_politica(filename_politica)
        
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
                estado_tuple, q_tirar, q_plantarse = row
                q_tirar = float(q_tirar)
                q_plantarse = float(q_plantarse)
                
                # Determinar la mejor acción: 0 para tirar, 1 para plantarse
                mejor_accion = 0 if q_tirar >= q_plantarse else 1
                
                # Guardar en el diccionario de política
                politica[estado_tuple] = mejor_accion
        
        return politica
    
    def jugar(self, estado):
        """Dada una representación del estado actual del juego, devuelve la acción a tomar.

        Args:
            estado (str): Estado actual del juego como una cadena.

        Returns:
            int: La acción a tomar, 0 para tirar, 1 para plantarse.
        """
        return self.politica.get(estado, 0)  # Por defecto, tirar si el estado no está en la política
    









    