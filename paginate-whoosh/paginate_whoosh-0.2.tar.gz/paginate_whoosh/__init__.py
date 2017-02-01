# Copyright (c) 2017 Lukas Weissenböck <lukas@lukes.space>
# See the file LICENCE for copying permissions

""" Allows the paginate module to work with Whoosh. """

import paginate


class WhooshWrapper():
    """ Wrapper class to access results of a `whoosh.searching.Results`
        object. """

    def __init__(self, obj):
        self.obj = obj


    def __getitem__(self, range):
        if not isinstance(range, slice):
            raise Exception("slice required for __getitem__")

        return self.obj[range]


    def __len__(self):
        return len(self.obj)


class WhooshPage(paginate.Page):
    """ A pagination class to deal with Whoosh searches. """

    def __init__(self, *args, **kwargs):
        super(WhooshPage, self).__init__(
            *args, wrapper_class=WhooshWrapper, **kwargs)