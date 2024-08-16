import random

from numpy import arange

from instruction import instruction
from measurement import BatchMeasurements
from design import VolumeFile
from decorator import fedt_experiment
from flowchart_render import render_flowchart
from iterators import Parallel, Series, include_last
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

PYRAMID = Printer.slice_and_print(VolumeFile("pyramid.stl"))

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

@fedt_experiment
def placement_response():
    # geometry_file = VolumeFile("pyramid.stl")

    # for coverage_condition in ['high','low']:
    #     for distance_condition in ['near','far']:
    #         for mirror_condition in range(1,2):
    #             StlEditor.edit(geometry_file, f"add an electrode with coverage {coverage_condition} and distance {distance_condition}")

    electrodes = list(range(7))

    fabbed_object = PYRAMID
    raw_results = BatchMeasurements.empty()
    test_values = BatchMeasurements.empty()

    for participant in Parallel(range(10)):
        for repetition in range(1): # not sure how many random touches were required
            User.do(fabbed_object, f"touch electrode #{random.choice(electrodes)}, rep #{repetition}", participant)
        for touch in Series(latinsquare(len(electrodes))[participant % len(electrodes)]): # how was the square truncated?
            User.do(fabbed_object, f"touch electrode #{touch}", participant)
            raw_results += CustomCapacitanceSystem.measure_capacitances(fabbed_object)
            test_values += CustomCapacitanceSystem.measure_capacitances(fabbed_object)

    summarize(raw_results.get_all_data())
    # some processing to the test values...
    summarize(test_values.get_all_data())

@fedt_experiment
def force_response():
    fabbed_object = PYRAMID

    ground_truth = BatchMeasurements.empty()
    test_values = BatchMeasurements.empty()

    forces = list(arange(10,90+include_last,20))

    for participant in Parallel(range(10)):
        for force_level in [0,100]:
            User.do(fabbed_object, f"touch the top with {force_level}% force", participant)
            ground_truth += CustomCapacitanceSystem.measure_capacitances(fabbed_object)
        for force in Series(latinsquare(len(forces))[participant % len(forces)]): # not sure how many repetitions
            User.do(fabbed_object, f"touch with force {force}", participant)
            test_values += CustomCapacitanceSystem.measure_capacitances(fabbed_object)

    summarize(ground_truth.get_all_data())
    # some processing to the test_values...
    summarize(test_values.get_all_data())


if __name__ == "__main__":
    render_flowchart(placement_response)
    #render_flowchart(force_response)