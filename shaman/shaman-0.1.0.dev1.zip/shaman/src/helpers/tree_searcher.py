class Searcher:
    def __init__(self):
        class SearchNode:
            def __init__(self, symbol='/', node_result=None):
                self.successors = dict()
                self.symbol = symbol
                self.node_result = None
                if node_result:
                    self.add_result(node_result)

            def add_successor(self, successor):
                self.successors[successor.symbol] = successor

            def get_successor(self, with_letter):
                if with_letter in self.successors:
                    return self.successors[with_letter]
                return None

            def add_result(self, result):
                if not self.node_result:
                    self.node_result = set()
                self.node_result.add(result)

            def get_result(self):
                return self.node_result

        self.tree = SearchNode()
        self.SearchNodeClass = SearchNode

    def train(self, search_string, search_result):
        if not search_string:
            return

        current_node = self.tree

        for letter in search_string:
            successor = current_node.get_successor(letter)
            if successor:
                current_node = successor
            else:
                new_node = self.SearchNodeClass(symbol=letter)
                current_node.add_successor(new_node)
                current_node = new_node

        current_node.add_result(search_result)

    def search(self, search_string):
        result = set()
        current_node = self.tree
        for letter in search_string:
            cur_successor = current_node.get_successor(letter)
            if cur_successor:
                res = cur_successor.get_result()
                current_node = cur_successor
                if res:
                    result.update(res)
            else:
                break
        return result
