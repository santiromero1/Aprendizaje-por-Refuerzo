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
        if puntaje_tirada == 0:
            if accion == JUGADA_TIRAR: #penalizar fuerte si decidio tirar y quedo BUSTED
                reward += -3 
            self.reset_turno()
            self.turno_terminado = True
        
        elif accion == JUGADA_TIRAR:
            self.puntaje_turno += puntaje_tirada
            dados = [randint(1, 6) for _ in range(len(dados_a_tirar))] 
            self.turno_terminado = False
            reward += 1
            if len(dados_a_tirar) <= 2: # Penalización si sigue tirando con pocos dados 
                reward += -2
            elif len(dados_a_tirar) >= 4:# felicitar si tiro cuando tenia muchos dados 
                reward += 6
            if self.puntaje_turno <= 200:
                reward += 3

        elif accion == JUGADA_PLANTARSE or len(dados_a_tirar) == 0:
                self.puntaje_turno += puntaje_tirada
                self.puntaje_total += self.puntaje_turno
                
                # Felicitar si en dados habían 3 iguales, si eran 3 unos felicitar más
                contador_dados = Counter(dados)
                for valor, cantidad in contador_dados.items():
                    if cantidad == 3:  # Si hay 3 o más dados iguales
                        if valor == 1:
                            reward += 7  # Recompensa mayor si son tres unos (si o si me planto con 1000)
                        else:
                            reward += 3  # Recompensa estándar por 3 dados iguales
                        break  # Solo contar una vez la primera combinación de 3 iguales
                    elif cantidad > 3:
                        reward += 10  # Recompensa por tener 3 o más dados iguales
                if len(dados_a_tirar) >= 3:  # Penalizar si tenía más de 3 dados y se quedó
                    reward += -1
                    if self.puntaje_turno <= 200:  # Penalizar si se quedó y tenía pocos puntos 
                        reward += -2
                    elif self.puntaje_turno >= 300:
                        reward += 2  # Recompensa positiva por tomar una decisión segura
                
                self.turno_terminado = True
            
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
        self.alpha = 0.1 # nose?
        self.gamma = 0.9 # tiene muy en cuenta el rweard de haber hecho dicha accion
        self.epsilon = 0.1 #10% veces va a hacer random
        self.epsilon_decay = 0.999 # va a ir disminuyendo el epsilon
        self.q_table = defaultdict(lambda: [0.0, 0.0])
    
    def elegir_accion(self, dados):
        """Selecciona una acción de acuerdo a una política ε-greedy."""
        if np.random.rand() < self.epsilon:
            accion = np.random.choice([JUGADA_PLANTARSE, JUGADA_TIRAR]) # random entre JUGADA_PLANTARSE o JUGADA_TIRAR
            return [JUGADA_PLANTARSE, JUGADA_TIRAR].index(accion) #devuelve la poscion donde esta accion
        else:
            return np.argmax(self.q_table[tuple(sorted(dados))]) # accede a los valores de Q almacenados para dados y devuelve el reward maximo entre las dos acciones
                                                         # si los dos valores son iguales, devuelve 0 (plantarse)
                                                         
    def entrenar(self, episodios: int, verbose: bool = False) -> None:
        """Dada una cantidad de episodios (cantidad de juegos diezmil),
           se repite el ciclo del algoritmo de Q-learning."""
        contador_episodio = 0
        for episodio in tqdm(range(episodios), desc="Entrenando al Agente Q-Learning"):
            # print(f'{episodio}/{episodios}')
            self.estado.reset()
            contador_episodio += 1
            while self.estado.puntaje_total <= 10000:
                tirada = 0
                while not self.estado.turno_terminado: # mientras no haya terminado el turno (turno_terinado = False)
                    tirada += 1
                    accion = self.elegir_accion(self.estado.dados) # 1(TIRAR) o 0(PLANTARSE)
                    dados = self.estado.dados # Guardar los dados 
                    reward, dados_nuevos = self.estado.step(accion, dados) # Realizar la acción y obtener la recompensa

                    # print(f"Episodio: {contador_episodio}")
                    # print(f"q_table_vieja: {self.q_table[tuple(sorted(dados))]}")
                    # print(f"Turnos: {self.estado.cantidad_turnos+1}")
                    # print(f"Tirada: {tirada}")
                    # print(f"Dados: {dados}")
                    # print(f"Accion: {JUGADAS_STR[accion]}")
                    # print(f"reward: {reward}")

                    max_q = float(np.max(self.q_table[tuple(sorted(dados_nuevos))])) # guarda la maxima recompensa entre las acciones (tirar, plantarse)
                    self.q_table[tuple(sorted(dados))][accion] += self.alpha * (reward + self.gamma * max_q - self.q_table[tuple(sorted(dados))][accion])
                    
                    # print(f"q_table: {self.q_table[tuple(sorted(dados))]}")
                    # print(f"Puntaje de Turno: {self.estado.puntaje_turno}")
                    # print(f"Puntaje Total: {self.estado.puntaje_total}")

                    self.estado.dados = dados_nuevos
                self.estado.reset_turno()
            self.epsilon *= self.epsilon_decay
            if verbose and (episodio + 1) % 100 == 0:
                print(f"Episodio {episodio + 1}/{episodios} completado. Puntaje Total: {self.ambiente.puntaje_total}")
                
    # def log_accion(self, episodio, turno, dados, puntaje_tirada, puntaje_total, accion):
    #     """Guarda la acción realizada en un archivo CSV."""
    #     with open(self.log_file, 'a', newline='') as file:
    #         writer = csv.writer(file)
    #         writer.writerow([episodio, turno, dados, puntaje_tirada, puntaje_total, JUGADAS_STR[accion]])

    def guardar_politica(self, filename: str):
        """Almacena la política del agente en un archivo CSV."""
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Estado Dados', 'Q(Plantarse)', 'Q(Tirar)'])
            
            for dados, valores_q in self.q_table.items():
                writer.writerow([dados, valores_q[0], valores_q[1]])

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
        # print(tuple(sorted(dados)))
        # print(self.politica['(1, 3, 4, 4, 5, 5)'])
        accion_idx = self.politica.get(str(tuple(sorted(dados))),0)
        
        if accion_idx == 0:
            accion = JUGADA_PLANTARSE
        else:
            accion = JUGADA_TIRAR

        return accion, dados_a_tirar
    






    