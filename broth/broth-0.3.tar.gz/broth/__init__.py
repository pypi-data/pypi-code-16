from bs4 import BeautifulSoup

class Broth:

    def __init__(self, text):
        soups = []
        errors = []
        for parser in ["html5lib", "html.parser"]:
            try:
                soup = BeautifulSoup(text, parser)
                soups.append([soup, len(soup), parser])
            except Exception as e:
                errors.append(parser)

        if soups:
            if errors:
                print "[broth] We weren't able to parse with ", errors, "but don't worry we were able to parse with", [lst[2] for lst in soups]
            self.soup = sorted(soups, key=lambda tup: -1 * tup[1])[0][0]
        else:
            print "[broth] We weren't able to parse with any parsers"

    @property
    def tables(self):
        return self.soup.select("table")
