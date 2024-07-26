from instruction import instruction
from measurement import Measurements
from fabricate import RealWorldObject
from decorator import fedt_experiment
from lib import *


def summarize(data):
    return "Oh wow, great data!"


@fedt_experiment
def test_height_vs_focal_point():
    mylaser = Laser() # TODO: when we initialize the laser, we should probably tell it about all the cut variables we plan to send so we can build that file. static analysis?

    line_file = SvgEditor.build_geometry(SvgEditor.draw_circle)
    instruction("Check that wood is in the bed.")
    fabbed_objects: list[RealWorldObject] = []
    for focal_height_mm in range(1, 5):
        fabbed_objects.append(
            mylaser.circ_wood_fab(line_file, focal_height_mm=focal_height_mm))
    results = Measurements.empty()
    for fabbed_object in fabbed_objects:
        results += Multimeter.measure_resistance(fabbed_object)
    data = results.get_data()
    return summarize(data)


@fedt_experiment
def test_optimal_number_of_scans():
    mylaser = Laser() # TODO: when we initialize the laser, we should probably tell it about all the cut variables we plan to send so we can build that file. static analysis?

    line_file = SvgEditor.build_geometry(SvgEditor.draw_circle)
    instruction("Check that wood is in the bed.")
    results = Measurements.empty()
    for focal_offset_height_mm in range(1, 5):
        fabbed_object = mylaser.circ_wood_fab(line_file,
                                              focal_offset_height_mm)
        results += Multimeter.measure_resistance(fabbed_object)
    data = results.get_data()
    return summarize(data)


if __name__ == "__main__":
    print(test_height_vs_focal_point())
