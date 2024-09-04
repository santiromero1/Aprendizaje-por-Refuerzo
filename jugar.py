import argparse
from diezmil import JuegoDiezMil
from jugador import Jugador, JugadorAleatorio, JugadorSiempreSePlanta
from modelo_agente import JugadorEntrenado
import matplotlib.pyplot as plt

def jugar_partidas(jugador, num_juegos=100, verbose=False):
    aux_cant_turnos = 0
    for juego in range(num_juegos):
        juego = JuegoDiezMil(jugador)
        cantidad_turnos, puntaje_final = juego.jugar(verbose=verbose)
        aux_cant_turnos += cantidad_turnos
    promedio_turnos = aux_cant_turnos / num_juegos
    print(f'Promedio en {num_juegos} juegos de {jugador.nombre} es {promedio_turnos} turnos.')
    return promedio_turnos

def main():
    # Lista de episodios para los diferentes archivos
    episodios = [10, 50, 100, 200, 500, 1000, 5000, 10000, 50000, 75000, 100000]

    # Número de juegos a jugar
    num_juegos = 1000  # Ajusta este valor según lo necesites

    # Listas para almacenar los resultados
    x_values = []
    y_values = []

    # Itera sobre la lista de episodios
    for episodio in episodios:
        nombre = f'agente_{episodio}eps'
        archivo = f'politica_{episodio}.csv'

        # Jugador Entrenado
        jugador_entrenado = JugadorEntrenado(nombre, archivo)
        promedio_entrenado = jugar_partidas(jugador_entrenado, num_juegos, verbose=False)

        # Guarda los valores para el plot
        x_values.append(episodio * 1000)  # Para representar la cantidad real de episodios
        y_values.append(promedio_entrenado)


    def jugar_y_obtener_promedios(jugadores, num_juegos=1000):
        promedios = {}
        
        for nombre, politica in jugadores:
            jugador_entrenado = JugadorEntrenado(nombre, politica)
            promedio = jugar_partidas(jugador_entrenado, num_juegos, verbose=False)
            promedios[nombre] = promedio
        
        return promedios

    # Lista de jugadores entrenados con sus correspondientes políticas
    jugadores_entrenados = [
        ('QLearn_50eps', 'politica_50.csv'),
        ('QLearn_100eps', 'politica_100.csv'),
        ('QLearn_1000eps', 'politica_1000.csv'),
        # ('QLearn_10000eps', 'politica_10000.csv'),
        # ('QLearn_100000eps', 'politica_100000.csv'),
        # ('QLearn_500.000eps', 'politica_500000.csv')
    ]

    # Ejecutar la función y obtener los promedios
    promedios = jugar_y_obtener_promedios(jugadores_entrenados, num_juegos=1000)


if __name__ == "__main__":
    # Llamar a la función principal con los argumentos proporcionados
    main()