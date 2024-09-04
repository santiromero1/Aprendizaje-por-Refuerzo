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
    episodios = [1000,10000,50000,75000,100000,500000] #, 50000, 100000
    for episodio in episodios:
        main(episodio, False)
