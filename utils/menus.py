from . import utils
from pymongo import MongoClient
from bson import ObjectId

def muestra_mensaje_bienvenida() -> None:
    # A. Mostrar mensaje de bienvenida: “Cardo ”
    print('°------------°')
    print('|            |')
    print('|  Cardo 🃏  |')
    print('|            |')
    print('°------------°')

def muestra_menu_eleccion_cardoelector(jugador, cartas):

    d1, d2, d3, p1, p2, p3 = utils.destructura_cartas(cartas)

    print(f"Hora de elegir {jugador}")
    print("-" * 70)
    print(f"{'1)':<4} {d1:<50} ({p1})")
    print(f"{'2)':<4} {d2:<50} ({p2})")
    print(f"{'3)':<4} {d3:<50} ({p3})")
    print("-" * 70)
    idx_carta = int(input(' -> ')) - 1
    return cartas[idx_carta]

def muestra_menu_eleccion_cardomante(jugador, cartas):

    d1, d2, d3, p1, p2, p3 = utils.destructura_cartas(cartas)

    print(f"Hora de adivinar {jugador}")
    print("-" * 70)
    print(f"{'1)':<4} {d1:<50} ({p1})")
    print(f"{'2)':<4} {d2:<50} ({p2})")
    print(f"{'3)':<4} {d3:<50} ({p3})")
    print("-" * 70)
    idx_carta = int(input(' -> ')) - 1
    return cartas[idx_carta]

def muestra_resultado_final_optimizado(partida, mongo_uri="mongodb://localhost:27017/", db_name="cardo"):
    """
    Muestra el resultado final de la partida, resolviendo las cartas directamente desde MongoDB de forma optimizada.
    
    :param partida: diccionario con la estructura de la partida
    :param mongo_uri: URI de conexión a MongoDB
    :param db_name: nombre de la base de datos
    """
    client = MongoClient(mongo_uri)
    db = client[db_name]

    ganador = partida["resultado_final"]["ganador"]
    puntajes = partida["resultado_final"]["puntajes"]
    
    print(f"\n¡Gana {ganador}!\n")
    
    # Reunir todos los ObjectId de cartas de la partida
    all_ids = set()
    for info in puntajes.values():
        all_ids.update(info.get("cartas_adivinadas", []))
        all_ids.update(info.get("cartas_no_adivinadas", []))
    
    # Crear un diccionario de lookup: {ObjectId: "descripcion (puntaje)"}
    cartas_lookup = {}
    for coleccion in ["situaciones", "objetos", "emociones", "lugares"]:
        cursor = db[coleccion].find({"_id": {"$in": list(all_ids)}})
        for carta in cursor:
            cartas_lookup[carta["_id"]] = f"{carta['descripcion']} ({carta['puntaje']})"
    
    # Mostrar resultados
    for jugador, info in puntajes.items():
        print(f"Puntos como “cardomante” de {jugador}:")
        if info.get("cartas_adivinadas"):
            for cid in info["cartas_adivinadas"]:
                print(f"  - {cartas_lookup.get(cid, 'Carta no encontrada')}")
        else:
            print("  - Ninguna")
        
        print(f"Puntos como “cardoelector” de {jugador}:")
        if info.get("cartas_no_adivinadas"):
            for cid in info["cartas_no_adivinadas"]:
                print(f"  - {cartas_lookup.get(cid, 'Carta no encontrada')}")
        else:
            print("  - Ninguna")
        
        print(f"Total de puntos: {info['total']}\n")

    client.close()


# cartas = [
#     {"descripcion": "Un niño volando una cometa", "puntaje": 1},
#     {"descripcion": "Un observatorio marino", "puntaje": 2},
#     {"descripcion": "Alivio tras un peligro", "puntaje": 3}
# ]

# muestra_menu_eleccion_cardoelector('helios', cartas)

def muestra_resultado_final_optimizado(partida, mongo_uri="mongodb://localhost:27017/", db_name="cardo"):

    client = MongoClient(mongo_uri)
    db = client[db_name]

    ganador = partida["resultado_final"]["ganador"]
    puntajes = partida["resultado_final"]["puntajes"]
    
    print(f"\n¡Gana {ganador}!\n")
    
    for jugador, info in puntajes.items():
        print(f"Puntos como “cardomante” de {jugador}:")
        if info.get("cartas_adivinadas"):
            for carta in info["cartas_adivinadas"]:
                print(f"  - {carta['descripcion']} ({carta['puntaje']})")
        else:
            print("  - Ninguna")
        
        print(f"Puntos como “cardoelector” de {jugador}:")
        if info.get("cartas_no_adivinadas"):
            for carta in info["cartas_no_adivinadas"]:
                print(f"  - {carta['descripcion']} ({carta['puntaje']})")
        else:
            print("  - Ninguna")
        
        print(f"Total de puntos: {info['total']}\n")

    client.close()
