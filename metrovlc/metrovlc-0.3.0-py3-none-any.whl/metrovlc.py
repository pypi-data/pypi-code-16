# -*- coding: utf-8 -*-

import re
import time
import urllib.request

from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from metrovlc import buildparser


def metrosaldo(bono):
    """ return saldo and zona from metrovalencia.es """

    titulo = None
    saldo = None

    urlapi = 'http://www.metrovalencia.es/tools_consulta_tsc.php?tsc='

    # try:
    url = '{_urlapi}{_bono}'.format(_urlapi=urlapi, _bono=bono)
    print(url)
    r = urllib.request.urlopen(url)
    enc = r.info().get_content_charset('utf-8')
    data = r.read()
    html = data.decode(enc)

    # tipo de titulo
    f = re.findall('Título: (.*)<br>', html)
    if f:
        titulo = f[0]

    # saldo
    f = re.findall('Saldo.*: (.*) <', html)
    if f:
        saldo = str(f[0]).replace('€', 'Euros')

    return titulo, saldo


def _id_estacion(estacion):
    """ recuperamos el id de una estación """

    # listado de estaciones (feo de cojones que esté en código)
    estaciones = [[121, 'Aeroport'],
                  [14, 'Alameda'],
                  [5, 'Albalat dels Sorells'],
                  [36, 'Alberic'],
                  [10, 'Alboraya-Palmaret'],
                  [9, 'Alboraya-Peris Aragó'],
                  [128, 'Alfauir'],
                  [43, 'Alginet'],
                  [8, 'Almàssera'],
                  [23, 'Amistat-Casa de Salud'],
                  [17, 'Àngel Guimerà'],
                  [24, 'Aragón'],
                  [42, 'Ausiàs March'],
                  [18, 'Av. del Cid'],
                  [22, 'Ayora'],
                  [109, 'Bailén'],
                  [107, 'Bétera'],
                  [69, 'Benaguasil 1r'],
                  [70, 'Benaguasil 2n'],
                  [97, 'Benicalap'],
                  [54, 'Beniferri'],
                  [12, 'Benimaclet'],
                  [57, 'Benimàmet'],
                  [40, 'Benimodo'],
                  [72, 'Burjassot'],
                  [73, 'Burjassot - Godella'],
                  [59, 'Campament'],
                  [53, 'Campanar'],
                  [103, 'Campus'],
                  [56, 'Canterería'],
                  [41, 'Carlet'],
                  [15, 'Colón'],
                  [50, 'Col·legi El Vedat'],
                  [83, 'Dr. Lluch'],
                  [108, 'El Clot'],
                  [55, 'Empalme'],
                  [65, 'Entrepins'],
                  [45, 'Espioca'],
                  [130, 'Estadi del Llevant'],
                  [81, 'Eugenia Viñes'],
                  [13, 'Facultats'],
                  [200, 'Faitanar'],
                  [106, 'Fira València'],
                  [99, 'Florista'],
                  [6, 'Foios'],
                  [44, 'Font Almaguer'],
                  [122, 'Francesc Cubells'],
                  [62, 'Fuente del Jarro'],
                  [98, 'Garbí'],
                  [74, 'Godella'],
                  [123, 'Grau - Canyamelar'],
                  [80, 'Horta Vella'],
                  [25, 'Jesús'],
                  [39, "L'Alcúdia"],
                  [67, "L'Eliana"],
                  [85, 'La Cadena'],
                  [63, 'La Canyada'],
                  [88, 'La Carrasca'],
                  [111, 'La Coma'],
                  [183, 'La Cova'],
                  [101, 'La Granja'],
                  [84, 'La Marina'],
                  [2, 'La Pobla de Farnals'],
                  [68, 'La Pobla de Vallbona'],
                  [184, 'La Presa'],
                  [64, 'La Vallesa'],
                  [82, 'Les Arenes'],
                  [58, 'Les Carolines/Fira'],
                  [114, 'Ll. Llarga - Terramelar'],
                  [71, 'Llíria'],
                  [11, 'Machado'],
                  [119, 'Manises'],
                  [115, 'Marítim - Serrería'],
                  [126, 'Marina Reial Joan Carles I'],
                  [95, 'Marxalenes'],
                  [110, 'Mas del Rosari'],
                  [185, 'Masia de Traver'],
                  [79, 'Masies'],
                  [37, 'Massalavés'],
                  [3, 'Massamagrell'],
                  [76, 'Massarrojos'],
                  [127, 'Mediterrani'],
                  [7, 'Meliana'],
                  [20, 'Mislata'],
                  [21, 'Mislata - Almassil'],
                  [77, 'Moncada - Alfara'],
                  [66, 'Montesol'],
                  [38, 'Montortal'],
                  [4, 'Museros'],
                  [19, "Nou d'Octubre"],
                  [46, 'Omet'],
                  [129, 'Orriols'],
                  [31, 'Paiporta'],
                  [100, 'Palau de Congressos'],
                  [60, 'Paterna'],
                  [26, 'Patraix'],
                  [32, 'Picanya'],
                  [47, 'Picassent'],
                  [51, 'Pl. Espanya'],
                  [92, 'Pont de Fusta'],
                  [91, 'Primado Reig'],
                  [117, 'Quart de Poblet'],
                  [1, 'Rafelbunyol'],
                  [49, 'Realón'],
                  [94, 'Reus'],
                  [186, 'Riba-roja de Túria'],
                  [75, 'Rocafort'],
                  [120, 'Rosas'],
                  [27, 'Safranar'],
                  [93, 'Sagunt'],
                  [118, "Salt de l'Aigua"],
                  [28, 'Sant Isidre'],
                  [102, 'Sant Joan'],
                  [131, 'Sant Miquel dels Reis'],
                  [48, 'Sant Ramón'],
                  [113, 'Santa Gemma - Parc Científic UV'],
                  [61, 'Santa Rita'],
                  [78, 'Seminari - CEU'],
                  [86, 'Serrería'],
                  [87, 'Tarongers'],
                  [52, 'Túria'],
                  [112, 'Tomás y Valiente'],
                  [201, 'Torre del Virrei'],
                  [33, 'Torrent'],
                  [34, 'Torrent Avinguda'],
                  [132, 'Tossal del Rei'],
                  [96, 'Trànsits'],
                  [105, 'TVV'],
                  [89, 'Universitat Politècnica'],
                  [30, 'València Sud'],
                  [104, 'Vicent Andrés Estellés'],
                  [90, 'Vicente Zaragozá'],
                  [35, 'Villanueva de Castellón'],
                  [16, 'Xàtiva']]

    for e in estaciones:
        if SequenceMatcher(None, e[1], estacion).ratio() > 0.65:
            return e[0]

    return None


