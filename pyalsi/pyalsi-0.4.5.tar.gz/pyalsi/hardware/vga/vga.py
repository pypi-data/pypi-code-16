import os


class VgaCard(object):
    pass


class Pci(object):
    @staticmethod
    def get_vga_devices():
        out = os.popen("lspci | grep VGA").read().splitlines()
        cards = {}
        for line in out:
            line = line.split(":")[-1]
            if line in cards.keys():
                count = cards[line]
                cards.pop(line)
                cards[line] = count + 1
            else:
                cards[line] = 1
        output = []
        if len(cards) > 0:
            for k, v in cards.iteritems():
                output.append("{}{}".format(k, ("(x{})".format(v)) if v > 1 else ""))
        else:
            return False
        return output
