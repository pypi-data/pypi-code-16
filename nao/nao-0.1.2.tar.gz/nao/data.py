import pandas as pd
import numpy as np
import decimal as dec


import itertools

from inspect import isclass, getmro

from . import logger, benchmark, odict

from sqlalchemy.types import DateTime, Date
from sqlalchemy.types import Integer, BigInteger, Float, Numeric, Boolean, Enum
from sqlalchemy.types import String, Text, Unicode, UnicodeText
from sqlalchemy.schema import Column
from sqlalchemy.orm import sessionmaker
from sqlalchemy.inspection import inspect
from sqlalchemy.ext.declarative import declared_attr

log = logger(__name__)


class LoaderError(Exception): pass

class LoadableMixin(object):
    """
    This is the Basic mixin that performs loading functionality

    This should be created similarly to declarative base otherwise
    shared among all model classes in the same interpreter process

    """
    __loader__ = None  #: override class attribute in subclasses
    __loader_args__ = {} #: loading arguments shared by subclasses

    @classmethod
    def load(cls, engine=None, params=None):
        """
        loads the data into the database based on the
        __loader__ attribute of the model class

        typical usage
        for cls in Base.sorted_subclasses:
            cls.load()

        """
        #: check self.__loader__
        # TODO initialize loader class here based on inheritance (Mixin's loader_class and __loader_args__)
        if isinstance(cls.__loader__, Loader):
            # delegate task to loader object
            log.debug('Loading for model class: {}'.format(cls))

            return cls.__loader__.load( engine, params)

        else:
            # rasie some more sensible error
            log.info("{} is not loadable!".format(cls))

    
    
    @classmethod
    @benchmark
    def load_all(cls, base, source_engine, target_engine, params=None, ranges=None):
        """

        `params`
        These params are used to prepare sql-statements 


        `ranges`
        Used to iterate through ranges (preferably an `odict`)
        `range` should be an iterator
        for advanced date mangling a custom iterator is necessary
        """
        # TODO this should go back to the declarative base class which has metadata
        # and create the necessary classes
        # That way load_all could be called from anywhere
        # the collecting mechanism would be that the classes should be inherited from the caller

        # TODO somehow stop relying on table names
        # check the not classical mappings for help


        s = sessionmaker(bind=target_engine)()

        loader_classes = {}

        for c in base._decl_class_registry.values():
            # _decl_class_registry has some special elements as well
            # class included if it is a subclass of the one `load_all` called on
            if isclass(c) and issubclass(c, cls):
                loader_classes[c.__tablename__] = c

        def sorted_subclasses_generator():
            for t in base.metadata.sorted_tables:
                if t.name in loader_classes:
                    yield loader_classes[t.name]


        @benchmark
        def _load(params):

            # TODO use cache only if there is implicit foreign
            cache = odict()
            implicit_foreign = []

            for c in sorted_subclasses_generator():

                res = c.load(source_engine, params)

                cache[c.__tablename__] = res

                for r in inspect(c).relationships:

                    # check if target allows imlicit foreign key addition
                    if issubclass(loader_classes[r.target.name], ImplicitForeignMixin):
                        # target should already exist in the cache because of sorted_tables
                        implicit_foreign.append((c, r))
                        

                # TODO For DiffLoader check existence here
                # New (add new items with insert_date)
                # Match (implicit records should drop, others update_date)
                # Delete (no actual deletion only delete_date)


            # making implicit foregin key happen
            # TODO many to many??? association proxies???
            # TODO not null howto?

            log.debug("Searching implicit foreign keys...")

            def get_index(table, keys):
                """
                TODO might implement caching of indices here
                """
                index = []
                for row in cache[table.name]:
                    index.append(tuple([row[k] for k in keys]))
                return index

            for klass, relation in implicit_foreign:
                # source is the table with foreign_keys to target

                fks, pks = tuple(zip(*[(l.name, r.name) for l, r in relation.local_remote_pairs]))
                # print(fks, pks)
                # target is accepting new records with implicit_foreign flag
                target_index = get_index(relation.target, pks)
                # print(target_index)
                target_class = loader_classes[relation.target.name]

                for row in cache[klass.__tablename__]:
                    ind = tuple([row[k] for k in fks])
                    if any([i is None for i in ind]): continue

                    # print(ind)
                    if ind not in target_index:

                        log.warning("Implicit Foreign {} ({}) from table {}".format(
                            relation.target.name,
                            ", ".join([str(i) for i in ind]),
                            klass.__tablename__
                        ))

                        new_row = dict((k,v) for k,v in zip(pks, ind))
                        new_row[IMPLICIT_FOREIGN] = True
                        cache[relation.target.name].append(new_row)

                        # update target_index
                        target_index.append(ind)
                        # target_class.add_implicit_foreign(ind) # return a dict...

                # read all data from klass and check if already in target_data


            # bulk insert chould operate separately by the cache
            for key, res in cache.items():
                c = loader_classes[key]
                s.bulk_insert_mappings(c, res)

            s.commit()
        
            # TODO implement row-by-row insert for debugging
            # for row in res:
            #     s.bulk_insert_mappings(self.cls, [row])
            #     s.commit()


        # generating runs based on the ranges iterables
        if ranges is not None:

            names, iterables = ranges.keys(), ranges.values()

            # initialize all parameters once with a Carthesian product
            prod = itertools.product(*iterables)

            for vector in prod:
                
                d = dict(zip(names, vector))

                log.info("LOADING values: {}".format(d))

                p = params.copy()
                p.update(d)
                _load(p)


        # simply loading with params
        else:
            _load(params)

        s.close()



