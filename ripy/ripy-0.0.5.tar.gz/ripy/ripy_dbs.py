import os
import pickle
import pandas as pd
import yaml
import html5lib
import bs4

from ripy_objects import *


# region RiInfoDb

class RiInfoDb:
    """Class that parses the refractiveindex.info YAML database"""

    # region Initialisation

    def __init__(self, db_path, force_update=False):
        self.cache = None
        self.catalog = None
        # Load paths.
        self.referencePath = os.path.normpath(db_path)
        self.catalog_path = os.path.join(self.referencePath, os.path.normpath('catalog.pkl'))
        self.cache_path = os.path.join(self.referencePath, os.path.normpath('cache.pkl'))
        # Load catalogue.
        if os.path.isfile(self.catalog_path) and not force_update:
            self.catalog = pickle.load(open(self.catalog_path, 'rb'))
        else:
            self.__parseCatalogue()
        # Load entries.
        if os.path.isfile(self.cache_path) and not force_update:
            self.cache = pickle.load(open(self.cache_path, 'rb'))
        else:
            self.__parseEntries()

    def __parseCatalogue(self):
        with open(os.path.join(self.referencePath, os.path.normpath('library.yml')), 'r') as stream:
            self.catalog = yaml.safe_load(stream)
        pickle.dump(self.catalog, open(self.catalog_path, 'wb'))

    def __parseEntries(self):
        self.cache = {}
        for sh in self.catalog:
            self.cache[sh['SHELF']] = {}
            for b in sh['content']:
                if 'DIVIDER' not in b:
                    self.cache[sh['SHELF']][b['BOOK']] = {}
                    for p in b['content']:
                        if 'DIVIDER' not in p:
                            filename = os.path.join(self.referencePath, os.path.normpath(p['path']))
                            self.cache[sh['SHELF']][b['BOOK']][p['PAGE']] = self.__parseMaterial(b['BOOK'], p['PAGE'],
                                                                                                 filename)
        pickle.dump(self.cache, open(self.cache_path, 'wb'))

    def __parseMaterial(self, b, p, filename):
        refractiveIndex = None
        extinctionCoefficient = FixedIndexData(0)
        comments = None
        name = u'{}, {}'.format(b, p)

        try:
            f = open(filename)
            material = yaml.safe_load(f)
            f.close()

            if 'COMMENTS' in material.keys():
                comments = material['COMMENTS']

            for data in material['DATA']:
                if data['type'].split()[0] == 'tabulated':
                    rows = data['data'].split('\n')
                    splitrows = [c.split() for c in rows]
                    wavelengths = []
                    n = []
                    k = []
                    for s in splitrows:
                        if len(s) > 0:
                            wavelengths.append(float(s[0]))
                            n.append(float(s[1]))
                            if len(s) > 2:
                                k.append(float(s[2]))

                    if (data['type'].split())[1] == 'n':

                        if refractiveIndex is not None:
                            Exception('Bad Material YAML File')

                        refractiveIndex = setup_index(formula=-1, wavelengths=wavelengths, values=n)
                    elif (data['type'].split())[1] == 'k':

                        extinctionCoefficient = setup_index(formula=-1, wavelengths=wavelengths, values=n)

                    elif (data['type'].split())[1] == 'nk':

                        if refractiveIndex is not None:
                            Exception('Bad Material YAML File')

                        refractiveIndex = setup_index(formula=-1, wavelengths=wavelengths, values=n)
                        extinctionCoefficient = setup_index(formula=-1, wavelengths=wavelengths, values=k)
                elif data['type'].split()[0] == 'formula':

                    if refractiveIndex is not None:
                        Exception('Bad Material YAML File')

                    formula = int((data['type'].split())[1])
                    coefficents = [float(s) for s in data['coefficients'].split()]
                    rangeMin = float(data['range'].split()[0])
                    rangeMax = float(data['range'].split()[1])

                    refractiveIndex = setup_index(formula=formula,
                                                  rangeMin=rangeMin,
                                                  rangeMax=rangeMax,
                                                  coefficients=coefficents)
        except Exception as ex:
            print('Error loading {}'.format(filename))
        return Material(refractiveIndex, extinctionCoefficient, name, {'comments': comments})
        # return Material(b, p, refractiveIndex, extinctionCoefficient, comments)

    # endregion

    # region Info methods

    def getShelfs(self):
        return [sh['SHELF'] for sh in self.catalog]

    def getBooks(self, shelf):
        s_matches = [sh['content'] for sh in self.catalog if sh['SHELF'] == shelf]
        if len(s_matches) == 0:
            raise ValueError('shelf not found')

        return [b['BOOK'] for b in s_matches[0] if 'DIVIDER' not in b]

    def getPages(self, shelf, book):
        s_matches = [sh['content'] for sh in self.catalog if sh['SHELF'] == shelf]
        if len(s_matches) == 0:
            raise ValueError('shelf not found')
        b_matches = [b['content'] for b in s_matches[0] if 'DIVIDER' not in b and b['BOOK'] == book]
        if len(b_matches) == 0:
            ValueError('book not found')

        return [p['PAGE'] for p in b_matches[0] if 'DIVIDER' not in p]

    # endregion

    # region Material interface

    def getMaterial(self, shelf, book, page):
        return self.cache[shelf][book][page]

    def findMaterials(self, n, wl, tol):
        result = []
        self.__loopDb(lambda m: result.append(m) if abs((m.get_complex_ri(wl, True) - n)) < tol else None)
        return result

    def findMaterial(self, n, wl):
        result = []
        self.__loopDb(lambda m: self.__updateBestMatch(n, wl, result, m))
        return result[0]

    # endregion

    # region Help methods

    def __updateBestMatch(self, n, lmb, result, m):
        if np.isnan(m.get_complex_ri(lmb, True)):
            return
        if len(result) == 0:
            result.append(m)
        elif abs((m.get_complex_ri(lmb) - n)) < abs((result[0].get_complex_ri(lmb) - n)):
            result[0] = m

    def __loopDb(self, func):
        for sh in self.cache:
            for b in self.cache[sh]:
                for p in self.cache[sh][b]:
                    material = self.cache[sh][b][p]
                    # Skip unimplemented formulas for now.
                    if material.is_valid():
                        func(material)


