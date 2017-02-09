import console
from colour import ConsoleColour
from window import CharacterString

'''
font = None#Font('window.ttf', 12)

a  = CharacterString('Hello', font, (0, 0), (255, 255, 255), True)
b  = CharacterString('World', font, (0, 0), (255, 255, 255), True)

print(a)
print(b)
print(a + b)
print(a*5)
'''

config = {'font': 'windows.ttf',
          'font_size': 18,
          'title': 'Dun',
          'resizeable': True,}

console = console.Console(config)

console.write('Hello')
console.write('World')
console.write_line()

console.write_line('Hello World')

i = 0
for col in ConsoleColour.items():
    console.foreground_colour = col
    console.write(i)
    if i % 9 == 0:
        console.write_line()
        i = 0
    i += 1
console.write_line()
l = console.read_line('Input: ')
d = console.read_line()
print(l)

k = console.read_key()
print(k)

console.clear()

console.write_line('memes')

console.read_key()

console.quit()
