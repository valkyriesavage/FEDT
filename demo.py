from instruction import instruction
from measurement import Measurements
from fabricate import RealWorldObject
from decorator import fedt_experiment
from lib import *


def summarize(data):
    return "Oh wow, great data!"


@fedt_experiment
def my_experiment1():
    line_file = SvgEditor.design()
    instruction("Check that wood is in the bed.")
    fabbed_objects: list[RealWorldObject] = []
    for focal_offset_height_mm in range(1, 5):
        fabbed_objects.append(
            LaserSlicer.cam_and_fab(line_file, focal_offset_height_mm))
    results = Measurements.empty()
    for fabbed_object in fabbed_objects:
        results += Multimeter.measure_resistance(fabbed_object)
    data = results.get_data()
    return summarize(data)


@fedt_experiment
def my_experiment2():
    line_file = SvgEditor.design()
    instruction("Check that wood is in the bed.")
    results = Measurements.empty()
    for focal_offset_height_mm in range(1, 5):
        fabbed_object = LaserSlicer.cam_and_fab(line_file,
                                                focal_offset_height_mm)
        results += Multimeter.measure_resistance(fabbed_object)
    data = results.get_data()
    return summarize(data)


if __name__ == "__main__":
    print(my_experiment1())
