from instruction import instruction
from iterators import Parallel, Series, Infinite, shuffle
from measurement import Measurements
from fabricate import RealWorldObject
from decorator import fedt_experiment
from lib import *
from itertools import tee


def summarize(data):
    return "Oh wow, great data!"


@fedt_experiment
def my_experiment1():
    instruction("Check that wood is in the bed.")
    fabbed_objects: list[RealWorldObject] = []
    offsets = shuffle(list(range(1, 5)))
    for (i, focal_offset_height_mm) in Parallel(enumerate(offsets)):
        fabbed_objects.append(
            Laser.fab(
                LineFile(f"{i}.svg"),
                focal_height_mm = focal_offset_height_mm,
                material="wood"))
    results = Measurements.empty()
    for fabbed_object in Series(fabbed_objects):
        results += Multimeter.measure_resistance(fabbed_object)
    data = results.get_data()
    return summarize(data)

@fedt_experiment
def my_experiment2():
    instruction("Check that wood is in the bed.")
    results = Measurements.empty()
    fabbed_objects = []
    for repetition in Parallel(range(4)):
        for ripetition in Parallel(range(4)):
            for ropetition in Parallel(range(4)):
                fabbed_object = RealWorldObject(random.randint(0,100),{"woo":"yeah"})
                fabbed_objects.append(fabbed_object)
                results += Multimeter.measure_resistance(fabbed_object)
    data = results.get_data()
    return summarize(data)

@fedt_experiment
def my_experiment3():
    snowman = Laser.fab(LineFile('snowman.svg'))

    current_measures = Measurements.empty()
    instruction('connect a 1kOhm resistor to the plate')
    for time_elapsing in Infinite(range(10000)):
        current = Multimeter.measure_current(snowman)
        timestamp = Timestamper.get_ts(snowman)
        current_measures += current
        current_measures += timestamp
        if current.get_data() == 0: # TODO how to do this in FEDT?
            # we are done
            break

    summarize(current_measures.get_data())


if __name__ == "__main__":
    print(my_experiment2())
