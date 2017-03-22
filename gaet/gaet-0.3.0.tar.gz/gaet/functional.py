from typing import Iterable, Optional, TypeVar

T = TypeVar('T')

def ffirst(xs: Iterable[Iterable[T]]) -> Optional[T]:
    realised = list(xs)
    if realised:
        return list(realised[0])[0]
    else:
        return None

def identity(x: T) -> T:
    return x
