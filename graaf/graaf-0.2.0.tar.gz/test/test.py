import sys

import markdown
import yaml

config = []

count = 2

lines = sys.stdin.readlines()

for line in sys.stdin:
    if line.rstrip() == '---':
        count -= 1
        if not count:
            break
    config.append(line)

config = yaml.load(''.join(config))
# content = sys.stdin.read()
print markdown.markdownFromFile(input=sys.stdin)
