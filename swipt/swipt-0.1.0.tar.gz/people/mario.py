import copy
import os
import random
import time
import struct
import sys


class MediaPrinter(object):

    def center_text(self, fix=0, clear_screen=True):
        if clear_screen:
            self.clear_screen()
        for i in range(self._get_terminal_size_linux()[1]/2-5+fix):
            print('')

    def clear_screen(self):
        os.system('clear')

    def _get_terminal_size_linux(self):  # AKA: funcion patilla que acabo de encontrar en internet
        def ioctl_GWINSZ(fd):
            try:
                import fcntl
                import termios
                cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
                return cr
            except:
                pass
        cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
        if not cr:
            try:
                fd = os.open(os.ctermid(), os.O_RDONLY)
                cr = ioctl_GWINSZ(fd)
                os.close(fd)
            except:
                pass
        if not cr:
            try:
                cr = (os.environ['LINES'], os.environ['COLUMNS'])
            except:
                return None
        return int(cr[1]), int(cr[0])

    def print_warning(self):
        warning = '''
         _       _____    ____  _   _______   ________
        | |     / /   |  / __ \/ | / /  _/ | / / ____/
        | | /| / / /| | / /_/ /  |/ // //  |/ / / __
        | |/ |/ / ___ |/ _, _/ /|  // // /|  / /_/ /
        |__/|__/_/  |_/_/ |_/_/ |_/___/_/ |_/\____/
        '''
        self.center_text()
        print(warning)
        print('\tDon\'t touch your keyboard during this script (o "Muerte Por Kiki" vendra a por ti..)')

    def print_msg(self):
        msg_ascii = '''
        _|      _|    _|_|        _|_|_|_|_|  _|_|_|_|      _|      _|    _|_|      _|_|_|        _|_|
        _|_|    _|  _|    _|          _|      _|            _|      _|  _|    _|  _|            _|    _|
        _|  _|  _|  _|    _|          _|      _|_|_|        _|      _|  _|_|_|_|    _|_|        _|_|_|_|
        _|    _|_|  _|    _|          _|      _|              _|  _|    _|    _|        _|      _|    _|
        _|      _|    _|_|            _|      _|_|_|_|          _|      _|    _|  _|_|_|        _|    _|


                                                                                                                      _|
        _|        _|_|_|  _|_|_|    _|_|_|      _|_|    _|_|_|        _|_|_|    _|_|_|_|      _|      _|  _|            _|
        _|          _|    _|    _|  _|    _|  _|    _|  _|    _|      _|    _|  _|            _|_|  _|_|          _|    _|
        _|          _|    _|_|_|    _|_|_|    _|_|_|_|  _|_|_|        _|    _|  _|_|_|        _|  _|  _|  _|            _|
        _|          _|    _|    _|  _|    _|  _|    _|  _|    _|      _|    _|  _|            _|      _|  _|            _|
        _|_|_|_|  _|_|_|  _|_|_|    _|    _|  _|    _|  _|    _|      _|_|_|    _|_|_|_|      _|      _|  _|      _|    _|
                                                                                                                      _|
        '''
        self.center_text()
        hours = ['coding', 'futbol (aunque no muchas)', 'pizzas', 'birras', 'burgers', 'play', 'AMISTAD']
        print 'Muchisimas gracias por las horas de trabajo'
        for i, j in enumerate(hours):
            if i != len(hours)-1:
                time.sleep(3)
            else:
                time.sleep(random.random())
            spaces = random.randint(10, 40)
            print('{0}{1}'.format(' '*spaces, j))
        time.sleep(3)
        print('\nPero esto no acaba aqui, seguimos en contacto.')
        time.sleep(5)
        self.center_text()
        print(msg_ascii)
        time.sleep(4)

    def print_europe(self):
        def print_europe_array(europe_map, legend=''):
            center_adjustment = -8
            self.center_text(center_adjustment)
            for line in europe_map:
                for column in line:
                    sys.stdout.write(column)
                    sys.stdout.flush()
                print('')
            for i, l in enumerate(legend):
                if i == len(legend)-1:
                    print('\033[0;93;4m')
                    print(l)
                    print('\033[0m')
                else:
                    print(l)

        def add_point(map, direction, symbol):
            map[direction[1]][direction[0]] = symbol

        def remove_point(map, direction):
            map[direction[1]][direction[0]] = ' '

        europe_ascii = '''
                                -.            .      .-.
                         '       /      / ./
                  _  __,     .--'      / <
                 ~_-~ /     <         <   \_ .-~7
               _. \   >      \.-'\     >`   ~ .-~
              <  ><  /         ,  7   <      ~7
              /_/  ! \       .-L  \  _//   <'~
              ~  .-~  !      ! /o& `' .     7
                 _>_._ >  _.-' '-._.-._.--./
                '-~   ~._/                               .
                  ,-.-'                                  .
                 <                                       .
                  \                                      .
                   7                                ..   .
                   !       _.-.     ..             <  ~v~
            .-~---'   .-.-~    ~\  <  \            /
            )         >      o  <   >  \           \_.--._
           /       .-'      <>   \  \   7       .  '
           7       > . - '        > _\  !   _,-' `.
           ~--,.--'           ._ /.- ~` <   \ .   \\
                              7/ ~       \.,< .  ` `-~-.-~
                                            __  .`


        '''
        madrid = [15, 18]
        berlin = [32, 11]
        europe_map = [[]]
        for e in europe_ascii:
            if e == '\n':
                europe_map.append([])
            else:
                europe_map[-1].append(e)

        legend = []
        legend.append('Europe, Today (hopefully)')
        print_europe_array(europe_map, legend)
        time.sleep(5)
        add_point(europe_map, madrid, 'X')
        legend.append('X - Madrid')
        print_europe_array(europe_map, legend)
        time.sleep(4)
        add_point(europe_map, berlin, '#')
        legend.append('# - Berlin (aprox.. ASCII art sucks!)')
        print_europe_array(europe_map, legend)
        time.sleep(5)
        mario = copy.deepcopy(madrid)
        add_point(europe_map, mario, 'M')
        legend.append('M - It\'s a me! Mario!')
        print_europe_array(europe_map, legend)
        time.sleep(5)
        origin_reshown = False
        while mario != berlin:
            distances = [0, 0]
            for i in range(len(mario)):
                remove_point(europe_map, mario)
                if mario[i] != berlin[i]:
                    mario[i] += 1 if mario[i] < berlin[i] else -1
                    distances[i] = abs(berlin[i] - mario[i])
            try:
                max_axis_distance = (max(distances)/min(distances))
                if max_axis_distance > 2:
                    if distances[0] > distances[1]:
                        axis_to_overincr = 0
                    else:
                        axis_to_overincr = 1
                    mario[axis_to_overincr] += max_axis_distance-1
            except ZeroDivisionError:
                pass
            add_point(europe_map, mario, 'M')
            if not origin_reshown:
                add_point(europe_map, madrid, 'X')
            print_europe_array(europe_map, legend)
            time.sleep(1)
        time.sleep(1)
        legend.append('\nMario: Took me a couple hours!!! Looks like it wasn\'t that far!!! ^^U')
        print_europe_array(europe_map, legend)
        time.sleep(5)
        legend.append('')
        print_europe_array(europe_map, legend)
        print('\033[0;93;4m')
        sys.stdout.write('Pedro: Willkommen Mario')
        sys.stdout.flush()
        time.sleep(0.5)
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(0.4)
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(1)
        sys.stdout.write(' AGAIN -.-')
        sys.stdout.flush()
        print('\033[0m')
        time.sleep(5)
        self.center_text()
        print('Por cierto.. viva el Open Source! Dediquemos unos instantes al creador del mapa original en ascii..')
        time.sleep(4)
        self.center_text()
        print('''
        Peer Wandel Hansen
        - Friday, October 11, 1996 at 04:08:24 (EDT)''')
        time.sleep(0.1)
        self.center_text()
        print('Suficiente.. XD')
        time.sleep(2)

    def call_function_with_timer(self, function, time_after):
        getattr(self, function)()
        time.sleep(time_after)
        self.clear_screen()


def run():
    mp = MediaPrinter()
    mp.call_function_with_timer('print_warning', 3)
    mp.call_function_with_timer('print_europe', 2)
    mp.call_function_with_timer('print_msg', 2)
    mp.center_text()
    print('\tBIS BALD!')
    time.sleep(3)
    print('\t\t\tEl programa ha terminado.. si quieres saber mas de mi.. llamame cojones!')
    time.sleep(1)
    print('\t\t\t\t\t\t\t\t\tPulsa INTRO :)')

run()
