import numpy as np
from utils import puntaje_y_no_usados, separar, JUGADA_PLANTARSE, JUGADA_TIRAR, JUGADAS_STR
from collections import defaultdict
from tqdm import tqdm
from jugador import Jugador
from random import randint
import csv

class AmbienteDiezMil:
    
    def __init__(self):
        """Definir las variables de instancia de un ambiente.
        ¿Qué es propio de un ambiente de 10.000?
        """
        return self.reset()

    def reset(self):
        """Reinicia el ambiente para volver a realizar un episodio.
        """
        self.puntaje_total = 0
        self.puntaje_turno = 0 
        self.cantidad_turnos = 0 
        dados_a_tirar: list[int] = [1, 2, 3, 4, 5, 6]
        self.dados = [randint(1, 6) for _ in range(len(dados_a_tirar))]
        self.turno_terminado = False
    
    # def get_estado(self):
    #     # Devuelve una representación del estado actual
    #     return (self.puntaje_total, self.puntaje_turno, tuple(self.dados))

    def step(self, dados, accion):
        """Dada una acción devuelve una recompensa.
        El estado es modificado acorde a la acción y su interacción con el ambiente.
        Podría ser útil devolver si terminó o no el turno.

        Args:
            accion: Acción elegida por un agente.

        Returns:
            tuple[int, bool]: Una recompensa y un flag que indica si terminó el turno. 
        """

        (puntaje_tirada, dados_a_tirar) = puntaje_y_no_usados(dados)

        if puntaje_tirada == 0:
                self.turno_terminado = True
                return self.puntaje_total, self.turno_terminado
        
        elif accion == JUGADA_PLANTARSE:
            self.puntaje_total += puntaje_tirada + self.puntaje_turno
            self.turno_terminado = True
            return self.puntaje_total, self.turno_terminado  # Se planta, termina el turno
        
        elif accion == JUGADA_TIRAR:
            self.puntaje_turno += puntaje_tirada
            self.dados = [randint(1, 6) for _ in range(len(dados_a_tirar))]
            self.turno_terminado = False

class EstadoDiezMil():
    def __init__(self, puntaje_total, puntaje_turno=0, dados=None, turno_terminado=False):
        """Definir qué hace a un estado de diez mil.
        Recordar que la complejidad del estado repercute en la complejidad de la tabla del agente de q-learning.
        """
        self.puntaje_total = puntaje_total
        self.puntaje_turno = puntaje_turno
        self.dados = len(dados) if dados else 6
        self.turno_terminado = turno_terminado

    def actualizar_estado(self, nuevo_puntaje_turno, nuevos_dados):
        """Modifica las variables internas del estado luego de una tirada.
        """
        self.puntaje_turno = nuevo_puntaje_turno
        self.dados = nuevos_dados
    
    def fin_turno(self):
        """Modifica el estado al terminar el turno.
        """
        self.puntaje_total += self.puntaje_turno
        self.puntaje_turno = 0
        self.dados = [1, 2, 3, 4, 5, 6] # habria que randomizar los dados?
        self.turno_terminado = True

    def __str__(self):
        """Representación en texto de EstadoDiezMil.
        Ayuda a tener una versión legible del objeto.

        Returns:
            str: Representación en texto de EstadoDiezMil.
        """
        return f"Total: {self.puntaje_total}, Turno: {self.puntaje_turno}, Dados: {self.dados}"   