IMPLICIT_FOREIGN = 'implicit_foreign'

class ImplicitForeignMixin(LoadableMixin):
    """
    This class is mainly an indicator to initiate
    impliciet loading mechanism based on the foreign keys
    of other `Loadable` classes of the same `LoadableBase`.

    Adds a `Column` by the name defined in `IMPLICIT_FOREIGN`
    constant.
    """

def anon(cls):
    return None

# TODO remove column from load iteration!
# PATCH using `declared_attr` moves it to the end otherwise
# `column_instance._create_order` defines or need to flag mixin
# columns otherwise

setattr(ImplicitForeignMixin, IMPLICIT_FOREIGN, declared_attr(lambda cls: Column(Boolean, default=False)))

        

class Loader(object):
    """
    Base class for all the loading functionality

    Inheritance checked in the LoaderBase class

    This could be an abstract base class


    """
    @staticmethod
    def prepare_sql(sql, **kwds):
        sql = sql.strip()
        if sql.endswith(';'): sql = sql[:-1]
        sql = sql.format(**kwds)
        return sql


    #############################################################
    # OLD LOADER based on Pandas
    # It was not working mainly due to mixed types row handling difficulties

    # @benchmark
    # def _parse_sql(self, sql, engine):
    #     """
    #     TODO not in use anymore
        
    #     Cannot be significantly faster as it is necessary to read data into memory
    #     for conversions
    #     """
    #     # coerce_float=False ensures all dtypes are object_
    #     with benchmark("Reading data into memory..."):
    #         df = pd.read_sql(sql, engine, coerce_float=False)

    #     # TODO create own describe based on pandas
    #     # show more sophisticated data
    #     log.debug("Describing dataframe before conversion:")
    #     log.debug(df.describe(include='all'))

    #     log.debug("Datatypes of dataframe:")
    #     log.debug(df.dtypes)

    #     # print(df)

    #     col_names = [c.name for c in self.cls.__table__.columns]
    #     df.columns = col_names
    #     # TODO check compatibility of dimensions

    #     index = []
    #     for i, c in enumerate(self.cls.__table__.columns):

    #         log.debug("COLUMN {} ({}) pk: {}".format(c.name, c.type, c.primary_key))
    #         # df[c.name] = df[c.name].astype(str)

    #         col = df[c.name] # working with one col at a time
    #         col = col[pd.notnull(col)] # working with not None only

    #         print(col)

    #         # TODO check foreign keys for uniqueness and no None!
    #         if c.foreign_keys:
    #             log.debug("Foreign keys for {} are {}".format(c.name, c.foreign_keys))


    #         if isinstance(c.type, (Date, DateTime)):
    #             col = pd.to_datetime(col)
    #             # TODO unrealistic date (what is realistic? (today +/- 120)
    #             # series.between(left, right)

    #         elif isinstance(c.type, (Integer, BigInteger, Numeric, Float)):
    #             # Everything casted to Decimal to avoid precision problems, only one conversion occurs at the SQL side
    #             if col.str.startswith('0').any():
    #                 log.warning("Converting '0' starting strig to numeric")
    #             # check dtypes and issue warnings
    #             col = col.astype(dec.Decimal)
    #             # pd.to_numeric(df[c.name], errors='coerce')  
    #             # df.ix(pd.notnull(df[c.name]), c.name).astype(dec.Decimal) #
    #             # df[c.name].replace(pd.nan, None, inplace=True)

    #         elif isinstance(c.type, (String, Text, Unicode, UnicodeText)):
    #             col = col.str.strip()
    #             mx = col.str.len().max()  # .map(len).max() is quicker a bit
    #             log.debug("COLUMN {} max length: {}".format(c.name, mx))
    #             # check string and unicode columns length attribute
    #             if mx > c.type.length:
    #                 raise ValueError("COLUMN {} would have been truncated".format(c.name))


    #         elif isinstance(c.type, (Boolean, )):
    #             col = col.astype('bool')  # remove none!
    #             # Allow Y-N, 0-1, True-False conversion explicitly

    #         #   print(i.enums)

    #         df[c.name] = col # write back parsed col
            

    #     # to_numeric introduce np.nan -> monkey-patch:
    #     # df = df.where(pd.notnull(df), None) # notnull selects the elements NOT replaced
    #     # TODO move this to to_dict somehow as in a simple dict no np.nan should occur...

    #     # show more sophisticated data
    #     log.debug("Describing dataframe after conversion:")
    #     log.debug(df.describe(include='all'))

    #     log.debug("Datatypes of dataframe:")
    #     log.debug(df.dtypes)

    #     # print(df)
            
    #     # convert to dictionary works only without using index
    #     # df.set_index(index, inplace=True)

    #     # custom df.to_dict
    #     res = []
    #     for df_row in df.itertuples():
    #         r = {}
    #         for i,c in enumerate(col_names):
    #             r[c] = df_row[i]
    #         res.append(r)

    #     return res

    #     # return df.to_dict(orient='records')  # avoid indices for this operation!


