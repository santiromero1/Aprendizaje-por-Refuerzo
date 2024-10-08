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
    episodios = [10,100,1000,5000,10000,25000,75000,100000,150000,250000] 

    # Número de juegos a jugar
    num_juegos = 10000  # Ajusta este valor según lo necesites

    # Listas para almacenar los resultados
    x_values = []
    y_values = []

    # Itera sobre la lista de episodios
    for episodio in episodios:
        nombre = f'agente_{episodio}eps'
        archivo = f'./22_definitivo/politica_{episodio}.csv'

        # Jugador Entrenado
        jugador_entrenado = JugadorEntrenado(nombre, archivo)
        promedio_entrenado = jugar_partidas(jugador_entrenado, num_juegos, verbose=False)

        # Guarda los valores para el plot
        x_values.append(episodio)  # Para representar la cantidad real de episodios
        y_values.append(promedio_entrenado)
    
    aux_cant_turnos_planton = 0
    aux_cant_turnos_random = 0
    for jueguito in range(num_juegos):
        
        jugador = JugadorSiempreSePlanta("palton")
        juego = JuegoDiezMil(jugador)
        cantidad_turnos, _ = juego.jugar(verbose=False)
        aux_cant_turnos_planton += cantidad_turnos

        jugador = JugadorAleatorio("random")
        juego = JuegoDiezMil(jugador)
        cantidad_turnos, _ = juego.jugar(verbose=False)
        aux_cant_turnos_random += cantidad_turnos
    
    promedio_planton = aux_cant_turnos_planton / num_juegos
    promedio_random = aux_cant_turnos_random / num_juegos
    
    print(f'Promedio en {num_juegos} juegos de JugadorSiempreSePlanta es {promedio_planton} turnos.')
    print(f'Promedio en {num_juegos} juegos de JugadorAleatorio es {promedio_random} turnos.')



    # Crear el plot
    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values, marker='o', linestyle='-', color='b', label='Promedio de turnos por episodio')

    # Mostrar exactamente los valores en el eje X
    plt.xticks(x_values, rotation=90)

    # Añadir etiquetas sobre cada punto con el valor del promedio
    for x, y in zip(x_values, y_values):
        plt.text(x, y+0.02, f'{y:.2f}', fontsize=10, ha='center', va='bottom')
    
    # Añadir líneas horizontales para el promedio del JugadorSiempreSePlanta y JugadorAleatorio
    plt.axhline(y=promedio_planton, color='green', linestyle='-', linewidth=1, label='Promedio SiempreSePlanta')
    plt.axhline(y=promedio_random, color='red', linestyle='-', linewidth=1, label='Promedio Aleatorio')

    # Configuración del gráfico
    plt.xlabel('Número de episodios')
    plt.ylabel('Promedio de turnos para ganar en 10.000 juegos')
    plt.title('Rendimiento del Agente Q-Learning en el juego 10 Mil')
    plt.legend()
    plt.grid(False)

    # Mostrar el gráfico
    plt.show()

if __name__ == "__main__":
    # Llamar a la función principal
    main()
