import fileinput

import phyltr.utils.cladeprob

import ete2

def run():

    for line in fileinput.input():
        t = ete2.Tree(line)
        dead_nodes = []
        for node in t.traverse("preorder"):
            if node in dead_nodes:
                continue
            desc = node.get_descendants()
            desc.append(node)
            if all([n.support >=0.5 for n in desc]):
                dead_nodes.extend(desc)
                node.name = "+".join([l.name for l in node.get_leaves()])
                for child in node.get_children():
                    child.detach()

        print t.write()

    # Done
    return 0
