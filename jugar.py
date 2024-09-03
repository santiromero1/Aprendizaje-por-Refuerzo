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

    # Plotear los resultados
    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values, marker='o', linestyle='-', color='b')

    # Configurar etiquetas y título
    plt.xlabel('Cantidad de Episodios')
    plt.ylabel('Promedio de Turnos')
    plt.title('Relación entre Cantidad de Episodios y Promedio de Turnos')
    plt.grid(True)

    # Mostrar el gráfico
    plt.show()

if __name__ == "__main__":
    # Llamar a la función principal con los argumentos proporcionados
    main()

    # parser = argparse.ArgumentParser(description="Jugar una partida de 'Diez Mil' con un agente entrenado usando una política predefinida.")

    # # Agregar argumentos
    # parser.add_argument('-f', '--politica_filename', type=str, help='Archivo con la política entrenada')
    # parser.add_argument('-v', '--verbose', action='store_true', help='Activar modo verbose para ver más detalles durante el juego')

    # # Parsear los argumentos
    # args = parser.parse_args()

