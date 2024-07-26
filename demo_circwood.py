import math

from numpy import arange

from instruction import instruction
from measurement import Measurements
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

    line_file = SvgEditor.build_geometry(SvgEditor.draw_circle)
    instruction("Check that wood is in the bed.")
    fabbed_objects: list[RealWorldObject] = []
    for focal_height_mm in range(0, 5):
        fabbed_objects.append(
            Laser.fab(line_file, focal_height_mm=focal_height_mm))
    results = Measurements.empty()
    for fabbed_object in fabbed_objects:
        results += Multimeter.measure_resistance(fabbed_object)
    data = results.get_data()
    return summarize(data)

@fedt_experiment
def test_height_vs_focal_point():
    line_file = SvgEditor.build_geometry(SvgEditor.draw_circle)
    instruction("Check that wood is in the bed.")
    fabbed_objects: list[RealWorldObject] = []
    for focal_height_mm in range(0, 5):
        fabbed_objects.append(
            Laser.fab(line_file, focal_height_mm=focal_height_mm))
    results = Measurements.empty()
    for fabbed_object in fabbed_objects:
        results += Multimeter.measure_resistance(fabbed_object)
    data = results.get_data()
    return summarize(data)


@fedt_experiment
def test_optimal_number_of_scans():
    line_file = SvgEditor.build_geometry(SvgEditor.draw_circle)
    instruction("Check that wood is in the bed.")
    results = Measurements.empty()
    resistance = None
    best_result = math.inf
    num_scans = 0
    while(True):
        num_scans += num_scans
        fabbed_object = Laser.fab(line_file, num_scans=num_scans) # is this the right way to do this? in a single function with the previous one?
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
    data = results.get_data()
    return summarize(data)

@fedt_experiment
def test_laser_power_and_speed():
    speeds = arange(20,81,10)
    powers = arange(10,51,5)
    setting_names = Laser.prep_cam(speeds, powers)

    line_file = SvgEditor.build_geometry(SvgEditor.draw_circle)
    instruction("Check that wood is in the bed.")
    results = Measurements.empty()

    for cut_speed in speeds:
      for cut_power in powers:
          for repetition in range(4):
            fabbed_object = Laser.fab(line_file, setting_names, cut_speed, cut_power, color_to_setting=Laser.GREEN)
            resistance = Multimeter.measure_resistance(fabbed_object)
            results += resistance
    summarize(results)

@fedt_experiment
def test_grain_direction():
    line_file = SvgEditor.build_geometry(SvgEditor.draw_circle)
    instruction("Check that wood is in the bed.")
    fabbed_objects: list[RealWorldObject] = []
    for orientation in ["orthogonal","along grain"]:
        fabbed_objects.append(
            Laser.fab(line_file, orientation=orientation)) # TODO need to add tracking of orientation to this function
    results = Measurements.empty()
    for fabbed_object in fabbed_objects:
        results += Multimeter.measure_resistance(fabbed_object)
    data = results.get_data()
    return summarize(data)

@fedt_experiment
def test_change_over_time():
    line_file = SvgEditor.design()
    fabbed_objects = []
    '''
    for post_process_condition in ['varnished','unvarnished']:
    	for repetition in range(1, 4):
    		fabbed_object = Laser.fab_tracked(line_file)
    		fabbed_object = post_process(fabbed_object, post_process_condition)
    		fabbed_objects.push(fabbed_object)
    results = []
    for wait_months in range(1, 6):
    	wait_up_to_months(wait_months)
    	for fabbed_object in fabbed_objects:
    		results.push(multimeter.measure_resistance(fabbed_object))
    summarize(results)'''

if __name__ == "__main__":
    print(test_height_vs_focal_point())
