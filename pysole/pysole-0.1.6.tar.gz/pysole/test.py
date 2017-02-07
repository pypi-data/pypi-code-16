import console
from colour import ConsoleColour


config = {'font': 'windows.ttf',
          'font_size': 14,
          'title': 'Dun',
          'resizeable': True,}

console = console.Console(config)

console.write_line('Hello World')

for i, col in enumerate(ConsoleColour.__iter__()):
    console.foreground_color = col
    console.write(i + 1000)
console.write_line()
l = console.read_line('hi this is a programi this is a program: ')
print(l)

k = console.read_key()
print(k)

console.clear()

console.quit()
