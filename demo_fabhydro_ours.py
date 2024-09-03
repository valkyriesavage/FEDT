from numpy import arange

from instruction import instruction
from iterators import Series, Parallel, include_last
from measurement import BatchMeasurements
from design import VolumeFile
from decorator import fedt_experiment
from flowchart_render import render_flowchart
from lib import *

def summarize(data):
    return "Oh wow, great data!"


@fedt_experiment
def resin_types():
    stl = VolumeFile('bellows_1mm.stl')

    compression_results = BatchMeasurements.empty()
    tension_results = BatchMeasurements.empty()
    for resin in Parallel(['standard','tenacious','f39/f69']):
        fabbed_object = Printer.slice_and_print(stl, material=resin)
        instruction(f"compress object #{fabbed_object.uid} as much as possible (?)") # with what? how much?
        compression_results += Calipers.measure_size(fabbed_object,"height after compression")
        instruction(f"extend object #{fabbed_object.uid} as much as possible (?)") # with what? how much?
        tension_results += Calipers.measure_size(fabbed_object,"height after stretching")
    
    summarize(compression_results.get_all_data())
    summarize(tension_results.get_all_data())


@fedt_experiment
def bend_vs_thickness():

    bend_results = BatchMeasurements.empty()

    for thickness in Parallel(arange(1,5.5+include_last,.5)):
        stl = StlEditor.cube((20,30,thickness))
        fabbed_object = Printer.slice_and_print(stl)
        instruction(f"fix object #{fabbed_object.uid} at one end and hang a load of 0.49N at the other end")
        bend_results += Protractor.measure_angle(fabbed_object,"angle of tip below 90 degrees")
        # measurements were repeated multiple times. this was improvised!
        # used a camera which was fixed to take pictures, then measured pixels on the images.
        # ...but this is not always accurate. the error bars come from that repetition.

    # were these measurements repeated? were the prints repeated? there are error bars but I'm not sure what from

    summarize(bend_results.get_all_data())

@fedt_experiment
def min_wall_thickness():

    pressure_results = BatchMeasurements.empty()

    base_stl = VolumeFile("wall_thickness_test.stl")
    for orientation in Parallel([0,90]):
        stl = StlEditor.rotate(base_stl, orientation)
        for repetition in Parallel(range(3)):
            fabbed_object = Printer.slice_and_print(stl, repeitition=repetition)
            instruction(f"inflate object #{fabbed_object.uid} until it ruptures")
            pressure_results += PressureSensor.measure_pressure(fabbed_object,"pressure at rupture")

    summarize(pressure_results.get_all_data())

@fedt_experiment
def min_wall_spacing():
    # not clear what the experiment was? they say "Based on our printing test, ..."
    # was trying to shrink into minimum unit. changing spacings by .1 mm during the study, looking for failure
    summarize("1.4mm")

@fedt_experiment
def min_thin_wall_area():
    expansion_results = BatchMeasurements.empty()

    for edge_length in Parallel(arange(6,15+include_last)):
        stl_loc = Human.do_and_respond(f"create an STL with edge length {edge_length}, thin wall 0.7mm, other walls 5mm",
                                          "where is the STL?")
        stl = VolumeFile(stl_loc)
        fabbed_object = Printer.slice_and_print(stl)
        instruction("pump 20psi into the fabricated object")
        expansion_results += Calipers.measure_size(fabbed_object,"vertical expansion height")

    summarize(expansion_results.get_all_data())
 
@fedt_experiment
def pneumatic_vs_hydraulic():
    # this reads more like a demonstration than an experiment; not sure how to classify it
    # scientifically, air compresses more than liquid, and we know the effect. this is more of a demonstration.
    # not trying to report numbers.
    # pre-knowledge: there would be a huge difference, but unclear how much.
    expansion_results = BatchMeasurements.empty()

    stl = VolumeFile("single_actuator_single_generator.stl")
    for fill in Parallel(['water','air']):
        fabbed_object = Printer.slice_and_print(stl)
        filled_object = Human.post_process(fabbed_object,f"fill object with {fill}")
        expansion_results += Calipers.measure_size(filled_object,"displacement of tip")

    summarize(expansion_results.get_all_data())

@fedt_experiment
def lasting():
    # this actually didn't happen in 16 days, because we couldn't print 48 of them in a single day.
    # 4-5 per layer in a printer, 2-3 hours for a print. only 20 per day, and it was used for other stuff
    # measuring based on the day that the cube was printed.
    stl = VolumeFile("side_11mm_wall_1mm.stl")
    fabbed_objects = []
    for repetition in Parallel(range(48)):
        fabbed_objects.append(Printer.slice_and_print(stl, repetition=repetition))

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
    # render_flowchart(resin_types)
    # render_flowchart(bend_vs_thickness)
    # render_flowchart(min_wall_thickness)
    # render_flowchart(min_wall_spacing)
    # render_flowchart(min_thin_wall_area)
    # render_flowchart(pneumatic_vs_hydraulic)
    render_flowchart(lasting) # crashes
    #print(lasting())