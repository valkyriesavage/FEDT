from numpy import arange

from instruction import instruction
from iterators import Series, Parallel, include_last
from measurement import BatchMeasurements
from design import GeometryFile
from decorator import fedt_experiment
from flowchart_render import render_flowchart
from lib import *

def summarize(data):
    return "Oh wow, great data!"

aline_defaults = {
    Slicer.TEMPERATURE: 200,
    Slicer.SPEED: 5000,
    Slicer.BED_HEAT: 0,
    Slicer.LAYER_HEIGHT: '0.1 mm',
    Slicer.NOZZLE: '0.4 mm'
}

@fedt_experiment
def cross_section_ratios():

    stl = StlEditor.cube((4,4,60))
    results = BatchMeasurements.empty()

    for bending_direction in Parallel(['d7','d8 and d6','d1 and d5','d3','d2 and d4']):
        for cross_section_ratio in Parallel(arange(1,8+include_last)):
            for repetition in Parallel(range(3)):
                fabbed_object = Printer.fab(stl,
                                            direction = bending_direction,
                                            cross_section_ratio = cross_section_ratio,
                                            repetition = repetition,
                                            defaults=aline_defaults)
                actuated_object = Human.post_process(fabbed_object, "trigger the object in hot water")
                results += Protractor.measure_angle(actuated_object, "triggered angle")
    
    summarize(results.get_all_data())


@fedt_experiment
def bend_vs_thickness():

    results = BatchMeasurements.empty()

    for thickness in Parallel(arange(1,6+include_last)):
        stl = StlEditor.cube((thickness,thickness,60))
        for bending_direction in Parallel(['diagonal','orthogonal']):
                fabbed_object = Printer.fab(stl,
                                            direction = bending_direction,
                                            defaults=aline_defaults)
                actuated_object = Human.post_process(fabbed_object, "trigger the object in hot water")
                results += Protractor.measure_angle(actuated_object, "triggered angle")

    summarize(results.get_all_data())

if __name__ == "__main__":
    render_flowchart(cross_section_ratios)
    render_flowchart(bend_vs_thickness)
