from ripy_dbs import *
import time


def ri_info_db():
    # Benchmarking.
    start = time.time()
    db = RiInfoDb('database', True)
    print "db initialised: {}".format(time.time() - start)
    start = time.time()
    mat = db.findMaterial(1.5, 500)
    print "single material look-up: {}".format(time.time() - start)
    start = time.time()
    mats = db.findMaterials(1.5, 500, 0.01)
    print "range material look-up: {}".format(time.time() - start)

    # Information example.
    print('')
    print(db.getShelfs())
    print(db.getBooks('main'))
    print(db.getPages('main', 'Si'))

    # Search examples.
    print('')
    print('{}, {}, {}'.format(mat.get_complex_ri(500), mat.name, mat.meta))
    print('')
    for mat in mats:
        print(u'{}, {}, {}'.format(mat.get_complex_ri(500), mat.name, mat.meta))


def pvl_db():
    db = PvlDb('Scrape@23-11-2015')
    mat = db.get_material('Ag-Pure [Pal85a].xls')
    print('{}, {}'.format(mat.get_complex_ri(500), mat.name))

# ri_info_db()
# pvl_db()
