import console
from colour import ConsoleColour


config = {'font': 'windows.ttf',
          'font_size': 20,
          'title': 'Dun',
          'resizeable': False,}

console = console.Console(config)

console.write('helhelhelhel')

console.write_line('Hello World')
console.write_line('Laugh Laugh Laugh')
console.write_line('Hello World its me')

for i, col in enumerate(ConsoleColour.__iter__()):
    console.foreground_color = col
    console.write(i)
console.write_line()
l = console.read_line('hi this is a programi this is a program: ')
print(l)

k = console.read_key()
print(k)

console.clear()

console.write_line('memes')

console.read_key()

console.quit()
