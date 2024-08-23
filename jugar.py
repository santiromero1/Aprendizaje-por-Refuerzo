import argparse
from diezmil import JuegoDiezMil
from template import JugadorEntrenado

def main(politica_filename, verbose):
    jugador = JugadorEntrenado('qlearning', politica_filename)
    juego = JuegoDiezMil(jugador)
    cantidad_turnos, puntaje_final = juego.jugar(verbose=verbose)

    print(f"Cantidad de turnos: {cantidad_turnos}")
    print(f"Puntaje final: {puntaje_final}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Jugar una partida de 'Diez Mil' con un agente entrenado usando una política predefinida.")

    # Agregar argumentos
    parser.add_argument('-f', '--politica_filename', type=str, help='Archivo con la política entrenada')
    parser.add_argument('-v', '--verbose', action='store_true', help='Activar modo verbose para ver más detalles durante el juego')

    # Parsear los argumentos
    args = parser.parse_args()

    # Llamar a la función principal con los argumentos proporcionados
    main(args.politica_filename, args.verbose)
