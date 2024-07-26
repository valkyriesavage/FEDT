import math

from instruction import instruction
from measurement import Measurements
from fabricate import RealWorldObject
from decorator import fedt_experiment
from lib import *


def summarize(data):
    return "Oh wow, great data!"


@fedt_experiment
def test_height_vs_focal_point():
    # TODO: when we initialize the laser, we should probably tell it about all the cut variables we plan to send so we can build that run file. static analysis?
    # setting_names = Laser.prep_cam(cut_speeds, cut_powers, whatever)
    # for cut_speed in cut_speeds:
    #   for cut_power in cut_powers:
    #       setting_names[Laser.generate_setting_key(cut_power=cut_power,cut_speed=cut_speed)]
    #       fabbed_objects.append(Laser.circ_wood_fab(line_file, ...))

    line_file = SvgEditor.build_geometry(SvgEditor.draw_circle)
    instruction("Check that wood is in the bed.")
    fabbed_objects: list[RealWorldObject] = []
    for focal_height_mm in range(1, 5):
        fabbed_objects.append(
            Laser.circwood_fab(line_file, focal_height_mm=focal_height_mm))
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
        fabbed_object = Laser.circwood_fab(line_file, focal_height_mm=Laser.default_laser_settings[Laser.FOCAL_HEIGHT_MM], num_scans=num_scans)
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


if __name__ == "__main__":
    print(test_optimal_number_of_scans())
