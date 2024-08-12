import math

from numpy import arange

import control
from control import Execute, Evaluate
from instruction import instruction
from iterators import Parallel, Series, Infinite, include_last
from measurement import BatchMeasurements
from fabricate import RealWorldObject
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

    line_file = SvgEditor.build_geometry(SvgEditor.draw_circle)
    fabbed_objects: list[RealWorldObject] = []
    for material in Parallel(materials):
        for coating in Parallel(coatings):
            instruction(f"get a piece of {material} with coating {coating}")
            fabbed_objects.append(Laser.fab(line_file, material=material, coating=coating))
            # not completely sure how to capture what they did here... it seems like
            # they did some experimentation, but it's not really documented?
    results = BatchMeasurements.empty()
    for fabbed_object in Parallel(fabbed_objects):
        results += Multimeter.measure_resistance(fabbed_object)
    data = results.get_all_data()
    return summarize(data)

@fedt_experiment
def test_height_vs_focal_point():
    line_file = SvgEditor.build_geometry(SvgEditor.draw_circle)
    fabbed_objects: list[RealWorldObject] = []
    for focal_height_mm in Parallel(range(0, 5+include_last)):
        fabbed_objects.append(
            Laser.fab(line_file, focal_height_mm=focal_height_mm))
    results = BatchMeasurements.empty()
    for fabbed_object in Parallel(fabbed_objects):
        results += Multimeter.measure_resistance(fabbed_object)
    data = results.get_all_data()
    return summarize(data)


@fedt_experiment
def test_optimal_number_of_scans():
    line_file = SvgEditor.build_geometry(SvgEditor.draw_circle)
    results = BatchMeasurements.empty()
    resistance = None
    best_result = None
    for num_scans in Infinite(0): # TODO fix this
        fabbed_object = Laser.fab(line_file, num_scans=num_scans)
        resistance = Multimeter.measure_resistance(fabbed_object)
        results += resistance
        if not best_result:
            best_result = resistance
        if Multimeter.lower_resistance(resistance, best_result):
            # we are getting better
            best_result = resistance
        else:
            # we are getting worse
            break
    data = results.get_all_data()
    return summarize(data)

@fedt_experiment
def test_laser_power_and_speed():
    speeds = arange(20,80+include_last,10)
    powers = arange(10,50+include_last,5)
    setting_names = Laser.prep_cam(cut_speeds=speeds, cut_powers=powers)

    line_file = SvgEditor.build_geometry(SvgEditor.draw_circle)
    results = BatchMeasurements.empty()

    for cut_speed in Parallel(speeds):
      for cut_power in Parallel(powers):
          for repetition in Parallel(range(4)):
            fabbed_object = Laser.fab(line_file, setting_names, cut_speed, cut_power, color_to_setting=Laser.SvgColor.GREEN)
            resistance = Multimeter.measure_resistance(fabbed_object)
            results += resistance
    summarize(results.get_all_data())

@fedt_experiment
def test_grain_direction():
    line_file = SvgEditor.build_geometry(SvgEditor.draw_circle)
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
    line_file = SvgEditor.build_geometry(SvgEditor.draw_circle)
    fabbed_objects = []
    for post_process_condition in Parallel(['varnished','unvarnished']):
        for repetition in Parallel(range(4)):
            fabbed_object = Laser.fab(line_file)
            fabbed_objects.append(Human.post_process(fabbed_object, post_process_condition))
    results = BatchMeasurements.empty()
    for wait_months in Series(range(1, 6)):
        fabbed_objects = Environment.wait_up_to_time_multiple(fabbed_objects, num_months=wait_months)
        for fabbed_object in fabbed_objects:
            results += Multimeter.measure_resistance(fabbed_object)
    summarize(results.get_all_data())

if __name__ == "__main__":
    #control.MODE = Execute()
    Laser.default_laser_settings[Laser.MATERIAL] = 'wood'
    print(test_optimal_number_of_scans())
