import random

from numpy import arange

from instruction import instruction
from measurement import BatchMeasurements
from decorator import fedt_experiment
from flowchart_render import render_flowchart
from iterators import Parallel, Series, include_last, shuffle
from lib import *

include_last = .001

def summarize(data):
    return "Oh wow, great data!"

class CustomCapacitanceSystem:
    capacitances = [Measurement(
        name="capacitance",
        description="The capacitance of the object on a specific electrode.",
        procedure="""
            Have the user touch the object, then capture the output.
            """,
        units="pF",
        feature=f"electrode {i}") for i in range(7)]

    @staticmethod
    def measure_capacitances(obj: RealWorldObject, feature: str='') -> BatchMeasurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        return BatchMeasurements.multiple(obj, set(CustomCapacitanceSystem.capacitances))

def latinsquare(n):  
    k = n + 1
    sq = []
    for i in range(1, n + 1, 1):
        sqrw = []
        temp = k  
        while (temp <= n) : 
            sqrw.append(temp)
            temp += 1
        for j in range(1, k): 
            sqrw.append(j)
        k -= 1
        sq.append(sqrw)
    return sq

PYRAMID = None

def get_pyramid():
    global PYRAMID
    fabbed_object = PYRAMID
    if PYRAMID is None:
        geometry_file = GeometryFile("pyramid.stl")

        for coverage_condition in Parallel(['high','low']):
            for distance_condition in Parallel(['near','far']):
                for mirror_condition in Parallel(range(1,2)):
                    StlEditor.modify_design(geometry_file, "electrode", "coverage {coverage_condition} and distance {distance_condition}")

        fabbed_object = Printer.fab(geometry_file)

    PYRAMID = fabbed_object
    return PYRAMID

@fedt_experiment
def placement_response():
    electrodes = list(range(7))

    fabbed_object = get_pyramid()
    
    raw_results = BatchMeasurements.empty()
    test_values = BatchMeasurements.empty()

    for participant in Parallel(range(12)):
        for repetition in Series(range(1)):
            # the same number of repetitions per participant, but not sure of the number
            User.do(fabbed_object, f"touch electrode #{random.choice(electrodes)}, rep #{repetition}", participant)
        for touch in Series(latinsquare(len(electrodes))[participant % len(electrodes)]):
            User.do(fabbed_object, f"touch electrode #{touch}", participant)
            raw_results += CustomCapacitanceSystem.measure_capacitances(fabbed_object)
            test_values += CustomCapacitanceSystem.measure_capacitances(fabbed_object)

    summarize(raw_results.get_all_data())
    # some processing to the test values...
    summarize(test_values.get_all_data())

@fedt_experiment
def force_response():
    fabbed_object = get_pyramid()

    ground_truth = BatchMeasurements.empty()
    test_values = BatchMeasurements.empty()

    forces = list(arange(10,90+include_last,20))

    for participant in Parallel(range(12)):
        for force_level in Parallel([0,100]):
            User.do(fabbed_object, f"touch electrode #3 with {force_level}% force", participant)
            ground_truth += CustomCapacitanceSystem.measure_capacitances(fabbed_object)
        seven_repetitions = forces*7
        for force in Series(shuffle(seven_repetitions)):
            User.do(fabbed_object, f"touch with force {force}", participant)
            test_values += CustomCapacitanceSystem.measure_capacitances(fabbed_object)

    summarize(ground_truth.get_all_data())
    # some processing to the test_values...
    summarize(test_values.get_all_data())


if __name__ == "__main__":
    render_flowchart(placement_response)
    render_flowchart(force_response)