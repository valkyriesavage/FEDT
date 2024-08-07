from instruction import instruction
from measurement import Measurements
from fabricate import RealWorldObject
from decorator import fedt_experiment
from lib import *
from itertools import tee


def summarize(data):
    return "Oh wow, great data!"


class Parallel:

    def __init__(self, iterator):
        left, right = tee(iter(iterator))
        self.cloned = left
        self.iterator = right

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.iterator)


@fedt_experiment
def my_experiment1():
    instruction("Check that wood is in the bed.")
    fabbed_objects: list[RealWorldObject] = []
    for (i, focal_offset_height_mm) in Parallel(enumerate(range(1, 5))):
        fabbed_objects.append(
            RealWorldObject(
                i, {"focal_offset_height_mm": focal_offset_height_mm}))
    results = Measurements.empty()
    for fabbed_object in fabbed_objects:
        results += Multimeter.measure_resistance(fabbed_object)
    data = results.get_data()
    return summarize(data)


@fedt_experiment
def my_experiment2():
    instruction("Check that wood is in the bed.")
    results = Measurements.empty()
    fabbed_objects = []
    for (i, focal_offset_height_mm) in Parallel(enumerate(range(1, 5))):
        fabbed_object = RealWorldObject(
            i, {"focal_offset_height_mm": focal_offset_height_mm})
        fabbed_objects.append(fabbed_object)
        results += Multimeter.measure_resistance(fabbed_object)
    data = results.get_data()
    return summarize(data)


if __name__ == "__main__":
    print(my_experiment1())
