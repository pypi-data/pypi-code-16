class Trie:
    def __init__(self):
        self.root = Node('')

    def __repr__(self):
        self.output([self.root])
        return ''

    def output(self, currentPath, indent=''):
        # Depth First Search
        currentNode = currentPath[-1]
        if currentNode.isTerminal:
            word = ''.join([node.letter for node in currentPath])
            print
            indent + word
            indent += '  '
        for letter, node in sorted(currentNode.children.items()):
            self.output(currentPath[:] + [node], indent)

    def insert(self, word):
        current = self.root
        for letter in word:
            if letter not in current.children:
                current.children[letter] = Node(letter)
            current = current.children[letter]
        current.isTerminal = True

    def __contains__(self, word):
        current = self.root
        for letter in word:
            if letter not in current.children:
                return False
            current = current.children[letter]
        return current.isTerminal

    def getAllPrefixesOfWord(self, word):
        prefix = ''
        prefixes = []
        current = self.root
        for letter in word:
            if letter not in current.children:
                return prefixes
            current = current.children[letter]
            prefix += letter
            if current.isTerminal:
                prefixes.append(prefix)
        return prefixes


class Node:
    def __init__(self, letter=None, isTerminal=False):
        self.letter = letter
        self.children = {}
        self.isTerminal = isTerminal