# http://www.metrovalencia.es/horarios.php
# ?origen=14&hini=00%3A00&hfin=23%3A59
# &destino=24&fecha=30%2F09%2F2014&calcular=1
# def metrohorarios(origen, destino):
def metrohorarios(origen, destino, fecha=None, hini='00:00', hfin='23:59'):
    """ Obtiene los horarios desde origen a destino, luego ya veré como le
    meto la fecha """

    # verificamos tanto el origen como el destino
    origen_id = _id_estacion(origen)
    destino_id = _id_estacion(destino)

    # Si alguna de las dos es None, salimos
    if not origen_id or not destino_id:
        return None

    urlapi = 'http://www.metrovalencia.es/horarios.php'
    apiparam = '?origen=%s&hini=%s&hfin=%s&destino=%s&fecha=%s&calcular=1'

    # Recuperamos la fecha y hora de la consulta
    if not fecha:
        fecha = time.strftime('%d%%2F%m%%2F%Y')
    else:
        fecha = fecha.replace('/', '%2F')
    hini = hini.replace(':', '%3A')
    hfin = hfin.replace(':', '%3A')

    # completamos los parámetros
    param = apiparam % (origen_id, hini, hfin, destino_id, fecha)

    url = urlapi + param
    # print url

    # 1. Obtenemos los números asociados al origen y destino, ya que existe una
    # relacion entre un nombre de estación y un entero.
    #
    # IDEAS: Dos soluciones, a) tenemos en el script un diccionario que nos
    # devuelve a partir del nombre un entero. b) recuperamos de la web un
    # destino vacío para recuperar luego la relación de nombre-número.
    #
    # PERO: la segunda solución serían dos llamadas, y esto no mola, pero en la
    # primera opción, si hay una reordenación de los nombre-número entonces no
    # funcionará.
    #
    # ¿SOLUCIÓN?: Algo mixto, tener el diccionario, y cuando recuperamos la web
    # aseguramos que esté bien, en otro caso, con la información ya recuperada
    # podemos volver a llamar. En el mejor de los casos es una llamada, en el
    # peor son dos. Pero siempre devolvemos el dato correctamente.

    # 2. Recuperamos

    r = urllib.request.urlopen(url)
    enc = r.info().get_content_charset('utf-8')
    data = r.read()
    html = data.decode(enc)

    soup = BeautifulSoup(html, "html.parser")
    # print soup.body.find('div', attrs={'class': 'consulta'}).text
    consulta = soup.body.find('div', attrs={'class': 'consulta'})

    # guardamos aquí todos los cambios que queremos
    reemplazos = [['<td>', ''],
                  ['</td>', ' | '],
                  ['<tr>', ''],
                  ['</tr>', '\n'],
                  ['---', '-----'],
                  ['</li>', '\n'],
                  ['Trenes con destino', ', Trenes con destino'],
                  ['Hora de salida', ', Hora de salida\n'],
                  ['Imprimir la consulta', ''],
                  ['Paso ', '\nPaso '],
                  ['td>', ' | ']]

    for reemplazo in reemplazos:
        consulta = str(consulta).replace(reemplazo[0], reemplazo[1])

    text = BeautifulSoup(consulta, "html.parser").get_text()

    return text


def main():

    """Run the command-line interface."""
    parser = buildparser.build_parser()
    options = parser.parse_args()

    if options.bono:
        # Para metrovalencia, únicamente son importantes los 10 primeros
        # dígitos, cosa bastante marciana
        bono = options.bono[0:10]
        titulo, saldo = metrosaldo(bono)
        if options.solosaldo:
            print('{}'.format(saldo.split()[0]))
        else:
            print('Bono:{}, Título:{}, saldo:{}'.format(bono, titulo, saldo))

    if options.horario:
        origen = options.horario[0]
        destino = options.horario[1]
        horarios = metrohorarios(origen, destino)
        if horarios:
            print(horarios)
        else:
            print('No encuentro horarios: {} -> {}'.format(origen, destino))


if __name__ == '__main__':
    main()
