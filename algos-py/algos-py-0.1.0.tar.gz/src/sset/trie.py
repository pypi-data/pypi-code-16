class Node:

    def __init__(self, top, val=None):

        self.top = top
        self.val = val

        self.edges = {}

    def __len__(self):
        """Returns the number of child nodes.

        :returns: the number of child nodes
        """
        return len(self.edges)

    def __bool__(self):
        """Returns true if the node is important.

        :returns: true if the node stores a value or has children
        """
        return self.val is not None or bool(len(self))

    def __iter__(self):
        return iter(self.edges)

    def __getitem__(self, key):
        """Returns a child reachable with :param: key from this node.

        :returns: a child node
        """
        return self.edges[key]

    def __setitem__(self, key, val):
        self.edges[key] = val

    def __str__(self):
        return "top: {}, val: {}, edges: {}".format(
            self.top, self.val, self.edges
        )

    def __repr__(self):
        return self.__str__()

    def pop(self, key):
        self.edges.pop(key)

    def get_node_with_parent(self, key):
        for i in range(len(key)):
            if key[i] not in self:
                return self, self.top, i

            self = self[key[i]]
        return self, self.top, len(key)

    def put(self, key, val, i):
        for n in range(i, len(key)):
            if key[n] not in self:
                self[key[n]] = Node(self)

            self = self[key[n]]
            self.val = val

    def get(self, key):
        node, _, i = self.get_node_with_parent(key)
        return None if len(key) != i else node.val

    def gcp(self, key):
        return self.get_node_with_parent(key)[2]

    def startswith(self, key):
        """Returns all keys from the Trie that start with ``key``.

        :returns: a (possibly empty) list of keys
        """
        node, _, i = self.get_node_with_parent(key)

        if i < len(key):
            return []

        results = []

        def dfs(node, prefix):
            for k in node:
                dfs(node[k], prefix + k)

            if node.val is not None: results.append(prefix)

        dfs(node, key)

        return results


class Trie:
    """Represents the Trie datastructure."""

    def __init__(self):
        self.root = None

    def get_node_with_parent(self, key):
        """Returns the node and its parent that are reachable with key.

        :returns: ``(node, parent, length)``

        If the search is successful, ``node != None`` and ``length ==
        len(key)``.  Otherwise, ``either node == None`` or ``length <
        len(key)``.
        """

        if self.root is None: return None, None, 0
        return self.root.get_node_with_parent(key)

    def get(self, key):
        return None if self.root is None else self.root.get(key)

    def put(self, key, val):
        """Puts ``val`` into Trie using ``key[i:len(key)]`` as key.

        If ``key`` is already present in the Trie, its value will
        be overwritten with ``val``.

        :returns: ``None``
        """

        node, parent, i = self.get_node_with_parent(key)

        if node is None and parent is None:
            self.root = Node(None)
            node = self.root

        node.put(key, val, i)

    def remove(self, key):
        node, _, i = self.get_node_with_parent(key)

        if node is None or node.val is None or i < len(key): return

        node.val = None

        for i in range(len(key) - 1, 0, -1):
            if node: return

            node = node.top
            node.pop(key[i])

        if len(node) == 0:
            self.root.pop(key[0])

            if len(self.root) == 0:
                self.root = None

    def gcp(self, key):
        return 0 if self.root is None else self.root.gcp(key)

    def startswith(self, key):
        return [] if self.root is None else self.root.startswith(key)

    def all(self):
        if self.root is None: return []

        result = []

        def dfs(node, prefix):
            for k in node:
                dfs(node[k], prefix + k)

            if node.val is not None:
                result.append(prefix)

        dfs(self.root, "")

        return result
