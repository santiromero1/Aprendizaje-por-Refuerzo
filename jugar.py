import argparse
from diezmil import JuegoDiezMil
from jugador import Jugador, JugadorAleatorio, JugadorSiempreSePlanta
from modelo_agente import JugadorEntrenado


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
    num_juegos = 10000

    # Jugador Aleatorio
    jugador_random = JugadorAleatorio('random')
    promedio_random = jugar_partidas(jugador_random, num_juegos, verbose=False)

    # Jugador que Siempre se Planta
    jugador_planton = JugadorSiempreSePlanta('planton')
    promedio_planton = jugar_partidas(jugador_planton, num_juegos, verbose=False)

    # Jugador Entrenado
    jugador_entrenado = JugadorEntrenado('QLearn_100.000eps', 'politica_100000.csv')
    promedio_entrenado = jugar_partidas(jugador_entrenado, num_juegos, verbose=False)

    # Jugador Entrenado
    jugador_entrenado = JugadorEntrenado('QLearn_10.000eps', 'politica_10000.csv')
    promedio_entrenado = jugar_partidas(jugador_entrenado, num_juegos, verbose=False)

    # # Imprimir resultados finales
    # print(f'Promedio de turnos para {num_juegos} juegos:')
    # print(f'{jugador_random.nombre}: {promedio_random}')
    # print(f'{jugador_planton.nombre}: {promedio_planton}')
    # print(f'{jugador_entrenado.nombre}: {promedio_entrenado}')

if __name__ == "__main__":
    # Llamar a la función principal con los argumentos proporcionados
    main()

    # parser = argparse.ArgumentParser(description="Jugar una partida de 'Diez Mil' con un agente entrenado usando una política predefinida.")

    # # Agregar argumentos
    # parser.add_argument('-f', '--politica_filename', type=str, help='Archivo con la política entrenada')
    # parser.add_argument('-v', '--verbose', action='store_true', help='Activar modo verbose para ver más detalles durante el juego')

    # # Parsear los argumentos
    # args = parser.parse_args()

