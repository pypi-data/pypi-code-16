import time
import sys


drawhomero = '''
                                       +--------+
                                      /        /|
                                     /        / |
                                    +--------+  |
                                    |        |  |
                                    |        |  +
                                    |        | /
                                    |        |/
                                    +--------+
                             +
                           +
                         +
                       +
               ,---. 
            ,.'-.   \ 
           ( ( ,'"""""-. 
           `,X          `. 
           /` `           `._ 
          (            ,   ,_\ 
          |          ,---.,'o `. 
          |         / o   \     ) 
           \ ,.    (      .____, 
            \| \    \____,'     \ 
          '`'\  \        _,____,' 
          \  ,--      ,-'     \ 
            ( C     ,'         \ 
             `--'  .'           | 
               |   |         .O | 
             __|    \        ,-'_ 
            / `L     `._  _,'  ' `. 
           /    `--.._  `',.   _\  ` 
           `-.       /\  | `. ( ,\  \ 
          _/  `-._  /  \ |--'  (     \ 
         '  `-.   `'    \/\`.   `.    ) 
               \  -hrr-    \ `.  |    | 



'''

drawpizza = '''
                     )   (    )
                  (    ___  (
                    _.'   `._  )
                _(_____________)___
                pizza dough
'''

drawplay = '''



               _=====_                               _=====_
              / _____ \                             / _____ \
            +.-'_____'-.---------------------------.-'_____'-.+
           /   |     |  '.        S O N Y        .'  |  _  |   \\
          / ___| /|\ |___ \                     / ___| /_\ |___ \\
         / |      |      | ;  __           _   ; | _         _ | ;
         | | <---   ---> | | |__|         |_:> | ||_|       (_)| |
         | |___   |   ___| ;SELECT       START ; |___       ___| ;
         |\    | \|/ |    /  _     ___      _   \    | (X) |    /|
         | \   |_____|  .','" "', |___|  ,'" "', '.  |_____|  .' |
         |  '-.______.-' /       \ANALOG/       \  '-._____.-'   |
         |               |       |------|       |                |
         |              /\       /      \       /\               |
         |             /  '.___.'        '.___.'  \              |
         |            /                            \             |
          \          /                              \           /
           \________/                                \_________/




PUTA BIDA es imposible que salga bien este mando ... :/
'''

drawchao = '''
Un abrazo muy grande.

Also bis bald!
'''
history = [('parra', 'En parte la eleccion de entrar a SWS fue por la entrevista que tuvimos, en ese momento me diste muy buen rollo y por supuesto esa idea acabo siendo cierta. \nNo pude acertar mas!!! Y aqui empece un gran camino, que me ha hecho crecer muchisimo como persona, como trabajador y lo que mas, como informatico, y por supuesto muchisima culpa es tuya.'), ('parra', '\n'), ('time', 15.0), ('parra', 'Los comienzos fueron muy buenos, ese horario de becario no se me olvidara en la vida XD, pero a la par fueron un poco duros:'), ('parra', '\n'), ('time', 4.0), ('parra', drawhomero), ('time', 4.0), ('parra', 'maldito cubo!!! XD. Pero contigo siempre para echar un cable (y mariete que tambien ayudo mucho ), todo se veia de otra manera. '), ('parra', '\n'), ('time', 6.0), ('parra', 'Tampoco olvidare nunca los dias esos, (por suerte pocos XD) que nos toco quedarnos comiendo pizzas en la oficina '), ('time', 6.0), ('parra', drawpizza), ('time', 6.0), ('parra', 'Gracias a uno de esos dias de comer pizza me diste otro libre "para comprarme la play"'), ('parra', '\n'), ('time', 6.0), ('parra', drawplay), ('time', 6.0), ('parra', 'y casi no le hemos dedicado horas eeee XD.'), ('parra', '\n'), ('time', 4.0), ('parra', 'En fin .... , eres una persona de las que deja huella pet!! Me quedo con muchos recuerdos y muy buenos.  Se que todo te ira genial, espero que cuando vuelvas podamos vernos y echarnos unas cervezas. '), ('time', 6.0), ('parra', drawchao), ('time', 6.0)]


## Funcion que no se utiliza
def print_slow(parrafo):
    for letter in parrafo:
        sys.stdout.write(letter)
        time.sleep(.1)


def run():
    for moment in history:
        if moment[0] == 'parra':
            print(moment[1])
        elif moment[0] == 'time':
            time.sleep(moment[1])
    time.sleep(5)

run()