def setup_index(formula, **kwargs):
    """

    :param formula:
    :param kwargs:
    :return: :raise Exception:
    """
    if formula >= 0:
        return FormulaIndexData(formula, **kwargs)
    elif formula == -1:
        return TabulatedIndexData(**kwargs)
    else:
        raise Exception('Bad RefractiveIndex data type')


# endregion


# region PvlDb

class PvlDb:
    def __init__(self, data_path):
        self.data_path = data_path
        # files = [f for f in os.listdir(data_path) if os.path.splitext(f)[1] == '.xls']
        # splits = [str.split(f[:-4], '-') for f in files]
        # self.keys = [split[0] for split in splits]
        # self.details = dict((split[0], split[1]) for split in splits)
        # self.authors = dict((split[0], split[2]) for split in splits)
        # self.files = dict((splits[i][0], files[i]) for i in range(0, len(files)))

    def get_material(self, key):
        # Temporary simple parser.
        df = pd.read_html(os.path.join(self.data_path, key), skiprows=range(0, 2))
        # df = pd.read_html(os.path.join(self.data_path, self.files[key]), skiprows=range(0, 2))
        data = df[0].values
        wl_lst = []
        n_lst = []
        k_lst = []
        for i in np.arange(0, len(data)):
            wl_lst.append(data[i, 0] / 1000.0)
            n_lst.append(data[i, 1])
            k_lst.append(data[i, 4])
        # Filter out duplicate values.
        wl_n, n_lst = filter_data(wl_lst, n_lst)
        wl_k, k_lst = filter_data(wl_lst, k_lst)
        # Create material mapping.
        ri = setup_index(formula=-1, wavelengths=wl_n, values=n_lst)
        ec = setup_index(formula=-1, wavelengths=wl_k, values=k_lst)
        return Material(ri, ec, key)


def filter_data(wls, idxs):
    """ filter out duplicate values to allow proper interpolation """
    prev = idxs[0]
    tmp_lst = []
    wls_out = [wls[0]]
    idxs_out = [idxs[0]]
    for i in np.arange(0, len(wls)):
        if idxs[i] == prev:
            tmp_lst.append(wls[i])
        elif i is not 0:
            # Write values to output.
            idxs_out.append(prev)
            wls_out.append(np.mean(tmp_lst))
            # Update tmp values.
            tmp_lst = [wls[i]]
            prev = idxs[i]
    # Append any pending entries.
    if len(tmp_lst) > 0:
        idxs_out.append(prev)
        wls_out.append(np.max(tmp_lst))

    return np.array(wls_out), np.array(idxs_out)

# endregion
