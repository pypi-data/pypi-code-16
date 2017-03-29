# - *- coding: utf- 8 - *-
def run():
    import sys
    import traceback 


    list_question_response = [
        ('Examen de aleman!! Introduce las respuestas despues de cada mensaje y pulsa INTRO!', '', '', ''),
        ('Moneda de Alemania antes del Euro', 'Marco', 'No, en castellano no, en Aleman :)', 'No, en castellano no, en Aleman :)'),
        ('', 'Rahmen', 'Correcto aunque esa palabra no se si selvirá para mucho', 'No es correcto, es rahmen, pero vamos que tampoco te servira de mucho'),
        ('Palabra más dificil de pronunciar en alemán (ardilla)', 'herrschst ', 'HERRSCHST, (un audio al grupo para ver como suena)', 'HERRSCHST, un audio al grupo para ver como suena'),
        ('En alemania en un coche cual es la rueda que menos vueltas da en una curva', 'repuesto', 'Esa era chunga','Esa era chunga'),
        ('Bueno, la última¿ Que significa Omelett?', 'Tortilla de papas','Correcto','No es correcto, significa Tortilla de papas')
    ]

    mensaje =' *****  Muchas gracias por todo los ratos que hemos pasado, por toda la paciencia que has tenido y por todo lo que me has ensenado. Te deseo lo mejor un abrazo muy fuerte****. \n'

    try:
        for i in range(0, len(list_question_response)):
            print list_question_response[i][0]
            response = raw_input()

            print response

            if list_question_response[i][1].lower() == response.lower():
                print list_question_response[i][2]
            else:
                print list_question_response[i][3]

            print '\n'

    except:
        print 'ERROR: Ya has pulsado alguna tecla de esas chungas del aleman y lo has roto'

    print mensaje

run()