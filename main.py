import random
from pymongo import MongoClient
from utils import menus, utils

def main() -> None:
    # A. Mostrar mensaje de bienvenida: “Cardo ”
    menus.muestra_mensaje_bienvenida()
    

    # B. Preguntar por el nombre/alias del Jugador 1.
    jugador_1 = input('Introduzca el nombre del jugador 1 -> ')

    # C. Preguntar por el nombre/alias del Jugador 2.
    jugador_2 = input('Introduzca el nombre del jugador 2 -> ')

    jugadores = [jugador_1, jugador_2]

    # D. Preguntar por el número de rondas (máximo 10, mínimo 3). En caso de recibir un
    # número inválido, iniciar el juego con 5 rondas.
    rondas = int(input('¿Cuántas rondas desean jugar? -> '))
    if not 3 <= rondas <= 10:
        rondas = 5

    # E. Se registra el documento de la partida en base de datos.
    # Conexión a MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["cardo"]
    partidas_col = db["partidas"]
    partida = {
        "jugadores": {"jugador1": jugador_1, "jugador2": jugador_2},
        "configuracion": {"rondas_totales": rondas},
        "rondas": [],
        "resultado_final": {},
    }
    print('registrando documento de partida...')
    partida_id = partidas_col.insert_one(partida).inserted_id
    print(f"Partida registrada con id: {partida_id}")

    # F. Limpiar consola.
    utils.limpia_consola()

    
    # G. Elegir al “cardoelector”
    idx_cardoelector = random.randint(0,1)
    cardoelector = jugadores[idx_cardoelector]
    cardomante = cardoelector

    puntajes = {jugador_1: {"cartas_adivinadas": [], "cartas_no_adivinadas": [], "total": 0},
                jugador_2: {"cartas_adivinadas": [], "cartas_no_adivinadas": [], "total": 0}}


    for ronda_num in range(1, rondas + 1):
        # Obtener 3 cartas aleatorias de colecciones distintas
        cartas = []
        colecciones = ["situaciones", "objetos", "emociones", "lugares"]
        elegidas_cats = random.sample(colecciones, 3)
        for cat in elegidas_cats:
            carta = db[cat].aggregate([{"$sample": {"size": 1}}]).next()
            cartas.append({"categoria": cat, "descripcion": carta["descripcion"], "carta_id": carta["_id"], "puntaje": carta["puntaje"]})

        # y mostrar: Hora de elegir...
        # H. Esperar la elección del “cardoelector” y borrar la información de la consola.
        carta_cardoelector = menus.muestra_menu_eleccion_cardoelector(cardoelector, cartas)
        utils.limpia_consola()

        # I. Elegir al “cardomante” y mostrar: Hora de adivinar ...
        
        if ronda_num == 1 and cardomante == cardoelector:
            cardomante = jugadores[0 if idx_cardoelector == 1 else 1]
        # J. Esperar la elección del “cardomante” y borrar la información de la consola.
        carta_cardomante = menus.muestra_menu_eleccion_cardomante(cardomante, cartas)
        utils.limpia_consola()

        # K. El sistema actualiza el registro de la partida agregando la información de la ronda
        cat_elector = next(c["categoria"] for c in cartas if c["descripcion"] == carta_cardoelector["descripcion"])
        carta_info = db[cat_elector].find_one({"_id": carta_cardoelector["carta_id"]})
        puntaje_carta = carta_info["puntaje"]

        if carta_cardomante == carta_cardoelector:
            puntos = puntaje_carta - 1 if puntaje_carta > 1 else 1
            puntajes[cardomante]["cartas_adivinadas"].append(carta_cardoelector)
            puntajes[cardomante]["total"] += puntos
        else:
            puntos = puntaje_carta
            puntajes[cardoelector]["cartas_no_adivinadas"].append(carta_cardoelector)
            puntajes[cardoelector]["total"] += puntos

        # Guardar info de la ronda en la partida
        ronda_doc = {
            "numero": ronda_num,
            "cardoelector": cardoelector,
            "cardomante": cardomante,
            "cartas_mostradas": cartas,
            "carta_elegida": carta_cardoelector,
            "carta_adivinada": carta_cardomante,
        }
        partidas_col.update_one({"_id": partida_id}, {"$push": {"rondas": ronda_doc}})

        print('actualizando documento con información de la ronda')

        # L. Alternar los roles para la siguiente ronda.
        cardoelector, cardomante = utils.alterna_roles_jugadores(jugadores, cardoelector)

    # M. Al finalizar la última ronda, el sistema actualiza el registro de la partida agregando
    # el ganador y muestra en la consola el resultado final:
    if puntajes[jugador_1]["total"] > puntajes[jugador_2]["total"]:
        ganador = jugador_1
    elif puntajes[jugador_2]["total"] > puntajes[jugador_1]["total"]:
        ganador = jugador_2
    else:
        ganador = "Empate"

    resultado_final = {"ganador": ganador, "puntajes": puntajes}
    partidas_col.update_one({"_id": partida_id}, {"$set": {"resultado_final": resultado_final}})

    # Recuperar partida completa desde MongoDB
    partida_actualizada = partidas_col.find_one({"_id": partida_id})

    # Mostrar en consola con función optimizada
    menus.muestra_resultado_final_optimizado(partida_actualizada, mongo_uri="mongodb://localhost:27017/", db_name="cardo")

    client.close()


if __name__ == '__main__':
    main()