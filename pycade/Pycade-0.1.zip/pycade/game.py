import pygame

from collections import defaultdict

class Game(object):
    defaults = {
        'FPS': 20,
        'WINDOW_CAPTION': 'PyCade',
        'WINDOW_WIDTH': 600,
        'WINDOW_HEIGHT': 600,
    }

    def __init__(self, constants):
        pygame.init()

        self.state = defaultdict(lambda: None)
        self.state['constants'] = constants
        self.state['events'] = []
        self.state['font'] = pygame.font.Font('freesansbold.ttf', 32)
        self.setup_loops()
        self.setup_objects()

        self.create_window()
        self.clock = pygame.time.Clock()
        self.fps = self.defined_or_default('FPS')

    def create_window(self):
        window_width = self.defined_or_default('WINDOW_WIDTH')
        window_height = self.defined_or_default('WINDOW_HEIGHT')
        self.state['surface'] = pygame.display.set_mode((window_width, window_height))

        caption = self.defined_or_default('WINDOW_CAPTION')
        pygame.display.set_caption(caption)

    def setup_loops(self):
        self.initialized_loops = { key: loop(self.state) for key, loop in self.loops.items() }
        self.loops = self.initialized_loops
        self.state['current_loop'] = self.initial_loop
        self.state['next_loop'] = self.initial_loop

    def setup_objects(self):
        pass

    def update_loops(self):
        self.state['current_loop'] = self.state['next_loop']

    def run_triggered_events(self):
        for event_name in self.state['events']:
            f = getattr(self, event_name)
            if f:
                f()
            else:
                raise AttributeError('Undefined event: ' + event_name)
        self.state['events'] = []


    def defined_or_default(self, var):
        if var in self.state['constants']:
            return self.state['constants'][var]
        elif var in self.defaults:
            return self.defaults[var]
        else:
            raise KeyError(var)

    def run(self):
        while True:
            current_loop = self.state['current_loop']
            self.loops[current_loop].run()
            self.update_loops()
            self.run_triggered_events()
            self.clock.tick(self.fps)
