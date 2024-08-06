from numpy import arange

from instruction import instruction
from measurement import Measurements
from design import VolumeFile
from decorator import fedt_experiment
from lib import *

include_last = .001

def summarize(data):
    return "Oh wow, great data!"

def configure_for_aline():
    Slicer.default_slicer_settings[Slicer.TEMPERATURE] = 200
    Slicer.default_slicer_settings[Slicer.SPEED] = 5000
    Slicer.default_slicer_settings[Slicer.BED_HEAT] = 0
    Slicer.default_slicer_settings[Slicer.LAYER_HEIGHT] = 0.1
    Slicer.default_slicer_settings[Slicer.NOZZLE] = 0.4

@fedt_experiment
def cross_section_ratios():
    configure_for_aline()

    stl = StlEditor.cube((4,4,60))
    results = Measurements.empty()

    for bending_direction in ['d7','d8&d6','d1&d5','d3','d2&d4']:
        for cross_section_ratio in arange(1,8+include_last):
            for repetition in range(1,3):
                gcode = Slicer.slice(stl,
                                     direction = bending_direction,
                                     cross_section_ratio = cross_section_ratio)
                fabbed_object = Printer.print(gcode)
                actuated_object = Human.post_process(fabbed_object, "trigger the object in hot water")
                results += Protractor.measure_angle(actuated_object, "triggered angle")
    
    summarize(results.get_data())


@fedt_experiment
def bend_vs_thickness():
    configure_for_aline()

    results = Measurements.empty()

    for thickness in arange(1,6+include_last):
        stl = StlEditor.cube((thickness,thickness,60))
        for bending_direction in ['diagonal','orthogonal']:
                gcode = Slicer.slice(stl,
                                     direction = bending_direction)
                fabbed_object = Printer.print(gcode)
                actuated_object = Human.post_process(fabbed_object, "trigger the object in hot water")
                results += Protractor.measure_angle(actuated_object, "triggered angle")

    summarize(results.get_data())

if __name__ == "__main__":
    print(cross_section_ratios())