class ParamLoader(Loader):

    def __init__(self, model_class, **kwds):
        """
        `__loader__` should be declared as a `declared_attr`
        so the `cls` comes from there
        """
        self.config = self._get_config(model_class, kwds)
        self.cls = model_class
        # TODO do not use cls here


    def load(self, engine, params=None):

        cfg = self.config

        # debug usually from load or load_all call
        debug = cfg.get('debug', False)

        tbl = self.cls.__table__
        # log.debug(tbl)

        # get engine
        # log.debug(engine)

        p = cfg.get('params', {})  # might use defaultdict here with str
        p.update(params)
        # INFO no defaults needed as if there is it should be in the
        # SQL (otherwise a cfg called params could be used)
        sql = cfg.get('load_sql')
        # create prepare sql class which use parameter inclusion
        # might wanna check sqlalchemy syntax for that!
        sql = self.prepare_sql(sql, **p)
        # log.debug(sql)
        
        # read sql
        res = self._parse_sql_light(sql, engine)
        # res = self._read_sql_slow(sql, engine)

        # search duplicates
        if debug:
            df = pd.DataFrame(res)
            pks = [c.name for c in self.cls.__table__.columns if c.primary_key]
            log.debug("primary key: {}".format(pks))
            dpl = df.duplicated(subset=pks, keep=False)
            if dpl.any():
                log.debug("DUPLICATE: {}".format(df.duplicated(subset=pks).any()))
                df[dpl].to_csv('dupidup.csv')
                # TODO make output filename more sane

        # TODO add callback mechanism for other tables
        # for c in self.cls.__table__.columns:
        #     if c.foreign_keys:
        #         log.debug("Foreign keys for {} are {}".format(c.name, c.foreign_keys))

        return res


    def _get_config(self, cls, kwds):
        x = cls.__loader_args__.copy()
        x.update(kwds)
        return x


    def _parse_value(self, val, col):

        # TODO check foreign keys for uniqueness and no None!
        # if c.foreign_keys:
        #     log.debug("Foreign keys for {} are {}".format(c.name, c.foreign_keys))

        # determine numerical input types
        raw_numeric_types = (int, dec.Decimal, float)

        # SQLalchemy types categorized
        numeric_types = (Integer, BigInteger, Numeric, Float)
        date_types = (Date, DateTime)
        string_types = (String, Unicode, Text, UnicodeText)
        bool_types = (Boolean, )

        # very lazy approach to bool casting
        true_vals = (True, 'Y', 'I', 1, '1')  
        # false_vals = (False, 'N', 'N', 0, '0')

        # numeric types only go to numeric types
        if isinstance(val, raw_numeric_types):
            if isinstance(col.type, numeric_types):
                pass
                # TODO check for possible precision loss
                # log.debug("Casting numeric to numeric")
                # val = dec.Decimal(str(val)) OR let the engine do that :)

            else:
                raise ValueError("Casting numeric to non-numeric!")

        # str and anything except for numeric and None
        else: 
            if isinstance(col.type, date_types):
                val = pd.to_datetime(val)
                # TODO stp using pd
                # TODO unrealistic date (what is realistic? (today +/- 120 years)
            # series.between(left, right)

            elif isinstance(col.type, numeric_types):
                # Everything casted to Decimal to avoid precision problems, only one conversion occurs at the SQL side
                if val.startswith('0'):
                    log.warning("Converting '0' starting strig to numeric")
                # check dtypes and issue warnings
                val = dec.Decimal(val)

            elif isinstance(col.type, string_types):
                val = val.strip()
                # callback mechanism for maximum string length in column! (self._callback_string_length)
                # check string and unicode columns length attribute
                if col.type.length is not None and len(val) > col.type.length:
                    raise ValueError("COLUMN {} would have been truncated {}".format(col.name, val))


            elif isinstance(col.type, bool_types):
                val = val in true_vals

        return val



    @benchmark
    def _parse_sql_light(self, sql, engine):
        """
        returns a list of dicts

        validated and coerced to the corresponding model
        """

        # TODO remove columns with special usage
        columns = self.cls.__table__.columns

        res = []

        # TODO if slow then pandas might use some C magic for this but I doubt (should check)
        i, j = 0, 0  # if the resultproxy has no rows...

        for i,row in enumerate(engine.execute(sql)):
            # allow extra columns at the end with default values or null
            if len(row) > len(columns):
                raise ValueError("Degenarate raw (col count mismatch)")

            new_row = {}

            for j,col in enumerate(columns):

                # it is OK to have extra columns at the end
                if j >= len(row): break

                val = row[j]

                if val is not None:
                    try:
                        val = self._parse_value(val, col)
                    except:
                        log.error("row {}, col {}, value [{}], type {}".format(i, j, row[j], type(row[j])))
                        log.error("COLUMN {} ({}) pk: {}".format(col.name, col.type, col.primary_key))
                        raise

                new_row[col.name] = val

            res.append(new_row)

        log.debug("Parsed {} rows with {} columns".format(i+1, j+1))

        return res

    



class DiffLoader(ParamLoader):
    """
    Search for new items based on primary key

    Auto-add functionality if pk is missing
    (tricky it should be used from other table loaders!!!)
    TODO

    TODO Implement callback functionality to add missing entities
    """

