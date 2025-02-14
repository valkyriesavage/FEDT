import math

from numpy import arange

from design import VirtualWorldObject
from instruction import instruction
from iterators import Series, Parallel, Infinite, include_last
from fabricate import RealWorldObject
from flowchart_render import render_flowchart
from measurement import BatchMeasurements, ImmediateMeasurements
from decorator import fedt_experiment
from fabricate import RealWorldObject
from flowchart_render import render_flowchart
from lib import *

def summarize(data):
    return "Oh wow, great data!"

electripop_laser_defaults = {
    Laser.MATERIAL: 'mylar',
    Laser.CUT_SPEED: 100,
    Laser.CUT_POWER: 5
}

class ManualGeometryScanner:
    geometry_scan = Measurement(
        name="manual geometry scan",
        description="A full copy of the object's geometry, stored in a file.",
        procedure="""
            Take a photograph of the object from 3 angles,
            and extract the profiles from it into Blender.
            """,
        units="filename",
        feature="full object")

    @staticmethod
    def scan(obj: RealWorldObject) -> BatchMeasurements:
        instruction(f"Scan object #{obj.uid}.", header=True)
        instruction(ManualGeometryScanner.geometry_scan.procedure)
        return BatchMeasurements.single(obj, ManualGeometryScanner.geometry_scan)

class CustomSimulator:
    def runsimulation(*args, **kwargs):
        pass

@fedt_experiment
def optimize_simulation():

    test_files = [GeometryFile(fname) for fname in ['compound_slits.svg', 'nested_flaps.svg', 'dragonfly.svg']]

    ground_truths = BatchMeasurements.empty()
    simmed = BatchMeasurements.empty()

    for f in Parallel(test_files):
        fabbed_object = Laser.fab(f, default_settings=electripop_laser_defaults) # not clear what machine was used. they also mention vinyl cutters and scissors
        ground_truths += ManualGeometryScanner.scan(fabbed_object)
        for weight_of_be_exp in Parallel(arange(-3,6+include_last)):
            for weight_of_ee_exp in Parallel(arange(-1, 1+include_last, .2)):
                sim = VirtualWorldObject('file.sim', {'weight of bending energy': math.pow(10, weight_of_be_exp),
                                            'weight of electrical energy': math.pow(10, weight_of_ee_exp),
                                            'file': CustomSimulator.runsimulation(f, weight_of_be_exp, weight_of_ee_exp)})
                simmed += ManualGeometryScanner.scan(sim)
        
    summarize(ground_truths.get_all_data())
    summarize(simmed.get_all_data())

@fedt_experiment
def electrical_inflation():
    # not sure if this is an experiment. it takes "on the order of 10ms to fully saturate the mylar with charge"
    # but it's not clear if this was tested on more than one object or more than one repetition
    pass

@fedt_experiment
def physical_inflation():
    fabbed_objects = [Laser.fab(GeometryFile(fname), default_settings=electripop_laser_defaults) for fname in ['snowman.svg','christmas_tree.svg']]
    
    elapsed_times = BatchMeasurements.empty()
    for obj in Parallel(fabbed_objects):
        # were there repetitions? were there other objects? mention of "remarkably consistent", and implication that some others were tested
        elapsed_times += Stopwatch.measure_time(obj, "inflate to full")
    
    summarize(elapsed_times.get_all_data())
    

@fedt_experiment
def electrical_deflation():
    snowman = Laser.fab(GeometryFile('snowman.svg'), default_settings=electripop_laser_defaults)

    current_measures = ImmediateMeasurements.empty()
    instruction('connect a 1kOhm resistor to the plate')
    current = 9999999999
    while current > 0:
        current = current_measures.do_measure(snowman, Multimeter.current)
        current = float(current) if current else 99999999
        current_measures += Timestamper.get_ts(snowman)

    summarize(current_measures.dump_to_csv())

@fedt_experiment
def physical_deflation():
    # discuss whether this is an experiment, or a measurement/characterization
    snowman = Laser.fab(GeometryFile('snowman.svg'), default_settings=electripop_laser_defaults)
    elapsed_times = BatchMeasurements.empty()
    elapsed_times += Stopwatch.measure_time(snowman, "deflate fully")
    summarize(elapsed_times.get_all_data())

@fedt_experiment
def volumetric_change():
    # discuss whether this is an experiment, or a measurement/characterization
    instruction("set up the snowman linefile and programmatically inflate it")
    snowman_virt = GeometryFile('snowman.svg')
    snowman_phys = Laser.fab(snowman_virt, default_settings=electripop_laser_defaults)
    volumes = BatchMeasurements.empty()
    volumes += ManualGeometryScanner.scan(snowman_phys)
    volumes += ManualGeometryScanner.scan(snowman_virt)
    summarize(volumes.get_all_data())

@fedt_experiment
def fabrication_time():
    # discuss whether this is an experiment, or a measurement/characterization
    snowman = GeometryFile('snowman.svg')
    elapsed_times = BatchMeasurements.empty()
    elapsed_times += Stopwatch.measure_time(snowman, "fabricate on the laser")
    summarize(elapsed_times.get_all_data())

@fedt_experiment
def geometric_accuracy():

    test_files = [GeometryFile(fname) for fname in ['rose.svg', 'snowman.svg', 'christmas_tree.svg']]

    ground_truths = BatchMeasurements.empty()
    simmed = BatchMeasurements.empty()

    for f in Parallel(test_files):
        fabbed_object = Laser.fab(f, default_settings=electripop_laser_defaults) # not clear what machine was used. they also mention vinyl cutters and scissors
        ground_truths += ManualGeometryScanner.scan(fabbed_object)
        for sim_repetition in Parallel(range(100)):
            sim = VirtualWorldObject({'file': CustomSimulator.runsimulation(f)})
            simmed += ManualGeometryScanner.scan(sim)
            simmed += Stopwatch.measure_time(sim, "converge simulation")
        
    summarize(ground_truths.get_all_data())
    summarize(simmed.get_all_data())

@fedt_experiment
def user_experience():
    # not an experiment, but rather a study
    pass

if __name__ == "__main__":
    render_flowchart(optimize_simulation)
    render_flowchart(physical_inflation)
    render_flowchart(electrical_inflation)
    render_flowchart(electrical_deflation)
    render_flowchart(physical_deflation)
    render_flowchart(fabrication_time)
    render_flowchart(geometric_accuracy)
