import numpy as np
from utils import puntaje_y_no_usados, separar, JUGADA_PLANTARSE, JUGADA_TIRAR, JUGADAS_STR
from collections import defaultdict
from tqdm import tqdm
from jugador import Jugador
from random import randint
import csv

# episodio = un juego entero de diezmil
# estado = es un turno dentro del juego
# step = una tirada de dados

class AmbienteDiezMil:
    
    def __init__(self): # por juego
        """Definir las variables de instancia de un ambiente.
        ¿Qué es propio de un ambiente de 10.000?
        """
        return self.reset()

    def reset(self): # por turno
        """Reinicia el ambiente para volver a realizar un episodio.
        """
        self.puntaje_total = 0
        self.cantidad_turnos = 0
        self.puntaje_turno = 0  
        dados_a_tirar: list[int] = [1, 2, 3, 4, 5, 6]
        self.dados = [randint(1, 6) for _ in range(len(dados_a_tirar))]
        self.turno_terminado = False
    
    # def get_estado(self):
    #     # Devuelve una representación del estado actual
    #     return (self.puntaje_total, self.puntaje_turno, tuple(self.dados))

class EstadoDiezMil:
    def __init__(self, puntaje_total: int, puntaje_turno: int, dados: list[int], cantidad_turnos: int):

        self.puntaje_total = puntaje_total
        self.cantidad_turnos = cantidad_turnos
        self.puntaje_turno = 0  
        dados_a_tirar: list[int] = [1, 2, 3, 4, 5, 6]
        self.dados = [randint(1, 6) for _ in range(len(dados_a_tirar))]
        self.turno_terminado = False

    def actualizar_estado(self, puntaje_total, cantidad_turnos):
        """Modifica las variables internas del estado luego de una tirada.
        Args:
            ___ (_type_): _description_
            ___ (_type_): _description_
        """
        estado = (self.puntaje_total, self.puntaje_turno, tuple(self.dados), self.cantidad_turnos)
        return estado
        self.puntaje_total = puntaje_total
        self.puntaj_turnos = cantidad_turnos
        self.cantidad_turnos += 1

    def fin_turno(self):
        """Modifica el estado al terminar el turno.
        """
        self.puntaje_total += self.puntaje_turno
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
        (puntaje_tirada, dados_a_tirar) = puntaje_y_no_usados(dados)

        if puntaje_tirada == 0:
                self.turno_terminado = True
                return self.puntaje_total, self.turno_terminado
        
        elif accion == JUGADA_TIRAR:
            self.puntaje_turno += puntaje_tirada
            self.dados = [randint(1, 6) for _ in range(len(dados_a_tirar))]
            self.turno_terminado = False

        elif accion == JUGADA_PLANTARSE or len(dados_a_tirar) == 0:
            self.puntaje_total += puntaje_tirada + self.puntaje_turno
            self.turno_terminado = True
            self.cantidad_turnos += 1
            return self.puntaje_total, self.turno_terminado
    
    def __str__(self):
        """Representación en texto de EstadoDiezMil.
        Ayuda a tener una versión legible del objeto.

        Returns:
            str: Representación en texto de EstadoDiezMil.
        """
        return f"Total: {self.puntaje_total}, Turno: {self.puntaje_turno}, Dados: {self.dados}, #Turnos: {self.cantidad_turnos}"   

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
        self.estado = EstadoDiezMil(0, 0, [], 0)
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
        for episodios in tqdm(range(episodios), desc="Entrenando al Agente Q-Learning"):
            self.ambiente.reset()
            if self.estado.puntaje_total <= 10000:
                estado = (self.ambiente.puntaje_total, self.ambiente.puntaje_turno, tuple(self.ambiente.dados))
                terminado = False

                while not terminado:
                    # El agente selecciona una acción basado en la política epsilon-greedy
                    accion = self.elegir_accion(estado)
                    
                    # Ejecutar la acción en el entorno
                    nuevo_puntaje_total, turno_terminado = self.ambiente.step(self.ambiente.dados, accion)
                    nuevo_estado = (self.ambiente.puntaje_total, self.ambiente.puntaje_turno, tuple(self.ambiente.dados))
                    
                    # Calcular la recompensa: la recompensa podría ser el cambio en el puntaje total o alguna otra función
                    recompensa = nuevo_puntaje_total - estado[0]  # Diferencia en puntaje total como recompensa
                    
                    # Actualizar la Q-table
                    accion_idx = [JUGADA_PLANTARSE, JUGADA_TIRAR].index(accion)
                    mejor_q = np.max(self.q_table[nuevo_estado])  # Valor Q máximo para el nuevo estado
                    
                    # Regla de actualización de Q-learning
                    self.q_table[estado][accion_idx] += self.alpha * (recompensa + self.gamma * mejor_q - self.q_table[estado][accion_idx])
                    
                    # Actualizar el estado actual
                    estado = nuevo_estado
                    
                    # Determinar si el turno ha terminado
                    terminado = turno_terminado
                
                if verbose and (episodio + 1) % 100 == 0:
                    print(f"Episodio {episodio + 1}/{episodios} completado. Puntaje Total: {self.ambiente.puntaje_total}")

    def guardar_politica(self, filename: str):
        """Almacena la política del agente en un archivo CSV.

        Args:
            filename (str): Nombre/Path del archivo a generar.
        """
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            # Escribir el encabezado
            writer.writerow(['Estado', 'Accion'])
            
            for estado, valores_q in self.q_table.items():
                # Determinar la acción con el valor Q más alto para el estado dado
                mejor_accion = np.argmax(valores_q)
                accion_str = 'Plantarse' if mejor_accion == 0 else 'Tirar'
                # Guardar el estado y la acción
                writer.writerow([estado, accion_str])

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
                if len(row) != 2:
                    print(f"Fila con formato incorrecto: {row}")
                    continue
                estado_str, accion_str = row
                try:
                    estado = eval(estado_str)  # Convertir el string a un tuple
                    accion = 0 if accion_str.strip() == 'Plantarse' else 1
                    politica[estado] = accion
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
        estado = (puntaje_turno, tuple(sorted(dados)))  # Definir el estado de manera consistente
        
        # Obtener la jugada correspondiente al estado actual
        jugada = self.politica.get(estado, JUGADA_TIRAR)  # Por defecto, tirar si el estado no está en la política
        
        if jugada == 0:  # JUGADA_PLANTARSE
            return (JUGADA_PLANTARSE, [])
        elif jugada == 1:  # JUGADA_TIRAR
            return (JUGADA_TIRAR, no_usados)