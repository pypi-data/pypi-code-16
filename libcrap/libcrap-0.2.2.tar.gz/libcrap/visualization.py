from numpy import linspace

from typing import List, Iterable, Tuple, Callable, Any, TypeVar, Sequence


T1 = TypeVar('T1')
T2 = TypeVar('T2')


def _unzip(sequence_of_tuples: Iterable[Tuple[T1, ...]]) -> List[List[T1]]:
    '''Returns N lists where N is the size of tuples'''
    return list(zip(*list(sequence_of_tuples)))


def generate_points(
    func: Callable[[float], float],
    start: float, end: float, num: int
) -> Sequence[Sequence[float]]:
    """Takes a mathematical function on real numbers and generates
    points for plotting it.
    Returns a list of 2 lists. The first list is x coordinates, the second is
    y coordinates.
    """
    return _unzip((x, func(x)) for x in linspace(start, end, num))
