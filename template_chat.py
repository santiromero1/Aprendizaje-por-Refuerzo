import numpy as np
from utils import puntaje_y_no_usados, JUGADA_PLANTARSE, JUGADA_TIRAR, JUGADAS_STR
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
        self.reset()

    def reset(self):
        """Reinicia el ambiente para volver a realizar un episodio.
        """
        # Reinicia el ambiente: puntaje total, puntaje del turno, dados
        self.puntaje_total = 0
        self.puntaje_turno = 0
        self.dados = [1, 2, 3, 4, 5, 6]  # Siempre se empieza con 6 dados
        return self._get_estado()
    
    def _get_estado(self):
        # Devuelve una representación del estado actual
        return (self.puntaje_total, self.puntaje_turno, tuple(self.dados))

    def step(self, accion):
        """Dada una acción devuelve una recompensa.
        El estado es modificado acorde a la acción y su interacción con el ambiente.
        Podría ser útil devolver si terminó o no el turno.

        Args:
            accion: Acción elegida por un agente.

        Returns:
            tuple[int, bool]: Una recompensa y un flag que indica si terminó el turno. 
        """
                # Realiza una acción y devuelve la recompensa y si el turno terminó
        if accion == JUGADA_PLANTARSE:
            self.puntaje_total += self.puntaje_turno
            self.puntaje_turno = 0
            return self.puntaje_total, True  # Se planta, termina el turno
        
        elif accion == JUGADA_TIRAR:
            # Simular la tirada de los dados
            tirada = [randint(1, 6) for _ in range(len(self.dados))]
            puntaje_tirada, no_usados = puntaje_y_no_usados(tirada)
            
            if puntaje_tirada == 0:
                # No suma puntos, pierde el turno
                self.puntaje_turno = 0
                return 0, True  # Termina el turno

            else:
                self.puntaje_turno += puntaje_tirada
                self.dados = no_usados if no_usados else [1, 2, 3, 4, 5, 6]  # Volver a tirar todos si se usaron todos
                return puntaje_tirada, False  # No termina el turno

class EstadoDiezMil:
    def __init__(self):
        """Definir qué hace a un estado de diez mil.
        Recordar que la complejidad del estado repercute en la complejidad de la tabla del agente de q-learning.
        """
        self.puntaje_total = 0
        self.puntaje_turno = 0
        self.dados = [1, 2, 3, 4, 5, 6]

    def actualizar_estado_base(self, *args, **kwargs) -> None:
        """Modifica las variables internas del estado luego de una tirada.

        Args:
            ... (_type_): _description_
            ... (_type_): _description_
        """
        pass

    def actualizar_estado(self, puntaje_total, puntaje_turno, dados):
        self.puntaje_total = puntaje_total
        self.puntaje_turno = puntaje_turno
        self.dados = dados
    
    def fin_turno(self):
        """Modifica el estado al terminar el turno.
        """
        self.puntaje_total += self.puntaje_turno
        self.puntaje_turno = 0
        self.dados = [1, 2, 3, 4, 5, 6]

    def __str__(self):
        """Representación en texto de EstadoDiezMil.
        Ayuda a tener una versión legible del objeto.

        Returns:
            str: Representación en texto de EstadoDiezMil.
        """
        return f"Total: {self.puntaje_total}, Turno: {self.puntaje_turno}, Dados: {self.dados}"   

class AgenteQLearning:
    def __init__(
        self,
        ambiente: AmbienteDiezMil,
        alpha: float = 0.1,
        gamma: float = 0.9,
        epsilon: float = 0.1,
        ##*args,
        ##**kwargs
    ):
        """Definir las variables internas de un Agente que implementa el algoritmo de Q-Learning.

        Args:
            ambiente (AmbienteDiezMil): Ambiente con el que interactuará el agente.
            alpha (float): Tasa de aprendizaje.
            gamma (float): Factor de descuento.
            epsilon (float): Probabilidad de explorar.
        """
        self.ambiente = ambiente
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
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
                recompensa, done = self.ambiente.step(accion)
                nuevo_estado = self.ambiente._get_estado()

                # Q-learning update
                max_q_nuevo_estado = max(self.q_table[nuevo_estado])
                self.q_table[estado][accion] += self.alpha * (
                    recompensa + self.gamma * max_q_nuevo_estado - self.q_table[estado][accion]
                )

                estado = nuevo_estado

            if verbose:
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
            reader = csv.reader(file)
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
        
        jugada = self.politica.get(str(estado), JUGADA_TIRAR)  # Obtener la acción correspondiente
        
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