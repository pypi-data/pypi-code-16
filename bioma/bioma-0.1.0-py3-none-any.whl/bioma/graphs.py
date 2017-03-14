"""Simple triplestore implementation.

This module contains a simple implementation of a general purpose triple and
triplestore, based on provided examples at Programming the Semantic Web by Toby
Segaran, Colin Evans, and Jamie Taylor. Copyright 2009 Toby Segaran, Colin
Evans, and Jamie Taylor, 978-0-596-15381-6.
"""

import jsonpickle
import os


class Triple():
    """General purpose triple."""

    def __init__(self, subject, predicate, objct):
        """Triple initializer.

        Args:
            subject (str): Triple subject.
            predicate (str): Triple predicate.
            objct (str): Triple object.

        Returns:
            None.
        """
        self.sub = subject
        self.pre = predicate
        self.obj = objct

    def __eq__(self, other):
        """Custom Triple comparison.

        Args:
            other (Triple): Triple to be compared to.

        Returns:
            True if both Triples are equal.
            False otherwise.
        """
        if self.sub == other.sub and self.pre == other.pre and \
           self.obj == other.obj:
            return True
        else:
            return False

    def pos(self):
        """Return triple in predicate, object, subject form.

        Args:
            None.

        Returns:
            Triple: Triple in predicate, object, subject form.
        """
        return Triple(self.pre, self.obj, self.sub)

    def osp(self):
        """Return triple in object, subject, predicate form.

        Args:
            None.

        Returns:
            Triple: Triple in object, subject, predicate form.
        """
        return Triple(self.obj, self.sub, self.pre)


class Triplestore():
    """General purpose triplestore."""

    def __init__(self, name='my-triplestore'):
        """Triplestore initializer.

        Args:
            name (str): Triplestore name.

        Returns:
            None.
        """
        self._name = name
        self._spo = {}
        self._pos = {}
        self._osp = {}

    def add(self, triple):
        """Add given triple to triplestore.

        Args:
            triple (Triple): Triple to be stored.

        Returns:
            None.
        """
        self._add_to_container(self._spo, triple)
        self._add_to_container(self._pos, triple.pos())
        self._add_to_container(self._osp, triple.osp())

    def _add_to_container(self, container, triple):
        """Add triple to given container.

        Args:
            container (dict): Container to be used.
            triple (Triple): Triple to be stored.

        Return:
            None.
        """
        if triple.sub not in container:
            container[triple.sub] = {triple.pre: set([triple.obj])}
        else:
            if triple.pre not in container[triple.sub]:
                container[triple.sub][triple.pre] = set([triple.obj])
            else:
                container[triple.sub][triple.pre].add(triple.obj)

    def remove(self, triple):
        """Remove triple from triplestore.

        Args:
            triple (Triple): Triple to be removed.

        Returns:
            None.
        """
        self._remove_from_container(self._spo, triple)
        self._remove_from_container(self._pos, triple.pos())
        self._remove_from_container(self._osp, triple.osp())

    def _remove_from_container(self, container, triple):
        """Remove triple from given container, deleting those that become empty.

        Args:
            container (dict): Container to be used.
            triple (Triple): Triple to be removed.

        Returns:
            None.
        """
        container[triple.sub][triple.pre].remove(triple.obj)
        self._clear_empty_containers(container, triple)

    def _clear_empty_containers(self, container, triple):
        """Clear empty data structures in a container.

        Args:
            container (dict): Container to be cleaned.
            triple (Triple): Triple for direct access to possible empty data
                             structure.

        Returns:
            None.
        """
        if len(container[triple.sub][triple.pre]) == 0:
            del container[triple.sub][triple.pre]
        if len(container[triple.sub]) == 0:
            del container[triple.sub]

    def query_by_pattern(self, pattern, wildcard='?'):
        """Query triplestore for given pattern.

        Args:
            pattern (Triple): Triple containing pattern.
            wildcard (str): String to be used as wildcard.

        Returns:
            results (list): List containing all triples that matches with the
                            pattern.
        """
        results = []

        try:
            if pattern.sub != wildcard:
                if pattern.pre != wildcard:
                    # sub pre obj
                    if pattern.obj != wildcard:
                        if pattern.obj in self._spo[pattern.sub][pattern.pre]:
                            results.append(Triple(pattern.sub, pattern.pre,
                                           pattern.obj))
                    # sub pre wildcard
                    else:
                        for obj in self._spo[pattern.sub][pattern.pre]:
                            results.append(Triple(pattern.sub, pattern.pre,
                                           obj))
                else:
                    # sub wildcard obj
                    if pattern.obj != wildcard:
                        for pre in self._osp[pattern.obj][pattern.sub]:
                            results.append(Triple(pattern.sub, pre,
                                           pattern.obj))
                    else:
                        # sub wildcard wildcard
                        for pre, objs in self._spo[pattern.sub].items():
                            for obj in objs:
                                results.append(Triple(pattern.sub, pre, obj))
            else:
                if pattern.pre != wildcard:
                    # wildcard pre obj
                    if pattern.obj != wildcard:
                        for sub in self._pos[pattern.pre][pattern.obj]:
                            results.append(Triple(sub, pattern.pre,
                                           pattern.obj))
                    # wildcard pre wildcard
                    else:
                        for obj, subs in self._pos[pattern.pre].items():
                            for sub in subs:
                                results.append(Triple(sub, pattern.pre, obj))
                else:
                    # wildcard wildcard obj
                    if pattern.obj != wildcard:
                        for sub, pres in self._osp[pattern.obj].items():
                            for pre in pres:
                                results.append(Triple(sub, pre, pattern.obj))
                    # wildcard wildcard wildcard
                    else:
                        for sub, pres in self._spo.items():
                            for pre, objs in pres.items():
                                for obj in objs:
                                    results.append(Triple(sub, pre, obj))
        except KeyError:
            pass

        return results


class JSONTriplestore(Triplestore):
    """Implements JSON persistence for a triplestore."""

    def save(self, path='my-ts.txt'):
        """Save triplestore in a JSON file at path (relative).

        Args:
            path (str): Relative path to file destination.

        Returns:
            None.
        """
        json_triplestore = jsonpickle.encode(self)
        destination = os.path.join(os.getcwd(), path)
        with open(destination, mode='w') as output_file:
            output_file.write(json_triplestore)

    def load(self, path='my-ts.txt'):
        """Load triplestore from JSON file at path (relative).

        Args:
            path (str): Relative path to source file.

        Returns:
            triplestore (JSONTriplestore): Decoded Triplestore object.
        """
        source_file = os.path.join(os.getcwd(), path)
        with open(source_file, mode='r') as source:
            json = source.read()
            return jsonpickle.decode(json)
