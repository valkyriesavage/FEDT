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
def test_density_and_materials():

    # test impact of ruffle density and materials on compression
    results = Measurements.empty()
    for ruffle_design in ['default', 'wide', 'dense']:
        ruffle_file = SvgEditor.design(ruffle_design)
        for load_direction in ['X','Y']: # ? I'm not sure if this should be the outer loop or the inner one, were the same objects used?
            for material in ['flipchart', 'office paper', 'plastic']:
                instruction(f"ensure {material} is loaded in the lasercutter")
                fabbed_object = Laser.fab(ruffle_file, material=material)
                fabbed_object = Human.post_process(fabbed_object, "assemble matched ruffles")
                loads = [0,10,20,50,100,200]
                results += Calipers.measure_size(fabbed_object,'height at rest in {load_direction}')
                Human.post_process(fabbed_object, "apply acrylic plate in {load_direction}")
                current_load = 0
                while Human.is_reasonable(fabbed_object) and current_load < len(loads):
                    results += Calipers.measure_size(fabbed_object,f'height at load {loads[current_load]} in {load_direction}')
                    current_load += 1
                    Human.post_process(fabbed_object, f"apply load {loads[current_load]} in {load_direction}")
                    # how did they determine how much load to add?
                # then relax it
                Human.post_process(fabbed_object, "remove all loads")
                results += Calipers.measure_size(fabbed_object,'height at unload in {load_direction}')

    summarize(results.get_data())

@fedt_experiment
def design_versus_stiffness():
    results = Measurements.empty()
    ruffle_file = LineFile("default_ruffle.svg")
    for load_direction in ['X','Y']: # ? I'm not sure if this should be the outer loop or the inner one
        instruction("ensure 160g paper is loaded in the lasercutter")
        for tab_condition in ['cut tabs', 'engrave + tape']:
            fabbed_object = Laser.fab(ruffle_file, material="160g paper", tab_condition=tab_condition)
            fabbed_object = Human.post_process(fabbed_object, f"assemble matched ruffles with {tab_condition}")
            loads = [0,10,20,50,100,200]
            results += Calipers.measure_size(fabbed_object,'height at rest in {load_direction}')
            Human.post_process(fabbed_object, "apply acrylic plate in {load_direction}")
            current_load = 0
            while Human.is_reasonable(fabbed_object) and current_load < len(loads):
                results += Calipers.measure_size(fabbed_object,f'height at load {loads[current_load]} in {load_direction}')
                current_load += 1
                Human.post_process(fabbed_object, f"apply load {loads[current_load]} in {load_direction}")
                # how did they determine how much load to add?
            # then relax it
            Human.post_process(fabbed_object, "remove all loads")
            results += Calipers.measure_size(fabbed_object,'height at unload in {load_direction}')

    summarize(results.get_data())

if __name__ == "__main__":
    print(test_density_and_materials())
