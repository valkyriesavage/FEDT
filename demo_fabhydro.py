from numpy import arange

from instruction import instruction
from measurement import Measurements
from design import VolumeFile
from decorator import fedt_experiment
from lib import *

include_last = .001

def summarize(data):
    return "Oh wow, great data!"


@fedt_experiment
def resin_types():
    stl = VolumeFile('bellows_1mm.stl')

    compression_results = Measurements.empty()
    tension_results = Measurements.empty()
    for resin in ['standard','tenacious','f39/f69']:
        fabbed_object = Printer.slice_and_print(stl, material=resin)
        instruction(f"compress object #{fabbed_object.uid} as much as possible (?)") # with what? how much?
        compression_results += Calipers.measure_size(fabbed_object,"height after compression")
        instruction(f"extend object #{fabbed_object.uid} as much as possible (?)") # with what? how much?
        tension_results += Calipers.measure_size(fabbed_object,"height after stretching")
    
    summarize(compression_results.get_data())
    summarize(tension_results.get_data())


@fedt_experiment
def bend_vs_thickness():

    bend_results = Measurements.empty()

    for thickness in arange(1,5.5+include_last,.5):
        stl = StlEditor.cube((20,30,thickness))
        fabbed_object = Printer.slice_and_print(stl)
        instruction(f"fix object #{fabbed_object.uid} at one end and hang a load of 0.49N at the other end")
        bend_results += Protractor.measure_angle(fabbed_object,"angle of tip below 90 degrees")

    # were these measurements repeated? were the prints repeated? there are error bars but I'm not sure what from

    summarize(bend_results.get_data())

@fedt_experiment
def min_wall_thickness():

    pressure_results = Measurements.empty()

    base_stl = VolumeFile("wall_thickness_test.stl")
    for orientation in [0,90]:
        stl = StlEditor.rotate(base_stl, orientation)
        for repetition in range(3):
            fabbed_object = Printer.slice_and_print(stl)
            pressure_results += PressureSensor.measure_pressure(fabbed_object,"pressure at rupture")

    summarize(pressure_results.get_data())

@fedt_experiment
def min_wall_spacing():
    # not clear what the experiment was? they say "Based on our printing test, ..."
    summarize("1.4mm")

@fedt_experiment
def min_thin_wall_area():

    expansion_results = Measurements.empty()

    for edge_length in arange(6,15+include_last):
        stl_loc = Human.do_and_respond(f"create an STL with edge length {edge_length}, thin wall 0.7mm, other walls 5mm",
                                          "where is the STL?")
        stl = VolumeFile(stl_loc)
        fabbed_object = Printer.slice_and_print(stl)
        instruction("pump 20psi into the fabricated object")
        expansion_results += Calipers.measure_size(fabbed_object,"vertical expansion height")

    summarize(expansion_results.get_data())
 
@fedt_experiment
def pneumatic_vs_hydraulic():
    # this reads more like a demonstration than an experiment; not sure how to classify it
    expansion_results = Measurements.empty()

    stl = VolumeFile("single_actuator_single_generator.stl")
    for fill in ['water','air']:
        fabbed_object = Printer.slice_and_print(stl)
        filled_object = Human.post_process(fabbed_object,f"fill object with {fill}")
        expansion_results += Calipers.measure_size(filled_object,"displacement of tip")

    summarize(expansion_results.get_data())

@fedt_experiment
def lasting():

    stl = VolumeFile("side_11mm_wall_1mm.stl")
    gcode = Slicer.slice(stl)
    fabbed_objects = []
    for repetition in range(48):
        fabbed_objects.append(Printer.print(gcode))

    pre_weights = Measurements.empty()
    post_weights = Measurements.empty()

    cubes_per_day = 3
    for day in range(16):
        Environment.wait_up_to_time_multiple(fabbed_objects, num_days=day)
        cubes = fabbed_objects[day*cubes_per_day:(day+1)*cubes_per_day]
        for cube in cubes:
            pre_weights += Scale.measure_weight(cube)
            leaked_cube = Human.post_process(cube, f"cut open the cube and let the fluid leak out")
            post_weights += Scale.measure_weight(leaked_cube)

    summarize([pre_weights.get_data(),post_weights.get_data()])

if __name__ == "__main__":
    print(min_thin_wall_area())
