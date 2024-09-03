import math

from numpy import arange

from instruction import instruction
from iterators import Series, Parallel, include_last
from control import Execute, Evaluate
from measurement import BatchMeasurements
from fabricate import RealWorldObject
from flowchart_render import render_flowchart
from decorator import fedt_experiment
from lib import *


def summarize(data):
    return "Oh wow, great data!"


@fedt_experiment
def test_density_and_materials():
    results = BatchMeasurements.empty()
    for ruffle_design in Parallel(['default', 'wide', 'dense']):
        ruffle_file = SvgEditor.design(ruffle_design)
        for material in Parallel(['flipchart', 'office paper', 'plastic']):
            for load_direction in Parallel(['X','Y']): # unclear if different objects were used for X and Y or not (series? parallel?)
                fabbed_object = Laser.fab(ruffle_file, material=material)
                fabbed_object = Human.post_process(fabbed_object, "assemble matched ruffles")
                loads = [0,10,20,50,100,200]
                results += Calipers.measure_size(fabbed_object,'height at rest in {load_direction}')
                fabbed_object = Human.post_process(fabbed_object, "apply acrylic plate in {load_direction}")
                for current_load in Series(loads):
                    results += Calipers.measure_size(fabbed_object,f'height at load {current_load} in {load_direction}')
                    if not Human.is_reasonable(fabbed_object):
                        break
                    fabbed_object = Human.post_process(fabbed_object, f"apply load {current_load} in {load_direction}")
                fabbed_object = Human.post_process(fabbed_object, "remove all loads")
                results += Calipers.measure_size(fabbed_object,'height at unload in {load_direction}')

    summarize(results.get_all_data())

@fedt_experiment
def design_versus_stiffness():
    results = BatchMeasurements.empty()
    tab_conditions_files = [("cut tabs", LineFile("default_ruffle_cuttabs.svg")),
                            ("no tabs + tape", LineFile("default_ruffle_notabs.svg"))]
    loads = [0,10,20,50,100,200]

    for tab_condition, ruffle_file in Parallel(tab_conditions_files):
        for load_direction in Parallel(['X','Y']): # unclear if different objects were used for X and Y or not
            fabbed_object = Laser.fab(ruffle_file, material="160g paper")
            fabbed_object = Human.post_process(fabbed_object, f"assemble matched ruffles with {tab_condition}")
            results += Calipers.measure_size(fabbed_object,'height at rest in {load_direction}')
            fabbed_object = Human.post_process(fabbed_object, "apply acrylic plate in {load_direction}")
            is_reasonable = True
            current_load = 0
            while is_reasonable:
                results += Calipers.measure_size(fabbed_object,f'height at load {loads[current_load]} in {load_direction}')
                fabbed_object = Human.is_reasonable(fabbed_object)
                is_reasonable = fabbed_object.metadata["human reasonableness check"]
                current_load += 1
                fabbed_object = Human.post_process(fabbed_object, f"apply load {loads[current_load]} in {load_direction}")
                # how did they determine how much load to add?
            # then relax it
            fabbed_object = Human.post_process(fabbed_object, "remove all loads")
            results += Calipers.measure_size(fabbed_object,f'height at unload in {load_direction}')

    summarize(results.get_all_data())

if __name__ == "__main__":
    #render_flowchart(test_density_and_materials) # broken due to too many loops
    render_flowchart(design_versus_stiffness) # broken due to too many loops
