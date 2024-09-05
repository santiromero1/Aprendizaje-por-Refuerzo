import argparse
from modelo_agente import AgenteQLearning, DiezMil

def main(episodios, verbose):
    # Crear una instancia del ambiente
    # Crear un agente de Q-learning
    agente = AgenteQLearning()
    # Entrenar al agente con un número de episodios
    agente.entrenar(episodios, verbose=verbose)
    agente.guardar_politica(f"politica_{episodios}.csv")


if __name__ == '__main__':
    # Crear un analizador de argumentos
    parser = argparse.ArgumentParser(description="Entrenar un agente usando Q-learning en el ambiente de 'Diez Mil'.")
    episodios = [10,100,500,1000,5000,10000,25000,50000,75000,100000,150000,175000,250000,500000,1000000] 
    for episodio in episodios:
        main(episodio, False)
0