import random

from numpy import arange

from instruction import instruction
from measurement import Measurements
from design import VolumeFile
from decorator import fedt_experiment
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
    
    estimated_location = Measurement(
        name="estimated location",
        description="The estimated location of a touch on the object.",
        procedure="""
            Have the user touch the object, then capture and post-process the output.
            """,
        units="xyz location",
        feature=f"n/a")
    
    force = Measurement(
        name="capacitance at force",
        description="The capacitance of the object at a given force %.",
        procedure="""
            Have the user touch the object at the force level in feature, then measure the capacitance.
            """,
        units="pF at % of max force",
        feature=f"100")
    
    estimated_force = Measurement(
        name="estimated force",
        description="The estimated force of a touch on the object.",
        procedure="""
            Have the user touch the object, then capture and post-process the output.
            """,
        units="% of max force",
        feature=f"n/a")

    @staticmethod
    def measure_capacitances(obj: RealWorldObject) -> Measurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        return Measurements.multiple(obj, set(CustomCapacitanceSystem.capacitances))
    
    @staticmethod
    def estimate_location(obj: RealWorldObject) -> Measurements:
        instruction(CustomCapacitanceSystem.estimated_location.procedure)
        return Measurements.single(obj, CustomCapacitanceSystem.estimated_location)
    
    @staticmethod
    def get_capacitance_at_force(obj: RealWorldObject, force_level=force.feature) -> Measurements:
        instruction(CustomCapacitanceSystem.estimated_force.procedure)
        instruction(f"Force level: {force_level}")
        return Measurements.single(obj, CustomCapacitanceSystem.estimated_force.set_feature(force_level))
    
    @staticmethod
    def estimate_force(obj: RealWorldObject) -> Measurements:
        instruction(CustomCapacitanceSystem.estimated_force.procedure)
        return Measurements.single(obj, CustomCapacitanceSystem.estimated_force)

@fedt_experiment
def placement_response():
    geometry_file = VolumeFile("pyramid.stl")

    for coverage_condition in ['high','low']:
        for distance_condition in ['near','far']:
            for mirror_condition in range(1,2):
                StlEditor.edit(geometry_file, f"add an electrode with coverage {coverage_condition} and distance {distance_condition}")

    electrodes = list(range(7))

    fabbed_object = Printer.slice_and_print(geometry_file)
    raw_results = Measurements.empty()
    processed_results = Measurements.empty()
    for participant in range(10):
        for repetition in range(1): # not sure how many random touches were required
            User.do(fabbed_object, f"touch electrode #{random.choice(electrodes)}", participant)
        for touch in latinsquare(electrodes, repetitions=10): # how was the square truncated?
            User.do(fabbed_object, f"touch electrode #{touch}", participant)
            raw_results += CustomCapacitanceSystem.measure_capacitances(fabbed_object)
            processed_results += CustomCapacitanceSystem.estimate_location(fabbed_object)

    summarize(raw_results.get_data())
    summarize(processed_results.get_data())

@fedt_experiment
def force_response():
    fabbed_object = reuse_from_above_experiment() # !!!!! ?? how to do ??

    ground_truth = Measurements.empty()
    processed_results = Measurements.empty()

    forces = list(arange(10,90+include_last,20))

    for participant in range(10):
        for force_level in [0,100]:
            User.do(fabbed_object, f"touch the top with {force_level}% force", participant)
            ground_truth += CustomCapacitanceSystem.get_capacitance_at_force(fabbed_object, str(force_level))
        for force in latinsquare(forces, repetitions=1): # not sure how many repetitions
            User.do(fabbed_object, f"touch with force {force}", participant)
            processed_results += CustomCapacitanceSystem.estimate_force(fabbed_object)

    summarize(ground_truth.get_data())
    summarize(processed_results.get_data())


if __name__ == "__main__":
    print(placement_response())
