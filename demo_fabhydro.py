from numpy import arange

from instruction import instruction
from iterators import Series, Parallel, include_last
from measurement import BatchMeasurements, ImmediateMeasurements
from design import GeometryFile
from decorator import fedt_experiment
from flowchart_render import render_flowchart
from lib import *

def summarize(data):
    return "Oh wow, great data!"


@fedt_experiment
def resin_types():
    stl = GeometryFile('bellows_1mm_priorwork_recompiled.stl')

    compression_results = BatchMeasurements.empty()
    tension_results = BatchMeasurements.empty()
    for resin in Parallel(['standard','tenacious','f39/f69']):
        fabbed_object = Printer.fab(stl, material=resin)
        instruction(f"compress object #{fabbed_object.uid} as much as possible")
        compression_results += Human.judge_something(fabbed_object, "height after squishing is good")
        compression_results += Human.judge_something(fabbed_object, "speed of squshing is good")
        instruction(f"extend object #{fabbed_object.uid} as much as possible")
        compression_results += Human.judge_something(fabbed_object, "height after stretching is good")
        compression_results += Human.judge_something(fabbed_object, "speed of stretching is good")
    
    summarize(compression_results.get_all_data())
    summarize(tension_results.get_all_data())


@fedt_experiment
def bend_vs_thickness():

    bend_results = BatchMeasurements.empty()

    for thickness in Parallel(arange(1,5.5+include_last,.5)):
        stl = StlEditor.cube((20,30,thickness))
        fabbed_object = Printer.fab(stl)
        for repetition in Series(arange(1,3+include_last)): # it was somewhat unofficial how many times each was repeated
            instruction(f"fix object #{fabbed_object.uid} at one end and hang a load of 0.49N at the other end")
            instruction("take a photo of the object and use a protractor on the image")
            bend_results += Protractor.measure_angle(fabbed_object,"angle of tip below 90 degrees")

    summarize(bend_results.get_all_data())

@fedt_experiment
def min_wall_thickness():

    pressure_results = BatchMeasurements.empty()

    base_stl = GeometryFile("wall_thickness_test.stl")
    for orientation in Parallel([0,90]):
        stl = StlEditor.rotate(base_stl, orientation)
        for repetition in Parallel(range(3)):
            fabbed_object = Printer.fab(stl, repeitition=repetition)
            instruction(f"inflate object #{fabbed_object.uid} until it ruptures")
            pressure_results += PressureSensor.measure_pressure(fabbed_object,"pressure at rupture")

    summarize(pressure_results.get_all_data())

@fedt_experiment
def min_wall_spacing():
    acceptability_results = ImmediateMeasurements.empty()
    base_stl = GeometryFile("thin_wall.stl")
    neighbours_separated = True
    separation = 2.5
    while neighbours_separated:
        printing_stl = StlEditor.modify_design(base_stl, "spacing between copies", separation)
        fabbed_object = Printer.fab(printing_stl)
        neighbours_separated = acceptability_results.do_measure(fabbed_object,
                                                                TrueFalser.truefalse.set_feature("did the neighbouring cubes separate?"))
        if neighbours_separated:
            separation -= .1

    summarize(acceptability_results)

@fedt_experiment
def min_thin_wall_area():
    expansion_results = BatchMeasurements.empty()

    for edge_length in Parallel(arange(6,15+include_last)):
        stl = StlEditor.create_design({'edge_length': edge_length, 'thin wall': '0.7mm', 'other walls': '5mm'})
        fabbed_object = Printer.fab(stl)
        instruction("pump 20psi into the fabricated object")
        expansion_results += Calipers.measure_size(fabbed_object,"vertical expansion height")

    summarize(expansion_results.get_all_data())

@fedt_experiment
def lasting():
    # this actually didn't happen in 16 days, because we couldn't print 48 of them in a single day.
    # 4-5 per layer in a printer, 2-3 hours for a print. only 20 per day, and it was used for other stuff
    # measuring based on the day that the cube was printed. : this is not possible to encode currently.
    stl = GeometryFile("side_11mm_wall_1mm.stl")
    fabbed_objects = []
    for repetition in Parallel(range(48)):
        fabbed_objects.append(Printer.fab(stl, repetition=repetition))

    pre_weights = BatchMeasurements.empty()
    post_weights = BatchMeasurements.empty()

    cubes_per_day = 3
    for day in Series(range(16)):
        Environment.wait_up_to_time_multiple(fabbed_objects, num_days=day)
        cubes = fabbed_objects[day*cubes_per_day:(day+1)*cubes_per_day]
        for cube in Parallel(cubes):
            pre_weights += Scale.measure_weight(cube)
            leaked_cube = Human.post_process(cube, f"cut open the cube and let the fluid leak out")
            post_weights += Scale.measure_weight(leaked_cube)

    summarize([pre_weights.get_all_data(),post_weights.get_all_data()])

if __name__ == "__main__":
    render_flowchart(resin_types)
    render_flowchart(bend_vs_thickness)
    render_flowchart(min_wall_thickness)
    render_flowchart(min_wall_spacing)
    render_flowchart(min_thin_wall_area)
    render_flowchart(lasting)
    #print(lasting())