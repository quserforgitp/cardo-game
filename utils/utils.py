import os

def limpia_consola() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')

def destructura_cartas(cartas):
    descripciones = [carta["descripcion"] for carta in cartas]
    puntajes = [carta["puntaje"] for carta in cartas]
    d1, d2, d3 = descripciones
    p1, p2, p3 = puntajes
    return d1, d2, d3, p1, p2, p3

def alterna_roles_jugadores(jugadores, cardoelector):

    idx_cardoelector = jugadores.index(cardoelector)

    cardomante = jugadores[idx_cardoelector]
    cardoelector = jugadores[0 if idx_cardoelector == 1 else 1]

    return cardoelector, cardomante