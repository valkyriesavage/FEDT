import math

from numpy import arange

import control
from control import Execute, Evaluate
from instruction import instruction
from iterators import Parallel, Series, Infinite, include_last
from measurement import BatchMeasurements, ImmediateMeasurements
from fabricate import RealWorldObject
from flowchart_render import render_flowchart
from decorator import fedt_experiment
from lib import *


def summarize(data):
    return "Oh wow, great data!"


@fedt_experiment
def test_materials():
    materials = ["lauan solid wood", "lauan plywood", "Japanese cypress",
                         "paulownia", "Magnolia obovata", "Japanese cedar", "basswood",
                         "beech", "oak", "walnut"]
    coatings = ['fire retardant', 'no coating']

    line_file = SvgEditor.build_geometry(SvgEditor.draw_line)
    fabbed_objects: list[RealWorldObject] = []
    for material in Parallel(materials):
        for coating in Parallel(coatings):
            instruction(f"get a piece of {material} with coating {coating}")
            fabbed_objects.append(Laser.fab(line_file, material=material, coating=coating))
    results = BatchMeasurements.empty()
    for fabbed_object in Parallel(fabbed_objects):
        results += Multimeter.measure_resistance(fabbed_object)
    data = results.get_all_data()
    return summarize(data)

@fedt_experiment
def test_height_vs_focal_point():
    
    results = BatchMeasurements.empty()

    for focal_height_mm in Parallel(arange(0, 6+include_last)):
        line_file = SvgEditor.build_geometry(SvgEditor.draw_line,
                                             label_function=SvgEditor.labelcentre)
        fabbed_object = Laser.fab(line_file, focal_height_mm=focal_height_mm, material='wood')
        results += Multimeter.measure_resistance(fabbed_object)
    data = results.get_all_data()
    return summarize(data)


@fedt_experiment
def test_optimal_number_of_scans():
    line_file = SvgEditor.build_geometry(SvgEditor.draw_line)
    results = ImmediateMeasurements.empty()
    resistance = 9999999999
    best_result = resistance
    num_scans = 0
    while resistance == best_result:
        num_scans = num_scans + 1
        fabbed_object = Laser.fab(line_file, num_scans=num_scans, material='wood')
        instruction("leave the material in the bed in between")
        resistance = results.do_measure(fabbed_object, Multimeter.resistance)
        resistance = float(resistance) if resistance else best_result
        if not best_result or resistance < best_result:
            best_result = resistance

    data = results.dump_to_csv()
    return summarize(data)

@fedt_experiment
def test_laser_power_and_speed():
    speeds_powers = [(50,50),
                     (45,50),(45,60),(45,70),(45,80),
                     (40,50),(40,60),(40,70),(40,80),
                     (35,50),(35,60),(35,70),(35,80),
                     (30,50),(30,60),(30,70),
                     (25,50),(25,60),
                     (20,40),
                     (15,40),
                     (10,20),(10,30)]
    setting_names = Laser.prep_cam(cut_speeds=[speed for speed,power in speeds_powers],
                                   cut_powers=[power for speed,power in speeds_powers])

    line_file = SvgEditor.build_geometry(SvgEditor.draw_line)
    results = BatchMeasurements.empty()

    for cut_speed, cut_power in Parallel(speeds_powers):
        for repetition in Parallel(range(4)):
            fabbed_object = Laser.fab(line_file, setting_names=setting_names,
                                      cut_speed=cut_speed, cut_power=cut_power,
                                      color_to_setting=Laser.SvgColor.GREEN,
                                      repetition=repetition,
                                      material='wood')
            resistance = Multimeter.measure_resistance(fabbed_object)
            results += resistance
    summarize(results.get_all_data())

@fedt_experiment
def test_grain_direction():
    line_file = SvgEditor.design("a file with two perpendicular lines")
    fabbed_objects: list[RealWorldObject] = []
    for orientation in Parallel(["orthogonal","along grain"]):
        instruction("orient the wood {}".format(orientation))
        fabbed_objects.append(
            Laser.fab(line_file, orientation=orientation))
    results = BatchMeasurements.empty()
    for fabbed_object in Parallel(fabbed_objects):
        results += Multimeter.measure_resistance(fabbed_object)
    data = results.get_all_data()
    return summarize(data)

@fedt_experiment
def test_change_over_time():
    line_file = SvgEditor.build_geometry(SvgEditor.draw_line)
    fabbed_objects = []
    for post_process_condition in Parallel(['varnished','unvarnished']):
        for repetition in Parallel(range(4)):
            fabbed_object = Laser.fab(line_file, repetition=repetition)
            fabbed_objects.append(Human.post_process(fabbed_object, post_process_condition))
    results = BatchMeasurements.empty()
    for wait_months in Series(range(0, 6)):
        fabbed_objects = Environment.wait_up_to_time_multiple(fabbed_objects, num_months=wait_months)
        for fabbed_object in Parallel(fabbed_objects):
            results += Multimeter.measure_resistance(fabbed_object)
    summarize(results.get_all_data())

if __name__ == "__main__":
    render_flowchart(test_materials)
    render_flowchart(test_height_vs_focal_point)
    render_flowchart(test_optimal_number_of_scans)
    render_flowchart(test_laser_power_and_speed)
    render_flowchart(test_grain_direction)
    render_flowchart(test_change_over_time)
    # from control import MODE, Execute
    # control.MODE = Execute()
    # test_height_vs_focal_point()