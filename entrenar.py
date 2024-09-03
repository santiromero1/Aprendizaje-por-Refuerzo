import argparse
from modelo_agente import AmbienteDiezMil, AgenteQLearning, EstadoDiezMil

def main(episodios, verbose):
    # Crear una instancia del ambiente
    ambiente = AmbienteDiezMil()
    estado = EstadoDiezMil

    # Crear un agente de Q-learning
    agente = AgenteQLearning(ambiente)

    # Entrenar al agente con un número de episodios
    agente.entrenar(episodios, verbose=verbose)
    agente.guardar_politica(f"politica_{episodios}.csv")


if __name__ == '__main__':
    # Crear un analizador de argumentos
    parser = argparse.ArgumentParser(description="Entrenar un agente usando Q-learning en el ambiente de 'Diez Mil'.")
    episodios = [10, 50, 100, 200, 500, 1000, 5000, 10000, 50000, 75000, 100000]
    for episodio in episodios:
        # Agregar argumentos
        # parser.add_argument('-e', '--episodios', type=int, default=1000, help='Número de episodios para entrenar al agente (default: 10000)')
        # parser.add_argument('-v', '--verbose', action='store_true', help='Activar modo verbose para ver más detalles durante el entrenamiento')

        # # Parsear los argumentos
        # args = parser.parse_args()

        # # Llamar a la función principal con los argumentos proporcionados
        main(episodio, False)