class AgenteQLearning:
    def __init__(self, ambiente: AmbienteDiezMil, alpha: float = 0.1, gamma: float = 0.9, epsilon: float = 0.1, *args, **kwargs):
        """Inicializa un agente de Q-learning.

        Args:
            ambiente (AmbienteDiezMil): El ambiente con el que el agente interactuará.
            alpha (float): Tasa de aprendizaje (controla cuánto se ajustan las estimaciones de Q).
            gamma (float): Factor de descuento (cuánto se valora la recompensa futura).
            epsilon (float): Probabilidad de explorar (ε-greedy).
        """
        self.ambiente = ambiente  # El entorno en el que el agente opera
        self.alpha = alpha  # Tasa de aprendizaje
        self.gamma = gamma  # Factor de descuento
        self.epsilon = epsilon  # Probabilidad de exploración
        self.q_table = defaultdict(lambda: [0, 0])  # Diccionario que devuelve [Q(plantarse), Q(tirar)]


    def elegir_accion(self, estado):
        """Selecciona una acción de acuerdo a una política ε-greedy.
        """
        if np.random.rand() < self.epsilon:
            # Explorar: elige una acción aleatoria
            return np.random.choice([JUGADA_PLANTARSE, JUGADA_TIRAR])
        else:
            # Explotar: elige la mejor acción según la Q-table
            return np.argmax(self.q_table[estado])

    def entrenar(self, episodios: int, verbose: bool = False) -> None:
        """Dada una cantidad de episodios, se repite el ciclo del algoritmo de Q-learning.
        Recomendación: usar tqdm para observar el progreso en los episodios.

        Args:
            episodios (int): Cantidad de episodios a iterar.
            verbose (bool, optional): Flag para hacer visible qué ocurre en cada paso. Defaults to False.
        """
        for episodio in tqdm(range(episodios)):
            estado = self.ambiente.reset()
            done = False
            
            while not done:
                accion = self.elegir_accion(estado)
                recompensa, done = self.ambiente.step(accion) # por eso en el step devolvemos la recompensa y si termino o no
                nuevo_estado = self.ambiente.get_estado()

                # Q-learning update
                max_q_nuevo_estado = max(self.q_table[nuevo_estado])
                self.q_table[estado][accion] += self.alpha * (
                    recompensa + self.gamma * max_q_nuevo_estado - self.q_table[estado][accion]
                )

                estado = nuevo_estado

            if verbose:
                print(f"Episode {episodio + 1}/{episodios} completed.")
                print(f"Episode {episodio + 1}: Score {self.ambiente.puntaje_total}")

    def guardar_politica(self, filename: str):
        """Almacena la política del agente en un formato conveniente.

        Args:
            filename (str): Nombre/Path del archivo a generar.
        """
        # Guardar la Q-table como política
        with open(filename, 'w') as f:
            for estado, q_values in self.q_table.items():
                f.write(f"{estado},{q_values[0]},{q_values[1]}\n")

class JugadorEntrenado(Jugador):
    def __init__(self, nombre: str, filename_politica: str):
        self.nombre = nombre
        self.politica = self._leer_politica(filename_politica)
        
    def _leer_politica(self, filename:str, SEP:str=','):
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
            for row in reader:
                if len(row) != 3:
                    print(f"Fila con formato incorrecto: {row}")
                    continue
                estado_str = row[0].strip()
                try:
                    q_value1 = float(row[1].strip())
                    q_value2 = float(row[2].strip())
                    estado = eval(estado_str)  # Convertir el string a un tuple
                    politica[estado] = [q_value1, q_value2]
                except (ValueError, SyntaxError) as e:
                    print(f"Error al procesar la fila: {row}. Error: {e}")
                    continue
        return politica
    
        # politica = {}
        # with open(filename, 'r') as f:
        #     for linea in f:
        #         partes = linea.strip().split(SEP)
        #         estado_str = partes[0].strip()
        #         try:
        #             estado = eval(estado_str)  # Convertir el estado de string a tuple
        #             acciones = list(map(float, partes[1:]))  # Convertir las acciones a floats
        #             politica[estado] = acciones.index(max(acciones))  # Guardar la acción con el máximo valor Q
        #         except (SyntaxError, ValueError) as e:
        #             print(f"Error al procesar la línea: {linea}")
        #             print(f"Detalles del error: {e}")
        # return politica
    
    def jugar(
        self,
        puntaje_total: int,
        puntaje_turno: int,
        dados: list[int],
    ) -> tuple[int, list[int]]:
        """Devuelve una jugada y los dados a tirar.

        Args:
            puntaje_total (int): Puntaje total del jugador en la partida.
            puntaje_turno (int): Puntaje en el turno del jugador.
            dados (list[int]): Tirada del turno.

        Returns:
            tuple[int, list[int]]: Una jugada y la lista de dados a tirar.
        """
        puntaje, no_usados = puntaje_y_no_usados(dados)
        estado = (puntaje_total, puntaje_turno, tuple(sorted(dados)))  # Definir el estado de manera consistente
        
        # jugada = self.politica[estado]
        jugada = self.politica.get(estado, JUGADA_TIRAR)  # Obtener la acción correspondiente
        
        if jugada == JUGADA_PLANTARSE:
            return (JUGADA_PLANTARSE, [])
        elif jugada == JUGADA_TIRAR:
            return (JUGADA_TIRAR, no_usados)
        
        ## COMENTARIOS DE LA BASE ##
        # puntaje, no_usados = puntaje_y_no_usados(dados)
        # COMPLETAR
        # estado = ...
        # jugada = self.politica[estado]
       
        # if jugada==JUGADA_PLANTARSE:
        #     return (JUGADA_PLANTARSE, [])
        # elif jugada==JUGADA_TIRAR:
        #     return (JUGADA_TIRAR, no_usados)