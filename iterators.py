import random
from typing import Iterator, TypeVar
import control
from instruction import note

include_last = 0.0001

class Parallel:

    def __init__(self, iterator):
        self.iterator = iter(iterator)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.iterator)

    def kind(self):
        return "parallel"


class Series:

    def __init__(self, iterator):
        self.iterator = iter(iterator)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.iterator)

    def kind(self):
        return "series"


class Infinite:

    def __init__(self):
        self.iterator = iter(range(0, 100))

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.iterator)

    def kind(self):
        return "infinite"


A = TypeVar("A")


def shuffle(xs: list[A]) -> list[A]:
    if control.MODE == control.Execute():
        random.shuffle(xs)
    note(f"In the real experiment, {xs} is shuffled.")
    return xs
