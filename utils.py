PUNTAJE_ESCALERA: int = 3000
PUNTAJE_3_PARES: int = 1500
PUNTAJE_6_IGUALES: int = 10000

JUGADA_PLANTARSE: int = 0
JUGADA_TIRAR: int = 1

JUGADAS_STR = {
    JUGADA_PLANTARSE: "Plantarse",
    JUGADA_TIRAR: "Tirar",
}

def puntaje_y_no_usados(ds: list[int]) -> tuple[int, list[int]]:
    ''' Dada ds, una lista de enteros del 1 al 6 (dados), devuelve una tupla
        con el puntaje de los dados y los dados no usados (en orden).
        Precondición: len(ds)>0
        Ejemplo: para [2,1,3,1,4,5], devuelve (250, [2,3,4]) porque 100+100+50
        y no se usaron los dados 2, 3, 4.
    '''
    # Dejo en cants las veces que salió cada número.
    cants: dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    for d in ds:
        cants[d] += 1

    if len(ds) == 6:  # Puntajes validos solo cuando se tiran los 6 dados.
        cants_aux: list[int] = sorted(list(cants.values()))
        if cants_aux == [1, 1, 1, 1, 1, 1]:
            return (PUNTAJE_ESCALERA, [])
        elif cants_aux == [0, 0, 0, 2, 2, 2] or cants_aux == [0, 0, 0, 0, 2, 4]:
            return (PUNTAJE_3_PARES, [])
        elif cants_aux == [0, 0, 0, 0, 0, 6]:
            return (PUNTAJE_6_IGUALES, [])

    # Cálculo general del puntaje:
    puntaje: int = 0
    if cants[1] >= 3:
        puntaje += 1000
        cants[1] -= 3
    for d in [2, 3, 4, 5, 6]:
        if cants[d] >= 3:
            puntaje += d * 100
            cants[d] -= 3
    puntaje += cants[1] * 100
    cants[1] = 0
    puntaje += cants[5] * 50
    cants[5] = 0
    no_usados: list[int] = []
    for dado, cantidad in cants.items():
        no_usados += [dado] * cantidad
    return (puntaje, sorted(no_usados))


def separar(xs: list[int], ys: list[int]) -> list[int]:
    ''' Devuelve la lista resultante de eliminar la primera instancia en xs 
        de cada elemento de ys.
        Precondición: ys está incluido en xs.
        Ejemplo: separar([3,2,4,2,1,2,3,2], [2,3,2]) --> [4,1,2,3,2]
    '''
    res: list[int] = list(xs)
    for y in ys:
        res.remove(y)
    return res
